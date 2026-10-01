from typing import Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.services.base import BaseService
from app.models.cms import ContentEntry
from app.repositories.base import BaseRepository

class CMSService(BaseService[ContentEntry]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(ContentEntry, session, tenant_id))

    async def get_by_slug(self, slug: str) -> Optional[ContentEntry]:
        """
        Get a published content entry by slug.
        """
        query = select(ContentEntry).where(ContentEntry.slug == slug)
        if self.repository.tenant_id:
            query = query.where(ContentEntry.tenant_id == self.repository.tenant_id)

        # Filter by published status and not deleted
        # Assuming "published" is the correct status string based on previous Context
        query = query.where(ContentEntry.status == "published")
        query = query.where(ContentEntry.is_deleted == False)

        result = await self.repository.session.exec(query)
        return result.first()

    async def get_all_routes(self) -> list[str]:
        """
        Get all valid public routes for sitemap.
        """
        query = select(ContentEntry.slug).where(ContentEntry.status == "published").where(ContentEntry.is_deleted == False)
        result = await self.repository.session.exec(query)
        slugs = result.all()
        # Ensure they start with /
        return [f"/{slug}" if not slug.startswith("/") else slug for slug in slugs]
