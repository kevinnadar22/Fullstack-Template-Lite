#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: password.py
Author: Maria Kevin
Description: Password reset and management endpoints
"""

from fastapi import APIRouter

from app.api import dependencies
from app.core import config, exceptions
from app.domain import schemas
from app.workers import tasks

router = APIRouter(prefix="/password-reset")


@router.post("/", response_model=schemas.APIResponse[schemas.CommentResponse])
async def request_password_reset(
    request: schemas.ForgotPasswordRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.CommentResponse]:
    """
    Handles password reset requests.
    """
    email = request.email
    message = "If the email is registered, a password reset link has been sent."

    if not await auth_service.is_email_registered(email):
        return schemas.APIResponse(
            data=schemas.CommentResponse(detail=message),
            message=message
        )

    token = auth_service.generate_password_reset_token(email)
    reset_link = f"{config.settings.FRONTEND_URL}/reset-password?token={token}"
    tasks.send_password_reset_email_task.delay(email, reset_link)
    
    return schemas.APIResponse(
        data=schemas.CommentResponse(detail=message),
        message=message
    )


@router.post("/verify", response_model=schemas.APIResponse[schemas.VerifyResetTokenResponse])
async def verify_password_reset_token(
    request: schemas.VerifyResetTokenRequest, 
    auth_service: dependencies.AuthServiceDep
) -> schemas.APIResponse[schemas.VerifyResetTokenResponse]:
    """
    Verify the validity of a password reset token.
    """
    token = request.token
    email = auth_service.verify_password_reset_token(token)
    if not email:
        raise exceptions.BadRequestError("Invalid or expired reset token.")
    
    return schemas.APIResponse(
        data=schemas.VerifyResetTokenResponse(valid=True),
        message="Reset token is valid"
    )


@router.post(
    "/confirm",
    responses={400: {"detail": "Invalid or expired reset token."}},
    response_model=schemas.APIResponse[schemas.CommentResponse],
)
async def confirm_password_reset(
    token: dependencies.UseAndBlacklistResetToken,
    request: schemas.ResetPasswordRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.CommentResponse]:
    """
    Reset user's password using a valid reset token.
    """
    new_password = request.new_password
    await auth_service.reset_user_password(token, new_password)
    
    return schemas.APIResponse(
        data=schemas.CommentResponse(detail="Password has been reset successfully."),
        message="Password reset successful"
    )
