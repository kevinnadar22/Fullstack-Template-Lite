"""
Google OAuth authentication service.

This module handles Google OAuth 2.0 authentication flow including
authorization redirect, callback processing, and user creation/retrieval.
"""

from typing import Any

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from app.core import config, exceptions
from app.db import AsyncSession
from app.domain import models
from app.repository import UserRepository
from app.utils import auth_utils

from .auth import AuthService

oauth = OAuth()
oauth.register(
    name="hairtryon",
    client_id=config.settings.GOOGLE_CLIENT_ID,
    client_secret=config.settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config.settings.GOOGLE_REDIRECT_URL,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)


class GoogleAuthService:
    """Service to handle Google OAuth authentication."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)

    @staticmethod
    async def authorize_redirect(request: Request):
        """
        Redirect user to Google OAuth consent screen.

        Args:
            request: FastAPI request object.

        Returns:
            RedirectResponse: Redirect to Google authorization URL.
        """
        redirect_url = config.settings.GOOGLE_REDIRECT_URL
        return await oauth.hairtryon.authorize_redirect(  # type: ignore
            request, redirect_url, prompt="consent"
        )

    async def handle_authorization_callback(self, request: Request) -> dict[str, Any]:
        """
        Process Google OAuth callback and create/login user.

        Args:
            request (Request): FastAPI request with OAuth callback data.

        Returns:
            dict: JWT access token for authenticated user.

        Raises:
            exceptions.GoogleAuthException: If token retrieval or user info fetch fails.
        """
        try:
            token_dict = await oauth.hairtryon.authorize_access_token(request)  # type: ignore
        except Exception as e:
            raise exceptions.GoogleAuthException(
                "Failed to retrieve access token"
            ) from e

        access_token = token_dict.get("access_token")
        if not access_token:
            raise exceptions.GoogleAuthException(
                "No access token found in OAuth response"
            )

        userinfo = await self.fetch_userinfo(access_token)
        if userinfo is None:
            raise exceptions.GoogleAuthException("Failed to retrieve user info")

        email = userinfo.get("email")
        user_id = userinfo.get("sub")

        if not email or not user_id:
            raise exceptions.GoogleAuthException(
                "Email or user ID not found in user info"
            )

        user = await self.create_or_get_user(email)
        # Use user_id as password placeholder for OAuth users if needed by login_user logic
        token_response = await self.auth_service.login_user(
            email=email, password=user_id, user=user
        )
        return token_response

    async def create_or_get_user(self, email: str) -> models.Users:
        """
        Retrieve existing user or create new one from Google OAuth data.

        Args:
            email (str): User email.

        Returns:
            models.Users: Existing or newly created user object.
        """
        exists = await self.user_repo.get_user_by_email(email)
        if exists:
            return exists

        password = auth_utils.generate_fake_password()

        new_user = await self.user_repo.create_user(
            email=email,
            hashed_password=password,
            verified=True,
        )

        return new_user

    async def fetch_userinfo(self, access_token: str) -> dict[str, Any] | None:
        """
        Fetch user information from Google OAuth API.

        Args:
            access_token (str): Google OAuth access token.

        Returns:
            dict | None: User information if successful, None otherwise.
        """
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_endpoint, headers=headers)
            if response.status_code != 200:
                return None
            return response.json()
