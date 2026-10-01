from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from app.repositories.base import BaseRepository, ModelType
from sqlmodel import SQLModel

class BaseService(Generic[ModelType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def get(self, id: Union[UUID, str]) -> Optional[ModelType]:
        return await self.repository.get(id)

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return await self.repository.get_list(skip=skip, limit=limit)

    async def create(self, obj_in: Union[SQLModel, Dict[str, Any]]) -> ModelType:
        return await self.repository.create(obj_in)

    async def update(self, db_obj: ModelType, obj_in: Union[SQLModel, Dict[str, Any]]) -> ModelType:
        return await self.repository.update(db_obj=db_obj, obj_in=obj_in)

    async def delete(self, id: Union[UUID, str]) -> Optional[ModelType]:
        return await self.repository.delete(id=id)
