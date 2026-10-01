from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return via API
class UserResponse(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
