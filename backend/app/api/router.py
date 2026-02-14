#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: router.py
Author: Maria Kevin
Created: 2026-01-23
Description: Main API router that includes all v1 endpoints
"""

from fastapi import APIRouter

from .v1 import health

router = APIRouter(prefix="/api/v1")

# Include all v1 routers
router.include_router(health.router)
