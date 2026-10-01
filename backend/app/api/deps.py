from typing import AsyncGenerator, Callable, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import event, select
from sqlalchemy.orm import Session, with_loader_criteria
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_factory
from app.core.auth_zitadel import verify_token, ZitadelUser
from app.models.base import TenantMixin, AuditMixin
from app.models.tenant import Tenant

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token", # Not used for flow, just for Swagger UI
    description="OIDC Token from Zitadel",
    auto_error=False # Allow Guest Access (we check token manually)
)

# 1. Base Session (No Tenant Lock)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# 2. Authentication
async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[ZitadelUser]:
    """
    Validates JWT and returns ZitadelUser context if present.
    """
    if not token:
        return None
    try:
        return await verify_token(token)
    except Exception:
        # If token is invalid (expired/bad signature), treat as anonymous/guest
        # instead of hard 401, unless endpoint explicitly requires auth.
        return None

async def get_current_user(user: Optional[ZitadelUser] = Depends(get_current_user_optional)) -> ZitadelUser:
    """ Enforce Authentication """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# 3. Tenant Resolution
async def get_tenant_from_host(request: Request) -> Optional[UUID]:
    # Extract host (ignore port)
    host = request.headers.get("host", "").split(":")[0]

    # Use a raw session to find tenant by domain
    async with async_session_factory() as session:
        statement = select(Tenant).where((Tenant.domain == host) | (Tenant.slug == host))
        result = await session.execute(statement)
        tenant = result.scalar_one_or_none()
        if tenant:
            return tenant.id
    return None

async def get_tenant_id(
    request: Request,
    user: Optional[ZitadelUser] = Depends(get_current_user_optional)
) -> UUID:
    tenant_id: Optional[UUID] = None

    # A. User Context (Strongest Source set by Zitadel)
    if user and user.org_id:
        try:
            tenant_id = UUID(user.org_id)
        except ValueError:
            pass # Invalid UUID from token?

    # B. Host Context (Public/Guest)
    host_tenant_id = await get_tenant_from_host(request)

    # C. Security Cross-Check (The "Confused Deputy" Protection)
    if tenant_id and host_tenant_id:
        if tenant_id != host_tenant_id:
             # User belongs to Tenant A but is visiting Tenant B's domain
             # We BLOCK this to prevent accidental data leaks or modifying wrong tenant data
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN,
                 detail=f"Cross-Tenant Access Forbidden. You are logged into Tenant {tenant_id} but accessing {host_tenant_id}"
             )

    # D. Selection
    final_id = tenant_id or host_tenant_id

    if not final_id:
        # We cannot identify who owns this data. Block request.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not identified from Host or Token"
        )

    return final_id

# 4. RBAC Factory
class RequirePermission:
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, user: ZitadelUser = Depends(get_current_user)):
        if self.role not in user.project_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {self.role}"
            )
        return True

# 5. Strict Multi-Tenancy DB Session
async def get_tenant_db(
    tenant_id: UUID = Depends(get_tenant_id),
    user: Optional[ZitadelUser] = Depends(get_current_user_optional)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Returns a Database Session that is:
    1. Restricted to the Resolved Tenant (ROW LEVEL SECURITY).
    2. Automatically populates Audit fields.
    """

    # Function to apply Tenant Filter to all queries
    def _tenant_filter_do_orm_execute(orm_execute_state):
        if (
            orm_execute_state.is_select
            or orm_execute_state.is_update
            or orm_execute_state.is_delete
        ):
            orm_execute_state.session.enable_relationship_loading(orm_execute_state)
            orm_execute_state.statement = orm_execute_state.statement.options(
                with_loader_criteria(
                    TenantMixin,
                    lambda cls: cls.tenant_id == tenant_id,
                    include_aliases=True
                )
            )

    # Function to inject Tenant ID and User ID
    def _audit_before_flush(session, flush_context, instances):
        for instance in session.new:
            if isinstance(instance, TenantMixin):
                if not instance.tenant_id:
                    instance.tenant_id = tenant_id
                elif instance.tenant_id != tenant_id:
                    raise HTTPException(500, "Security Violation: Writes to wrong tenant detected.")

            if isinstance(instance, AuditMixin):
                uid = str(user.id) if user else "guest"
                instance.created_by = uid
                instance.updated_by = uid

        for instance in session.dirty:
            if isinstance(instance, AuditMixin):
                uid = str(user.id) if user else "guest"
                instance.updated_by = uid

    async with async_session_factory() as session:
        sync_session = session.sync_session

        # Apply Security Hooks
        event.listen(sync_session, "do_orm_execute", _tenant_filter_do_orm_execute)
        event.listen(sync_session, "before_flush", _audit_before_flush)

        yield session
