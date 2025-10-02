"""
VALEO-NeuroERP Logging Configuration
Structured logging with JSON format for production
"""

import logging
import sys
from typing import Dict, Any
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add custom fields
        log_record['service'] = 'valeo-neuro-erp'
        log_record['version'] = '3.0.0'

        # Add request ID if available (will be set by middleware)
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id


def setup_logging():
    """
    Configure logging for the application
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.LOG_FORMAT == "json":
        # JSON format for production
        formatter = CustomJsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

    # Log startup
    logger.info("Logging configured", extra={
        'log_level': settings.LOG_LEVEL,
        'log_format': settings.LOG_FORMAT,
        'debug_mode': settings.DEBUG
    })


def get_request_logger(request_id: str = None):
    """
    Get a logger with request context
    """
    logger = logging.getLogger('request')
    if request_id:
        # Create a logger adapter with request ID
        class RequestLoggerAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs['extra'] = kwargs.get('extra', {})
                kwargs['extra']['request_id'] = request_id
                return msg, kwargs

        return RequestLoggerAdapter(logger, {'request_id': request_id})

    return logger