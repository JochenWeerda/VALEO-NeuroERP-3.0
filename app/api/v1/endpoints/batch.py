"""
OData-style $batch endpoint for bundling multiple read requests.

Accepts up to MAX_SUBREQUESTS GET-only sub-requests, executes them in
parallel via the ASGI app, and returns a combined JSON response.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_SUBREQUESTS = 10
SUBREQUEST_TIMEOUT_S = 5.0
ALLOWED_PATH_PREFIX = "/api/v1/"


class SubRequest(BaseModel):
    id: str = Field(description="Client-assigned correlation id")
    path: str = Field(description="Relative API path, e.g. /api/v1/contacts?skip=0&limit=25")

    @field_validator("path")
    @classmethod
    def _validate_path(cls, v: str) -> str:
        if not v.startswith(ALLOWED_PATH_PREFIX):
            raise ValueError(f"Only paths starting with {ALLOWED_PATH_PREFIX} are allowed")
        return v


class BatchRequest(BaseModel):
    requests: list[SubRequest] = Field(max_length=MAX_SUBREQUESTS)


class SubResponse(BaseModel):
    id: str
    status: int
    body: Any


class BatchResponse(BaseModel):
    responses: list[SubResponse]


async def _execute_subrequest(
    app: Any,
    sub: SubRequest,
    headers: list[tuple[bytes, bytes]],
) -> SubResponse:
    """Execute a single GET sub-request through the ASGI app."""
    path_and_query = sub.path.split("?", 1)
    path = path_and_query[0]
    query_string = path_and_query[1] if len(path_and_query) > 1 else ""

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": path,
        "query_string": query_string.encode(),
        "root_path": "",
        "headers": headers,
    }

    response_started = False
    status_code = 500
    body_parts: list[bytes] = []

    async def receive() -> dict:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict) -> None:
        nonlocal response_started, status_code
        if message["type"] == "http.response.start":
            response_started = True
            status_code = message["status"]
        elif message["type"] == "http.response.body":
            body_parts.append(message.get("body", b""))

    try:
        await asyncio.wait_for(app(scope, receive, send), timeout=SUBREQUEST_TIMEOUT_S)
    except asyncio.TimeoutError:
        return SubResponse(id=sub.id, status=504, body={"detail": "Sub-request timed out"})
    except Exception as exc:
        logger.warning("Batch sub-request %s failed: %s", sub.id, exc)
        return SubResponse(id=sub.id, status=500, body={"detail": "Internal error"})

    import json
    raw = b"".join(body_parts)
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        parsed = raw.decode("utf-8", errors="replace")

    return SubResponse(id=sub.id, status=status_code, body=parsed)


@router.post(
    "/$batch",
    response_model=BatchResponse,
    summary="Execute multiple GET requests in a single call",
    tags=["batch"],
)
async def batch_execute(payload: BatchRequest, request: Request) -> BatchResponse:
    """
    OData-style batch endpoint. Accepts up to 10 GET sub-requests, runs them
    concurrently, and returns all responses in one payload. Auth context and
    tenant headers are inherited from the outer request.
    """
    forwarded_headers = [
        (k, v)
        for k, v in request.headers.raw
        if k.lower() in (
            b"authorization",
            b"x-tenant-id",
            b"x-correlation-id",
            b"accept-language",
            b"cookie",
        )
    ]
    forwarded_headers.append((b"host", request.headers.get("host", "localhost").encode()))

    app = request.app

    tasks = [
        _execute_subrequest(app, sub, forwarded_headers)
        for sub in payload.requests
    ]
    results = await asyncio.gather(*tasks)

    return BatchResponse(responses=list(results))
