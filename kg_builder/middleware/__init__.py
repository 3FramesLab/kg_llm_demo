"""Middleware package for FastAPI application."""
from kg_builder.middleware.logging_middleware import (
    DetailedLoggingMiddleware,
    log_function_calls
)

__all__ = ["DetailedLoggingMiddleware", "log_function_calls"]
