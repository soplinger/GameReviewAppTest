"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict
import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log entries."""
    event_dict["app"] = "game-review-platform"
    event_dict["environment"] = "development"  # TODO: Get from config
    return event_dict


def configure_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output logs in JSON format; otherwise use console format
    """
    # Determine processors based on output format
    if json_logs:
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_app_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            add_app_context,
            structlog.dev.set_exc_info,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )
    
    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


# Request logging middleware helper
def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any,
) -> None:
    """
    Log an HTTP request with structured data.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        **kwargs: Additional context to log
    """
    logger = get_logger("api")
    
    log_data: Dict[str, Any] = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **kwargs,
    }
    
    if status_code >= 500:
        logger.error("Request failed", **log_data)
    elif status_code >= 400:
        logger.warning("Client error", **log_data)
    else:
        logger.info("Request completed", **log_data)


# Convenience functions for common log scenarios
def log_database_query(query: str, duration_ms: float, row_count: int = 0) -> None:
    """Log a database query execution."""
    logger = get_logger("database")
    logger.debug(
        "Query executed",
        query=query[:200],  # Truncate long queries
        duration_ms=round(duration_ms, 2),
        row_count=row_count,
    )


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
) -> None:
    """Log an external API call."""
    logger = get_logger("external_api")
    logger.info(
        "External API call",
        service=service,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
    )


def log_auth_event(event_type: str, user_id: int | None = None, **kwargs: Any) -> None:
    """Log an authentication event."""
    logger = get_logger("auth")
    logger.info(
        event_type,
        user_id=user_id,
        **kwargs,
    )


def log_business_event(event_type: str, **kwargs: Any) -> None:
    """Log a business logic event."""
    logger = get_logger("business")
    logger.info(event_type, **kwargs)
