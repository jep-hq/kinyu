from pydantic import BaseModel
from typing import Optional, Dict, Any

class CheckoutRequest(BaseModel):
    cart_token: str
    email: str
    shipping_address: Dict[str, Any]
    billing_address: Optional[Dict[str, Any]] = None

class CheckoutResponse(BaseModel):
    checkout_url: str
    order_id: str
