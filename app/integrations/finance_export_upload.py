"""
Orchestrierung DMS dann S3 fuer Finance-Follow-up-Exports.
"""

from __future__ import annotations

from typing import Any

from app.integrations.finance_export_dms import try_upload_finance_csv_to_dms
from app.integrations.finance_export_s3 import try_upload_finance_csv_to_s3


def upload_finance_export_csv(
    file_path: str,
    *,
    label: str,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """
    Zuerst Mayan-DMS (falls konfiguriert), sonst S3/MinIO.
    """
    dms = try_upload_finance_csv_to_dms(file_path, label=label)
    if dms.get("ok"):
        return {**dms, "backend": "dms"}

    s3 = try_upload_finance_csv_to_s3(file_path, label=label, tenant_id=tenant_id)
    if s3.get("ok"):
        return {**s3, "backend": "s3"}

    err = dms.get("error") or s3.get("error") or "no upload backend succeeded"
    return {
        "ok": False,
        "document_id": None,
        "url": None,
        "error": err,
        "backend": None,
    }
