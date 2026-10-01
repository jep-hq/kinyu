from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.auth import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_session),
    password: str = Body(None),
    first_name: str = Body(None),
    last_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_user),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Update own user.
    """
    user_service = UserService(db, tenant_id=tenant_id)
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if first_name is not None:
        user_in.first_name = first_name
    if last_name is not None:
        user_in.last_name = last_name
    if email is not None:
        user_in.email = email

    user = await user_service.update(db_obj=current_user, obj_in=user_in)
    return user
