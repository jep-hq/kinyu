from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel
from sqlalchemy import text

class UUIDMixin(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
        nullable=False
    )

class SoftDeleteMixin(SQLModel):
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

class TenantMixin(SQLModel):
    # We use String to store Zitadel Org ID (which are usually strings of numbers)
    # We remove the foreign key constraint for now to avoid complexity if local Tenant table is partial
    tenant_id: str = Field(index=True, nullable=False, description="Zitadel Organization ID")

class AuditMixin(SQLModel):
    created_by: str = Field(default="system", max_length=255, nullable=False, description="Zitadel User Sub")
    updated_by: str = Field(default="system", max_length=255, nullable=False, description="Zitadel User Sub")
