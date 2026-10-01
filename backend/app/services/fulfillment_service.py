from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.services.base import BaseService
from app.models.fulfillment import Fulfillment, FulfillmentItem
from app.models.ecommerce import Order, LineItem
from app.schemas.order_ops import FulfillmentCreate
from app.repositories.base import BaseRepository
from fastapi import HTTPException

from uuid import UUID

class FulfillmentService(BaseService[Fulfillment]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Fulfillment, session, tenant_id))

    async def create_fulfillment(self, order_id: str, data: FulfillmentCreate) -> Fulfillment:
        # 1. Get Order with Line Items
        order = await self.repository.session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # 2. Extract Line Items map for validation
        # We need to ensure we don't fulfill more than ordered
        # (Simplified logic: In production, check against existing fulfillments)

        # 3. Create Fulfillment Record
        fulfillment = Fulfillment(
            order_id=order_id,
            status="success", # Assuming direct success for manual entry
            tracking_number=data.tracking_number,
            tracking_company=data.tracking_company,
            tracking_url=data.tracking_url,
            tenant_id=self.repository.tenant_id
        )
        self.repository.session.add(fulfillment)
        await self.repository.session.commit()
        await self.repository.session.refresh(fulfillment)

        # 4. Create Fulfillment Items
        for item in data.items:
            f_item = FulfillmentItem(
                fulfillment_id=fulfillment.id,
                line_item_id=item.line_item_id,
                quantity=item.quantity,
                tenant_id=self.repository.tenant_id
            )
            self.repository.session.add(f_item)

        # 5. Update Order Status
        # Check if all items are fulfilled (Simplistic check)
        order.fulfillment_status = "fulfilled"
        self.repository.session.add(order)

        await self.repository.session.commit()
        await self.repository.session.refresh(fulfillment)

        # TODO: Trigger email notification if data.notify_customer is True

        return fulfillment
