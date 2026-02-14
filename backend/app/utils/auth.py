"""
Authentication utilities for password hashing and JWT token management.

This module provides a class for secure password operations
and JWT token generation/validation.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Dict, Literal, Union

from jose import jwt
from passlib.hash import bcrypt_sha256

from app.core.config import settings


class AuthUtils:
    """Utilities for authentication including password and JWT handling."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthUtils, cls).__new__(cls)
        return cls._instance

    def hash_password(self, password: str) -> str:
        """Hash a plain password using bcrypt."""
        return bcrypt_sha256.hash(secret=password.encode(encoding="utf-8"))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt_sha256.verify(secret=plain_password, hash=hashed_password)

    def create_access_token(
        self, data: dict, expires_delta_minutes: int | None = None
    ) -> str:
        """Generate a JWT access token."""
        return self.create_token(
            data=data, expires_delta_minutes=expires_delta_minutes, token_type="access"
        )

    def create_refresh_token(
        self, data: dict, expires_delta_minutes: int | None = None
    ) -> str:
        """Generate a JWT refresh token."""
        return self.create_token(
            data=data, expires_delta_minutes=expires_delta_minutes, token_type="refresh"
        )

    def create_token(
        self,
        data: dict,
        expires_delta_minutes: int | None = None,
        token_type: Literal["access", "refresh"] = "access",
    ) -> str:
        """Generate a JWT token."""
        to_encode = data.copy()
        to_encode.update({"jti": str(object=uuid.uuid4())})
        expire = datetime.now(UTC) + timedelta(
            minutes=expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})

        secret_key = self.get_secret_key(token_type)
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Union[Dict[str, str], None]:
        """Decode a JWT access token."""
        return self.decode_token(token, token_type="access")

    def decode_refresh_token(self, token: str) -> Union[Dict[str, str], None]:
        """Decode a JWT refresh token."""
        return self.decode_token(token, token_type="refresh")

    def decode_token(
        self, token: str, token_type: Literal["access", "refresh"] = "access"
    ) -> Union[Dict[str, str], None]:
        """Decode a JWT token."""
        try:
            secret_key = self.get_secret_key(token_type)
            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
            return payload
        except Exception:
            return None

    def get_secret_key(
        self, token_type: Literal["access", "refresh"] = "access"
    ) -> str:
        """Get the secret key for a specific token type."""
        return (
            settings.SECRET_KEY
            if token_type == "access"
            else settings.REFRESH_SECRET_KEY
        )

    def generate_fake_password(self) -> str:
        """Generate a fake password for OAuth users."""
        return bcrypt_sha256.hash(f"oauth_user_default_password_{uuid.uuid4()}")

    def get_jti_from_token(self, token: str) -> Union[str, None]:
        """Extract the JTI (JWT ID) from a JWT token."""
        payload = self.decode_access_token(token)
        if payload and "jti" in payload:
            return payload["jti"]
        return None


# Singleton instance
auth_utils = AuthUtils()
