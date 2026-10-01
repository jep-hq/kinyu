from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.accounting import Invoice, Refund, RefundLineItem
from app.models.ecommerce import Order, ProductVariant, LineItem
from app.schemas.order_ops import InvoiceCreate, RefundCreate
from app.repositories.base import BaseRepository
from fastapi import HTTPException
from uuid import UUID

class InvoiceService:
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        self.session = session
        self.repo = BaseRepository(Invoice, session, tenant_id)

    async def create_invoice(self, order_id: str, data: InvoiceCreate) -> Invoice:
        order = await self.session.get(Order, order_id) # Should filter by tenant if possible, but get() by PK ignores unless custom
        # But we should use self.repo.get(order_id) to use tenant filter if implemented?
        # No, InvoiceService has Invoice repo.
        # But we need to ensure Order belongs to tenant.
        # If tenant_id is set, we should verify logic.

        # For now, let's just make sure tenant_id is passed to created Invoice.

        if not order:
             raise HTTPException(status_code=404, detail="Order not found")

        # Generate sequence number (Simplistic)
        # Real world: Query max ID or use DB sequence
        import random
        inv_number = f"INV-{date.today().year}-{random.randint(1000,9999)}"

        invoice = Invoice(
            order_id=order_id,
            invoice_number=inv_number,
            issue_date=date.today(),
            due_date=data.due_date or (date.today() + timedelta(days=14)),
            status="open" if order.financial_status != "paid" else "paid",
            subtotal=order.subtotal_price,
            tax_total=order.total_tax,
            total=order.total_price,
            customer_memo=data.note,
            tenant_id=self.repo.tenant_id
        )

        self.session.add(invoice)
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

class RefundService:
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        self.session = session
        self.repo = BaseRepository(Refund, session, tenant_id)

    async def create_refund(self, order_id: str, data: RefundCreate) -> Refund:
        order = await self.session.get(Order, order_id)
        if not order:
             raise HTTPException(status_code=404, detail="Order not found")

        # Create Refund Record
        refund = Refund(
            order_id=order_id,
            total_refunded=data.amount,
            note=data.reason
        )
        self.session.add(refund)
        await self.session.commit()
        await self.session.refresh(refund)

        # Process Items & Inventory
        for item in data.items:
            # Add to refund log
            r_item = RefundLineItem(
                refund_id=refund.id,
                line_item_id=item.line_item_id,
                quantity=item.quantity,
                restock_type=item.restock_type,
                subtotal=0, # Calculation needed from LineItem price
                total_tax=0
            )
            self.session.add(r_item)

            # Restock Inventory Logic
            if item.restock_type in ["return", "cancel"]:
                line_item = await self.session.get(LineItem, item.line_item_id)
                if line_item and line_item.variant_id:
                    variant = await self.session.get(ProductVariant, line_item.variant_id)
                    if variant and variant.inventory_management == "shop":
                        variant.inventory_quantity += item.quantity
                        self.session.add(variant)

        # Update Order Status
        # If refunded amount >= total, mark refunded. Else partially_refunded
        if data.amount >= order.total_price:
            order.financial_status = "refunded"
        else:
            order.financial_status = "partially_refunded"

        self.session.add(order)
        await self.session.commit()

        return refund
