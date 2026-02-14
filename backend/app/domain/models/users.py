"""
User database model.

This module defines the SQLAlchemy ORM model for user accounts
including authentication credentials and profile information.
"""

from app.db import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(length=150), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=128), nullable=False)
    verified: Mapped[bool] = mapped_column(nullable=False, server_default="false")
