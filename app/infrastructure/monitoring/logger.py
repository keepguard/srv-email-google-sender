"""Structured Logging Configuration."""

import structlog
import logging
import sys
from typing import Optional


def configure_logging(level: str = "info", format_type: str = "json") -> None:
    """Configure structured logging."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get structured logger."""
    return structlog.get_logger(name)


def log_email_send_started(
    to: str,
    subject: str,
    correlation_id: str
) -> None:
    """Log email send started."""
    logger = get_logger()
    logger.info(
        "email_send_started",
        to=to,
        subject=subject,
        correlation_id=correlation_id
    )


def log_email_sent_success(
    to: str,
    subject: str,
    duration_ms: int,
    message_id: str,
    correlation_id: str
) -> None:
    """Log email sent success."""
    logger = get_logger()
    logger.info(
        "email_sent_success",
        to=to,
        subject=subject,
        duration_ms=duration_ms,
        message_id=message_id,
        correlation_id=correlation_id
    )


def log_email_send_failed(
    to: str,
    subject: str,
    error_type: str,
    error_message: str,
    retry_attempt: int,
    correlation_id: str
) -> None:
    """Log email send failure."""
    logger = get_logger()
    logger.error(
        "email_send_failed",
        to=to,
        subject=subject,
        error_type=error_type,
        error_message=error_message,
        retry_attempt=retry_attempt,
        correlation_id=correlation_id
    )


def log_rabbitmq_message_consumed(
    queue: str,
    message_id: str,
    correlation_id: str
) -> None:
    """Log RabbitMQ message consumed."""
    logger = get_logger()
    logger.info(
        "rabbitmq_message_consumed",
        queue=queue,
        message_id=message_id,
        correlation_id=correlation_id
    )


def log_rabbitmq_message_ack(
    queue: str,
    message_id: str,
    duration_ms: int,
    correlation_id: str
) -> None:
    """Log RabbitMQ message ACK."""
    logger = get_logger()
    logger.info(
        "rabbitmq_message_ack",
        queue=queue,
        message_id=message_id,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )


def log_rabbitmq_message_nack(
    queue: str,
    message_id: str,
    error: str,
    correlation_id: str
) -> None:
    """Log RabbitMQ message NACK."""
    logger = get_logger()
    logger.error(
        "rabbitmq_message_nack",
        queue=queue,
        message_id=message_id,
        error=error,
        correlation_id=correlation_id
    )


def log_token_refresh_started(
    email: str,
    expires_in_seconds: int,
    correlation_id: str
) -> None:
    """Log token refresh started."""
    logger = get_logger()
    logger.info(
        "token_refresh_started",
        email=email,
        expires_in_seconds=expires_in_seconds,
        correlation_id=correlation_id
    )


def log_token_refresh_success(
    email: str,
    new_expiry: str,
    duration_ms: int,
    correlation_id: str
) -> None:
    """Log token refresh success."""
    logger = get_logger()
    logger.info(
        "token_refresh_success",
        email=email,
        new_expiry=new_expiry,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )


def log_gmail_api_call(
    method: str,
    status: str,
    duration_ms: int,
    correlation_id: str
) -> None:
    """Log Gmail API call."""
    logger = get_logger()
    logger.info(
        "gmail_api_call",
        method=method,
        status=status,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: int,
    correlation_id: str
) -> None:
    """Log API request."""
    logger = get_logger()
    logger.info(
        "api_request",
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )

