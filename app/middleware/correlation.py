"""
Correlation ID Middleware
Generates and tracks correlation IDs for request tracing
"""

import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import set_correlation_id, get_correlation_id

logger = logging.getLogger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track correlation IDs."""
    
    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Set in context
        set_correlation_id(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        
        return response

