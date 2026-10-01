from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from app.core.config import settings
from app.core.db import init_db
from app.api.api_v1.api import api_router

# Middleware to Ensure Guest Token
class GuestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check existing token
        guest_token = request.cookies.get("guest_token")

        # Call endpoint
        response = await call_next(request)

        # If missing, set it on response
        if not guest_token:
            new_token = str(uuid.uuid4())
            response.set_cookie(
                key="guest_token",
                value=new_token,
                max_age=31536000, # 1 year
                samesite="lax",
                httponly=True,
                secure=True # Ensure HTTPS
            )

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB (Check connection, create tables if dev)
    # in prod you might want to remove init_db and rely on alembic
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/swagger",
    lifespan=lifespan
)

# Add Guest Middleware BEFORE CORS (or after? Usually before to ensure cookie is present)
app.add_middleware(GuestMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Kinyu Headless Commerce API is running"}
