"""
User repository for database operations.

This module provides data access layer for User model operations
including retrieval and creation.
"""

from sqlalchemy import select

from app.db import AsyncSession
from app.domain import models


class UserRepository:
    """Repository to handle database operations for User."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> models.Users | None:
        """
        Get a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The retrieved user object, or None if not found.
        """
        result = await self.db.execute(
            select(models.Users).filter(models.Users.email == email)
        )
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> models.Users | None:
        """
        Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The retrieved user object, or None if not found.
        """
        result = await self.db.execute(
            select(models.Users).filter(models.Users.id == user_id)
        )
        return result.scalars().first()

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        verified: bool = False,
    ) -> models.Users:
        """Create a new user in the database.

        Args:
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.

        Returns:
            Users: The created user object.
        """
        new_user = models.Users(
            email=email, hashed_password=hashed_password, verified=verified
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user_password(
        self, user: models.Users, new_hashed_password: str
    ) -> models.Users:
        """
        Update the user's password.

        Args:
            user (User): The user object to update.
            new_hashed_password (str): The new hashed password.

        Returns:
            User: The updated user object.
        """
        user.hashed_password = new_hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: models.Users) -> models.Users:
        """
        Update the user details.

        Args:
            user (User): The user object to update.

        Returns:
            User: The updated user object.
        """
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def mark_user_as_verified(self, user: models.Users) -> models.Users:
        """
        Mark the user as verified.

        Args:
            user (User): The user object to update.
        Returns:
            User: The updated user object with verified status.
        """
        user.verified = True
        return await self.update_user(user)
