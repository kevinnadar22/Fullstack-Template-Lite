"""
Database configuration and session management.

This module sets up SQLAlchemy engine, session factory, and base class
for ORM models, along with database dependency injection.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.database.url)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


__all__ = ["AsyncSession", "get_async_session", "Base", "engine"]
__all__ = ["AsyncSession", "get_async_session", "Base", "engine"]
