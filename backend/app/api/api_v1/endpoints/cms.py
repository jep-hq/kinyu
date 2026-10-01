from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.cms_service import CMSService
from app.models.cms import ContentEntry
from uuid import UUID

router = APIRouter()

@router.get("/routes", response_model=List[str])
async def get_all_cms_routes(
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Get all public routes for sitemap generation.
    """
    service = CMSService(db, tenant_id=tenant_id)
    return await service.get_all_routes()

@router.get("/entries/slug/{slug:path}", response_model=ContentEntry)
async def get_content_entry_by_slug(
    slug: str,
    db: AsyncSession = Depends(deps.get_session),
    tenant_id: UUID = Depends(deps.get_tenant_id),
) -> Any:
    """
    Get a content entry by its slug.
    Using {slug:path} to allow slashes in the slug (e.g. "blog/my-post")
    """
    service = CMSService(db, tenant_id=tenant_id)
    entry = await service.get_by_slug(slug)

    if not entry:
        raise HTTPException(status_code=404, detail="Page not found")

    return entry
