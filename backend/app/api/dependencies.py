#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dependencies.py
Author: Maria Kevin
Description: FastAPI dependencies for service injection and authentication.
"""

from typing import Annotated

from fastapi import Depends

from app.db import AsyncSession, get_async_session


DatabaseDep = Annotated[AsyncSession, Depends(get_async_session)]
