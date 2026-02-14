#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: register.py
Author: Maria Kevin
Description: User registration endpoints
"""

from typing import cast

from fastapi import APIRouter

from app.api import dependencies
from app.core import config, exceptions
from app.domain import enums, models, schemas

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.APIResponse[schemas.SignupUserResponse],
    responses={409: {"detail": "Email already registered"}},
)
async def register(
    request: schemas.SignupRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.SignupUserResponse]:
    """
    Direct registration with name, email and password.
    Fails if OTP is enabled for registration.
    """
    if config.settings.ENABLE_SIGNUP_OTP:
        raise exceptions.BadRequestError("OTP is enabled.")

    # Create the user
    created_user = await auth_service.create_user(
        email=request.email, password=request.password
    )

    # Mark user as verified immediately
    await auth_service.user_repository.mark_user_as_verified(created_user)

    # Generate tokens
    token_data = await auth_service.login_user(
        email=created_user.email, password=request.password, user=created_user
    )

    return schemas.APIResponse(
        data=schemas.SignupUserResponse(
            id=created_user.id,
            email=created_user.email,
            verified=True,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
        ),
        message="User registered successfully",
    )


@router.post(
    "/register/otp",
    response_model=schemas.APIResponse[schemas.RequestSignupTokenResponse],
    responses={409: {"detail": "Email already registered"}},
)
async def request_registration_otp(
    request: schemas.SignupRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.RequestSignupTokenResponse]:
    """
    Initiate registration and request a verification token.
    Fails if OTP is disabled for registration.
    """
    if not config.settings.ENABLE_SIGNUP_OTP:
        raise exceptions.BadRequestError("OTP is disabled.")

    try:
        # Try to create the user
        user = await auth_service.create_user(
            email=request.email, password=request.password
        )
    except exceptions.ConflictError:
        # Check if user is unverified
        user = await auth_service.get_user_by_email(request.email)
        if user and user.verified:
            raise exceptions.ConflictError("Email already registered and verified.")

    user = cast(models.Users, user)
    # Issue signup verification code (or resend if they already had it)
    signup_verify_token = auth_service.issue_verification_code(user, mail_type="signup")

    return schemas.APIResponse(
        data=schemas.RequestSignupTokenResponse(
            id=user.id,
            email=user.email,
            verify_token=signup_verify_token,
            verified=user.verified,
        ),
        message="Verification code sent successfully",
    )


@router.post(
    "/register/verify",
    responses={400: {"detail": "Invalid verification code"}},
    response_model=schemas.APIResponse[schemas.VerifyLoginResponse],
)
async def verify_registration(
    payload: schemas.VerifySignupRequest,
    token: dependencies.UseAndBlacklistVerifyToken,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.VerifyLoginResponse]:
    """
    Verify user's email using the registration verification code.
    """

    # Verify the registration code
    user = await auth_service.verify_signup(payload.token, payload.code)

    # blacklist the signup token after successful verification
    await auth_service.token_repository.blacklist_token(
        token, token_type=enums.TokenType.SIGNUP_VERIFY
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
        message="Email verified successfully",
    )
