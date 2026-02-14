#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: lifespan.py
Author: Maria Kevin
Created: 2025-12-01
Description: Brief description
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # creates the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
