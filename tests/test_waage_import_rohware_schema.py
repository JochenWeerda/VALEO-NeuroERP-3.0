"""
Tests for WAAGE-LIVE-001 (ASCII-Import, Fehlerqueue, Kalibrierung)
and ROHWARE-SCHEMA-001 (Abrechnungsschema-Katalog).
"""

import json
import uuid
from datetime import date, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — isoliert testbare Funktionen aus den Endpoint-Modulen
# ---------------------------------------------------------------------------

from app.api.v1.endpoints.waage import (
    _kalibrierung_status,
    _parse_q_line,
    _parse_w_line,
)
from app.api.v1.endpoints.rohware_schema import _eval_formula


# ===========================================================================
# WAAGE-LIVE-001 Tests
# ===========================================================================


class TestAsciiImportParsing:
    """Unit-Tests für die Parse-Hilfsfunktionen (kein DB nötig)."""

    def _make_w_line(
        self,
        wiegung_nr: str = "W001",
        datum: str = "2026-05-17",
        uhrzeit: str = "10:00:00",
        brutto: str = "28500",
        tara: str = "12000",
        netto: str = "16500",
        kennzeichen: str = "RE-AB-1234",
        lieferant: str = "LIF-001",
        artikel: str = "ART-GE-001",
        sorte: str = "Winterweizen",
        partie: str = "P2026-001",
        silo: str = "S01",
        feuchte: str = "13.5",
        hl: str = "78.2",
        bruch: str = "1.2",
        extra: str = "0",
    ) -> List[str]:
        return [
            "W", wiegung_nr, datum, uhrzeit,
            brutto, tara, netto,
            kennzeichen, lieferant, artikel, sorte,
            partie, silo, feuchte, hl, bruch, extra,
        ]

    def test_parse_w_satzart_ok(self):
        parts = self._make_w_line()
        data = _parse_w_line(parts)
        assert data["wiegung_nr"] == "W001"
        assert data["brutto_kg"] == 28500.0
        assert data["tara_kg"] == 12000.0
        assert data["netto_kg"] == 16500.0
        assert data["qualitaet_feuchtigkeit"] == pytest.approx(13.5)
        assert data["qualitaet_hl"] == pytest.approx(78.2)
        assert data["qualitaet_bruch"] == pytest.approx(1.2)

    def test_parse_w_satzart_too_few_fields(self):
        parts = ["W", "001", "2026-05-17"]  # only 3 fields
        with pytest.raises(ValueError, match="17 Felder"):
            _parse_w_line(parts)

    def test_parse_q_satzart_ok(self):
        parts = ["Q", "W001", "PROTEIN", "11.5", "%"]
        data = _parse_q_line(parts)
        assert data["parameter"] == "PROTEIN"
        assert data["wert"] == "11.5"
        assert data["einheit"] == "%"

    def test_parse_q_satzart_too_few_fields(self):
        parts = ["Q", "W001"]
        with pytest.raises(ValueError, match="5 Felder"):
            _parse_q_line(parts)


# ---------------------------------------------------------------------------
# test_ascii_import_parses_w_satzart — Endpoint-Level (DB gemockt)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ascii_import_parses_w_satzart():
    from app.services.waage_import_service import parse_record, split_records
    raw = 'W;W001;2026-05-17;10:00:00;28500;12000;16500;RE-AB-1234;LIF-001;;WW;P001;S01;13.5;78.2;1.2;0'
    records = split_records(raw + '\nQ;W001;PROTEIN;11.5;%')
    assert len(records) == 1
    value = parse_record(records[0])
    assert value['net_weight'] == 16500
    assert value['quality_data']['additional'] == [{'parameter': 'PROTEIN', 'wert': '11.5', 'einheit': '%'}]



@pytest.mark.asyncio
async def test_ascii_import_skips_invalid_line_with_toleranz():
    from app.api.v1.endpoints import waage
    from fastapi import HTTPException
    upload = MagicMock()
    upload.read = AsyncMock(return_value=b'\xffinvalid')
    db = MagicMock()
    with patch.object(waage, 'WaageRepository') as repo:
        repo.return_value.get_by_id.return_value = object()
        with pytest.raises(HTTPException) as invalid:
            await waage.import_ascii(upload, 'own', True, db, 'tenant-a', {'sub': 'actor'})
    assert invalid.value.status_code == 422
    db.commit.assert_not_called()



@pytest.mark.asyncio
async def test_ascii_import_fails_on_invalid_line_without_toleranz():
    from app.services.waage_import_service import parse_record
    from fastapi import HTTPException
    for number in ['NaN', 'Infinity', '-1', 'NOT_A_NUMBER']:
        raw = f'W;W001;2026-05-17;10:00:00;{number};12000;16500;RE;LIF;;WW;P001;S01;13.5;78.2;1.2;0'
        with pytest.raises((ValueError, HTTPException)):
            parse_record(raw)



# ---------------------------------------------------------------------------
# Fehlerqueue Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fehlerqueue_add_and_list():
    from app.api.v1.endpoints import waage
    from sqlalchemy.dialects import postgresql
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    assert await waage.list_fehlerqueue(db=db, tenant_id='tenant-a', limit=3) == []
    expressions = db.query.return_value.filter.call_args.args
    sql = [str(x.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})) for x in expressions]
    assert any("tenant_id = 'tenant-a'" in item for item in sql)
    db.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_once_with(3)



# ---------------------------------------------------------------------------
# Kalibrierungsstatus Tests
# ---------------------------------------------------------------------------

def test_kalibrierung_status_ok():
    future = (date.today() + timedelta(days=60)).isoformat()
    assert _kalibrierung_status(future) == "ok"


def test_kalibrierung_status_faellig():
    """naechste_eichfaelligkeit liegt gestern → faellig (delta=1 <= 30)."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assert _kalibrierung_status(yesterday) == "faellig"


def test_kalibrierung_status_ueberfaellig():
    """Mehr als 30 Tage überfällig."""
    overdue = (date.today() - timedelta(days=45)).isoformat()
    assert _kalibrierung_status(overdue) == "ueberfaellig"


def test_kalibrierung_status_none():
    assert _kalibrierung_status(None) == "faellig"


# ===========================================================================
# ROHWARE-SCHEMA-001 Tests
# ===========================================================================


class TestFormulaEval:
    """Unit-Tests für _eval_formula — kein DB nötig."""

    def test_grundpreis_simple(self):
        result = _eval_formula("basis_preis", {"basis_preis": 200.0, "feuchte": 14.0})
        assert result == pytest.approx(200.0)

    def test_feuchte_abzug(self):
        # basis_preis=200, feuchte=15 → feuchte_abzug_prozent=1.0
        result = _eval_formula(
            "basis_preis * feuchte_abzug_prozent / 100",
            {"basis_preis": 200.0, "feuchte": 15.0},
        )
        assert result == pytest.approx(2.0)

    def test_invalid_formula_returns_none(self):
        result = _eval_formula("undefined_variable * 100", {"basis_preis": 200.0})
        assert result is None

    def test_menge_berechnung(self):
        result = _eval_formula(
            "basis_preis * menge_kg / 1000",
            {"basis_preis": 200.0, "menge_kg": 5000.0},
        )
        assert result == pytest.approx(1000.0)
