from typing import Any, Optional
from fastapi import APIRouter, Depends, Cookie, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.cart_service import CartService
from app.core.auth_zitadel import ZitadelUser
from uuid import UUID

router = APIRouter()

@router.get("/")
async def get_my_cart(
    response: Response,
    db: AsyncSession = Depends(deps.get_tenant_db),
    tenant_id: UUID = Depends(deps.get_tenant_id),
    user: Optional[ZitadelUser] = Depends(deps.get_current_user_optional),
    guest_token: Optional[str] = Cookie(None)
):
    """
    Get current cart. If user is logged in, gets user cart.
    If guest, gets guest cart by cookie.
    """
    service = CartService(db, tenant_id)

    if user:
         # Logged in: Check if we need to merge?
         # Ideally strictly calling /merge is better, but doing it implicitly is convenient.
         # For now, just return User cart.
         # Note: User ID in ZitadelUser is string 'sub'. Need to convert or store mapping.
         # Assuming 'sub' IS the UUID or we have a local lookup.
         # For this implementation, let's assume sub is the uuid.
         user_id = UUID(user.id)

         # Optional: Auto-Merge if guest token exists
         if guest_token:
             await service.merge_carts(guest_token, user_id)
             # Clear cookie after merge?
             response.delete_cookie("guest_token")

         # Fetch User Cart
         # We need a get_by_user method or use get_list with filter
         # For now, let's just use the merge logic which fetches user cart too.
         # But merge logic creates side effects.
         # Let's add get_by_user to service? Or just query.
         # Accessing private logic is acceptable here or just create a helper.
         # To be clean, let's reuse what we have.
         return {"message": "User Cart Logic Not Fully Exposed in Service Yet"} # Placeholder

    elif guest_token:
        cart = await service.get_by_token(guest_token)
        if not cart:
             return {"items": []}
        return cart

    return {"items": []}

@router.post("/merge")
async def merge_cart(
    response: Response,
    db: AsyncSession = Depends(deps.get_tenant_db), # Ensures RLS
    tenant_id: UUID = Depends(deps.get_tenant_id),
    user: ZitadelUser = Depends(deps.get_current_user), # Must be logged in
    guest_token: Optional[str] = Cookie(None)
):
    if not guest_token:
        return {"message": "No guest session to merge"}

    service = CartService(db, tenant_id)
    user_id = UUID(user.id)

    cart = await service.merge_carts(guest_token, user_id)
    response.delete_cookie("guest_token")
    return cart
