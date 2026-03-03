"""
Authentication utilities for password hashing and JWT token management.

This module provides a class for secure password operations
and JWT token generation/validation.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Dict, Literal, Union

from jose import jwt

from app.core.config import settings


class AuthUtils:
    """Utilities for authentication including password and JWT handling."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthUtils, cls).__new__(cls)
        return cls._instance

    def create_access_token(self, data: dict) -> str:
        """Generate a JWT access token."""
        return self.create_token(data=data, token_type="access")

    def create_token(
        self,
        data: dict,
        expires_delta_minutes: int = 60 * 60,
        token_type: Literal["access", "refresh"] = "access",
    ) -> str:
        """Generate a JWT token."""
        to_encode = data.copy()
        to_encode.update({"jti": str(object=uuid.uuid4())})
        expire = datetime.now(UTC) + timedelta(minutes=expires_delta_minutes)
        to_encode.update({"exp": expire})

        secret_key = self.get_secret_key(token_type)
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
        return encoded_jwt

    def decode_access_token(self, token: str) -> Union[Dict[str, str], None]:
        """Decode a JWT access token."""
        return self.decode_token(token, token_type="access")

    def decode_token(
        self, token: str, token_type: Literal["access", "refresh"] = "access"
    ) -> Union[Dict[str, str], None]:
        """Decode a JWT token."""
        try:
            secret_key = self.get_secret_key(token_type)
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except Exception:
            return None

    def get_secret_key(
        self, token_type: Literal["access", "refresh"] = "access"
    ) -> str:
        """Get the secret key for a specific token type."""
        return settings.secret_key


# Singleton instance
auth_utils = AuthUtils()
