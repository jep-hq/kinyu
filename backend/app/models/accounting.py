from typing import Optional, List
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import UUIDMixin, TimestampMixin, TenantMixin
from app.models.ecommerce import Order

class Invoice(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", unique=True) # Usually 1 invoice per order, but can be many. strict 1:1 for now.
    invoice_number: str = Field(unique=True, index=True) # e.g. "INV-2026-0001"

    status: str = Field(default="draft") # draft, open, paid, void, uncollectible
    issue_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = None

    currency_code: str = Field(default="USD")
    subtotal: Decimal = Field(max_digits=12, decimal_places=2)
    tax_total: Decimal = Field(max_digits=12, decimal_places=2)
    total: Decimal = Field(max_digits=12, decimal_places=2)

    customer_memo: Optional[str] = None

    # Relationships
    order: Optional[Order] = Relationship()

class Refund(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id")

    note: Optional[str] = None
    user_id: Optional[uuid.UUID] = None # Staff member who processed it

    total_refunded: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(default="USD")

    # Relationships
    order: Optional[Order] = Relationship()
    refund_line_items: List["RefundLineItem"] = Relationship(back_populates="refund")

class RefundLineItem(UUIDMixin, TenantMixin, table=True):
    refund_id: uuid.UUID = Field(foreign_key="refund.id")
    line_item_id: uuid.UUID = Field(foreign_key="lineitem.id")
    quantity: int
    restock_type: str = Field(default="no_restock") # no_restock, return, cancel
    subtotal: Decimal = Field(max_digits=12, decimal_places=2)
    total_tax: Decimal = Field(max_digits=12, decimal_places=2)

    refund: Optional[Refund] = Relationship(back_populates="refund_line_items")
