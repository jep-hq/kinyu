from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from decimal import Decimal

# --- Fulfillment ---
class FulfillmentItemCreate(BaseModel):
    line_item_id: str
    quantity: int

class FulfillmentCreate(BaseModel):
    items: List[FulfillmentItemCreate]
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = None
    tracking_url: Optional[str] = None
    notify_customer: bool = True

# --- Invoice ---
class InvoiceCreate(BaseModel):
    due_date: Optional[date] = None
    note: Optional[str] = None

# --- Refund ---
class RefundLineItemCreate(BaseModel):
    line_item_id: str
    quantity: int
    restock_type: str = "no_restock" # return, cancel, no_restock

class RefundCreate(BaseModel):
    items: List[RefundLineItemCreate]
    amount: Decimal # Can be explicitly set (e.g. partial refund shipping) or calculated
    reason: Optional[str] = None
    notify_customer: bool = True
