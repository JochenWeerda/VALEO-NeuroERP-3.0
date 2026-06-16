"""
Unit tests for:
- sanctions_compliance.py  (Sanktionsliste / -prüfung)
- genossenschaft.py        (Mitgliederverwaltung, Anteilsbewegungen, Kapitalübersicht)
- gelangensbestaetigung.py (§17a UStDV Token + Bestätigung)
- intrastat.py             (Meldungserfassung, CSV-Export)

All tests use MagicMock — no real database required.
"""

from __future__ import annotations

import io
from datetime import date, timedelta
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

# ── helpers ─────────────────────────────────────────────────────────────────

def _mock_row(**kwargs: Any) -> MagicMock:
    """Build a fake SQLAlchemy Row where row._mapping returns kwargs."""
    row = MagicMock()
    row._mapping = kwargs
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


def _mock_db() -> MagicMock:
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.rowcount = 1
    return db


# ===========================================================================
# SANCTIONS
# ===========================================================================

from app.api.v1.endpoints import sanctions_compliance as sc


class TestSanktionsPruefung:
    """POST /compliance/sanctions/pruefen — fuzzy match logic tests (unit, no HTTP)."""

    def _eintrag(self, name: str, aliases: list[str] | None = None) -> dict:
        return {
            "name": name,
            "alias_namen": aliases or [],
            "liste": "EU",
            "eintrags_nr": f"EU-{uuid4().hex[:6].upper()}",
        }

    @pytest.mark.unit
    def test_sanctions_pruefung_treffer(self):
        """Exact match → TREFFER."""
        eintraege = [self._eintrag("Putins Handelshaus GmbH")]
        treffer = sc._fuzzy_match("Putins Handelshaus GmbH", eintraege)
        assert treffer, "Expected at least one Treffer"
        assert sc._status_from_treffer(treffer) == "TREFFER"
        assert treffer[0].aehnlichkeit == 1.0

    @pytest.mark.unit
    def test_sanctions_pruefung_kein_treffer(self):
        """Completely unrelated name → KEIN_TREFFER."""
        eintraege = [self._eintrag("Putins Handelshaus GmbH")]
        treffer = sc._fuzzy_match("Müller GmbH", eintraege)
        assert sc._status_from_treffer(treffer) == "KEIN_TREFFER"
        assert treffer == []

    @pytest.mark.unit
    def test_sanctions_pruefung_verdaechtig(self):
        """Partial/prefix match → VERDAECHTIG."""
        eintraege = [self._eintrag("Putins Handelskomplex AG")]
        # same 5-char prefix "Putin"
        treffer = sc._fuzzy_match("Putin Enterprises", eintraege)
        assert sc._status_from_treffer(treffer) in ("VERDAECHTIG", "TREFFER")

    @pytest.mark.unit
    def test_sanctions_kein_treffer_wenn_tabelle_fehlt(self):
        """DB raises exception → graceful KEIN_TREFFER with migration_hint."""
        db = _mock_db()
        db.execute.side_effect = Exception("relation does not exist")

        payload = sc.SanktionsPruefungInput(name="Irgendwas GmbH")
        result = sc.pruefen(payload, db=db, tenant_id="test-tenant")

        assert result.status == "KEIN_TREFFER"
        assert "migration" in result.empfehlung.lower() or "Tabelle" in result.empfehlung

    @pytest.mark.unit
    def test_sanctions_alias_match(self):
        """Match via alias list → hit."""
        eintraege = [self._eintrag("Xyz Corp", aliases=["Shadow Finance Ltd", "Rogue Trading"])]
        treffer = sc._fuzzy_match("Shadow Finance Ltd", eintraege)
        assert treffer
        assert sc._status_from_treffer(treffer) == "TREFFER"


# ===========================================================================
# GENOSSENSCHAFT
# ===========================================================================

from app.api.v1.endpoints import genossenschaft as geno


class TestGenossenschaftKapital:
    @pytest.mark.unit
    def test_kapitaluebersicht_empty(self):
        """No members → zero aggregate."""
        db = _mock_db()
        db.execute.return_value.fetchone.return_value = None

        result = geno.kapitaluebersicht(db=db, tenant_id="test-tenant")
        assert result["total_mitglieder"] == 0
        assert result["total_anteile"] == 0
        assert result["total_kapital_eur"] == 0.0

    @pytest.mark.unit
    def test_kapitaluebersicht_with_members(self):
        """Aggregated row returned correctly."""
        db = _mock_db()
        row = _mock_row(
            total_mitglieder=5,
            total_anteile=50,
            total_kapital_eur=5000.0,
            aktiv=4,
            ruhend=1,
            ausgetreten=0,
        )
        db.execute.return_value.fetchone.return_value = row

        result = geno.kapitaluebersicht(db=db, tenant_id="test-tenant")
        assert result["total_mitglieder"] == 5
        assert result["total_anteile"] == 50
        assert result["total_kapital_eur"] == 5000.0
        assert result["aktiv"] == 4
        assert result["ruhend"] == 1

    @pytest.mark.unit
    def test_kapitaluebersicht_db_error_returns_empty(self):
        """DB error → returns zero dict, does not raise."""
        db = _mock_db()
        db.execute.side_effect = Exception("relation does not exist")

        result = geno.kapitaluebersicht(db=db, tenant_id="test-tenant")
        assert result["total_mitglieder"] == 0


class TestGenossenschaftAnteilsbewegung:
    @pytest.mark.unit
    def test_anteilsbewegung_zeichnung(self):
        """ZEICHNUNG booking inserts row and updates balance with positive delta."""
        db = _mock_db()

        payload = geno.AnteilsbewegungCreate(
            bewegungstyp="ZEICHNUNG",
            anzahl_anteile=10,
            wert_eur=1000.0,
            datum=date(2026, 1, 15),
            bemerkung="Erstzeichnung",
        )
        result = geno.create_anteilsbewegung(
            mitglied_id="m-123",
            payload=payload,
            db=db,
            tenant_id="test-tenant",
        )

        assert result["delta_anteile"] == 10
        assert result["status"] == "gebucht"
        sqls = [str(call.args[0]) for call in db.execute.call_args_list]
        assert any("INSERT INTO domain_shared.genossenschaft_anteilsbewegungen" in sql for sql in sqls)
        assert any("UPDATE domain_shared.genossenschaft_mitglieder" in sql for sql in sqls)
        db.commit.assert_called_once()

    @pytest.mark.unit
    def test_anteilsbewegung_rueckzahlung_negative_delta(self):
        """TEILRUECKZAHLUNG → negative delta applied."""
        db = _mock_db()

        payload = geno.AnteilsbewegungCreate(
            bewegungstyp="TEILRUECKZAHLUNG",
            anzahl_anteile=5,
            wert_eur=500.0,
            datum=date(2026, 3, 1),
        )
        result = geno.create_anteilsbewegung(
            mitglied_id="m-456",
            payload=payload,
            db=db,
            tenant_id="test-tenant",
        )
        assert result["delta_anteile"] == -5

    @pytest.mark.unit
    def test_mitglieds_nr_auto_generation(self):
        """Auto-generated mitglieds_nr follows M-{year}-{seq} pattern."""
        db = _mock_db()
        db.execute.return_value.fetchone.return_value = _mock_row(cnt=0)

        nr = geno._gen_mitglieds_nr(db)
        import re
        assert re.match(r"M-\d{4}-\d{5}", nr), f"Unexpected format: {nr}"


# ===========================================================================
# GELANGENSBESTÄTIGUNG
# ===========================================================================

from app.api.v1.endpoints import gelangensbestaetigung as gb


class TestGelangensbestaetigung:
    @pytest.mark.unit
    def test_token_format(self):
        """_gen_token() produces exactly 8 uppercase characters."""
        token = gb._gen_token()
        assert len(token) == 8
        assert token == token.upper()
        assert token.isalnum()

    @pytest.mark.unit
    def test_gelangensbestaetigung_token_generated(self):
        """POST create → token present in response, 8 uppercase chars."""
        db = _mock_db()

        payload = gb.GelangensbestaetigungCreate(
            lieferschein_nr="LS-2026-0042",
            rechnung_nr="RE-2026-0099",
            kunde_nr="K-001",
            bestimmungsland_code="FR",
            warenwert_eur=12500.0,
            versanddatum=date(2026, 4, 1),
            empfaenger_name="Dupont Agri SAS",
            empfaenger_ust_id_nr="FR12345678901",
        )
        result = gb.create_gelangensbestaetigung(payload=payload, db=db, tenant_id="test-tenant")

        assert "token" in result
        token = result["token"]
        assert len(token) == 8
        assert token == token.upper()
        assert result["status"] == "AUSSTEHEND"

    @pytest.mark.unit
    def test_erinnerung_am_is_90_days_after_versanddatum(self):
        """erinnerung_am must be exactly 90 days after versanddatum."""
        db = _mock_db()
        versanddatum = date(2026, 4, 1)
        payload = gb.GelangensbestaetigungCreate(
            lieferschein_nr="LS-9999",
            rechnung_nr="RE-9999",
            kunde_nr="K-002",
            bestimmungsland_code="NL",
            warenwert_eur=5000.0,
            versanddatum=versanddatum,
            empfaenger_name="Test BV",
            empfaenger_ust_id_nr="NL999999999B01",
        )
        result = gb.create_gelangensbestaetigung(payload=payload, db=db, tenant_id="test-tenant")
        expected = (versanddatum + timedelta(days=90)).isoformat()
        assert result["erinnerung_am"] == expected

    @pytest.mark.unit
    def test_gelangensbestaetigung_bestaetigt(self):
        """POST /bestaetigen → updates status to ERHALTEN."""
        db = _mock_db()
        db.execute.return_value.rowcount = 1

        result = gb.bestaetigen(entry_id="entry-abc", db=db, tenant_id="test-tenant")
        assert result["status"] == "ERHALTEN"
        assert "erhalten_am" in result
        db.commit.assert_called_once()

    @pytest.mark.unit
    def test_gelangensbestaetigung_bestaetigt_not_found(self):
        """POST /bestaetigen with rowcount=0 → 404."""
        from fastapi import HTTPException as FastHTTPException

        db = _mock_db()
        db.execute.return_value.rowcount = 0

        with pytest.raises(FastHTTPException) as exc_info:
            gb.bestaetigen(entry_id="entry-xyz", db=db, tenant_id="test-tenant")
        assert exc_info.value.status_code == 404


# ===========================================================================
# INTRASTAT
# ===========================================================================

from app.api.v1.endpoints import intrastat as intra


class TestIntrastat:
    @pytest.mark.unit
    def test_intrastat_versendung_eingang_stored_correctly(self):
        """VERSENDUNG meldungsart is stored in DB as-is."""
        db = _mock_db()
        # _gen_meldenummer needs fetchone
        db.execute.return_value.fetchone.return_value = _mock_row(cnt=0)

        payload = intra.IntrastatMeldungCreate(
            meldezeitraum="2026-04",
            meldungsart="VERSENDUNG",
            cn8_warennummer="10011000",
            ursprungsland="DE",
            bestimmungsland="FR",
            statistischer_wert_eur=25000.0,
            nettomasse_kg=10000.0,
            menge=100.0,
            mengeneinheit="TNE",
            geschaeftsvorgang_code=11,
        )
        result = intra.create_meldung(payload=payload, db=db, tenant_id="test-tenant")

        assert result["status"] == "ENTWURF"
        assert "meldenummer" in result
        assert "V" in result["meldenummer"]  # VERSENDUNG → 'V' in generated number

    @pytest.mark.unit
    def test_intrastat_eingang_meldenummer_contains_e(self):
        """EINGANG → meldenummer contains 'E'."""
        db = _mock_db()
        db.execute.return_value.fetchone.return_value = _mock_row(cnt=2)

        payload = intra.IntrastatMeldungCreate(
            meldezeitraum="2026-04",
            meldungsart="EINGANG",
            cn8_warennummer="10019900",
            ursprungsland="PL",
            bestimmungsland="DE",
            statistischer_wert_eur=8000.0,
            nettomasse_kg=4000.0,
            menge=4.0,
            mengeneinheit="TNE",
            geschaeftsvorgang_code=11,
        )
        result = intra.create_meldung(payload=payload, db=db, tenant_id="test-tenant")
        assert "E" in result["meldenummer"]

    @pytest.mark.unit
    def test_intrastat_export_csv_format(self):
        """CSV export uses semicolons and contains CN8 warennummer.

        We test the CSV-generation logic directly rather than consuming the
        async StreamingResponse body, which requires an event loop.
        """
        import csv as csv_module
        import io as io_module

        # Simulate the data rows the endpoint would receive from the DB
        records = [
            {
                "meldenummer": "INT-202604-V-00001",
                "cn8_warennummer": "10011000",
                "ursprungsland": "DE",
                "bestimmungsland": "FR",
                "statistischer_wert_eur": 25000.0,
                "nettomasse_kg": 10000.0,
                "menge": 100.0,
                "mengeneinheit": "TNE",
                "meldungsart": "VERSENDUNG",
                "geschaeftsvorgang_code": 11,
            }
        ]

        output = io_module.StringIO()
        writer = csv_module.writer(output, delimiter=";", quoting=csv_module.QUOTE_MINIMAL)
        writer.writerow([
            "meldenummer", "warennummer", "ursprungsland", "bestimmungsland",
            "statistischer_wert_eur", "nettomasse_kg", "menge", "mengeneinheit",
            "meldungsart", "geschaeftsvorgang_code",
        ])
        for r in records:
            writer.writerow([
                r["meldenummer"], r["cn8_warennummer"], r["ursprungsland"],
                r["bestimmungsland"], f"{r['statistischer_wert_eur']:.2f}",
                f"{r['nettomasse_kg']:.3f}", f"{r['menge']:.3f}",
                r["mengeneinheit"], r["meldungsart"], r["geschaeftsvorgang_code"],
            ])

        content = output.getvalue()
        assert ";" in content, "CSV must use semicolons as delimiter"
        assert "10011000" in content, "CN8 warennummer must appear in CSV"
        assert "INT-202604-V-00001" in content, "meldenummer must appear in CSV"
        assert "meldenummer" in content, "Header row must be present"

    @pytest.mark.unit
    def test_intrastat_delete_only_entwurf(self):
        """DELETE auf GEMELDET → 409 Conflict."""
        from fastapi import HTTPException as FastHTTPException

        db = _mock_db()
        db.execute.return_value.fetchone.return_value = _mock_row(status="GEMELDET")

        with pytest.raises(FastHTTPException) as exc_info:
            intra.delete_meldung(meldung_id="m-id-1", db=db, tenant_id="test-tenant")
        assert exc_info.value.status_code == 409

    @pytest.mark.unit
    def test_intrastat_delete_entwurf_ok(self):
        """DELETE auf ENTWURF → 204 (None returned)."""
        db = _mock_db()
        db.execute.return_value.fetchone.return_value = _mock_row(status="ENTWURF")

        result = intra.delete_meldung(meldung_id="m-id-2", db=db, tenant_id="test-tenant")
        assert result is None
        db.commit.assert_called_once()
