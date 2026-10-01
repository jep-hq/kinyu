from decimal import Decimal
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.ecommerce import Order, Cart, LineItem
from app.models.payment import Transaction
from app.services.cart_service import CartService
from app.services.payment_service import PaymentService
from app.repositories.base import BaseRepository
from app.schemas.checkout import CheckoutRequest, CheckoutResponse
from fastapi import HTTPException
from uuid import UUID
from typing import Optional

class OrderService(BaseService[Order]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(BaseRepository(Order, session, tenant_id))
        self.cart_service = CartService(session, tenant_id)
        self.payment_service = PaymentService(session, tenant_id)

    def _calculate_totals(self, cart: Cart) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calculates subtotal, tax, shipping, and total.
        Returns: (subtotal, tax, shipping, total)
        """
        subtotal = Decimal(0)
        for item in cart.items:
            # Ensure price is Decimal
            price = item.variant.price
            subtotal += price * item.quantity

        # Logic for Tax and Shipping would go here (e.g. Avalara or EasyPost integration)
        # 2026 Standard: Use a dedicated service. Here we mock:
        tax_rate = Decimal("0.20")
        shipping = Decimal("10.00") if subtotal < 100 else Decimal("0.00")

        tax = subtotal * tax_rate
        total = subtotal + tax + shipping

        return subtotal, tax, shipping, total

    async def create_order_from_cart(self, checkout_in: CheckoutRequest) -> CheckoutResponse:
        # 1. Fetch Cart
        cart = await self.cart_service.get_by_token(checkout_in.cart_token)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # 2. Calculate Totals
        subtotal, tax, shipping, total = self._calculate_totals(cart)

        # 3. Create Order Record
        # Note: In a real world scenario, you'd handle Customer creation/lookup here using checkout_in.email

        order = await self.create({
            "email": checkout_in.email,
            "currency_code": "EUR", # Should match store currency
            "subtotal_price": subtotal,
            "total_tax": tax,
            "total_shipping": shipping,
            "total_discounts": 0,
            "total_price": total,
            "financial_status": "pending",
            "fulfillment_status": "unfulfilled",
            "status": "open",
            "shipping_address": checkout_in.shipping_address,
            "billing_address": checkout_in.billing_address or checkout_in.shipping_address
        })

        # 4. Create Line Items
        for item in cart.items:
            # Snapshotting data is crucial for orders!
            # If product price changes later, the order must remain historical.
            line_item = LineItem(
                order_id=order.id,
                variant_id=item.variant_id,
                product_id=item.variant.product_id,
                title=item.variant.product.title,
                variant_title=item.variant.title,
                sku=item.variant.sku,
                quantity=item.quantity,
                price=item.variant.price,
                vendor=item.variant.product.vendor
            )
            self.repository.session.add(line_item)

        # 5. Create Payment Intent (Mollie)
        payment = await self.payment_service.create_payment(
            order_id=str(order.id),
            amount=float(total),
            currency="EUR",
            description=f"Order #{order.order_number}"
        )

        # 6. Record Transaction
        transaction = Transaction(
            order_id=order.id,
            gateway="mollie",
            gateway_reference=payment.id,
            amount=total,
            currency="EUR",
            status=payment.status, # 'open' usually
            metadata_log={"initial_response": payment}
        )
        self.repository.session.add(transaction)

        # 7. Commit everything
        # If any step fails, using SQL transaction ensures no half-created orders
        await self.repository.session.commit()
        await self.repository.session.refresh(order)

        # 8. Return checkout info
        return CheckoutResponse(
            checkout_url=payment.get_checkout_url(),
            order_id=str(order.id)
        )
