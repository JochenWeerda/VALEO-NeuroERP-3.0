"""DOM-FINANCE-004 Unit Tests — SEPA (.2), Ratenzahlung (.3), Mahnstufe (.4)."""
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
# SEPA Service
# ---------------------------------------------------------------------------

class TestSEPAService:
    def test_create_mandat(self):
        from app.services.finance_sepa_service import create_sepa_mandat
        db = _mock_db({})
        result = create_sepa_mandat(db, "t1", "DE98ZZZ09999999999", "DE12345678901234567890", "TESTBIC")
        assert result["status"] == "AKTIV"
        assert result["mandat_ref"].startswith("MAND-")
        db.commit.assert_called_once()

    def test_create_mandat_invalid_typ_raises(self):
        from app.services.finance_sepa_service import create_sepa_mandat, SEPAError
        db = _mock_db({})
        with pytest.raises(SEPAError, match="Ungültiger SEPA-Typ"):
            create_sepa_mandat(db, "t1", "GL-ID", "IBAN", "BIC", typ="INVALID")

    def test_widerruf_mandat(self):
        from app.services.finance_sepa_service import widerruf_sepa_mandat
        mandat = {"id": "m-1", "tenant_id": "t1", "status": "AKTIV", "mandat_ref": "MAND-001"}
        db = _mock_db({"finance_sepa_mandate": mandat})
        result = widerruf_sepa_mandat(db, "m-1", "t1")
        assert result["status"] == "WIDERRUFEN"
        assert result["idempotent"] is False
        db.commit.assert_called_once()

    def test_widerruf_idempotent(self):
        from app.services.finance_sepa_service import widerruf_sepa_mandat
        mandat = {"id": "m-1", "tenant_id": "t1", "status": "WIDERRUFEN", "mandat_ref": "MAND-001"}
        db = _mock_db({"finance_sepa_mandate": mandat})
        result = widerruf_sepa_mandat(db, "m-1", "t1")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_create_batch(self):
        from app.services.finance_sepa_service import create_sepa_batch
        db = _mock_db({})
        eintraege = [
            {"mandat_ref": "MAND-001", "iban": "DE12...", "betrag_eur": 150.0},
            {"mandat_ref": "MAND-002", "iban": "DE99...", "betrag_eur": 75.50},
        ]
        result = create_sepa_batch(db, "t1", "2026-07-01", eintraege)
        assert result["gesamt_eur"] == pytest.approx(225.50)
        assert result["anzahl_eintraege"] == 2
        assert "<Document>" in result["xml_payload"]


# ---------------------------------------------------------------------------
# Ratenzahlung Service
# ---------------------------------------------------------------------------

class TestRatenzahlungService:
    def test_create_plan(self):
        from app.services.finance_ratenzahlung_service import create_ratenzahlungsplan
        db = _mock_db({"finance_ratenzahlungsplaene": None})  # no existing plan
        result = create_ratenzahlungsplan(db, "t1", "op-1", 300.0, 3, "2026-07-01")
        assert result["gesamt_eur"] == 300.0
        assert result["anzahl_raten"] == 3
        assert result["idempotent"] is False
        assert len(result["rate_ids"]) == 3
        db.commit.assert_called_once()

    def test_create_plan_idempotent(self):
        from app.services.finance_ratenzahlung_service import create_ratenzahlungsplan
        existing = {"id": "p-1", "op_id": "op-1", "tenant_id": "t1", "gesamt_eur": 300.0,
                    "anzahl_raten": 3, "restbetrag_eur": 300.0, "status": "AKTIV"}
        db = _mock_db({"finance_ratenzahlungsplaene": existing})
        result = create_ratenzahlungsplan(db, "t1", "op-1", 300.0, 3, "2026-07-01")
        assert result["idempotent"] is True

    def test_create_plan_too_few_raten_raises(self):
        from app.services.finance_ratenzahlung_service import create_ratenzahlungsplan, RatenzahlungError
        db = _mock_db({})
        with pytest.raises(RatenzahlungError, match="Mindestens 2"):
            create_ratenzahlungsplan(db, "t1", "op-1", 100.0, 1, "2026-07-01")

    def test_buche_rate_reduziert_restbetrag(self):
        from app.services.finance_ratenzahlung_service import buche_rate
        rate = {"id": "r-1", "plan_id": "p-1", "tenant_id": "t1",
                "rate_nr": 1, "betrag_eur": 100.0, "status": "OFFEN", "faellig_am": "2026-07-01"}
        plan = {"id": "p-1", "tenant_id": "t1", "restbetrag_eur": 300.0, "status": "AKTIV"}
        db = MagicMock()
        call_n = [0]

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            call_n[0] += 1
            if "finance_ratenzahlungsraten" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = rate
            elif "finance_ratenzahlungsplaene" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = plan
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        result = buche_rate(db, "r-1", "t1")
        assert result["plan_restbetrag_eur"] == pytest.approx(200.0)
        assert result["plan_status"] == "AKTIV"

    def test_buche_letzte_rate_schliesst_plan(self):
        from app.services.finance_ratenzahlung_service import buche_rate
        rate = {"id": "r-3", "plan_id": "p-1", "tenant_id": "t1",
                "rate_nr": 3, "betrag_eur": 100.0, "status": "OFFEN", "faellig_am": "2026-09-01"}
        plan = {"id": "p-1", "tenant_id": "t1", "restbetrag_eur": 100.0, "status": "AKTIV"}
        db = MagicMock()

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "finance_ratenzahlungsraten" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = rate
            elif "finance_ratenzahlungsplaene" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = plan
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        result = buche_rate(db, "r-3", "t1")
        assert result["plan_restbetrag_eur"] == pytest.approx(0.0)
        assert result["plan_status"] == "ABGESCHLOSSEN"


# ---------------------------------------------------------------------------
# Mahnstufe Service
# ---------------------------------------------------------------------------

class TestMahnstufeService:
    """Seit 23.11.2026 eskaliert die Mahnstufe ueber den einen Mahnweg (FinanceDunningService.run_dunning)."""

    def test_eskalation_erzeugt_eine_mahnung_ueber_den_mahnweg(self, monkeypatch):
        from app.services import finance_dunning_service as fds
        from app.services.finance_mahnstufe_service import eskaliere_mahnstufe

        aufrufe = []

        def lauf(self, rechnungsnr=None, bediener="KIM", **_):
            aufrufe.append((rechnungsnr, bediener))
            return {"ok": True, "erzeugt": 1, "mahnungen": [
                {"id": "n-1", "stufe": 2, "vorherige_stufe": 1, "gebuehr": 10.0, "rechnungsnr": rechnungsnr}]}

        monkeypatch.setattr(fds.FinanceDunningService, "run_dunning", lauf)
        result = eskaliere_mahnstufe(object(), "RE-001", "t1", "anna")
        assert aufrufe == [("RE-001", "anna")]
        assert (result["id"], result["stufe"], result["vorherige_stufe"]) == ("n-1", "2", "1")
        assert result["bearbeitungsgebuehr_eur"] == 10.0

    def test_nicht_mahnfaellig_wird_abgelehnt(self, monkeypatch):
        from app.services import finance_dunning_service as fds
        from app.services.finance_mahnstufe_service import MahnstufeError, eskaliere_mahnstufe

        monkeypatch.setattr(fds.FinanceDunningService, "run_dunning",
                            lambda self, **_: {"ok": True, "erzeugt": 0, "mahnungen": []})
        with pytest.raises(MahnstufeError, match="nicht mahnfällig"):
            eskaliere_mahnstufe(object(), "RE-001", "t1")


