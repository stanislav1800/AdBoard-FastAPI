from typing import Type, Generic, TypeVar, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import SessionDep
from app.models.base import Base

ModelType = TypeVar("ModelType")
ModelClass = TypeVar("Base", bound=Base)
PydanticModelType = TypeVar("PydanticModelType", bound=BaseModel)
RepoType = TypeVar("RepoType", bound="BaseRepository")

class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]
    m2m_fields: dict[str, Type[Base]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "model"):
            origin = getattr(cls, "__orig_bases__", [])
            for base in origin:
                if hasattr(base, "__args__") and base.__args__:
                    cls.model = base.__args__[0]

    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self):
        """Базовый query с предзагрузкой связанных полей, если нужно"""
        stmt = select(self.model)
        return stmt
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        stmt = self._base_query().where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_one_by_filters(self, **filters):
        stmt = self._base_query().filter_by(**filters)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_by_filters(self, **filters) -> list[Optional[ModelType]]:
        result = await self.db.execute(
            self._base_query().filter_by(**filters)
        )
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.db.execute(
            self._base_query().offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list(self, **filters) -> list[ModelType]:
        query = self._base_query().filter_by(**filters)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: PydanticModelType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update(
    self,
    obj: ModelClass,
    obj_in: PydanticModelType,
    exclude_unset: bool = False,
) -> ModelType:

        data = obj_in.model_dump(exclude_unset=exclude_unset)

        for key, value in data.items():

            if key in self.m2m_fields:
                if value is None:
                    continue

                related_model = self.m2m_fields[key]
                related = await self.db.scalars(
                    select(related_model).where(related_model.id.in_(value))
                )
                setattr(obj, key, list(related))

            else:
                setattr(obj, key, value)

        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, obj: ModelClass) -> bool:
        await self.db.delete(obj)
        await self.db.commit()
        return True


def get_repository(repo_class: Type[RepoType]):
    async def _get_repo(db: SessionDep) -> RepoType:
        return repo_class(db)
    return _get_repo
