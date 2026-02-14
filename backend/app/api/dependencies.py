#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dependencies.py
Author: Maria Kevin
Description: FastAPI dependencies for service injection and authentication.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core import exceptions
from app.db import AsyncSession, get_async_session
from app.domain import enums, models, schemas
from app.repository import UserRepository
from app.service import AuthService, BlacklistTokenService, GoogleAuthService
from app.utils import auth_utils

reusable_oauth2 = HTTPBearer()


async def get_current_user_id(
    token: Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)],
) -> int:
    """Extract user_id from Bearer token in Authorization header."""
    payload = auth_utils.decode_access_token(token.credentials)
    if not payload:
        raise exceptions.UnauthorizedError("Could not validate credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise exceptions.UnauthorizedError("Token does not contain user identification")

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise exceptions.UnauthorizedError("Invalid user identification in token")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> models.Users:
    """Dependency to get the current authenticated user object."""
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_id(user_id)

    if user is None:
        raise exceptions.UnauthorizedError("User not found")

    if not user.verified:
        raise exceptions.BadRequestError("User is not verified")

    return user


async def get_auth_service(
    db: AsyncSession = Depends(get_async_session),
) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)


async def get_blacklist_token_service(
    db: AsyncSession = Depends(get_async_session),
) -> BlacklistTokenService:
    """Dependency to get BlacklistTokenService instance."""
    return BlacklistTokenService(db)


async def get_google_auth_service(
    db: AsyncSession = Depends(get_async_session),
) -> GoogleAuthService:
    """Dependency to get GoogleAuthService instance."""
    return GoogleAuthService(db)


# Token blacklisting dependencies
async def use_and_blacklist_verify_token(
    payload: schemas.VerifyLoginRequest,
    token_service: Annotated[
        BlacklistTokenService, Depends(get_blacklist_token_service)
    ],
) -> str:
    """Validate a signup or login verification token."""
    token = payload.token
    if await token_service.is_token_blacklisted(token):
        raise exceptions.BadRequestError("Verification token is blacklisted")

    return token


async def use_and_blacklist_refresh_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)],
    token_service: Annotated[
        BlacklistTokenService, Depends(get_blacklist_token_service)
    ],
) -> AsyncGenerator[str, None]:
    """Validate and blacklist a refresh token."""
    refresh_token = token.credentials

    if await token_service.is_token_blacklisted(refresh_token):
        raise exceptions.UnauthorizedError("Refresh token is blacklisted")

    try:
        yield refresh_token
    finally:
        await token_service.blacklist_token(refresh_token, enums.TokenType.REFRESH)


async def use_and_blacklist_reset_token(
    request: schemas.ResetPasswordRequest,
    token_service: Annotated[
        BlacklistTokenService, Depends(get_blacklist_token_service)
    ],
) -> AsyncGenerator[str, None]:
    """Validate and blacklist a password reset token."""
    token = request.token

    if await token_service.is_token_blacklisted(token):
        raise exceptions.BadRequestError("Reset token is blacklisted")

    try:
        yield token
    finally:
        await token_service.blacklist_token(token, enums.TokenType.RESET_PASSWORD)


DatabaseDep = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
CurrentUserDep = Annotated[models.Users, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BlacklistTokenServiceDep = Annotated[
    BlacklistTokenService, Depends(get_blacklist_token_service)
]
GoogleAuthServiceDep = Annotated[GoogleAuthService, Depends(get_google_auth_service)]

UseAndBlacklistVerifyToken = Annotated[str, Depends(use_and_blacklist_verify_token)]
UseAndBlacklistRefreshToken = Annotated[str, Depends(use_and_blacklist_refresh_token)]
UseAndBlacklistResetToken = Annotated[str, Depends(use_and_blacklist_reset_token)]
