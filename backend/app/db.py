"""
Database configuration and session management.

This module sets up SQLAlchemy engine, session factory, and base class
for ORM models, along with database dependency injection.
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from collections.abc import AsyncGenerator

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


__all__ = ["AsyncSession", "get_async_session", "Base", "engine"]
