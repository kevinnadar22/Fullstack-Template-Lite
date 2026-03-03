#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: config.py
Author: Maria Kevin
Description: Brief description
"""

import os
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, YamlConfigSettingsSource
from pydantic_settings_yaml import YamlBaseSettings

default_file = "secrets/config.yaml"
dev_file = "secrets/dev.config.yaml"
prod_file = "secrets/prod.config.yaml"

# take dev is it exists, else prod exists then prod, else the default
if os.path.exists(dev_file):
    selected_config = dev_file
elif os.path.exists(prod_file):
    selected_config = prod_file
else:
    selected_config = default_file


class Database(BaseModel):
    url: str = Field(default="sqlite:///./instance/test.db")


class Admin(BaseModel):
    username: str = Field(default="admin")
    password: str = Field(default="123")


class Celery(BaseModel):
    rabbitmq_url: Optional[str] = Field(default=None)


class Settings(YamlBaseSettings):
    """Application configuration settings."""

    database: Database = Field(default_factory=Database)
    admin: Admin = Field(default_factory=Admin)
    celery: Celery = Field(default_factory=Celery)

    env: Literal["dev", "prod"] = "dev"
    log_level: str = ""
    frontend_url: str = "http://localhost:5173"
    logfire_token: Optional[str] = None
    tz: str = "UTC"
    secret_key: str = "your-secret"

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @property
    def resolved_log_level(self) -> str:
        """OS environ > explicit log_level > env-based default."""
        if self.log_level:
            return self.log_level.upper()
        return "INFO" if self.is_prod else "DEBUG"

    model_config = SettingsConfigDict(
        yaml_file=selected_config,
        extra="ignore",
        secrets_dir="secrets",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


settings = Settings()
