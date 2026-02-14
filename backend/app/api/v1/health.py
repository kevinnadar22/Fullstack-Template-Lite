#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: health.py
Author: Maria Kevin
Description: Health check endpoint for monitoring
"""

from fastapi import APIRouter

from app.domain import schemas

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=schemas.APIResponse[schemas.HealthResponse])
async def health_check() -> schemas.APIResponse[schemas.HealthResponse]:
    """
    Health check endpoint for Docker and monitoring systems.

    Returns:
        APIResponse[HealthResponse]: Status of the application
    """
    return schemas.APIResponse(
        data=schemas.HealthResponse(status="healthy", service="api", version="1.0.0")
    )
