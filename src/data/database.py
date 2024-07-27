from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from src.config import DB_NAME, DB_HOST, DB_PASSWORD, DB_PORT, DB_USER

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=True,
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


@asynccontextmanager
async def get_db():
    """ Dependency for getting async session """
    async with async_session() as session:
        yield session
