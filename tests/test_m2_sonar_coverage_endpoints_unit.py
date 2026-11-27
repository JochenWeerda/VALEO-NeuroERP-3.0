"""Executable Unit-Tests: M2 Sonar New-Code Coverage (Rohware/Mask/Artikel)."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import artikel_bestandteile, inventur_piv, mask_registry, milchvieh_crosssell, rohwarengruppen
from app.services.einkauf_compat_service import EinkaufCompatService
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


def test_rohwarengruppen_list_active_filter():
    db = MagicMock()
    row = SimpleNamespace(
        _mapping={
            "id": "g1",
            "tenant_id": "t1",
            "gruppe_nr": "GE",
            "bezeichnung": "Getreide",
            "artikel_nr": None,
            "ek_aktiv": True,
            "vk_aktiv": True,
            "waehrung": "EUR",
            "mengeneinheit": "t",
            "aktiv": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        }
    )
    result = MagicMock()
    result.fetchall.return_value = [row]
    db.execute.return_value = result
    listed = rohwarengruppen.list_rohwarengruppen(nur_aktive=True, db=db, tenant_id="t1")
    assert listed[0].gruppe_nr == "GE"
    sql = str(db.execute.call_args.args[0])
    assert "tenant_id" in sql


def test_milchvieh_produktgruppen_flacht_summary():
    db = MagicMock()
    with patch("app.api.v1.endpoints.milchvieh_crosssell.MilchviehCrossSellService") as svc_cls:
        svc_cls.return_value.summary.return_value = {"produktgruppen": [{"name": "Dipp"}, {"name": "KF"}]}
        assert milchvieh_crosssell.crosssell_produktgruppen(db=db) == [{"name": "Dipp"}, {"name": "KF"}]
        svc_cls.return_value.summary.return_value = {"produktgruppen": "x"}
        assert milchvieh_crosssell.crosssell_produktgruppen(db=db) == []
        svc_cls.return_value.summary.return_value = "bad"
        assert milchvieh_crosssell.crosssell_produktgruppen(db=db) == []


def test_einkauf_compat_list_suppliers_and_invalidate():
    db = MagicMock()
    row = SimpleNamespace(_mapping={"id": "s1", "name": "Hof", "tenant_id": "t1", "is_active": True})
    db.execute.return_value.fetchall.return_value = [row]
    svc = EinkaufCompatService(db, "t1")
    out = svc.list_suppliers(search="Hof", is_active=True, limit=10, skip=0)
    assert out["total"] == 1
    assert out["items"][0]["name"] == "Hof"
    with patch("app.core.cache.cache_delete_prefix", side_effect=RuntimeError("cache down")):
        svc._invalidate()  # Fehler wird geschluckt


def test_inventur_piv_list_and_get_404():
    db = MagicMock()
    row = SimpleNamespace(
        _mapping={
            "id": "p1",
            "abschluss_datum": datetime(2026, 1, 1, tzinfo=timezone.utc).date(),
            "inventurgruppe_nr": "IG1",
            "lager_nr": "L1",
            "status": "offen",
            "erfasst_von": None,
            "abgeschlossen_von": None,
            "abgeschlossen_am": None,
            "anzahl_positionen": 0,
            "differenzwert_eur": None,
            "bemerkung": None,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        }
    )
    list_result = MagicMock()
    list_result.fetchall.return_value = [row]
    missing = MagicMock()
    missing.fetchone.return_value = None
    db.execute.side_effect = [list_result, missing]

    listed = inventur_piv.list_piv_abschluesse(status="offen", lager_nr="L1", db=db, tenant_id="t1")
    assert listed[0].id == "p1"
    with pytest.raises(HTTPException) as exc:
        inventur_piv.get_piv_abschluss("missing", db=db, tenant_id="t1")
    assert exc.value.status_code == 404
