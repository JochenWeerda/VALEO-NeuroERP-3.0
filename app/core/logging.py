"""
Logging Configuration with PII Redaction
"""

import logging
import re
import sys
from typing import Any


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


def setup_logging():
    """
    Setup logging with PII redaction
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter (JSON-like for structured logging)
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
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
