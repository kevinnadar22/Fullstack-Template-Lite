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


from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core import config
from app.utils import auth_utils


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if (
            username != config.settings.admin.username
            or password != config.settings.admin.password
        ):
            return False

        token_data = {"sub": username}
        token = auth_utils.create_access_token(token_data)
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
        if payload.get("sub") != config.settings.admin.username:
            return False
        # Check the token in depth
        return True


admin_views = []
admin_authentication = AdminAuth(secret_key=config.settings.secret_key)
