from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# --- Product Variant Schemas ---

class ProductVariantBase(BaseModel):
    title: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Decimal = Field(default=0)
    compare_at_price: Optional[Decimal] = None
    cost_per_item: Optional[Decimal] = None
    inventory_quantity: int = 0
    inventory_management: str = "shop"
    inventory_policy: str = "deny"
    weight: Optional[Decimal] = None
    weight_unit: str = "kg"

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantUpdate(BaseModel):
    title: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    cost_per_item: Optional[Decimal] = None
    inventory_quantity: Optional[int] = None
    inventory_management: Optional[str] = None
    inventory_policy: Optional[str] = None
    weight: Optional[Decimal] = None
    weight_unit: Optional[str] = None

class ProductVariantResponse(ProductVariantBase):
    id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Product Schemas ---

class ProductBase(BaseModel):
    title: str
    handle: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = []
    status: str = "draft"
    options: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []

class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = []
    collection_ids: List[UUID] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    handle: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[Dict[str, Any]]] = None
    collection_ids: Optional[List[UUID]] = None

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    variants: List[ProductVariantResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Collection Schemas ---

class CollectionBase(BaseModel):
    title: str
    handle: str
    description: Optional[str] = None
    type: str = "manual"
    rules: Optional[Dict[str, Any]] = None
    image_id: Optional[UUID] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(BaseModel):
    title: Optional[str] = None
    handle: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    image_id: Optional[UUID] = None

class CollectionResponse(CollectionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    products: List[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)
