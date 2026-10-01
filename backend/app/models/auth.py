from typing import List, Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import UUIDMixin, TimestampMixin, TenantMixin

# Join Tables
class UserRoleLink(SQLModel, table=True):
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: Optional[uuid.UUID] = Field(default=None, foreign_key="role.id", primary_key=True)

class RolePermissionLink(SQLModel, table=True):
    role_id: Optional[uuid.UUID] = Field(default=None, foreign_key="role.id", primary_key=True)
    permission_id: Optional[uuid.UUID] = Field(default=None, foreign_key="permission.id", primary_key=True)

class Permission(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    slug: str = Field(unique=True, index=True) # e.g., "product:create", "order:read"
    description: Optional[str] = None

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermissionLink)

class Role(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermissionLink)

class User(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    email: str = Field(unique=True, index=True)
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
