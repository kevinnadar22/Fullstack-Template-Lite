#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: middleware.py
Author: Maria Kevin
Created: 2025-11-22
Description: Middleware for FastAPI application
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from app.core.config import settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


def setup_middlewares(app: FastAPI):
    # Add ProxyHeadersMiddleware FIRST to properly handle X-Forwarded-* headers
    # This ensures FastAPI recognizes HTTPS connections when behind a reverse proxy
    app.add_middleware(
        ProxyHeadersMiddleware,
        trusted_hosts="*",  # In production, specify your proxy IP addresses
    )

    origins = ["http://localhost:5173"]
    if settings.FRONTEND_URL:
        origins.append(settings.FRONTEND_URL)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        same_site="lax",
        https_only=settings.IS_PROD,
    )
