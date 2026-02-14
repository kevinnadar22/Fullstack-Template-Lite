#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: errors.py
Author: Maria Kevin
Description: Brief description
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from .exceptions import AppException


def setup_exception_handler(app: FastAPI, is_production: bool) -> None:
    if not is_production:
        return

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "success": False},
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "success": False,
            },
        )

    # RequestValidationError
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error, please check your input.",
                "success": False,
            },
        )
