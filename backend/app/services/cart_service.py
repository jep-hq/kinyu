from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from app.services.base import BaseService
from app.models.ecommerce import Cart, CartItem, ProductVariant, Product
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from typing import Optional, Union
from uuid import UUID

class CartService(BaseService[Cart]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Cart, session, tenant_id))

    async def get_by_token(self, token: str) -> Optional[Cart]:
        """
        Fetch cart by token with all relationships loaded (items -> variant -> product)
        """
        query = (
            select(Cart)
            .where(Cart.token == token)
        )
        if self.repository.tenant_id:
             query = query.where(Cart.tenant_id == self.repository.tenant_id)

        query = query.options(
            selectinload(Cart.items).selectinload(CartItem.variant).selectinload(ProductVariant.product)
        )
        result = await self.repository.session.exec(query)
        return result.first()

    async def add_item(self, cart_token: str, variant_id: str, quantity: int) -> Cart:
        cart = await self.get_by_token(cart_token)
        if not cart:
            # Create new cart if not exists
            cart = await self.create({"token": cart_token})

        # Check if item exists
        # Note: In a real app we'd check inventory here
        # For simplicity, we just add/update the item

        # We need to re-query items if we just created the cart, or check the loaded items
        # To keep it simple, let's search in the already loaded items if it existed
        existing_item = next((item for item in cart.items if item.variant_id == variant_id), None)

        if existing_item:
            existing_item.quantity += quantity
            self.repository.session.add(existing_item)
        else:
            new_item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=quantity)
            self.repository.session.add(new_item)

        await self.repository.session.commit()
        await self.repository.session.refresh(cart)
        return cart

    async def merge_carts(self, guest_token: str, user_id: UUID) -> Optional[Cart]:
        """
        Merges a guest cart (identified by token) into a logged-in user's cart.
        """
        # 1. Get Guest Cart
        guest_cart = await self.get_by_token(guest_token)

        # 2. Get User Cart
        # Note: We need to find if the user already has a cart
        query = select(Cart).where(Cart.customer_id == user_id)
        if self.repository.tenant_id:
             query = query.where(Cart.tenant_id == self.repository.tenant_id)

        # Load items for merging
        query = query.options(
            selectinload(Cart.items).selectinload(CartItem.variant).selectinload(ProductVariant.product)
        )

        result = await self.repository.session.exec(query)
        user_cart = result.first()

        if not guest_cart:
            # Nothing to merge
            return user_cart

        if not user_cart:
            # Easy case: Just assign the guest cart to the user
            guest_cart.customer_id = user_id
            # We keep the token as the active session token, or we could generate a new one
            # relying on the guest token becoming the user's active session token is fine.
            self.repository.session.add(guest_cart)
            await self.repository.session.commit()
            return guest_cart

        # 3. Hard case: User has a cart, Guest has a cart -> MERGE ITEMS
        for guest_item in guest_cart.items:
             # Check if variant exists in user cart
             existing_item = next(
                 (i for i in user_cart.items if i.variant_id == guest_item.variant_id),
                 None
             )

             if existing_item:
                 existing_item.quantity += guest_item.quantity
                 self.repository.session.add(existing_item)
             else:
                 # Move item from guest cart to user cart
                 # We must create a NEW item or reassign safely
                 # Reassigning cart_id is easiest
                 guest_item.cart_id = user_cart.id
                 self.repository.session.add(guest_item)

        # 4. Cleanup Guest Cart
        # The items were moved or merged. The guest cart shell is now empty/obsolete.
        self.repository.session.delete(guest_cart)

        await self.repository.session.commit()
        await self.repository.session.refresh(user_cart)
        return user_cart
