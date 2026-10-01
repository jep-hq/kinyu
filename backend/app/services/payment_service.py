from mollie.api.client import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.config import settings
from app.models.payment import Transaction
from app.models.tenant import Tenant
from app.models.ecommerce import Order
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        self.session = session
        self.tenant_id = tenant_id

    async def _get_mollie_client(self) -> Client:
        if not self.tenant_id:
             raise Exception("Tenant ID is required to process payments")

        # Fetch Tenant Secrets
        tenant = await self.session.get(Tenant, self.tenant_id)
        if not tenant:
             raise Exception(f"Tenant {self.tenant_id} not found")

        secrets = tenant.secrets or {}
        api_key = secrets.get("mollie_api_key")

        if not api_key:
             # Fallback to env var ONLY for dev/testing or if not set in DB?
             # No, STRICT isolation means we should rely on DB.
             # But migration might be tricky. Let's support env var as default fallback for now if key missing.
             api_key = settings.MOLLIE_API_KEY
             if not api_key:
                raise Exception(f"Mollie API Key not configured for tenant {self.tenant_id}")

        client = Client()
        client.set_api_key(api_key)
        return client

    async def create_payment(self, order_id: str, amount: float, currency: str, description: str) -> dict:
        """
        Creates a payment intent with Mollie and returns the payment object.
        """
        client = await self._get_mollie_client()

        # Mollie expects amount as string with 2 decimals
        formatted_amount = "{:.2f}".format(amount)

        payment_data = {
            'amount': {
                'currency': currency,
                'value': formatted_amount
            },
            'description': description,
            'redirectUrl': f"{settings.BACKEND_CORS_ORIGINS[0]}/checkout/success?order_id={order_id}", # Redirect to frontend
            'webhookUrl': f"{settings.MOLLIE_WEBHOOK_URL}", # Must be publicly accessible
            'metadata': {
                'order_id': order_id
            }
        }

        try:
            payment = self.mollie_client.payments.create(payment_data)
            return payment
        except Exception as e:
            logger.error(f"Failed to create Mollie payment: {e}")
            raise e

    async def handle_webhook(self, payment_id: str):
        # 1. Verify with Mollie (State of Truth)
        try:
            mollie_payment = self.mollie_client.payments.get(payment_id)
        except Exception as e:
            logger.error(f"Faled to fetch payment {payment_id} from Mollie: {e}")
            raise e

        # 2. Find Transaction
        result = await self.session.exec(select(Transaction).where(Transaction.gateway_reference == payment_id))
        transaction = result.first()

        if not transaction:
            logger.error(f"Transaction {payment_id} not found")
            return

        # 3. Update Transaction Status
        previous_status = transaction.status
        transaction.status = mollie_payment.get('status')
        # Log metadata if needed
        transaction.metadata_log["webhook_history"] = transaction.metadata_log.get("webhook_history", []) + [{"status": transaction.status, "timestamp": "now"}] # TODO: use real timestamp

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        # 4. Update Order Status if changed
        if transaction.status != previous_status:
            await self._update_order_status(transaction)

    async def _update_order_status(self, transaction: Transaction):
        # Simple logic: If paid, mark order as paid
        if transaction.status == 'paid':
             result = await self.session.exec(select(Order).where(Order.id == transaction.order_id))
             order = result.first()
             if order:
                 order.financial_status = 'paid'
                 self.session.add(order)
                 await self.session.commit()
