"""
Optional: Finance-Follow-up-CSV nach S3-kompatiblem Object Storage (AWS S3, MinIO).

Env:
- FINANCE_EXPORT_S3_BUCKET (Pflicht fuer Upload)
- FINANCE_EXPORT_S3_PREFIX (optional, default finance-exports/)
- AWS_REGION / AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
- AWS_ENDPOINT_URL_S3 (optional, z. B. MinIO http://localhost:9000)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def try_upload_finance_csv_to_s3(
    file_path: str,
    *,
    label: str,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """
    Returns:
        {"ok": bool, "document_id": None, "url": str|None, "error": str|None}
    """
    bucket = os.environ.get("FINANCE_EXPORT_S3_BUCKET")
    if not bucket:
        return {
            "ok": False,
            "document_id": None,
            "url": None,
            "error": "FINANCE_EXPORT_S3_BUCKET not set",
        }

    path = Path(file_path)
    if not path.is_file():
        return {
            "ok": False,
            "document_id": None,
            "url": None,
            "error": "file not found",
        }

    prefix = (os.environ.get("FINANCE_EXPORT_S3_PREFIX") or "finance-exports/").strip("/")
    safe_label = label.replace("..", "").replace("\\", "/")
    key = f"{prefix}/{tenant_id or 'global'}/{safe_label}".replace("//", "/")

    try:
        import boto3  # type: ignore[import-untyped]
    except ImportError:
        return {
            "ok": False,
            "document_id": None,
            "url": None,
            "error": "boto3 not installed",
        }

    try:
        session = boto3.session.Session()
        kwargs: dict[str, Any] = {}
        endpoint = os.environ.get("AWS_ENDPOINT_URL_S3")
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        client = session.client("s3", **kwargs)
        extra: dict[str, Any] = {}
        if os.environ.get("FINANCE_EXPORT_S3_SSE") == "1":
            extra["ServerSideEncryption"] = "AES256"
        client.upload_file(str(path), bucket, key, ExtraArgs=extra or None)

        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-central-1"
        if endpoint:
            base = endpoint.rstrip("/")
            url = f"{base}/{bucket}/{key}"
        else:
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        return {"ok": True, "document_id": None, "url": url, "error": None}
    except Exception as exc:
        logger.warning("Finance export S3 upload failed: %s", exc)
        return {"ok": False, "document_id": None, "url": None, "error": str(exc)}
