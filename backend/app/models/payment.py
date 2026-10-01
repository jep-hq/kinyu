from typing import Optional, Dict, Any
import uuid
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from app.models.base import UUIDMixin, TimestampMixin, TenantMixin

class Transaction(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    gateway_reference: str = Field(index=True) # Mollie ID tr_xxxx
    gateway: str = Field(default="mollie")

    amount: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(default="USD")

    status: str = Field(index=True) # open, pending, paid, failed, expired, canceled, refunded
    payment_method: Optional[str] = None # ideal, creditcard, etc.

    metadata_log: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # Store full webhook payload/logs

    # order: Relationship would be defined here if needed, but circular imports to be avoided.
    # Usually we resolve this in `__init__` or using string forward references successfully handled by SQLModel.
