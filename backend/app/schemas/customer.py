from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

# --- Address Schemas ---
class AddressBase(BaseModel):
    type: str = "shipping"
    company: Optional[str] = None
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country_code: str
    vat_id: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    type: Optional[str] = None
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    vat_id: Optional[str] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Customer Schemas ---

class CustomerBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    marketing_opt_in: bool = False
    tax_exempt: bool = False
    currency: str = "USD"
    tags: List[str] = []
    note: Optional[str] = None

class CustomerCreate(CustomerBase):
    password: Optional[str] = None
    addresses: List[AddressCreate] = []

class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    marketing_opt_in: Optional[bool] = None
    tax_exempt: Optional[bool] = None
    currency: Optional[str] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = None
    password: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    addresses: List[AddressResponse] = []

    model_config = ConfigDict(from_attributes=True)
