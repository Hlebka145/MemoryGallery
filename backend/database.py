from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator

# Создаем асинхронный движок для SQLite
engine = create_async_engine('sqlite+aiosqlite:///database.db', echo=True)

# Настраиваем асинхронную сессию
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Создаем базовый класс для моделей
Base = declarative_base()

#import models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных.
    Используется в маршрутах FastAPI с Depends.
    """
    session = async_session()
    try:
        yield session
    finally:
        await session.close()

async def get_db_session() -> AsyncSession:
    """
    Функция для прямого получения сессии базы данных.
    Для использования в сервисах без Depends.
    """
    return async_session()