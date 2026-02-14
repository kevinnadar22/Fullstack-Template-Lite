#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: config.py
Author: Maria Kevin
Description: Brief description
"""

import os
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings

dev_file = ".dev.env"
prod_file = ".prod.env"

load_dotenv(dev_file if os.path.exists(dev_file) else prod_file)


class Settings(BaseSettings):
    """Application configuration settings."""

    DATABASE_URL: str = "sqlite:///./instance/test.db"
    ENV: Literal["dev", "prod"] = "dev"
    FRONTEND_URL: str

    LOGFIRE_TOKEN: Optional[str] = None

    # Celery
    RABBITMQ_URL: Optional[str] = None  # If not None, celery enabled

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "123"

    # timezone
    TZ: str = "UTC"

    # Auth Configurations
    ENABLE_LOGIN_OTP: bool = False
    ENABLE_SIGNUP_OTP: bool = False
    ENABLE_GOOGLE_AUTH: bool = False

    SECRET_KEY: str = "your-secret"
    REFRESH_SECRET_KEY: str = "your-refresh-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10  # 10 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Google OAuth Configurations
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URL: Optional[str] = None

    # Mail Configurations
    BREVO_API_KEY: Optional[str] = None
    MAIL_FROM_EMAIL: Optional[str] = None
    MAIL_FROM_NAME: Optional[str] = None

    @model_validator(mode="after")
    def validate_config(self) -> "Settings":
        if self.ENABLE_GOOGLE_AUTH:
            if not all(
                [
                    self.GOOGLE_CLIENT_ID,
                    self.GOOGLE_CLIENT_SECRET,
                    self.GOOGLE_REDIRECT_URL,
                ]
            ):
                raise ValueError(
                    "Google OAuth credentials (ID, Secret, Redirect URL) must be provided when ENABLE_GOOGLE_AUTH is True"
                )

        if self.ENABLE_LOGIN_OTP or self.ENABLE_SIGNUP_OTP:
            if not all([self.BREVO_API_KEY, self.MAIL_FROM_EMAIL, self.MAIL_FROM_NAME]):
                raise ValueError(
                    "Mail configurations (Brevo API Key, From Email, From Name) must be provided when OTP is enabled"
                )

        return self

    @property
    def IS_PROD(self) -> bool:
        return self.ENV == "prod"

    model_config = ConfigDict(env_file=(dev_file, prod_file), extra="ignore")  # type: ignore


settings = Settings()  # type: ignore
