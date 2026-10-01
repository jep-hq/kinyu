from typing import Any, Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from uuid import UUID

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_service = UserService(db, tenant_id=tenant_id)
    user = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create tokens
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(user.id)

    # Set Refresh Token in HttpOnly Cookie (More secure for Headless)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=True, # Ensure HTTPS in prod
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_session)
) -> Any:
    """
    Create new user without the need to be logged in
    """
    user_service = UserService(db)
    user = await user_service.get_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = await user_service.create_user(user_in)
    return user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    db: AsyncSession = Depends(deps.get_session),
    refresh_token: str = Body(..., embed=True)
    # Or typically read from cookie: refresh_token: str = Cookie(None)
    # But for API symmetry, sometimes body is used if client manages storage.
    # Given requirements: "inside HttpOnly cookies", we should read from cookie.
):
    # Overriding to read from Cookie manually if Body is empty, or use logic below
    # NOTE: FastAPI's Cookie param is preferred if stricter.
    # For now, let's assume the frontend proxy might pass it or we read from request.
    pass

# Better implementation for Refresh using Cookie
from fastapi import Cookie

@router.post("/refresh-cookie", response_model=Token)
async def refresh_token_cookie(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(deps.get_session)
):
    """
    Get new access token using the refresh token from HttpOnly cookie
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type",
        )

    user_service = UserService(db)
    user = await user_service.get(token_data.sub)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    # Optional: Rotate refresh token
    new_refresh_token = security.create_refresh_token(user.id)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=True,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
