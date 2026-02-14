#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blacklist_tokens.py
Author: Maria Kevin
Created: 2025-11-18
Description: Blacklist Tokens
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from app.db import Base
from app.domain import enums
from sqlalchemy import DateTime, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class BlackListTokens(Base):
    __tablename__ = "blacklist_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    token_type: Mapped[enums.TokenType] = mapped_column(
        Enum(enums.TokenType), nullable=False
    )
    blacklisted_on: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
