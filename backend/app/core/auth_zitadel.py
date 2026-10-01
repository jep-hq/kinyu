import logging
import os
from typing import Optional, List, Dict, Any

import httpx
from fastapi import HTTPException, status
from jose import jwt
from jose.exceptions import JOSEError
from pydantic import BaseModel

from app.core.config import settings

# In-memory cache for OIDC config and JWKS
_oidc_config: Dict[str, Any] = {}
_jwks: Dict[str, Any] = {}

class ZitadelUser(BaseModel):
    sub: str
    email: Optional[str] = None
    email_verified: bool = False
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    preferred_username: Optional[str] = None
    # Tenant Info
    org_id: Optional[str] = None
    org_domain: Optional[str] = None
    # Role Info
    project_roles: List[str] = []

    @property
    def id(self) -> str:
        return self.sub

async def get_oidc_config() -> Dict[str, Any]:
    global _oidc_config
    if _oidc_config:
        return _oidc_config

    issuer = settings.ZITADEL_ISSUER.rstrip("/")
    url = f"{issuer}/.well-known/openid-configuration"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            _oidc_config = resp.json()
            return _oidc_config
        except Exception as e:
            logging.error(f"Failed to fetch OIDC config: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth provider unavailable")

async def get_jwks() -> Dict[str, Any]:
    global _jwks
    if _jwks:
        return _jwks

    config = await get_oidc_config()
    jwks_uri = config.get("jwks_uri")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(jwks_uri)
            resp.raise_for_status()
            _jwks = resp.json()
            return _jwks
        except Exception as e:
            logging.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Key verification failed")

async def verify_token(token: str) -> ZitadelUser:
    jwks = await get_jwks()

    try:
        # 1. Decode header to find Key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise ValueError("Token header missing kid")

        # 2. Find matching key in JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
             # Refresh JWKS once if key not found (maybe key rotation)
             global _jwks
             _jwks = {}
             jwks = await get_jwks()
             key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
             if not key:
                 raise ValueError("Signing key not found")

        # 3. Verify Signature & Claims
        # Zitadel access tokens might not have 'aud' depending on config.
        # We verify issuer at least.
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.ZITADEL_API_AUDIENCE or None, # Optional check
            issuer=settings.ZITADEL_ISSUER,
            options={
                "verify_aud": bool(settings.ZITADEL_API_AUDIENCE),
                "verify_at_hash": False
            }
        )

        # 4. Extract Custom Claims (Zitadel specific)
        # Roles are usually in "urn:zitadel:iam:org:project:roles" map
        # Structure: { "roleKey": { "domain.com": "orgId" } }
        roles = []
        role_map = payload.get("urn:zitadel:iam:org:project:roles", {})
        if role_map:
            # We flatten this: just get keys
             roles = list(role_map.keys())

        # Extract Org context from Custom Claims if available or standard claim
        # "urn:zitadel:iam:org:id": "123..."
        org_id = payload.get("urn:zitadel:iam:org:id")

        return ZitadelUser(
            sub=payload["sub"],
            email=payload.get("email"),
            email_verified=payload.get("email_verified", False),
            name=payload.get("name"),
            given_name=payload.get("given_name"),
            family_name=payload.get("family_name"),
            preferred_username=payload.get("preferred_username"),
            org_id=org_id,
            project_roles=roles
        )

    except (JOSEError, ValueError) as e:
        logging.warning(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
