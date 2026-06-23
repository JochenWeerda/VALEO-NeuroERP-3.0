"""DOM-COMPLIANCE-004 Unit Tests — PCN-Lifecycle (.2), VVVO-Sachkunde (.3), Sperre-Audit (.4)."""
from __future__ import annotations

import pytest
from datetime import date, timedelta
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
# PCN Lifecycle
# ---------------------------------------------------------------------------

class TestPCNLifecycle:
    def _meldung(self, status="DRAFT"):
        return {"id": "m-1", "tenant_id": "t1", "meldung_nummer": "PCN-20260623-ABCD1234",
                "artikel_id": "art-1", "meldungstyp": "ZULASSUNG", "status": status}

    def test_create_pcn_meldung(self):
        from app.services.compliance_pcn_lifecycle_service import create_pcn_meldung
        db = _mock_db({})
        result = create_pcn_meldung(db, "t1", "art-1", "ZULASSUNG")
        assert result["status"] == "DRAFT"
        assert result["meldung_nummer"].startswith("PCN-")
        db.commit.assert_called_once()

    def test_transition_draft_to_validated(self):
        from app.services.compliance_pcn_lifecycle_service import transition_pcn_status
        db = _mock_db({"compliance_pcn_meldungen": self._meldung()})
        result = transition_pcn_status(db, "m-1", "t1", "VALIDATED")
        assert result["status"] == "VALIDATED"
        assert result["previous_status"] == "DRAFT"
        db.commit.assert_called_once()

    def test_invalid_transition_raises(self):
        from app.services.compliance_pcn_lifecycle_service import transition_pcn_status, PCNError
        db = _mock_db({"compliance_pcn_meldungen": self._meldung(status="CLOSED")})
        with pytest.raises(PCNError, match="Ungültiger"):
            transition_pcn_status(db, "m-1", "t1", "DRAFT")

    def test_withdraw_from_draft(self):
        from app.services.compliance_pcn_lifecycle_service import withdraw_pcn_meldung
        db = _mock_db({"compliance_pcn_meldungen": self._meldung()})
        result = withdraw_pcn_meldung(db, "m-1", "t1", grund="Fehlerhafte Eingabe")
        assert result["status"] == "WITHDRAWN"
        assert result["idempotent"] is False

    def test_withdraw_idempotent(self):
        from app.services.compliance_pcn_lifecycle_service import withdraw_pcn_meldung
        db = _mock_db({"compliance_pcn_meldungen": self._meldung(status="WITHDRAWN")})
        result = withdraw_pcn_meldung(db, "m-1", "t1", grund="X")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_withdraw_from_closed_raises(self):
        from app.services.compliance_pcn_lifecycle_service import withdraw_pcn_meldung, PCNError
        db = _mock_db({"compliance_pcn_meldungen": self._meldung(status="CLOSED")})
        with pytest.raises(PCNError, match="DRAFT oder VALIDATED"):
            withdraw_pcn_meldung(db, "m-1", "t1", grund="X")


# ---------------------------------------------------------------------------
# VVVO + Sachkunde
# ---------------------------------------------------------------------------

class TestVVVOSachkunde:
    def test_list_faellige_vvvo(self):
        from app.services.compliance_vvvo_sachkunde_service import list_faellige_vvvo_pruefungen
        soon = (date.today() + timedelta(days=10)).isoformat()
        entries = [{"id": "v1", "tenant_id": "t1", "betrieb_name": "Hof Müller",
                    "vvvo_nummer": "VVVO-001", "naechste_pruefung_am": soon}]
        db = _mock_db({"compliance_vvvo_register": entries})
        result = list_faellige_vvvo_pruefungen(db, "t1", within_days=30)
        assert len(result) == 1
        assert result[0]["vvvo_nummer"] == "VVVO-001"

    def test_berechne_naechste_vvvo_pruefung(self):
        from app.services.compliance_vvvo_sachkunde_service import berechne_naechste_vvvo_pruefung
        vvvo = {"id": "v1", "tenant_id": "t1", "betrieb_name": "Hof A",
                "vvvo_nummer": "VVVO-001", "letzte_pruefung_am": None, "naechste_pruefung_am": None}
        db = _mock_db({"compliance_vvvo_register": vvvo})
        result = berechne_naechste_vvvo_pruefung(db, "v1", "t1", "2026-01-15")
        assert result["letzte_pruefung_am"] == "2026-01-15"
        assert result["naechste_pruefung_am"] == "2027-01-15"
        db.commit.assert_called_once()

    def test_sachkunde_status_gueltig(self):
        from app.services.compliance_vvvo_sachkunde_service import get_sachkunde_status
        ablauf = (date.today() + timedelta(days=20)).isoformat()
        sk = {"id": "sk-1", "tenant_id": "t1", "mitarbeiter_name": "Anna",
              "zertifikat_art": "PSM", "ablauf_datum": ablauf}
        db = _mock_db({"compliance_sachkunde_register": sk})
        result = get_sachkunde_status(db, "sk-1", "t1")
        assert result["gueltig"] is True
        assert result["alarm"] is True  # within 30 days

    def test_sachkunde_status_abgelaufen(self):
        from app.services.compliance_vvvo_sachkunde_service import get_sachkunde_status
        ablauf = (date.today() - timedelta(days=5)).isoformat()
        sk = {"id": "sk-1", "tenant_id": "t1", "mitarbeiter_name": "Anna",
              "zertifikat_art": "PSM", "ablauf_datum": ablauf}
        db = _mock_db({"compliance_sachkunde_register": sk})
        result = get_sachkunde_status(db, "sk-1", "t1")
        assert result["gueltig"] is False


# ---------------------------------------------------------------------------
# Sperre Audit-Trail
# ---------------------------------------------------------------------------

class TestSperreAudit:
    def _audit_row(self, aktion="SPERRE"):
        return {"id": "a-1", "artikel_id": "art-1", "tenant_id": "t1",
                "aktion": aktion, "operator": "system", "grund": "QS-Sperre", "nachweis_ref": None}

    def test_sperre_creates_audit_entry(self):
        from app.services.compliance_sperre_audit_service import sperre_artikel
        db = _mock_db({"compliance_artikel_sperre_audit": None})  # no existing sperre
        result = sperre_artikel(db, "art-1", "t1", grund="QS-Sperre")
        assert result["aktion"] == "SPERRE"
        assert result["idempotent"] is False
        db.commit.assert_called_once()

    def test_sperre_idempotent_wenn_bereits_gesperrt(self):
        from app.services.compliance_sperre_audit_service import sperre_artikel
        db = _mock_db({"compliance_artikel_sperre_audit": self._audit_row("SPERRE")})
        result = sperre_artikel(db, "art-1", "t1", grund="X")
        assert result["idempotent"] is True
        db.commit.assert_not_called()

    def test_freigabe_wenn_gesperrt(self):
        from app.services.compliance_sperre_audit_service import freigabe_artikel
        db = _mock_db({"compliance_artikel_sperre_audit": self._audit_row("SPERRE")})
        result = freigabe_artikel(db, "art-1", "t1")
        assert result["aktion"] == "FREIGABE"
        db.commit.assert_called_once()

    def test_freigabe_wenn_nicht_gesperrt_raises(self):
        from app.services.compliance_sperre_audit_service import freigabe_artikel, SperreAuditError
        db = _mock_db({"compliance_artikel_sperre_audit": None})
        with pytest.raises(SperreAuditError, match="nicht gesperrt"):
            freigabe_artikel(db, "art-1", "t1")

    def test_storno_wenn_gesperrt(self):
        from app.services.compliance_sperre_audit_service import storno_sperre
        db = _mock_db({"compliance_artikel_sperre_audit": self._audit_row("SPERRE")})
        result = storno_sperre(db, "art-1", "t1", grund="Fehler")
        assert result["aktion"] == "STORNO"

    def test_storno_wenn_freigegeben_raises(self):
        from app.services.compliance_sperre_audit_service import storno_sperre, SperreAuditError
        db = _mock_db({"compliance_artikel_sperre_audit": self._audit_row("FREIGABE")})
        with pytest.raises(SperreAuditError, match="letzte Aktion SPERRE"):
            storno_sperre(db, "art-1", "t1", grund="X")

    def test_get_audit_trail(self):
        from app.services.compliance_sperre_audit_service import get_sperre_audit_trail
        trail = [self._audit_row("SPERRE"), self._audit_row("FREIGABE")]
        db = _mock_db({"compliance_artikel_sperre_audit": trail})
        result = get_sperre_audit_trail(db, "art-1", "t1")
        assert len(result) == 2
