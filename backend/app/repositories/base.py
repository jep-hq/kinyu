from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import UUIDMixin

ModelType = TypeVar("ModelType", bound=UUIDMixin)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession, tenant_id: Optional[UUID] = None):
        self.model = model
        self.session = session
        self.tenant_id = tenant_id

    async def get(self, id: Union[UUID, str]) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == id)
        if self.tenant_id and hasattr(self.model, "tenant_id"):
             statement = statement.where(self.model.tenant_id == self.tenant_id)

        result = await self.session.exec(statement)
        return result.first()

    async def get_list(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model)
        if self.tenant_id and hasattr(self.model, "tenant_id"):
             statement = statement.where(self.model.tenant_id == self.tenant_id)

        result = await self.session.exec(statement.offset(skip).limit(limit))
        return result.all()

    async def create(self, obj_in: Union[SQLModel, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            # If it's a dict, we can just update it
            if self.tenant_id and "tenant_id" not in obj_in and hasattr(self.model, "tenant_id"):
                obj_in["tenant_id"] = self.tenant_id
            db_obj = self.model.model_validate(obj_in)
        else:
             # If it's a model, we set the attribute
            db_obj = self.model.model_validate(obj_in) # Works if input is a Pydantic model
            if self.tenant_id and hasattr(db_obj, "tenant_id") and getattr(db_obj, "tenant_id") is None:
                setattr(db_obj, "tenant_id", self.tenant_id)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[SQLModel, Dict[str, Any]]
    ) -> ModelType:
        obj_data = db_obj.model_dump()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, *, id: Union[UUID, str]) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
        return db_obj
