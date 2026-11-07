"""Real signature verification at the MCP command boundary, without database writes."""
import hashlib
import hmac
import json
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from app.services.mcp_execution_service import ToolExecutionRequest, _query_import_signed


@pytest.mark.parametrize("mode", ["dryRun", "execute"])
def test_tampered_signed_bundle_never_imports_or_records_success(mode):
    key = "synthetic-query-signing-key"
    payload = {"schema_version": 1, "definition": {"name": "Original"}}
    signature = hmac.new(key.encode(), json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
    bundle = {**payload, "signature": signature, "definition": {"name": "Tampered"}}
    db = Mock()
    request = ToolExecutionRequest(tool_name="reporting.query.import_signed", mode=mode,
        idempotency_key="synthetic-import-once", parameters={"reason": "Signaturpruefung", "bundle": bundle})
    with patch("app.core.config.settings.SECRET_KEY", key), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None), \
         patch("app.services.query_center_service.QueryCenterService.import_signed") as save, \
         patch("app.services.mcp_execution_service._write_audit") as audit, \
         patch("app.services.mcp_execution_service._store_execution") as record:
        with pytest.raises(HTTPException) as raised:
            _query_import_signed(db, request, "synthetic-actor", "synthetic-tenant")
    assert raised.value.status_code == 422
    assert "Signatur" in raised.value.detail
    save.assert_not_called()
    audit.assert_not_called()
    record.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    db.execute.assert_not_called()
