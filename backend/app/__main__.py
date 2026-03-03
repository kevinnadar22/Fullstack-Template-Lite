"""
FastAPI application for Hair Try-On API.

This module serves as the main entry point for the FastAPI application.
It configures middleware, sets up logging, and includes API routers.

Routes included:
- /api/v1/*: All API v1 routes (auth, files upload, image generation, user
management)
"""

from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from loguru import logger
from sqladmin import Admin

from app.admin import admin_authentication, admin_views
from app.api.router import router as api_router
from app.core.config import settings
from app.core.errors import setup_exception_handler
from app.core.logging import setup_logging
from app.core.middleware import setup_middlewares
from app.core.ratelimiting import setup_ratelimiting
from app.core.telementry import init_telemetry
from app.db import Base, engine

setup_logging(log_level=settings.resolved_log_level, is_prod=settings.is_prod)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # log with the logger
    logger.info(
        "Application starting up...",
        prod=settings.is_prod,
        log_level=settings.resolved_log_level,
        TZ=settings.tz,
        frontend_url=settings.frontend_url,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    logger.info("Application shutting down...")

    await engine.dispose()
    if settings.logfire_token:
        logfire.shutdown()
    logger.info("Application shutdown complete.")
    logger.remove()


app = FastAPI(
    responses={429: {"error": "Too Many Requests - Rate limit exceeded"}},
    debug=not settings.is_prod,
    title="Fullstack Template Lite API",
    description="API for Fullstack Template Lite",
    version="1.0.0",
    openapi_url=None if settings.is_prod else "/openapi.json",
    docs_url=None if settings.is_prod else "/docs",
    redoc_url=None if settings.is_prod else "/redoc",
    lifespan=lifespan,
)

admin = Admin(app, engine, authentication_backend=admin_authentication)
for view in admin_views:
    admin.add_view(view)

init_telemetry(app, engine=engine, logfire_token=settings.logfire_token)
setup_ratelimiting(app)
setup_middlewares(app)
setup_exception_handler(app, is_production=settings.is_prod)
app.include_router(api_router)
