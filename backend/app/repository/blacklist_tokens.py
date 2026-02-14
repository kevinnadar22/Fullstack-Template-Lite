"""
Blacklist tokens repository for database operations.
"""

from datetime import UTC, datetime

from sqlalchemy import select

from app.db import AsyncSession
from app.domain import enums, models


class BlacklistTokenRepository:
    """Repository to handle database operations for blacklist tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def blacklist_token(
        self, jti: str, token_type: enums.TokenType
    ) -> models.BlackListTokens:
        """
        Add a token to the blacklist.

        Args:
            jti (str): JWT ID.
            token_type (TokenType): Type of token being blacklisted.

        Returns:
            BlackListTokens: The created blacklist entry.
        """
        blacklist_entry = models.BlackListTokens(
            jti=jti, token_type=token_type, blacklisted_on=datetime.now(UTC)
        )
        self.db.add(blacklist_entry)
        await self.db.commit()
        await self.db.refresh(blacklist_entry)
        return blacklist_entry

    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            jti (str): JWT ID.

        Returns:
            bool: True if blacklisted, False otherwise.
        """
        result = await self.db.execute(
            select(models.BlackListTokens).filter(models.BlackListTokens.jti == jti)
        )
        return result.scalars().first() is not None
