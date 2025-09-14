from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, Dict, Any, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from models.photo_model import Photo

# Обобщенный тип для моделей
T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """Абстрактный базовый класс для CRUD-операций."""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, entity: Union[T, Dict[str, Any]], session: AsyncSession) -> Union[Dict[str, str], T]:
        """
        Создает новую сущность.
        Может принимать объект модели или словарь с данными.
        """
        if isinstance(entity, dict):
            entity = self.model(**entity)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def get_by_id(self, id: int, session: AsyncSession) -> Optional[T]:
        """Получает сущность по ID."""
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Получает все сущности."""
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def update(self, entity_or_id: Union[T, int], data: Optional[Dict[str, Any]] = None, session: AsyncSession = None) -> Optional[T]:
        """
        Обновляет сущность.
        Может принимать объект модели или ID и словарь с данными.
        """
        entity = entity_or_id
        
        if isinstance(entity_or_id, int) and data and session:
            entity = await self.get_by_id(entity_or_id, session)
            if entity:
                for key, value in data.items():
                    if value is not None:
                        setattr(entity, key, value)
        
        if session and entity:
            await session.commit()
            await session.refresh(entity)
            
        return entity

    async def delete(self, id: int, session: AsyncSession) -> dict:
        """Удаляет сущность по ID."""
        entity = await self.get_by_id(id, session)
        if entity:
            await session.delete(entity)
            await session.commit()
            return {"message": f"{self.get_model_name()} deleted successfully"}
        return {"message": f"{self.get_model_name()} not found"}

    @abstractmethod
    def get_model_name(self) -> str:
        """Возвращает имя модели для сообщений."""
        pass

class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self):
        super().__init__(User)

    def get_model_name(self) -> str:
        return "User"

    async def get_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        result = await session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()
    
    async def update_refresh_token(self, user_id: int, refresh_token: str, session: AsyncSession) -> Optional[User]:
        user = await session.execute(select(self.model).where(self.model.id == user_id))
        user = user.scalars().first()
        if not user:
            return None
        user.refresh_token = refresh_token
        await session.commit()
        await session.refresh(user)
        return user

class PhotoRepository(BaseRepository[Photo]):
    """Репозиторий для работы с фото."""

    def __init__(self):
        super().__init__(Photo)

    def get_model_name(self) -> str:
        return "Photo"

    async def get_by_path(self, path: str, session: AsyncSession) -> list[Photo]:
        result = await session.execute(select(self.model).where(self.model.path == path))
        return result.scalars().first()

    async def get_by_grade(self, grade: int, session: AsyncSession) -> list[Photo]:
        result = await session.execute(select(self.model).where(self.model.grade == grade))
        return result.scalars().all()

    async def get_by_parallel(self, parallel: str, session: AsyncSession) -> list[Photo]:
        result = await session.execute(select(self.model).where(self.model.parallel == parallel))
        return result.scalars().all()
