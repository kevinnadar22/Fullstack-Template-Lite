#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blacklist_token.py
Author: Maria Kevin
Created: 2025-11-18
Description: Blacklist token Service
"""

from app.db import AsyncSession
from app.domain import enums
from app.repository import BlacklistTokenRepository
from app.utils import auth_utils


class BlacklistTokenService:
    """Service to handle blacklisting of tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.token_repository = BlacklistTokenRepository(db)

    async def blacklist_token(self, token: str, token_type: enums.TokenType) -> None:
        """
        Blacklist a JWT token to invalidate it.

        Args:
            token (str): JWT token to blacklist.
        Returns:
            None
        """
        jti = auth_utils.get_jti_from_token(token)
        if jti:
            await self.token_repository.blacklist_token(jti, token_type=token_type)
        return None

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a JWT token is blacklisted.

        Args:
            token (str): JWT token to check.
        Returns:
            bool: True if token is blacklisted, False otherwise.
        """

        jti = auth_utils.get_jti_from_token(token)
        if jti:
            return await self.token_repository.is_token_blacklisted(jti)
        return False
