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
from pydantic import ConfigDict
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

    SECRET_KEY: str = "your-secret"

    @property
    def IS_PROD(self) -> bool:
        return self.ENV == "prod"

    model_config = ConfigDict(env_file=(dev_file, prod_file), extra="ignore")  # type: ignore


settings = Settings()  # type: ignore
