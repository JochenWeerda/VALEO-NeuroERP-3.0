"""Executable Unit-Tests: M2 Sonar New-Code Coverage (Rohware/Mask/Artikel)."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import artikel_bestandteile, mask_registry, rohwarengruppen
from app.services.studio_draft_store import StudioStorageUnavailable


def test_rohwarengruppen_staffel_berechnung_einfach_und_gestaffelt():
    zeilen = [
        {"bis_wert": "1", "umrechnungsfaktor": "0.1"},
        {"bis_wert": "3", "umrechnungsfaktor": "0.2"},
    ]
    einfach = rohwarengruppen._berechne_staffel(zeilen, Decimal("0.5"), "einfacher_umrechnungsfaktor")
    assert einfach == Decimal("0.0500")
    overflow = rohwarengruppen._berechne_staffel(zeilen, Decimal("9"), "einfacher_umrechnungsfaktor")
    assert overflow == Decimal("1.8000")
    assert rohwarengruppen._berechne_staffel([], Decimal("1"), "einfacher_umrechnungsfaktor") == Decimal("0")

    gestaffelt = rohwarengruppen._berechne_staffel(zeilen, Decimal("2.5"), "gestaffelte_abrechnung")
    assert gestaffelt == Decimal("0.4000")


def _screen_dict(screen_id: str = "demo/screen") -> dict:
    return {
        "id": screen_id,
        "title": "Demo",
        "domain": "admin",
        "layout": {"floorplan": "ops"},
        "agentContract": {"synonyms": ["demo"], "examplePrompts": ["öffne demo"]},
        "filters": [{"key": "q", "label": "Suche"}],
        "actions": [],
    }


def test_mask_registry_omnibox_tolerates_missing_studio_storage():
    with (
        patch("app.core.screen_definitions._SCREEN_DEFINITIONS", {"demo/screen": object()}),
        patch("app.core.screen_definitions.get_screen_definition", return_value=_screen_dict()),
        patch("app.core.screen_definitions.get_screen_list_route", return_value="/demo"),
        patch("app.core.stamm_object_page_parent.ensure_stamm_screen_registry"),
        patch(
            "app.services.studio_draft_store.list_published_definitions",
            side_effect=StudioStorageUnavailable("no studio"),
        ),
    ):
        entries = mask_registry._build_omnibox_catalog("tenant-a")
        assert len(entries) == 1
        assert entries[0]["screen_id"] == "demo/screen"
        assert entries[0]["route"] == "/demo"


def test_mask_registry_omnibox_rethrows_unexpected_errors():
    with (
        patch("app.core.screen_definitions._SCREEN_DEFINITIONS", {"demo/screen": object()}),
        patch("app.core.screen_definitions.get_screen_definition", return_value=_screen_dict()),
        patch("app.core.screen_definitions.get_screen_list_route", return_value="/demo"),
        patch("app.core.stamm_object_page_parent.ensure_stamm_screen_registry"),
        patch(
            "app.services.studio_draft_store.list_published_definitions",
            side_effect=RuntimeError("boom"),
        ),
    ):
        with pytest.raises(RuntimeError, match="boom"):
            mask_registry._build_omnibox_catalog("tenant-a")


def _bestandteil_row(**overrides):
    base = {
        "id": "1",
        "tenant_id": "t1",
        "bestandteil_nr": "B1",
        "bezeichnung": "Feuchte",
        "einheit": "%",
        "grenzwert_min": None,
        "grenzwert_max": None,
        "nutzung": "qualitaetsdaten",
        "typ_schad_naehr": "naehrstoff",
        "waage_qualitaet_nr": None,
        "aktiv": True,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    base.update(overrides)
    return SimpleNamespace(_mapping=base)


def test_artikel_bestandteile_list_get_create_paths():
    db = MagicMock()
    row = _bestandteil_row()

    list_result = MagicMock()
    list_result.fetchall.return_value = [row]
    get_missing = MagicMock()
    get_missing.fetchone.return_value = None
    create_existing = MagicMock()
    create_existing.fetchone.return_value = None
    create_final = MagicMock()
    create_final.fetchone.return_value = row

    db.execute.side_effect = [list_result, get_missing, create_existing, MagicMock(), create_final]

    listed = artikel_bestandteile.list_bestandteile_def(
        nutzung="qualitaetsdaten", typ="naehrstoff", db=db, tenant_id="t1"
    )
    assert listed[0].bestandteil_nr == "B1"

    with pytest.raises(HTTPException) as missing:
        artikel_bestandteile.get_bestandteil_def("missing", db=db, tenant_id="t1")
    assert missing.value.status_code == 404

    payload = SimpleNamespace(
        bestandteil_nr="B2",
        bezeichnung="Besatz",
        einheit="%",
        grenzwert_min=None,
        grenzwert_max=None,
        nutzung="qualitaetsdaten",
        typ_schad_naehr="schadstoff",
        waage_qualitaet_nr=None,
    )
    created = artikel_bestandteile.create_bestandteil_def(payload, db=db, tenant_id="t1")
    assert created.bestandteil_nr == "B1"
    db.commit.assert_called()
