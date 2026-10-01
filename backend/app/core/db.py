from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), echo=False, future=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def init_db():
    # In production, use Alembic.
    # This is for dev/testing to quickly create tables if needed without migrations
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create default tenant if not exists
    async with async_session_factory() as session:
        from app.models.tenant import Tenant
        from sqlmodel import select

        try:
             result = await session.exec(select(Tenant))
             tenant = result.first()
             if not tenant:
                 tenant = Tenant(name="Default Tenant", slug="default", domain="localhost")
                 session.add(tenant)
                 await session.commit()
                 # print(f"Created default tenant: {tenant.id}")
        except Exception as e:
            print(f"Error creating default tenant: {e}")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
