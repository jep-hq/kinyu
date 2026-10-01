from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.checkout import CheckoutRequest, CheckoutResponse
from app.services.order_service import OrderService
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=CheckoutResponse)
async def create_checkout_session(
    checkout_data: CheckoutRequest,
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Converts a cart to an order and initiates the payment flow.
    """
    order_service = OrderService(db, tenant_id=tenant_id)
    return await order_service.create_order_from_cart(checkout_data)
