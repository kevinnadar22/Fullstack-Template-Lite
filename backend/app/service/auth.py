"""
Authentication service for user registration and login.

This module provides business logic for user authentication including
password hashing, credential verification, and JWT token generation.
"""

import random
import string
from typing import Any, Literal, Optional

from app.core import config, exceptions
from app.db import AsyncSession
from app.domain import models
from app.repository import BlacklistTokenRepository, UserRepository
from app.utils import auth_utils
from app.workers import tasks


class AuthService:
    """Service to handle user authentication and registration."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.token_repository = BlacklistTokenRepository(db)

    async def create_user(self, email: str, password: str) -> models.Users:
        """
        Create a new user account with hashed password.

        Args:
            email (str): User email.
            password (str): User plain text password.

        Returns:
            Users: Created user object.

        Raises:
            ConflictError: If email is already in use.
        """
        if await self.is_email_registered(email):
            raise exceptions.ConflictError("Email already registered")

        # hash the password now
        hashed_password = auth_utils.hash_password(password)

        return await self.user_repository.create_user(
            email,
            hashed_password,
            verified=False,
        )

    async def login_user(
        self, email: str, password: str, user: Optional[models.Users] = None
    ) -> dict[str, Any]:
        """
        Authenticate user and generate access token.

        Args:
            email (str): User email address.
            password (str): User password.
            user (Optional[Users]): Pre-authenticated user object (for OAuth).

        Returns:
            dict: Access token and token type.

        Raises:
            UnauthorizedError: If authentication fails.
            BadRequestError: If user is not verified.
        """
        if user is None:
            user = await self.authenticate_user(email, password)

            if not user:
                raise exceptions.UnauthorizedError("Invalid credentials")

        if not user.verified:
            raise exceptions.BadRequestError("User not verified")

        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def is_email_registered(self, email: str) -> bool:
        """
        Check if email already exists in database.

        Args:
            email (str): Email address to check.

        Returns:
            bool: True if email exists, False otherwise.
        """
        user = await self.user_repository.get_user_by_email(email)
        return user is not None

    async def authenticate_user(self, email: str, password: str) -> models.Users | None:
        """
        Verify user credentials.

        Args:
            email (str): User email address.
            password (str): Plain text password to verify.

        Returns:
            Users | None: User object if valid, None if invalid.
        """
        user = await self.user_repository.get_user_by_email(email)
        if user and auth_utils.verify_password(password, user.hashed_password):
            return user
        return None

    def generate_access_token(self, user: models.Users) -> str:
        """
        Generate JWT access token for user.

        Args:
            user (Users): User object to encode in token.

        Returns:
            str: JWT access token.
        """
        return auth_utils.create_access_token({"sub": str(user.id)})

    def generate_refresh_token(self, user: models.Users) -> str:
        """
        Generate JWT refresh token for user.

        Args:
            user (Users): User object to encode in token.
        Returns:
            str: JWT refresh token.
        """
        return auth_utils.create_refresh_token(
            {"sub": str(user.id)},
            expires_delta_minutes=config.settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    async def get_user_by_email(self, email: str) -> Optional[models.Users]:
        """
        Retrieve user by email address.

        Args:
            email (str): Email address to search.

        Returns:
            Optional[models.Users]: User object if found, None otherwise.
        """
        return await self.user_repository.get_user_by_email(email)

    def generate_password_reset_token(self, email: str) -> str:
        """
        Generate a password reset token for the given email.

        Args:
            email (str): User email address.
        Returns:
            str: Password reset token.
        """
        return auth_utils.create_access_token({"sub": email}, expires_delta_minutes=15)

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        Verify the password reset token and extract the email.

        Args:
            token (str): Password reset token.
        Returns:
            Optional[str]: Email address if token is valid, None otherwise.
        """
        payload = auth_utils.decode_access_token(token)
        if not payload or "sub" not in payload:
            return None
        return payload["sub"]

    async def reset_user_password(self, token: str, new_password: str) -> None:
        """
        Reset the user's password.

        Args:
            token (str): Password reset token.
            new_password (str): New plain text password.

        Returns:
            None
        """

        email = self.verify_password_reset_token(token)
        if not email:
            raise exceptions.BadRequestError("Invalid or expired reset token")

        user = await self.get_user_by_email(email)
        if not user:
            raise exceptions.NotFoundError("User not found")

        hashed_password = auth_utils.hash_password(new_password)
        await self.user_repository.update_user_password(user, hashed_password)

    def generate_email_verification_code(self, user_id: int) -> str:
        """
        Generate an email verification code.

        Args:
            user_id (int): User ID.
        Returns:
            str: Email verification code.
        """
        code = "".join(random.choices(string.digits, k=6))
        return code

    def generate_signup_verify_token(self, user_id: int, code: str) -> str:
        """
        Generate a JWT signup verification token containing user ID and code.

        Args:
            user_id (int): User ID.
            code (str): Verification code.
        Returns:
            str: Signup verification token.
        """
        return auth_utils.create_access_token(
            {"sub": str(user_id), "code": code}, expires_delta_minutes=60
        )

    async def verify_signup(self, token: str, code: str) -> models.Users:
        """
        Verify the email signup code.

        Args:
            code (str): Email verification code.
            token (str): JWT token containing the verification code.

        Returns:
            Users: Verified user object.
        Raises:
            BadRequestError: If verification code is invalid or expired.
        """

        # Verify if the code and entered code match
        user = await self.verify_login(token, code)

        # Mark user as verified if not already
        if not user.verified:
            await self.user_repository.mark_user_as_verified(user)
        return user

    async def verify_login(self, token: str, code: str) -> models.Users:
        """
        Verify the email login code.

        Args:
            code (str): Email verification code.
            token (str): JWT token containing the verification code.

        Returns:
            Users: Verified user object.
        Raises:
            BadRequestError: If verification code is invalid or expired.
            UnauthorizedError: If user is not found.
        """
        jwt_payload = self.verify_code_token(token)
        if not jwt_payload:
            raise exceptions.BadRequestError("Verification code expired")

        generated_code = jwt_payload["code"]
        user_id = int(jwt_payload["sub"])

        if generated_code != code:
            raise exceptions.BadRequestError("Verification code invalid")

        user = await self.user_repository.get_user_by_id(user_id)

        if not user:
            raise exceptions.UnauthorizedError("User not found")

        return user

    def verify_code_token(self, token: str) -> Optional[dict]:
        """
        Verify the validity of a signup/ login verification token.

        Args:
            token (str): JWT token containing the verification code.

        Returns:
            Optional[dict]: JWT payload if token is valid, None otherwise.
        """
        jwt_payload = auth_utils.decode_access_token(token)
        if not jwt_payload or "sub" not in jwt_payload or "code" not in jwt_payload:
            return None
        return jwt_payload

    def issue_verification_code(
        self,
        user: models.Users,
        mail_type: Literal["signup", "login"],
    ) -> str:
        """
        Issue a new signup/login verification code for the user.

        Args:
            user (Users): User object.
            mail_type (str): Type of verification (signup/login).

        Returns:
            str: New verification code.
        """
        signup_code = self.generate_email_verification_code(user.id)

        if mail_type == "login":
            tasks.send_login_otp_email_task.delay(user.email, "Users", signup_code)
        else:
            tasks.send_signup_verification_email_task.delay(
                user.email, "Users", signup_code
            )

        signup_verify_token = self.generate_signup_verify_token(user.id, signup_code)
        return signup_verify_token

    async def refresh_user(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh user's access token.

        Args:
            refresh_token (str): Refresh token.

        Returns:
            dict: Response containing new tokens.
        """
        # decode refresh token
        decoded_refresh_token = auth_utils.decode_refresh_token(refresh_token)

        if not decoded_refresh_token:
            raise exceptions.UnauthorizedError("Invalid or expired refresh token")

        # Use id instead of email if that's what we encode now
        user_id = decoded_refresh_token["sub"]
        user = await self.user_repository.get_user_by_id(int(user_id))

        if not user:
            raise exceptions.NotFoundError("User not found")

        if not user.verified:
            raise exceptions.BadRequestError("User not verified")

        access_token = self.generate_access_token(user)
        new_refresh_token = self.generate_refresh_token(user)

        return {
            "verified": True,
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
