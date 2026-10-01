from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from app.models.base import UUIDMixin, TimestampMixin

class Tenant(UUIDMixin, TimestampMixin, table=True):
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    domain: Optional[str] = Field(default=None, unique=True, index=True)
    schema_name: str = Field(default="public")

    # Public configuration (Theme, public features) - readable by frontend
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Private configuration (API Keys, Secrets) - NEVER sent to frontend
    # Stored as encrypted strings or plain JSON (depending on security reqs, assuming securely managed environment)
    secrets: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
