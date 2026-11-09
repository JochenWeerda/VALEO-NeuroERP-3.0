"""DOM-SALES-004 Unit Tests — Lieferschein-Close (.3), Preisabweichung (.4)."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock


def _mock_db(sql_map: dict):
    db = MagicMock()

    def side_effect(stmt, params=None):
        sql = str(stmt)
        m = MagicMock()
        for keyword, value in sql_map.items():
            if keyword in sql:
                if isinstance(value, list):
                    m.mappings.return_value.all.return_value = value
                    m.mappings.return_value.first.return_value = value[0] if value else None
                else:
                    m.mappings.return_value.first.return_value = value
                    m.mappings.return_value.all.return_value = [value] if value is not None else []
                return m
        m.mappings.return_value.first.return_value = None
        m.mappings.return_value.all.return_value = []
        return m

    db.execute.side_effect = side_effect
    return db


# ---------------------------------------------------------------------------
# Lieferschein Close
# ---------------------------------------------------------------------------

class TestLieferscheinClose:
    def _ls(self, status="OFFEN"):
        return {"id": "ls-1", "tenant_id": "t1", "status": status, "delivery_number": "LS-2026-001"}

    def test_kommissionierung(self):
        from app.services.sales_lieferschein_close_service import advance_lieferschein
        db = _mock_db({"sales_delivery_notes": self._ls()})
        result = advance_lieferschein(db, "ls-1", "t1", "KOMMISSIONIERT")
        assert result["status"] == "KOMMISSIONIERT"
        assert result["idempotent"] is False

    def test_quittierung(self):
        from app.services.sales_lieferschein_close_service import advance_lieferschein
        db = _mock_db({"sales_delivery_notes": self._ls(status="VERSANDT")})
        result = advance_lieferschein(db, "ls-1", "t1", "QUITTIERT", quittiert_von="Empfänger GmbH")
        assert result["status"] == "QUITTIERT"

    def test_bereits_quittiert_idempotent(self):
        from app.services.sales_lieferschein_close_service import advance_lieferschein
        db = _mock_db({"sales_delivery_notes": self._ls(status="QUITTIERT")})
        result = advance_lieferschein(db, "ls-1", "t1", "QUITTIERT")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_rückwärts_transition_raises(self):
        from app.services.sales_lieferschein_close_service import advance_lieferschein, LSCloseError
        db = _mock_db({"sales_delivery_notes": self._ls(status="VERSANDT")})
        with pytest.raises(LSCloseError, match="Ungültiger"):
            advance_lieferschein(db, "ls-1", "t1", "OFFEN")


# ---------------------------------------------------------------------------
# Preisabweichung
# ---------------------------------------------------------------------------

class TestPreisabweichung:
    def test_auto_freigabe_unter_schwelle(self):
        from app.services.sales_preisabweichung_service import pruefe_preisabweichung
        db = _mock_db({"sales_preisabweichungen": None})
        result = pruefe_preisabweichung(db, "a-1", "t1", "art-1", 100.0, 101.5, schwelle_pct=2.0)
        assert result["status"] == "AUTO_FREIGEGEBEN"
        assert result["abweichung_pct"] == pytest.approx(1.5)

    def test_eskalation_über_schwelle(self):
        from app.services.sales_preisabweichung_service import pruefe_preisabweichung
        db = _mock_db({"sales_preisabweichungen": None})
        result = pruefe_preisabweichung(db, "a-1", "t1", "art-1", 100.0, 105.0, schwelle_pct=2.0)
        assert result["status"] == "ESKALIERT"
        assert result["abweichung_pct"] == pytest.approx(5.0)

    def test_idempotent_wenn_existiert(self):
        from app.services.sales_preisabweichung_service import pruefe_preisabweichung
        existing = {"id": "p-1", "auftrag_id": "a-1", "tenant_id": "t1",
                    "artikel_id": "art-1", "status": "ESKALIERT", "abweichung_pct": 5.0}
        db = _mock_db({"sales_preisabweichungen": existing})
        result = pruefe_preisabweichung(db, "a-1", "t1", "art-1", 100.0, 105.0)
        assert result["idempotent"] is True

    def test_freigabe_eskalierter_abweichung(self):
        from app.services.sales_preisabweichung_service import freigabe_preisabweichung
        abw = {"id": "p-1", "tenant_id": "t1", "auftrag_id": "a-1",
               "status": "ESKALIERT", "abweichung_pct": 5.0}
        db = _mock_db({"sales_preisabweichungen": abw})
        result = freigabe_preisabweichung(db, "p-1", "t1", "FREIGEGEBEN", "mgr-1", grund="Sonderkonditionen")
        assert result["status"] == "FREIGEGEBEN"
        db.commit.assert_called_once()

    def test_freigabe_nicht_eskalierter_raises(self):
        from app.services.sales_preisabweichung_service import freigabe_preisabweichung, PreisabweichungError
        abw = {"id": "p-1", "tenant_id": "t1", "status": "AUTO_FREIGEGEBEN", "abweichung_pct": 1.0}
        db = _mock_db({"sales_preisabweichungen": abw})
        with pytest.raises(PreisabweichungError, match="ESKALIERT"):
            freigabe_preisabweichung(db, "p-1", "t1", "FREIGEGEBEN", "mgr-1")
