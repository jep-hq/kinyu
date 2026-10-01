from typing import List, Any
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_tenant_db, RequirePermission, get_current_user, ZitadelUser
from app.models.ecommerce import Customer
from app.models.base import AuditMixin, TenantMixin, UUIDMixin

router = APIRouter()

# --------------------------------------------------------------------------
# SUPER-ADMIN / BACKOFFICE DEMO ROUTER
# --------------------------------------------------------------------------

@router.get("/me", response_model=ZitadelUser)
async def get_my_info(
    current_user: ZitadelUser = Depends(get_current_user)
):
    """
    Public debug endpoint to see what claims Zitadel provided.
    """
    return current_user

@router.get(
    "/customers",
    dependencies=[Depends(RequirePermission("customers.read"))]
)
async def list_customers(
    db: AsyncSession = Depends(get_tenant_db)
):
    """
    Lists all customers.
    Security:
    - OIDC Validated (get_tenant_db implies get_current_user)
    - Permission Check: "customers.read"
    - Row-Level Security: Only returns customers where tenant_id == current_user.org_id
    """
    # Developers just write "select(Customer)".
    # The magical 'db' dependency injects "WHERE tenant_id = '...'" automatically.
    statement = select(Customer)
    result = await db.exec(statement)
    return result.all()

@router.post(
    "/customers",
    dependencies=[Depends(RequirePermission("customers.write"))]
)
async def create_customer(
    customer_in: Customer,
    db: AsyncSession = Depends(get_tenant_db)
):
    """
    Creates a user.
    Security:
    - Auto-injection: 'tenant_id', 'created_by', 'updated_by' are set automatically by the session hook.
    """
    # Note: customer_in usually comes from a Schema, but for this demo using Model
    # We add it to session
    db.add(customer_in)
    await db.commit()
    await db.refresh(customer_in)
    return customer_in
