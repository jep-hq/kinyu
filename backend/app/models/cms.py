from typing import List, Optional, Any, Dict
import uuid
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, UniqueConstraint
from app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin

class SeoMixin(SQLModel):
    seo_title: Optional[str] = Field(default=None)
    seo_description: Optional[str] = Field(default=None)
    seo_keywords: Optional[List[str]] = Field(default=None, sa_type=JSONB)
    og_image_id: Optional[uuid.UUID] = Field(default=None, foreign_key="media_file.id")

class MediaFile(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    __tablename__ = "media_file"
    filename: str
    original_filename: str
    mime_type: str
    size: int
    url: str
    provider: str = Field(default="local") # or "s3", "cloudinary"
    provider_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    alt_text: Optional[str] = None
    caption: Optional[str] = None

class ContentModel(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    """
    Defines the structure of a content type (e.g. 'Article', 'Testimonial')
    resembling a Headless CMS schema definition.
    """
    # Tenant-Scoped Uniqueness enforced via __table_args__
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: Optional[str] = None
    fields_schema: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # JSON Schema

    entries: List["ContentEntry"] = Relationship(back_populates="model")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_contentmodel_tenant_name"),
        UniqueConstraint("tenant_id", "slug", name="uq_contentmodel_tenant_slug"),
    )

class ContentEntry(UUIDMixin, TimestampMixin, SoftDeleteMixin, SeoMixin, TenantMixin, table=True):
    """
    The actual content data.
    """
    model_id: uuid.UUID = Field(foreign_key="contentmodel.id")
    title: str = Field(index=True) # Display title
    slug: str = Field(index=True)
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB)) # Flexible data adhering to fields_schema
    status: str = Field(default="draft") # published, draft, archived

    model: Optional[ContentModel] = Relationship(back_populates="entries")

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_contententry_tenant_slug"),
    )

class Navigation(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    name: str = Field(index=True)
    handle: str = Field(index=True) # e.g. "main-menu", "footer"
    items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB)) # Recursive JSON structure for menu items

    __table_args__ = (
        UniqueConstraint("tenant_id", "handle", name="uq_navigation_tenant_handle"),
    )
