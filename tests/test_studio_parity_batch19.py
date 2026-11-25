"""Paritaet Batch 19: Sammelabrechnung, Qualitaets-Nachtrag, Mengenzeiträume."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_listen import (
    build_agrar_erntefenster_konfig_liste,
    build_agrar_qualitaet_nachtrag_liste,
    build_agrar_sammelabrechnung_liste,
    build_kontrakte_mengenzeitraeume_liste,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"


def _action_keys(sd: dict) -> set[str]:
    keys = {a["key"] for a in sd.get("actions") or []}
    for table in sd.get("tables") or []:
        keys |= {a["key"] for a in table.get("rowActions") or []}

    def walk(obj: object) -> set[str]:
        found: set[str] = set()
        if isinstance(obj, dict):
            if "rowActions" in obj:
                found |= {a["key"] for a in obj["rowActions"]}
            for v in obj.values():
                found |= walk(v)
        elif isinstance(obj, list):
            for v in obj:
                found |= walk(v)
        return found

    return keys | walk(sd)


def _create_field_keys(sd: dict, action_key: str) -> set[str]:
    for a in sd.get("actions") or []:
        if a.get("key") == action_key:
            return {f["key"] for f in a.get("inputFields") or []}
    return set()


@pytest.mark.unit
def test_sammelabrechnung_page_is_native_list():
    src = (PAGES / "agrar/sammelabrechnung.tsx").read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert "agrar/sammelabrechnung" in src
    assert "-legacy" not in src


@pytest.mark.unit
def test_sammelabrechnung_covers_legacy_create_and_lifecycle():
    sd = build_agrar_sammelabrechnung_liste()
    create_keys = _create_field_keys(sd, "anlegen")
    assert {
        "bezeichnung",
        "abrechnungsperiode",
        "harvest_acceptance_ids",
        "sammeldatum",
        "abrechnungsschema_id",
    }.issubset(create_keys)
    anlegen = next(a for a in sd["actions"] if a["key"] == "anlegen")
    assert anlegen["commandEndpoint"] == "/api/v1/agrar/sammelabrechnung"
    assert {"berechnen", "buchen", "loeschen"}.issubset(_action_keys(sd))


@pytest.mark.unit
def test_qualitaet_nachtrag_page_and_fields():
    src = (PAGES / "agrar/annahmen-qualitaet-nachtrag.tsx").read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert "agrar/annahmen-qualitaet-nachtrag" in src

    sd = build_agrar_qualitaet_nachtrag_liste()
    assert {"nachtragen", "batch_nachtragen"}.issubset(_action_keys(sd))
    row = None
    for table in sd.get("tables") or []:
        for a in table.get("rowActions") or []:
            if a["key"] == "nachtragen":
                row = a
    if row is None:
        # fallback walk
        for a in _walk_actions(sd):
            if a.get("key") == "nachtragen":
                row = a
                break
    assert row is not None
    fields = {f["key"] for f in row["inputFields"]}
    assert {
        "feuchte_prozent",
        "hektolitergewicht_kg_hl",
        "besatz",
        "protein_prozent",
        "fallzahl",
        "bemerkungen",
        "labor_code",
        "analysendatum",
    }.issubset(fields)
    assert row["commandEndpoint"].endswith("/qualitaetsprotokoll")


def _walk_actions(obj: object) -> list[dict]:
    found: list[dict] = []
    if isinstance(obj, dict):
        if "key" in obj and ("commandEndpoint" in obj or "inputFields" in obj):
            found.append(obj)
        for v in obj.values():
            found.extend(_walk_actions(v))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(_walk_actions(v))
    return found


@pytest.mark.unit
def test_mengenzeitraeume_replaces_stub_with_full_actions():
    src = (PAGES / "kontrakte/mengenzeitraeume.tsx").read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert "kontrakte/mengenzeitraeume" in src
    assert "-legacy" not in src

    sd = build_kontrakte_mengenzeitraeume_liste()
    assert sd["id"] == "kontrakte/mengenzeitraeume"
    # Stub hatte nur id/name/status — jetzt volle Aktionsmenge
    assert {
        "zeitraum_anlegen",
        "zeitraeume_generieren",
        "gruppe_anlegen",
        "zeitraum_loeschen",
        "abschlag_anlegen",
    }.issubset(_action_keys(sd))
    create_keys = _create_field_keys(sd, "zeitraum_anlegen")
    assert {
        "kontrakt_nr",
        "zeitraum_von",
        "zeitraum_bis",
        "menge_t",
        "variante",
        "bemerkung",
    }.issubset(create_keys)


@pytest.mark.unit
def test_erntefenster_konfig_parity():
    src = (PAGES / "agrar/erntefenster-konfig.tsx").read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert "agrar/erntefenster-konfig" in src
    assert "-legacy" not in src

    sd = build_agrar_erntefenster_konfig_liste()
    assert {
        "template_id",
        "name",
        "year",
        "start_mmdd",
        "end_mmdd",
    }.issubset(_create_field_keys(sd, "anlegen"))
    keys = _action_keys(sd)
    assert {"anlegen", "alt_daten_zuordnen", "settlement_pruefen", "sandbox"}.issubset(keys)
    anlegen = next(a for a in sd["actions"] if a["key"] == "anlegen")
    assert anlegen["commandEndpoint"] == "/api/v1/admin/erntefenster-from-template"
