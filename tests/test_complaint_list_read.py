from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.api.v1.endpoints.mask_frontend_bridges import list_qualitaet_reklamationen
from app.services import complaint_list_read


def test_list_scopes_tenant_and_preserves_status_and_unknown_priority(monkeypatch):
    db = MagicMock()
    rows = [
        {"reklamation_id": str(i), "status": status, "lieferant_id": "s", "positionen": []}
        for i, status in enumerate(["offen", "in_pruefung", "teilweise_anerkannt", "anerkannt", "geschlossen", "abgelehnt", "wartet", None])
    ]
    db.execute.return_value.mappings.return_value.all.return_value = rows
    resolve = MagicMock(return_value=SimpleNamespace(name="Lieferant", number="L-1"))
    monkeypatch.setattr(complaint_list_read, "resolve_reference", resolve)
    result = list_qualitaet_reklamationen(tenant_id="tenant-a", db=db)
    sql, params = db.execute.call_args.args
    assert "tenant_id = :t" in str(sql)
    assert "LIMIT 200" in str(sql)
    assert params == {"t": "tenant-a"}
    resolve.assert_called_once_with(db, "tenant-a", "supplier", "s")
    assert [item["status"] for item in result] == ["neu", "in-bearbeitung", "in-bearbeitung", "in-bearbeitung", "geloest", "abgelehnt", "wartet", "unbekannt"]
    assert all(item["prioritaet"] is None for item in result)
    assert result[0]["kunde"] == "Lieferant"


def test_list_database_failure_rolls_back_and_returns_sanitized_503():
    db = MagicMock()
    db.execute.side_effect = OperationalError("secret SQL", {}, Exception("secret database"))
    with pytest.raises(HTTPException) as caught:
        list_qualitaet_reklamationen(tenant_id="tenant-a", db=db)
    assert caught.value.status_code == 503
    assert "secret" not in str(caught.value.detail)
    db.rollback.assert_called_once()
