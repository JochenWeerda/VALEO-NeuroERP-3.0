"""
Logging Configuration with PII Redaction and Structured JSON
"""

import logging
import re
import sys
import json
from typing import Any
from datetime import datetime
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


class JSONFormatter(logging.Formatter):
    """
    Formatter for structured JSON logging with correlation IDs
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Add extra fields from record
        if hasattr(record, 'event_id'):
            log_data["event_id"] = record.event_id
        if hasattr(record, 'aggregate_id'):
            log_data["aggregate_id"] = record.aggregate_id
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class PIIRedactionFilter(logging.Filter):
    """
    Filter to redact PII from log messages
    """
    
    # Patterns to redact
    PATTERNS = [
        (re.compile(r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE), 'token=***'),
        (re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE), 'password=***'),
        (re.compile(r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE), 'secret=***'),
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE), 'api_key=***'),
        (re.compile(r'bearer\s+([a-zA-Z0-9_\-\.]+)', re.IGNORECASE), 'Bearer ***'),
        # Email-Adressen teilweise redaktieren
        (re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), r'***@\2'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact PII from log message"""
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        
        # Also redact args if present
        if record.args:
            record.args = tuple(
                self._redact_value(arg) for arg in record.args
            )
        
        return True
    
    def _redact_value(self, value: Any) -> Any:
        """Redact PII from a value"""
        if isinstance(value, str):
            for pattern, replacement in self.PATTERNS:
                value = pattern.sub(replacement, value)
        return value


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_var.set(correlation_id)


def setup_logging(json_format: bool = True):
    """
    Setup logging with PII redaction and optional JSON formatting
    
    Args:
        json_format: If True, use structured JSON logging. If False, use traditional format.
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    if json_format:
        # Structured JSON logging
        formatter = JSONFormatter()
    else:
        # Traditional logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add PII redaction filter
    console_handler.addFilter(PIIRedactionFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
