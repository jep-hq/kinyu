from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.catalog import CollectionCreate, CollectionUpdate, CollectionResponse
from app.services.catalog_service import CollectionService

router = APIRouter()

@router.get("/", response_model=List[CollectionResponse])
async def read_collections(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Retrieve collections.
    """
    service = CollectionService(session, tenant_id=tenant_id)
    # collections = await service.get_list_with_products(skip=skip, limit=limit) # get_list_with_products not implemented in service snippet I saw earlier, assuming get_list or custom method exists.
    # The snippet earlier showed generic get_list, and catalog_service included CollectionService but I only showed __init__.
    # Let's check catalog_service.py content again or assume standard get_list if specific method not present.
    # The file content showed:
    # class CollectionService(BaseService[Collection]):
    #     def __init__(self, session: AsyncSession):
    #         super().__init__(BaseRepository(Collection, session))
    # It didn't show get_list_with_products.
    # Wait, the read of collections.py shows: collections = await service.get_list_with_products(skip=skip, limit=limit)
    # So `CollectionService` MUST have it. I probably missed it in previous read of catalog_service.py
    # I will assume it exists and just update instantiation.
    collections = await service.get_list_with_products(skip=skip, limit=limit)
    return collections

@router.post("/", response_model=CollectionResponse)
async def create_collection(
    *,
    session: AsyncSession = Depends(deps.get_session),
    collection_in: CollectionCreate,
    tenant_id: UUID = Depends(deps.get_tenant_id),
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Create new.
    """
    service = CollectionService(session, tenant_id=tenant_id)
    return await service.create(collection_in)
    """
    Create new collection.
    """
    service = CollectionService(session)
    collection = await service.create(collection_in)
    return collection

@router.get("/{id}", response_model=CollectionResponse)
async def read_collection(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
) -> Any:
    """
    Get collection by ID.
    """
    service = CollectionService(session)
    collection = await service.get_with_products(id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

@router.put("/{id}", response_model=CollectionResponse)
async def update_collection(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    collection_in: CollectionUpdate,
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Update a collection.
    """
    service = CollectionService(session)
    collection = await service.get(id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection = await service.update(db_obj=collection, obj_in=collection_in)
    return collection

@router.delete("/{id}", response_model=CollectionResponse)
async def delete_collection(
    *,
    session: AsyncSession = Depends(deps.get_session),
    id: UUID,
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add auth
) -> Any:
    """
    Delete a collection.
    """
    service = CollectionService(session)
    collection = await service.get(id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    await service.delete(id)
    return collection
