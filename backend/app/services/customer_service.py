from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base import BaseService
from app.repositories.base import BaseRepository
from app.models.ecommerce import Customer, Address
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.security import get_password_hash

class CustomerService(BaseService[Customer]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Customer, session, tenant_id))

    async def get_with_addresses(self, id: UUID) -> Optional[Customer]:
        statement = select(Customer).options(selectinload(Customer.addresses)).where(Customer.id == id)
        if self.repository.tenant_id:
             statement = statement.where(Customer.tenant_id == self.repository.tenant_id)
        result = await self.repository.session.exec(statement)
        return result.first()

    async def get_list_with_addresses(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        statement = select(Customer).options(selectinload(Customer.addresses)).offset(skip).limit(limit)
        result = await self.repository.session.exec(statement)
        return result.all()

    async def create_customer(self, obj_in: CustomerCreate) -> Customer:
        customer_data = obj_in.model_dump(exclude={"addresses", "password"})
        if obj_in.password:
            customer_data["password_hash"] = get_password_hash(obj_in.password)

        db_customer = Customer(**customer_data)

        if obj_in.addresses:
            for address_in in obj_in.addresses:
                address = Address(**address_in.model_dump())
                db_customer.addresses.append(address)

        self.repository.session.add(db_customer)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_customer)
        return await self.get_with_addresses(db_customer.id)

    async def update_customer(self, customer_id: UUID, obj_in: CustomerUpdate) -> Optional[Customer]:
        db_customer = await self.get(customer_id) # Don't strictly need addresses for update, but good to have context
        if not db_customer:
            return None

        update_data = obj_in.model_dump(exclude_unset=True, exclude={"password"})
        if obj_in.password:
            update_data["password_hash"] = get_password_hash(obj_in.password)

        for key, value in update_data.items():
            setattr(db_customer, key, value)

        self.repository.session.add(db_customer)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_customer)
        return db_customer

