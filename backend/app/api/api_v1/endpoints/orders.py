from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.ecommerce import Order
from app.models.fulfillment import Fulfillment
from app.models.accounting import Invoice, Refund
from app.schemas.order_ops import FulfillmentCreate, InvoiceCreate, RefundCreate
from app.services.order_service import OrderService
from app.services.fulfillment_service import FulfillmentService
from app.services.accounting_service import InvoiceService, RefundService
from uuid import UUID

router = APIRouter()

# --- Standard Order CRUD ---
@router.get("/", response_model=List[Order])
async def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
    # current_user: User = Depends(deps.get_current_active_superuser) # Admin only
) -> Any:
    service = OrderService(db, tenant_id)
    return await service.get_list(skip=skip, limit=limit)

@router.get("/{id}", response_model=Order)
async def read_order(
    id: str,
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    service = OrderService(db, tenant_id)
    order = await service.get(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
    service = OrderService(db)
    order = await service.get(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# --- Order Operations ---

@router.post("/{id}/fulfillments", response_model=Fulfillment)
async def create_fulfillment(
    id: str,
    fulfillment_in: FulfillmentCreate,
    db: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Mark order line items as fulfilled (shipped).
    """
    service = FulfillmentService(db)
    return await service.create_fulfillment(order_id=id, data=fulfillment_in)

@router.post("/{id}/invoices", response_model=Invoice)
async def create_invoice(
    id: str,
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Generate an invoice for an order.
    """
    service = InvoiceService(db)
    return await service.create_invoice(order_id=id, data=invoice_in)

@router.post("/{id}/refunds", response_model=Refund)
async def create_refund(
    id: str,
    refund_in: RefundCreate,
    db: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Refund an order and optionally restock items.
    """
    service = RefundService(db)
    return await service.create_refund(order_id=id, data=refund_in)
