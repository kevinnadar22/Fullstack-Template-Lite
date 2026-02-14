#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: login.py
Author: Maria Kevin
Created: 2025-11-19
Description: Login and token request endpoints
"""

from fastapi import APIRouter

from app.api import dependencies
from app.core import config, exceptions
from app.domain import enums, schemas

router = APIRouter()


@router.post(
    "/login",
    response_model=schemas.APIResponse[schemas.TokenResponse],
    responses={
        400: {"detail": "User is not verified or OTP is required"},
        404: {"detail": "User not found"},
    },
)
async def login(
    payload: schemas.RequestLoginTokenRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.TokenResponse]:
    """
    Direct login with email and password.
    Fails if OTP is enabled for login.
    """
    if config.settings.ENABLE_LOGIN_OTP:
        raise exceptions.BadRequestError("OTP is enabled.")

    user = await auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise exceptions.NotFoundError("User not found")

    if not user.verified:
        raise exceptions.BadRequestError("User is not verified")

    token_data = await auth_service.login_user(
        email=payload.email, password=payload.password, user=user
    )
    return schemas.APIResponse(
        data=schemas.TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
        ),
        message="Login successful",
    )


@router.post(
    "/login/otp",
    response_model=schemas.APIResponse[schemas.RequestLoginTokenResponse],
    responses={
        400: {"detail": "User is not verified"},
        404: {"detail": "User not found"},
    },
)
async def request_login_otp(
    payload: schemas.RequestLoginTokenRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.RequestLoginTokenResponse]:
    """
    Request a new login verification token (OTP).
    Fails if direct login is enabled.
    """
    if not config.settings.ENABLE_LOGIN_OTP:
        raise exceptions.BadRequestError("OTP is disabled.")

    user = await auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise exceptions.NotFoundError("User not found")

    if not user.verified:
        raise exceptions.BadRequestError("User is not verified")

    login_verify_token = auth_service.issue_verification_code(user, mail_type="login")
    return schemas.APIResponse(
        data=schemas.RequestLoginTokenResponse(token=login_verify_token),
        message="Verification code sent successfully",
    )


@router.post(
    "/login/verify",
    responses={400: {"detail": "Invalid verification code"}},
    response_model=schemas.APIResponse[schemas.VerifyLoginResponse],
)
async def verify_login(
    payload: schemas.VerifyLoginRequest,
    token: dependencies.UseAndBlacklistVerifyToken,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.VerifyLoginResponse]:
    """
    Verify user's email using the login verification code.
    """

    # Verify the signup code
    user = await auth_service.verify_login(payload.token, payload.code)

    # blacklist the signup token after successful verification
    await auth_service.token_repository.blacklist_token(
        token, token_type=enums.TokenType.LOGIN_VERIFY
    )

    token_data = await auth_service.login_user(
        email=user.email, password=user.hashed_password, user=user
    )

    return schemas.APIResponse(
        data=schemas.VerifyLoginResponse(
            verified=True,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
        ),
        message="Login successful",
    )


@router.post("/logout", response_model=schemas.APIResponse[schemas.CommentResponse])
async def logout(
    auth_service: dependencies.AuthServiceDep,
    refresh_token: dependencies.UseAndBlacklistRefreshToken,
) -> schemas.APIResponse[schemas.CommentResponse]:
    """
    Logout user by blacklisting the refresh token.
    """
    await auth_service.token_repository.blacklist_token(
        refresh_token, token_type=enums.TokenType.REFRESH
    )
    return schemas.APIResponse(
        data=schemas.CommentResponse(detail="Logged out successfully"),
        message="Logout successful",
    )


@router.post(
    "/refresh",
    responses={400: {"detail": "Invalid authentication credentials"}},
    response_model=schemas.APIResponse[schemas.VerifyLoginResponse],
)
async def refresh(
    refresh_token: dependencies.UseAndBlacklistRefreshToken,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.VerifyLoginResponse]:
    """
    Refresh user's access token.
    """
    token_data = await auth_service.refresh_user(refresh_token=refresh_token)
    return schemas.APIResponse(
        data=schemas.VerifyLoginResponse(**token_data), message="Token refreshed"
    )
