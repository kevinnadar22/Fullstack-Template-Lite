#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: logging.py
Author: Maria Kevin
Created: 2025-11-21
Description: Brief description
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


import json
import logging
import sys
import traceback
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Record


def _json_formatter(record: "Record") -> str:
    """Emit only the essential fields as a compact JSON line."""
    payload: dict = {
        "time": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }
    # Add any extra context fields
    payload.update(record["extra"])

    exc = record["exception"]
    if exc is not None:
        payload["exception"] = "".join(traceback.format_exception(*exc))

    return json.dumps(payload) + "\n"


def _dev_formatter(record: "Record") -> str:
    """Formatter for dev logs that only shows {extra} if it's not empty."""
    extra = " <blue>{extra}</blue>" if record["extra"] else ""
    exception = "\n<level>{exception}</level>" if record["exception"] else ""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>" + extra + exception + "\n"
    )


class InterceptHandler(logging.Handler):
    """A logging handler that intercepts standard logging messages and redirects them to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        # find caller where logging was called
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(log_level: str = "DEBUG", is_prod: bool = False) -> None:
    """Set up logging configuration.

    - Dev:  human-readable colored output, DEBUG level, backtrace + diagnose enabled.
    - Prod: structured JSON logs, INFO (or configured) level, no diagnose (avoids leaking locals).
    """
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    for name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "starlette",
        "celery",
        "amqp",
        "kombu",
        "pika",
        "sqlalchemy",
    ):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.remove()

    if is_prod:
        logger.add(
            "log/app.log",
            rotation="10 MB",
            retention="10 days",
            level=log_level,
            format=_json_formatter,
        )
        logger.add(
            "log/error.log",
            rotation="10 MB",
            retention="30 days",
            level="ERROR",
            format=_json_formatter,
        )
        logger.add(
            sys.stdout,
            level=log_level,
            format=_json_formatter,
        )
    else:
        logger.add(
            "log/app.log",
            rotation="10 MB",
            retention="10 days",
            level=log_level,
            format=_dev_formatter,
        )
        logger.add(
            "log/error.log",
            rotation="10 MB",
            retention="30 days",
            level="ERROR",
            format=_dev_formatter,
        )
        logger.add(
            sys.stdout,
            level=log_level,
            format=_dev_formatter,
            backtrace=True,
            diagnose=True,
        )

    # Capture unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
            "Unhandled exception"
        )

    sys.excepthook = handle_exception

    logger.info("Logging is set up. level={} json={}", log_level, is_prod)
