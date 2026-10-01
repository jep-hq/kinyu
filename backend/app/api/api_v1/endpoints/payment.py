from fastapi import APIRouter, Depends, BackgroundTasks, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.payment_service import PaymentService

router = APIRouter()

@router.post("/webhook/mollie")
async def mollie_webhook(
    id: str = Form(...), # Mollie sends data as form-urlencoded
    db: AsyncSession = Depends(deps.get_session),
    background_tasks: BackgroundTasks = None
):
    """
    Webhook handler for Mollie.
    Mollie sends the 'id' of the transaction as a form parameter.
    We return 200 OK immediately and process in background to avoid timeouts.
    """
    if not id:
        raise HTTPException(status_code=400, detail="Missing payment ID")

    service = PaymentService(db)

    # Process in background (optional, but good practice for webhooks)
    if background_tasks:
        background_tasks.add_task(service.handle_webhook, id)
    else:
        await service.handle_webhook(id)

    return {"status": "received"}
