"""DOM-AGRAR-004 Unit Tests — PartieAggregate (.2), Trocknung (.3), Selbstabrechnung (.4)."""
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
# Partie Aggregate Service
# ---------------------------------------------------------------------------

class TestPartieAggregateService:
    def _acceptance(self, aid, gross_kg=1000.0, net_kg=950.0, moisture=14.5, impurity=2.0):
        return {
            "id": aid,
            "tenant_id": "t1",
            "gross_weight_kg": gross_kg,
            "net_weight_kg": net_kg,
            "moisture_content_pct": moisture,
            "impurity_pct": impurity,
            "article_id": "wheat-001",
        }

    def test_create_partie_aggregates_correctly(self):
        from app.services.agrar_partie_aggregate_service import create_partie
        acc1 = self._acceptance("acc-1", gross_kg=1000.0, moisture=15.0)
        acc2 = self._acceptance("acc-2", gross_kg=2000.0, moisture=13.0)
        db = _mock_db({
            "harvest_acceptances": None,  # overridden below
            "agrar_partie_links": None,
            "agrar_partien": {"cnt": 0},
        })
        # custom side_effect to return different acceptances
        call_count = [0]
        accs = [acc1, acc2]
        original_side = db.execute.side_effect

        def custom_side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "harvest_acceptances" in sql and "SELECT" in sql:
                aid = (params or {}).get("id", "")
                found = next((a for a in accs if a["id"] == aid), None)
                m.mappings.return_value.first.return_value = found
            elif "agrar_partie_links" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = None
            elif "LIKE" in sql:  # partie_number counter
                row = MagicMock()
                row.get = lambda k, d=None: 0 if k == "cnt" else d
                m.mappings.return_value.first.return_value = row
            else:
                m.mappings.return_value.first.return_value = None
                m.mappings.return_value.all.return_value = []
            return m

        db.execute.side_effect = custom_side
        result = create_partie(db, "t1", ["acc-1", "acc-2"])
        assert result["total_gross_kg"] == pytest.approx(3000.0)
        # weighted average: (1000*15 + 2000*13) / 3000 = 13.667
        assert result["avg_moisture_pct"] == pytest.approx(13.667, abs=0.01)
        assert result["status"] == "OFFEN"
        assert result["acceptance_count"] == 2
        db.commit.assert_called_once()

    def test_empty_acceptance_ids_raises(self):
        from app.services.agrar_partie_aggregate_service import create_partie, PartieError
        db = _mock_db({})
        with pytest.raises(PartieError, match="Mindestens"):
            create_partie(db, "t1", [])

    def test_missing_acceptance_raises(self):
        from app.services.agrar_partie_aggregate_service import create_partie, PartieError
        db = _mock_db({"harvest_acceptances": None})
        with pytest.raises(PartieError, match="nicht gefunden"):
            create_partie(db, "t1", ["acc-missing"])

    def test_duplicate_acceptance_raises(self):
        from app.services.agrar_partie_aggregate_service import create_partie, PartieError
        acc = {"id": "acc-1", "tenant_id": "t1", "gross_weight_kg": 1000.0,
               "net_weight_kg": 900.0, "moisture_content_pct": 14.0,
               "impurity_pct": 1.5, "article_id": "wheat-001"}
        link = {"partie_id": "existing-partie"}
        db = MagicMock()

        def side(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "harvest_acceptances" in sql:
                m.mappings.return_value.first.return_value = acc
            elif "agrar_partie_links" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = link
            elif "LIKE" in sql:
                row = MagicMock()
                row.get = lambda k, d=None: 0
                m.mappings.return_value.first.return_value = row
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side
        with pytest.raises(PartieError, match="bereits in Partie"):
            create_partie(db, "t1", ["acc-1"])


# ---------------------------------------------------------------------------
# Trocknung Service
# ---------------------------------------------------------------------------

class TestTrocknungAbrechnungService:
    def _partie(self, status="OFFEN", moisture=15.5, gross_kg=5000.0):
        return {"id": "p-1", "tenant_id": "t1", "status": status,
                "avg_moisture_pct": moisture, "total_gross_kg": gross_kg}

    def test_trocknung_berechnung_korrekt(self):
        from app.services.agrar_trocknung_abrechnung_service import berechne_trocknung
        db = _mock_db({"agrar_partien": self._partie(), "agrar_trocknung_abrechnungen": None})
        result = berechne_trocknung(db, "p-1", "t1", moisture_out_pct=13.0, cost_eur_per_pct_ton=2.0)
        # trocknung_pct = 15.5 - 13.0 = 2.5
        # trocknungsabzug_kg = 5000 * 2.5 / 100 = 125.0
        # trocknungskosten_eur = (5000/1000) * 2.5 * 2.0 = 25.0
        assert result["trocknungsabzug_kg"] == pytest.approx(125.0)
        assert result["trocknungskosten_eur"] == pytest.approx(25.0)
        assert result["idempotent"] is False
        db.commit.assert_called_once()

    def test_trocknung_moisture_out_too_high_raises(self):
        from app.services.agrar_trocknung_abrechnung_service import berechne_trocknung, TrocknungError
        db = _mock_db({"agrar_partien": self._partie(moisture=14.0), "agrar_trocknung_abrechnungen": None})
        with pytest.raises(TrocknungError, match="keine Trocknung"):
            berechne_trocknung(db, "p-1", "t1", moisture_out_pct=14.0)

    def test_trocknung_idempotent(self):
        from app.services.agrar_trocknung_abrechnung_service import berechne_trocknung
        existing = {"id": "tr-1", "partie_id": "p-1", "trocknungskosten_eur": 30.0}
        db = _mock_db({"agrar_partien": self._partie(), "agrar_trocknung_abrechnungen": existing})
        result = berechne_trocknung(db, "p-1", "t1", moisture_out_pct=13.0)
        assert result["idempotent"] is True
        assert result["id"] == "tr-1"
        db.commit.assert_not_called()

    def test_trocknung_wrong_status_raises(self):
        from app.services.agrar_trocknung_abrechnung_service import berechne_trocknung, TrocknungError
        db = _mock_db({"agrar_partien": self._partie(status="ABGERECHNET"), "agrar_trocknung_abrechnungen": None})
        with pytest.raises(TrocknungError, match="OFFEN"):
            berechne_trocknung(db, "p-1", "t1", moisture_out_pct=13.0)


# ---------------------------------------------------------------------------
# Selbstabrechnung Lifecycle
# ---------------------------------------------------------------------------

class TestSelbstabrechnungLifecycle:
    def _rechnung(self, status="DRAFT"):
        return {"id": "r-1", "tenant_id": "t1", "status": status,
                "invoice_number": "SA-2026-001", "total_net_amount_eur": 1500.0}

    def test_issue_from_draft_ok(self):
        from app.services.agrar_selbstabrechnung_lifecycle_service import transition_status
        db = _mock_db({"agrar_selbstabrechnungen": self._rechnung()})
        result = transition_status(db, "r-1", "t1", "ISSUED")
        assert result["status"] == "ISSUED"
        assert result["previous_status"] == "DRAFT"
        db.commit.assert_called_once()

    def test_invalid_transition_raises(self):
        from app.services.agrar_selbstabrechnung_lifecycle_service import transition_status, SelbstabrechnungError
        db = _mock_db({"agrar_selbstabrechnungen": self._rechnung(status="PAID")})
        with pytest.raises(SelbstabrechnungError, match="Ungültiger"):
            transition_status(db, "r-1", "t1", "DRAFT")

    def test_storno_from_issued_ok(self):
        from app.services.agrar_selbstabrechnung_lifecycle_service import storno_selbstabrechnung
        db = _mock_db({"agrar_selbstabrechnungen": self._rechnung(status="ISSUED")})
        result = storno_selbstabrechnung(db, "r-1", "t1", grund="Fehler")
        assert result["status"] == "CANCELLED"
        assert result["idempotent"] is False

    def test_storno_idempotent(self):
        from app.services.agrar_selbstabrechnung_lifecycle_service import storno_selbstabrechnung
        db = _mock_db({"agrar_selbstabrechnungen": self._rechnung(status="CANCELLED")})
        result = storno_selbstabrechnung(db, "r-1", "t1")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_storno_from_paid_raises(self):
        from app.services.agrar_selbstabrechnung_lifecycle_service import storno_selbstabrechnung, SelbstabrechnungError
        db = _mock_db({"agrar_selbstabrechnungen": self._rechnung(status="PAID")})
        with pytest.raises(SelbstabrechnungError, match="DRAFT oder ISSUED"):
            storno_selbstabrechnung(db, "r-1", "t1")
