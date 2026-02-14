#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: common.py
Author: Maria Kevin
Description: Common auth endpoints
"""

from fastapi import APIRouter

from app.api import dependencies
from app.core import exceptions
from app.domain import schemas

router = APIRouter()


@router.post("/email/status", response_model=schemas.APIResponse[schemas.CheckEmailStatusResponse])
async def check_email_status(
    payload: schemas.CheckEmailStatusRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.CheckEmailStatusResponse]:
    """
    Check if the email is verified.
    """
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise exceptions.NotFoundError("User not found")
    
    return schemas.APIResponse(
        data=schemas.CheckEmailStatusResponse(verified=user.verified),
        message="Email status retrieved"
    )


@router.post(
    "/verify/token",
    response_model=schemas.APIResponse[schemas.VerifyCodeTokenResponse],
    responses={400: {"detail": "Invalid verification token"}},
)
async def verify_code_token(
    payload: schemas.VerifyCodeTokenRequest,
    auth_service: dependencies.AuthServiceDep,
) -> schemas.APIResponse[schemas.VerifyCodeTokenResponse]:
    """
    Verify the validity of a registration/login verification token.
    """
    valid = auth_service.verify_code_token(payload.token)
    
    return schemas.APIResponse(
        data=schemas.VerifyCodeTokenResponse(valid=valid is not None),
        message="Token validity checked"
    )

