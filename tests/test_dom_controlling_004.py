"""DOM-CONTROLLING-004 Unit Tests — Budget-Lifecycle (.2), Abweichung (.3), KST-Abschluss (.4)."""
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
# Budget Lifecycle
# ---------------------------------------------------------------------------

class TestBudgetLifecycle:
    def _budget(self, status="ENTWURF"):
        return {"id": "b-1", "tenant_id": "t1", "kostenstelle_id": "kst-01",
                "periode": "2026-06", "plan_eur": 50000.0, "status": status}

    def test_create_budget(self):
        from app.services.controlling_budget_lifecycle_service import create_budget
        db = _mock_db({})
        result = create_budget(db, "t1", "kst-01", "2026-06", 50000.0, "IT-Budget", "mgr-1")
        assert result["status"] == "ENTWURF"
        assert result["plan_eur"] == 50000.0
        db.commit.assert_called_once()

    def test_freigabe_aus_entwurf(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status
        db = _mock_db({"controlling_budgets": self._budget()})
        result = transition_budget_status(db, "b-1", "t1", "FREIGEGEBEN", operator="mgr-1")
        assert result["status"] == "FREIGEGEBEN"
        db.commit.assert_called_once()

    def test_aktiv_aus_freigegeben(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status
        db = _mock_db({"controlling_budgets": self._budget(status="FREIGEGEBEN")})
        result = transition_budget_status(db, "b-1", "t1", "AKTIV")
        assert result["status"] == "AKTIV"

    def test_abschluss_aus_aktiv(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status
        db = _mock_db({"controlling_budgets": self._budget(status="AKTIV")})
        result = transition_budget_status(db, "b-1", "t1", "ABGESCHLOSSEN")
        assert result["status"] == "ABGESCHLOSSEN"

    def test_storno_aus_entwurf(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status
        db = _mock_db({"controlling_budgets": self._budget()})
        result = transition_budget_status(db, "b-1", "t1", "STORNIERT", operator="mgr-1")
        assert result["status"] == "STORNIERT"

    def test_idempotent_gleicher_status(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status
        db = _mock_db({"controlling_budgets": self._budget(status="FREIGEGEBEN")})
        result = transition_budget_status(db, "b-1", "t1", "FREIGEGEBEN")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_ungültiger_übergang_raises(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status, BudgetLifecycleError
        db = _mock_db({"controlling_budgets": self._budget(status="ABGESCHLOSSEN")})
        with pytest.raises(BudgetLifecycleError, match="Ungültiger"):
            transition_budget_status(db, "b-1", "t1", "ENTWURF")

    def test_nicht_gefunden_raises(self):
        from app.services.controlling_budget_lifecycle_service import transition_budget_status, BudgetLifecycleError
        db = _mock_db({})
        with pytest.raises(BudgetLifecycleError, match="nicht gefunden"):
            transition_budget_status(db, "missing", "t1", "FREIGEGEBEN")


# ---------------------------------------------------------------------------
# Abweichungsanalyse
# ---------------------------------------------------------------------------

class TestAbweichung:
    def test_ampel_gruen(self):
        from app.services.controlling_abweichung_service import get_abweichung
        db = MagicMock()
        call_n = [0]

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            call_n[0] += 1
            if "controlling_budgets" in sql:
                m.mappings.return_value.first.return_value = {"plan_eur": 10000.0}
            elif "controlling_ist_werte" in sql:
                m.mappings.return_value.first.return_value = {"ist_eur": 10200.0}
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        result = get_abweichung(db, "t1", "kst-01", "2026-06")
        assert result["ampel"] == "GRUEN"
        assert result["abweichung_pct"] == pytest.approx(2.0)

    def test_ampel_gelb(self):
        from app.services.controlling_abweichung_service import get_abweichung
        db = MagicMock()

        def side(stmt, params=None):
            m = MagicMock()
            sql = str(stmt)
            if "controlling_budgets" in sql:
                m.mappings.return_value.first.return_value = {"plan_eur": 10000.0}
            elif "controlling_ist_werte" in sql:
                m.mappings.return_value.first.return_value = {"ist_eur": 11000.0}
            return m

        db.execute.side_effect = side
        result = get_abweichung(db, "t1", "kst-01", "2026-06")
        assert result["ampel"] == "GELB"

    def test_ampel_rot(self):
        from app.services.controlling_abweichung_service import get_abweichung
        db = MagicMock()

        def side(stmt, params=None):
            m = MagicMock()
            sql = str(stmt)
            if "controlling_budgets" in sql:
                m.mappings.return_value.first.return_value = {"plan_eur": 10000.0}
            elif "controlling_ist_werte" in sql:
                m.mappings.return_value.first.return_value = {"ist_eur": 12000.0}
            return m

        db.execute.side_effect = side
        result = get_abweichung(db, "t1", "kst-01", "2026-06")
        assert result["ampel"] == "ROT"

    def test_kein_plan(self):
        from app.services.controlling_abweichung_service import get_abweichung
        db = MagicMock()

        def side(stmt, params=None):
            m = MagicMock()
            sql = str(stmt)
            if "controlling_budgets" in sql:
                m.mappings.return_value.first.return_value = None
            elif "controlling_ist_werte" in sql:
                m.mappings.return_value.first.return_value = {"ist_eur": 500.0}
            return m

        db.execute.side_effect = side
        result = get_abweichung(db, "t1", "kst-01", "2026-06")
        assert result["ampel"] == "KEIN_PLAN"

    def test_ist_buchen_ok(self):
        from app.services.controlling_abweichung_service import buche_ist_wert
        db = _mock_db({"controlling_kst_abschluss": None})
        result = buche_ist_wert(db, "t1", "kst-01", "2026-06", 1000.0, "BU-001")
        assert result["ist_eur"] == 1000.0
        db.commit.assert_called_once()

    def test_ist_buchen_abgeschlossen_raises(self):
        from app.services.controlling_abweichung_service import buche_ist_wert
        db = _mock_db({"controlling_kst_abschluss": {"id": "ka-1", "status": "ABGESCHLOSSEN"}})
        with pytest.raises(ValueError, match="abgeschlossen"):
            buche_ist_wert(db, "t1", "kst-01", "2026-06", 500.0, "BU-002")


# ---------------------------------------------------------------------------
# KST-Abschluss
# ---------------------------------------------------------------------------

class TestKSTAbschluss:
    def _ka(self, status="OFFEN"):
        return {"id": "ka-1", "tenant_id": "t1", "kostenstelle_id": "kst-01",
                "periode": "2026-06", "status": status}

    def test_neuer_eintrag_offen(self):
        from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss
        db = _mock_db({"controlling_kst_abschluss": None})
        result = advance_kst_abschluss(db, "kst-01", "2026-06", "t1", "OFFEN")
        assert result["status"] == "OFFEN"
        db.commit.assert_called_once()

    def test_offen_zu_in_bearbeitung(self):
        from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss
        db = _mock_db({"controlling_kst_abschluss": self._ka()})
        result = advance_kst_abschluss(db, "kst-01", "2026-06", "t1", "IN_BEARBEITUNG")
        assert result["status"] == "IN_BEARBEITUNG"

    def test_in_bearbeitung_zu_abgeschlossen(self):
        from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss
        db = _mock_db({"controlling_kst_abschluss": self._ka(status="IN_BEARBEITUNG")})
        result = advance_kst_abschluss(db, "kst-01", "2026-06", "t1", "ABGESCHLOSSEN")
        assert result["status"] == "ABGESCHLOSSEN"

    def test_abgeschlossen_idempotent(self):
        from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss
        db = _mock_db({"controlling_kst_abschluss": self._ka(status="ABGESCHLOSSEN")})
        result = advance_kst_abschluss(db, "kst-01", "2026-06", "t1", "ABGESCHLOSSEN")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_ungültiger_übergang_raises(self):
        from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss, KSTAbschlussError
        db = _mock_db({"controlling_kst_abschluss": self._ka()})
        with pytest.raises(KSTAbschlussError, match="Ungültiger"):
            advance_kst_abschluss(db, "kst-01", "2026-06", "t1", "ABGESCHLOSSEN")
