import asyncio
import os
import sys
import httpx
import time
from typing import Dict, Any

# Configuration
ZITADEL_URL = os.getenv("ZITADEL_ISSUER", "http://localhost:8080")
PAT = os.getenv("ZITADEL_FIRST_INSTANCE_PAT", "kinyu-bootstrap-pat-2026")
ORG_NAME = "Kinyu"
PROJECT_NAME = "Kinyu Commerce"
API_APP_NAME = "Kinyu Backend API"
FRONTEND_APP_NAME = "Kinyu Storefront"

headers = {
    "Authorization": f"Bearer {PAT}",
    "Content-Type": "application/json",
    "x-zitadel-orgid": "" # Will be filled dynamically
}

async def wait_for_zitadel():
    """Waits for Zitadel to be healthy."""
    print(f"Waiting for Zitadel at {ZITADEL_URL}...")
    async with httpx.AsyncClient() as client:
        retries = 0
        while retries < 60:
            try:
                resp = await client.get(f"{ZITADEL_URL}/debug/healthz")
                if resp.status_code == 200:
                    print("Zitadel is healthy!")
                    return
            except Exception:
                pass

            sys.stdout.write(".")
            sys.stdout.flush()
            await asyncio.sleep(2)
            retries += 1
        raise Exception("Zitadel failed to become ready.")

async def get_or_create_project(client: httpx.AsyncClient, org_id: str) -> str:
    """Creates the main project if it doesn't exist."""
    print("Checking Projects...")
    # List projects
    resp = await client.post(
        f"{ZITADEL_URL}/management/v1/projects/_search",
        headers={**headers, "x-zitadel-orgid": org_id},
        json={}
    )
    resp.raise_for_status()
    projects = resp.json().get("result", [])

    for p in projects:
        if p["name"] == PROJECT_NAME:
            print(f"Project '{PROJECT_NAME}' exists (ID: {p['id']})")
            return p["id"]

    print(f"Creating Project '{PROJECT_NAME}'...")
    resp = await client.post(
        f"{ZITADEL_URL}/management/v1/projects",
        headers={**headers, "x-zitadel-orgid": org_id},
        json={"name": PROJECT_NAME, "projectRoleAssertion": True, "projectRoleCheck": True}
    )
    resp.raise_for_status()
    project_id = resp.json()["id"]
    print(f"Project created with ID: {project_id}")
    return project_id

async def ensure_roles(client: httpx.AsyncClient, project_id: str, org_id: str):
    """Ensures Admin and Editor roles exist."""
    roles = ["admin", "editor", "customer"]

    print("Ensuring Roles...")
    # Get existing roles
    resp = await client.post(
        f"{ZITADEL_URL}/management/v1/projects/{project_id}/roles/_search",
        headers={**headers, "x-zitadel-orgid": org_id},
        json={}
    )
    existing_keys = [r["key"] for r in resp.json().get("result", [])]

    for role in roles:
        if role not in existing_keys:
            print(f"Creating Role: {role}")
            await client.post(
                f"{ZITADEL_URL}/management/v1/projects/{project_id}/roles",
                headers={**headers, "x-zitadel-orgid": org_id},
                json={"key": role, "displayName": role.capitalize(), "group": "Global"}
            )
        else:
            print(f"Role {role} exists.")

async def get_or_create_app(client: httpx.AsyncClient, project_id: str, org_id: str, app_name: str, app_type: str) -> Dict[str, Any]:
    """Creates an OIDC App."""
    print(f"Checking App '{app_name}'...")

    resp = await client.post(
        f"{ZITADEL_URL}/management/v1/projects/{project_id}/apps/_search",
        headers={**headers, "x-zitadel-orgid": org_id},
        json={}
    )
    apps = resp.json().get("result", [])
    for app in apps:
        if app["name"] == app_name:
            print(f"App '{app_name}' exists (ID: {app['id']})")
            # We can't retrieve the secret again, usually.
            return app

    print(f"Creating App '{app_name}'...")

    payload = {
        "name": app_name,
        "oidc": {}
    }

    if app_type == "spa":
        # Frontend
        payload["oidc"] = {
            "responseTypes": ["OIDC_RESPONSE_TYPE_CODE"],
            "grantTypes": ["OIDC_GRANT_TYPE_AUTHORIZATION_CODE"],
            "appType": "OIDC_APP_TYPE_USER_AGENT",
            "authMethodType": "OIDC_AUTH_METHOD_TYPE_NONE",
            "redirectUris": ["http://localhost:3000/api/auth/callback/zitadel"],
            "postLogoutRedirectUris": ["http://localhost:3000"]
        }
    elif app_type == "api":
        # Backend API Introspection env
        payload["oidc"] = {
            "responseTypes": ["OIDC_RESPONSE_TYPE_CODE"],
            "grantTypes": ["OIDC_GRANT_TYPE_AUTHORIZATION_CODE", "OIDC_GRANT_TYPE_REFRESH_TOKEN"],
            "appType": "OIDC_APP_TYPE_WEB",
            "authMethodType": "OIDC_AUTH_METHOD_TYPE_BASIC",
            "redirectUris": ["http://localhost:8000/docs/oauth2-redirect"],
            "devMode": True
        }

    resp = await client.post(
        f"{ZITADEL_URL}/management/v1/projects/{project_id}/apps/oidc",
        headers={**headers, "x-zitadel-orgid": org_id},
        json=payload
    )
    if resp.status_code != 200:
        print(f"Error creating app: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    print(f"App '{app_name}' created. Client ID: {data['clientId']}")
    if "clientSecret" in data:
        print(f"Client Secret: {data['clientSecret']}")

    return data

async def main():
    await wait_for_zitadel()

    async with httpx.AsyncClient() as client:
        # 1. Get My Org
        print("Getting current Organization...")
        resp = await client.get(
            f"{ZITADEL_URL}/auth/v1/users/me/org",
            headers=headers
        )
        # Note: Depending on PAT, we might default to the first instance org
        if resp.status_code != 200:
            # Fallback: Try to list orgs or assume we are in the default one if PAT is system level
            pass

        # If using the bootstrap PAT, we are likely the System user or Default Org admin
        # Let's get the default org from context or just create one?
        # With bootstrap PAT, usually we act on behalf of the creator.

        # Let's try to search orgs to find "Kinyu" or create it.
        # However, ZITADEL_FIRST_INSTANCE_ORG_NAME created Kinyu.
        # We need its ID.

        # We can look up /auth/v1/orgs if we have permission, or /management/v1/orgs/me

        # Let's try to get details of the current context
        # For simple bootstrap, let's assume the PAT is for the Kinyu org (created on start)

        # We need to find the Org ID to set in header x-zitadel-orgid for management calls
        # We can search for the org by name using V1 System API if we have permissions,
        # but simpler is /auth/v1/users/me/org

        resp = await client.get(f"{ZITADEL_URL}/auth/v1/users/me/org", headers=headers)
        if resp.status_code == 200:
            org = resp.json().get("org", {})
            org_id = org.get("id")
            print(f"Found Context Org: {org.get('name')} ({org_id})")
        else:
             # Fallback to listing
            print("Could not get context org, searching...")
            # This endpoint might vary based on permissions.
            # Assuming Kinyu org exists from docker-compose
            # Let's try to assume we can list projects directly and see if we get an error requesting an orgId
            org_id = "" # Try without?

        if org_id:
            headers["x-zitadel-orgid"] = org_id

        # 2. Get/Create Project
        project_id = await get_or_create_project(client, org_id)

        # 3. Roles
        await ensure_roles(client, project_id, org_id)

        # 4. Apps
        await get_or_create_app(client, project_id, org_id, FRONTEND_APP_NAME, "spa")
        await get_or_create_app(client, project_id, org_id, API_APP_NAME, "api")

        print("\n✅ Setup Complete! Update your .env files with the Client IDs above.")

if __name__ == "__main__":
    asyncio.run(main())
