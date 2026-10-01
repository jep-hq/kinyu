from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import UUIDMixin, TimestampMixin, TenantMixin
from app.models.ecommerce import Order
import uuid

class Fulfillment(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    status: str = Field(default="pending") # pending, open, success, cancelled, error, failure

    tracking_company: Optional[str] = None # e.g. "DHL", "UPS"
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None

    # Relationships
    order: Optional[Order] = Relationship()
    items: List["FulfillmentItem"] = Relationship(back_populates="fulfillment")

class FulfillmentItem(UUIDMixin, TenantMixin, table=True):
    fulfillment_id: uuid.UUID = Field(foreign_key="fulfillment.id")
    line_item_id: uuid.UUID = Field(foreign_key="lineitem.id") # Link to specific line item
    quantity: int

    fulfillment: Optional[Fulfillment] = Relationship(back_populates="items")
