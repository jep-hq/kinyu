from typing import List, Optional, Union, Dict, Any
from uuid import UUID
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base import BaseService
from app.repositories.base import BaseRepository
from app.models.ecommerce import Product, ProductVariant, Collection
from app.schemas.catalog import ProductCreate, ProductUpdate, CollectionCreate, CollectionUpdate, ProductVariantCreate

class ProductService(BaseService[Product]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Product, session, tenant_id))

    async def get_with_variants(self, id: UUID) -> Optional[Product]:
        statement = select(Product).options(selectinload(Product.variants)).where(Product.id == id)
        if self.repository.tenant_id:
            statement = statement.where(Product.tenant_id == self.repository.tenant_id)
        result = await self.repository.session.exec(statement)
        return result.first()

    async def get_list_with_variants(self, skip: int = 0, limit: int = 100) -> List[Product]:
        statement = select(Product).options(selectinload(Product.variants))
        if self.repository.tenant_id:
             statement = statement.where(Product.tenant_id == self.repository.tenant_id)

        statement = statement.offset(skip).limit(limit)
        result = await self.repository.session.exec(statement)
        return result.all()

    async def create_product(self, obj_in: ProductCreate) -> Product:
        product_data = obj_in.model_dump(exclude={"variants", "collection_ids"})
        if self.repository.tenant_id:
            product_data["tenant_id"] = self.repository.tenant_id
        db_product = Product(**product_data)

        if obj_in.variants:
            for variant_in in obj_in.variants:
                variant = ProductVariant(**variant_in.model_dump())
                db_product.variants.append(variant)

        if obj_in.collection_ids:
            statement = select(Collection).where(Collection.id.in_(obj_in.collection_ids))
            collections_result = await self.repository.session.exec(statement)
            db_product.collections.extend(collections_result.all())

        self.repository.session.add(db_product)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_product)
        return await self.get_with_variants(db_product.id)

    async def update_product(self, product_id: UUID, obj_in: ProductUpdate) -> Optional[Product]:
        # Need to load collections too
        statement = select(Product).options(selectinload(Product.variants), selectinload(Product.collections)).where(Product.id == product_id)
        result = await self.repository.session.exec(statement)
        db_product = result.first()

        if not db_product:
            return None

        product_data = obj_in.model_dump(exclude_unset=True, exclude={"collection_ids"})
        for key, value in product_data.items():
            setattr(db_product, key, value)

        if obj_in.collection_ids is not None:
            statement = select(Collection).where(Collection.id.in_(obj_in.collection_ids))
            collections_result = await self.repository.session.exec(statement)
            db_product.collections = collections_result.all()

        self.repository.session.add(db_product)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_product)
        return db_product

    async def add_variant(self, product_id: UUID, variant_in: ProductVariantCreate) -> Optional[Product]:
        product = await self.get(product_id)
        if not product:
            return None

        variant_data = variant_in.model_dump()
        variant_data["product_id"] = product_id
        if self.repository.tenant_id:
            variant_data["tenant_id"] = self.repository.tenant_id

        variant = ProductVariant(**variant_data)
        self.repository.session.add(variant)
        await self.repository.session.commit()
        # Refresh product to get updated variants
        return await self.get_with_variants(product_id)

class CollectionService(BaseService[Collection]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Collection, session, tenant_id))

    async def get_with_products(self, id: UUID) -> Optional[Collection]:
        # Depending on needing products immediately
        statement = select(Collection).options(selectinload(Collection.products)).where(Collection.id == id)
        result = await self.repository.session.exec(statement)
        return result.first()

    async def get_list_with_products(self, skip: int = 0, limit: int = 100) -> List[Collection]:
         statement = select(Collection).options(selectinload(Collection.products)).offset(skip).limit(limit)
         result = await self.repository.session.exec(statement)
         return result.all()
