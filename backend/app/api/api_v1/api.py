from fastapi import APIRouter
from app.api.api_v1.endpoints import payment, auth, users, checkout, cms, orders, products, collections, customers, backoffice, cart

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(checkout.router, prefix="/checkout", tags=["checkout"])
api_router.include_router(cms.router, prefix="/cms", tags=["cms"])
api_router.include_router(backoffice.router, prefix="/backoffice", tags=["backoffice"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
