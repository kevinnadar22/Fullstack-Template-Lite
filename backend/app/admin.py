#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: admin.py
Author: Maria Kevin
Created: 2025-11-08
Description: Admin interface for managing application data using SQLAdmin.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core import config
from app.domain import models
from app.utils import auth_utils


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if (
            username != config.settings.ADMIN_USERNAME
            or password != config.settings.ADMIN_PASSWORD
        ):
            return False

        token_data = {"sub": username}
        token = auth_utils.create_access_token(
            token_data, expires_delta_minutes=60 * 60
        )  # 1 hour validity
        request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False
        payload = auth_utils.decode_access_token(token)
        if not payload:
            return False
        if payload.get("sub") != config.settings.ADMIN_USERNAME:
            return False
        # Check the token in depth
        return True


class UserAdmin(ModelView, model=models.Users):
    column_list = [models.Users.id, models.Users.email, models.Users.verified]
    column_searchable_list = [models.Users.email]
    column_sortable_list = [models.Users.id, models.Users.verified]
    icon = "fa-solid fa-user"


class BlacklistTokenAdmin(ModelView, model=models.BlackListTokens):
    column_list = [
        models.BlackListTokens.id,
        models.BlackListTokens.jti,
        models.BlackListTokens.token_type,
        models.BlackListTokens.blacklisted_on,
    ]
    column_searchable_list = [models.BlackListTokens.jti]
    column_sortable_list = [
        models.BlackListTokens.id,
        models.BlackListTokens.blacklisted_on,
    ]
    icon = "fa-solid fa-ban"


admin_views = [UserAdmin, BlacklistTokenAdmin]
admin_authentication = AdminAuth(secret_key=config.settings.SECRET_KEY)
