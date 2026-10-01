from typing import Optional, Union, Any, Dict
from uuid import UUID
from app.services.base import BaseService
from app.models.auth import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

class UserService(BaseService[User]):
    def __init__(self, session: AsyncSession, tenant_id: Optional[Union[UUID, str]] = None):
        super().__init__(BaseRepository(User, session, tenant_id))

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        if self.repository.tenant_id:
            statement = statement.where(User.tenant_id == self.repository.tenant_id)
        result = await self.repository.session.exec(statement)
        return result.first()

    async def create_user(self, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            first_name=obj_in.first_name or "",
            last_name=obj_in.last_name or "",
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            tenant_id=self.repository.tenant_id
        )
        self.repository.session.add(db_obj)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_obj)
        return db_obj

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
