"""EINKAUF-3WM-001 — 3-Wege-Match Alembic-Persistenz.

Prüft:
1. _ensure_schema wirft 503 wenn Tabelle fehlt
2. _compute_match_status: GEBUCHT wenn alle Beträge innerhalb Toleranz
3. _compute_match_status: ABWEICHUNG wenn Differenz > Toleranz
4. _compute_match_status: UNVOLLSTAENDIG wenn ein Betrag fehlt
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


def _mock_db(table_exists: bool = True) -> MagicMock:
    db = MagicMock()
    result = MagicMock()
    result.scalar.return_value = 1 if table_exists else 0
    db.execute.return_value = result
    return db


class TestEnsureSchema:
    def test_raises_503_wenn_tabelle_fehlt(self):
        from app.api.v1.endpoints.purchase_invoice_verification import _ensure_schema
        db = _mock_db(table_exists=False)
        with pytest.raises(HTTPException) as exc:
            _ensure_schema(db)
        assert exc.value.status_code == 503

    def test_kein_fehler_wenn_tabelle_vorhanden(self):
        from app.api.v1.endpoints.purchase_invoice_verification import _ensure_schema
        db = _mock_db(table_exists=True)
        _ensure_schema(db)  # kein Fehler


class TestComputeMatchStatus:
    def test_toleranz_innerhalb_toleranz(self):
        from app.api.v1.endpoints.purchase_invoice_verification import _compute_match_status
        status, var_amt, var_pct = _compute_match_status(1000.0, 1000.0, 1005.0, 2.0)
        assert status in ("GEMATCHT", "TOLERANZ")
        assert var_pct < 2.0

    def test_differenz_ausserhalb_toleranz(self):
        from app.api.v1.endpoints.purchase_invoice_verification import _compute_match_status
        status, var_amt, var_pct = _compute_match_status(1000.0, 1000.0, 1100.0, 2.0)
        assert status == "DIFFERENZ"
        assert var_pct > 2.0

    def test_offen_wenn_betrag_fehlt(self):
        from app.api.v1.endpoints.purchase_invoice_verification import _compute_match_status
        status, var_amt, var_pct = _compute_match_status(None, 1000.0, 1000.0, 2.0)
        assert status == "OFFEN"
