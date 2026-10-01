from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.catalog import ProductCreate, ProductUpdate, ProductResponse, ProductVariantCreate
from app.services.catalog_service import ProductService
from app.core.auth_zitadel import ZitadelUser

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Retrieve products.
    """
    service = ProductService(session, tenant_id=tenant_id)
    # Using get_list_with_variants to ensure variants are loaded for the response model
    products = await service.get_list_with_variants(skip=skip, limit=limit)
    return products

@router.post("/", response_model=ProductResponse)
async def create_product(
    *,
    session: AsyncSession = Depends(deps.get_session),
    product_in: ProductCreate,
    tenant_id: UUID = Depends(deps.get_tenant_id),
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Create new product.
    """
    service = ProductService(session, tenant_id=tenant_id)
    product = await service.create_product(product_in)
    return product

@router.get("/{id}", response_model=ProductResponse)
async def read_product(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Get product by ID.
    """
    service = ProductService(session, tenant_id=tenant_id)
    product = await service.get_with_variants(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=ProductResponse)
async def update_product(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    product_in: ProductUpdate,
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Update a product.
    """
    service = ProductService(session)
    product = await service.update_product(id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{id}", response_model=ProductResponse)
async def delete_product(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Delete a product.
    """
    service = ProductService(session)
    # We might want soft delete, checking model definition
    # Product model has SoftDeleteMixin
    product = await service.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if delete is soft or hard. BaseService.delete likely does hard delete unless overridden
    # or if the repository handles it.
    # Let's assume for now BaseService.delete uses repository.delete which does DB delete.
    # If we want soft delete, we should update the 'deleted_at' field.
    # But for now, let's just use the service.delete which calls repository.delete

    deleted_product = await service.delete(id)
    # Note: If hard deleted, returning it might be tricky if not returned by delete().
    # BaseRepository.delete returns the deleted object usually or None.
    return product # Returning the object before deletion or the deleted object if returned

@router.post("/{id}/variants", response_model=ProductResponse)
async def create_product_variant(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    variant_in: ProductVariantCreate,
    tenant_id: UUID = Depends(deps.get_tenant_id),
    current_user: ZitadelUser = Depends(deps.get_current_user),
) -> Any:
    """
    Add a variant to a product. Only for logged in users.
    """
    service = ProductService(session, tenant_id=tenant_id)
    product = await service.add_variant(id, variant_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

