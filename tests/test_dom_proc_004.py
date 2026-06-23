"""DOM-PROC-004 Unit Tests — Bestellung-Lifecycle (.2), Wareneingang (.3), Rechnungsprüfung (.4)."""
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
# Bestellung Lifecycle
# ---------------------------------------------------------------------------

class TestBestellungLifecycle:
    def _bestellung(self, status="DRAFT"):
        return {"id": "b-1", "tenant_id": "t1", "status": status, "bestellnummer": "BES-2026-001"}

    def test_freigabe_aus_draft(self):
        from app.services.proc_bestellung_lifecycle_service import transition_bestellung_status
        db = _mock_db({"proc_purchase_orders": self._bestellung()})
        result = transition_bestellung_status(db, "b-1", "t1", "FREIGEGEBEN", operator="mgr-1")
        assert result["status"] == "FREIGEGEBEN"
        db.commit.assert_called_once()

    def test_versenden_aus_freigegeben(self):
        from app.services.proc_bestellung_lifecycle_service import transition_bestellung_status
        db = _mock_db({"proc_purchase_orders": self._bestellung(status="FREIGEGEBEN")})
        result = transition_bestellung_status(db, "b-1", "t1", "VERSANDT")
        assert result["status"] == "VERSANDT"

    def test_storno_aus_draft(self):
        from app.services.proc_bestellung_lifecycle_service import transition_bestellung_status
        db = _mock_db({"proc_purchase_orders": self._bestellung()})
        result = transition_bestellung_status(db, "b-1", "t1", "STORNIERT", reason="Nicht mehr benötigt")
        assert result["status"] == "STORNIERT"

    def test_ungültiger_übergang_raises(self):
        from app.services.proc_bestellung_lifecycle_service import transition_bestellung_status, BestellungLifecycleError
        db = _mock_db({"proc_purchase_orders": self._bestellung(status="WE_ERHALTEN")})
        with pytest.raises(BestellungLifecycleError, match="Ungültiger"):
            transition_bestellung_status(db, "b-1", "t1", "DRAFT")


# ---------------------------------------------------------------------------
# Wareneingang
# ---------------------------------------------------------------------------

class TestWareneingang:
    def _bestellung(self, status="VERSANDT"):
        return {"id": "b-1", "tenant_id": "t1", "status": status}

    def test_we_buchen_ok(self):
        from app.services.proc_wareneingang_service import buche_wareneingang
        db = MagicMock()
        call_n = [0]

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            call_n[0] += 1
            if "proc_purchase_orders" in sql and "SELECT" in sql:
                b = {"id": "b-1", "tenant_id": "t1", "status": "VERSANDT"}
                m.mappings.return_value.first.return_value = b
            elif "proc_wareneingaenge" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = None  # no existing WE
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        result = buche_wareneingang(db, "b-1", "t1", 100.0, "KG", "lager-1")
        assert result["menge_erhalten"] == 100.0
        assert result["qs_status"] == "AUSSTEHEND"
        assert result["idempotent"] is False
        db.commit.assert_called_once()

    def test_we_idempotent(self):
        from app.services.proc_wareneingang_service import buche_wareneingang
        db = MagicMock()

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "proc_purchase_orders" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = {"id": "b-1", "tenant_id": "t1", "status": "VERSANDT"}
            elif "proc_wareneingaenge" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = {
                    "id": "we-1", "bestellung_id": "b-1", "tenant_id": "t1",
                    "menge_erhalten": 100.0, "qs_status": "AUSSTEHEND",
                }
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        result = buche_wareneingang(db, "b-1", "t1", 100.0, "KG", "lager-1")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_we_falscher_status_raises(self):
        from app.services.proc_wareneingang_service import buche_wareneingang, WareneingangError
        db = _mock_db({"proc_purchase_orders": {"id": "b-1", "tenant_id": "t1", "status": "DRAFT"}})
        with pytest.raises(WareneingangError, match="VERSANDT"):
            buche_wareneingang(db, "b-1", "t1", 50.0, "KG", "lager-1")

    def test_qs_status_update(self):
        from app.services.proc_wareneingang_service import update_qs_status
        we = {"id": "we-1", "tenant_id": "t1", "qs_status": "AUSSTEHEND", "bestellung_id": "b-1"}
        db = _mock_db({"proc_wareneingaenge": we})
        result = update_qs_status(db, "we-1", "t1", "BESTANDEN")
        assert result["qs_status"] == "BESTANDEN"


# ---------------------------------------------------------------------------
# Rechnungsprüfung
# ---------------------------------------------------------------------------

class TestRechnungspruefung:
    def test_auto_freigabe_unter_schwelle(self):
        from app.services.proc_rechnungspruefung_service import pruefe_rechnung
        db = _mock_db({"proc_rechnungspruefungen": None})
        # soll = 10.0 * 100 = 1000, rechnung = 1020 → 2% < 3%
        result = pruefe_rechnung(db, "b-1", "t1", "RE-001", 1020.0, 10.0, 100.0, schwelle_pct=3.0)
        assert result["status"] == "FREIGEGEBEN"
        assert result["abweichung_pct"] == pytest.approx(2.0)

    def test_gesperrt_ueber_schwelle(self):
        from app.services.proc_rechnungspruefung_service import pruefe_rechnung
        db = _mock_db({"proc_rechnungspruefungen": None})
        # soll = 10.0 * 100 = 1000, rechnung = 1050 → 5% > 3%
        result = pruefe_rechnung(db, "b-1", "t1", "RE-001", 1050.0, 10.0, 100.0, schwelle_pct=3.0)
        assert result["status"] == "GESPERRT"
        assert result["abweichung_pct"] == pytest.approx(5.0)

    def test_idempotent(self):
        from app.services.proc_rechnungspruefung_service import pruefe_rechnung
        existing = {"id": "rp-1", "bestellung_id": "b-1", "rechnungs_nr": "RE-001",
                    "tenant_id": "t1", "status": "GESPERRT"}
        db = _mock_db({"proc_rechnungspruefungen": existing})
        result = pruefe_rechnung(db, "b-1", "t1", "RE-001", 1050.0, 10.0, 100.0)
        assert result["idempotent"] is True

    def test_manuelle_freigabe(self):
        from app.services.proc_rechnungspruefung_service import freigabe_rechnungspruefung
        row = {"id": "rp-1", "tenant_id": "t1", "bestellung_id": "b-1", "status": "GESPERRT"}
        db = _mock_db({"proc_rechnungspruefungen": row})
        result = freigabe_rechnungspruefung(db, "rp-1", "t1", "FREIGEGEBEN", "mgr-1", "Sonderfall")
        assert result["status"] == "FREIGEGEBEN"
        db.commit.assert_called_once()

    def test_freigabe_nicht_gesperrt_raises(self):
        from app.services.proc_rechnungspruefung_service import freigabe_rechnungspruefung, RechnungspruefungError
        row = {"id": "rp-1", "tenant_id": "t1", "status": "FREIGEGEBEN"}
        db = _mock_db({"proc_rechnungspruefungen": row})
        with pytest.raises(RechnungspruefungError, match="GESPERRT"):
            freigabe_rechnungspruefung(db, "rp-1", "t1", "FREIGEGEBEN", "mgr-1")
