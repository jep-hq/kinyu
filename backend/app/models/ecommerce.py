from typing import List, Optional, Any, Dict
import uuid
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, UniqueConstraint
from app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin
from app.models.cms import SeoMixin, MediaFile

# --- Customer Domain ---
class Customer(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    # Tenant-Scoped Uniqueness enforced via __table_args__
    email: str = Field(index=True)
    password_hash: Optional[str] = None # Optional for guest checkout/social auth
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    marketing_opt_in: bool = Field(default=False)

    # B2B & Tax
    tax_exempt: bool = Field(default=False)
    currency: str = Field(default="USD")
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))
    note: Optional[str] = None

    addresses: List["Address"] = Relationship(back_populates="customer")
    orders: List["Order"] = Relationship(back_populates="customer")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_customer_tenant_email"),
    )

class Address(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    customer_id: uuid.UUID = Field(foreign_key="customer.id")
    type: str = Field(default="shipping") # shipping, billing

    company: Optional[str] = None # B2B
    first_name: str
    last_name: str
    phone: Optional[str] = None

    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country_code: str

    # Tax
    vat_id: Optional[str] = None # EU VAT

    is_default: bool = Field(default=False)

    customer: Optional[Customer] = Relationship(back_populates="addresses")

# --- Product Domain ---
class ProductCategoryLink(SQLModel, table=True):
    product_id: Optional[uuid.UUID] = Field(default=None, foreign_key="product.id", primary_key=True)
    collection_id: Optional[uuid.UUID] = Field(default=None, foreign_key="collection.id", primary_key=True)

class Collection(UUIDMixin, TimestampMixin, SeoMixin, TenantMixin, table=True):
    title: str
    handle: str = Field(index=True)
    description: Optional[str] = None
    type: str = Field(default="manual") # manual, smart
    rules: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB)) # For smart collections
    image_id: Optional[uuid.UUID] = Field(default=None, foreign_key="media_file.id")

    products: List["Product"] = Relationship(back_populates="collections", link_model=ProductCategoryLink)

    __table_args__ = (
        UniqueConstraint("tenant_id", "handle", name="uq_collection_tenant_handle"),
    )

class Product(UUIDMixin, TimestampMixin, SoftDeleteMixin, SeoMixin, TenantMixin, table=True):
    title: str
    handle: str = Field(index=True)
    description: Optional[str] = None # HTML/Rich Text
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))
    status: str = Field(default="draft") # active, draft, archived

    options: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB)) # e.g. [{"name": "Size", "values": ["S", "M"]}]

    collections: List[Collection] = Relationship(back_populates="products", link_model=ProductCategoryLink)
    variants: List["ProductVariant"] = Relationship(back_populates="product")
    images: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB)) # List of image objects/IDs with order

    __table_args__ = (
        UniqueConstraint("tenant_id", "handle", name="uq_product_tenant_handle"),
    )

class ProductVariant(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    product_id: uuid.UUID = Field(foreign_key="product.id")
    title: str # e.g. "Small / Red"
    sku: Optional[str] = Field(default=None, index=True)
    barcode: Optional[str] = None

    # Pricing
    price: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    cost_per_item: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2) # Profit calculation

    # Inventory
    inventory_quantity: int = Field(default=0)
    inventory_management: str = Field(default="shop") # shop, null (no tracking)
    inventory_policy: str = Field(default="deny") # deny, continue

    # Shipping & Customs (Shopify Parity)
    weight: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=3)
    weight_unit: str = Field(default="kg") # kg, g, lb, oz
    requires_shipping: bool = Field(default=True)
    hs_code: Optional[str] = None # Harmonized System code
    country_of_origin: Optional[str] = None # ISO Code

    options: Dict[str, str] = Field(default={}, sa_column=Column(JSONB)) # e.g. {"Size": "S", "Color": "Red"}
    image_id: Optional[uuid.UUID] = Field(default=None, foreign_key="media_file.id")

    product: Optional[Product] = Relationship(back_populates="variants")

# --- Cart & Order Domain ---
class Cart(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    # If using DB for cart. Persistent carts can be linked to customers or anonymous tokens.
    customer_id: Optional[uuid.UUID] = Field(default=None, foreign_key="customer.id")
    token: str = Field(unique=True, index=True) # Session/Cookie ID

    items: List["CartItem"] = Relationship(back_populates="cart")

class CartItem(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    cart_id: uuid.UUID = Field(foreign_key="cart.id")
    variant_id: uuid.UUID = Field(foreign_key="productvariant.id")
    quantity: int = Field(default=1)

    cart: Optional[Cart] = Relationship(back_populates="items")
    # variant: Relationship to ProductVariant (omitted for brevity in relations, but implied foreign key is there)

class Order(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    order_number: int = Field(unique=True, sa_column_kwargs={"autoincrement": True})
    customer_id: Optional[uuid.UUID] = Field(default=None, foreign_key="customer.id")
    email: str

    currency_code: str = Field(default="USD")
    total_price: Decimal = Field(max_digits=12, decimal_places=2)

    # Erasure / Cancellation
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None # customer, fraud, inventory, other

    # Meta
    payment_terms: Optional[str] = None # net30, due_on_receipt
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))
    note: Optional[str] = None # Order notes from customer or staff
    total_shipping: Decimal = Field(max_digits=12, decimal_places=2)
    total_discounts: Decimal = Field(max_digits=12, decimal_places=2)

    financial_status: str = Field(default="pending") # pending, paid, refunded, voided
    fulfillment_status: str = Field(default="unfulfilled") # unfulfilled, partial, fulfilled
    status: str = Field(default="open") # open, closed, cancelled

    shipping_address: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # Snapshot
    billing_address: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # Snapshot

    customer: Optional[Customer] = Relationship(back_populates="orders")
    line_items: List["LineItem"] = Relationship(back_populates="order")
    # payments: Relationship to Payment/Transaction

class LineItem(UUIDMixin, TenantMixin, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id")
    variant_id: Optional[uuid.UUID] = Field(foreign_key="productvariant.id") # Optional if product deleted
    product_id: Optional[uuid.UUID] = Field(foreign_key="product.id")

    title: str
    quantity: int
    price: Decimal = Field(max_digits=12, decimal_places=2)
    sku: Optional[str] = None
    variant_title: Optional[str] = None
    vendor: Optional[str] = None

    properties: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # Customizations

    order: Optional[Order] = Relationship(back_populates="line_items")

class Discount(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    code: str = Field(unique=True, index=True)
    type: str # percentage, fixed_amount, shipping
    value: Decimal
    starts_at: datetime
    ends_at: Optional[datetime] = None
    usage_limit: Optional[int] = None
    used_count: int = Field(default=0)
    min_requirements: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # min_subtotal, min_quantity
