#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: google.py
Author: Maria Kevin
Description: Google OAuth endpoints
"""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.api import dependencies
from app.core import config, exceptions

router = APIRouter()


@router.get("/google")
async def google_login(
    request: Request, google_auth_service: dependencies.GoogleAuthServiceDep
):
    """
    Initiate Google OAuth authentication flow.
    """
    return await google_auth_service.authorize_redirect(request)


@router.get(
    "/google/callback", responses={400: {"detail": "Google authentication failed"}}
)
async def google_auth(
    request: Request,
    google_auth_service: dependencies.GoogleAuthServiceDep,
):
    """
    Handle Google OAuth callback and create user session.
    """
    try:
        token_data = await google_auth_service.handle_authorization_callback(request)
        redirect_url = (
            f"{config.settings.FRONTEND_URL}/auth/callback?"
            f"access_token={token_data['access_token']}&"
            f"refresh_token={token_data['refresh_token']}"
        )
    except exceptions.GoogleAuthException as e:
        redirect_url = f"{config.settings.FRONTEND_URL}/auth/callback?error={e.detail}"
    except Exception:
        redirect_url = (
            f"{config.settings.FRONTEND_URL}/auth/callback?error=unknown_error"
        )

    return RedirectResponse(redirect_url)
