"""Vertrag: Python-Builder und TypeScript-Fallback beschreiben denselben Vorgang."""

from __future__ import annotations

from pathlib import Path

from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_capture import (
    build_fuhrpark_fahrzeuge_screen_definition,
    build_logistik_frachttabellen_screen_definition,
    build_logistik_tour_fracht_arbeitsraum_screen_definition,
    build_logistik_tourenplanung_screen_definition,
    build_transporte_fahrer_screen_definition,
)

ROOT = Path(__file__).resolve().parents[1]
FALLBACK = (ROOT / "packages/frontend-web/src/masks/capture-screens.ts").read_text(encoding="utf-8")

TOUR_FIELDS = ["datum", "tour_id", "tour_status", "ziel", "lieferschein", "fahrzeug_id", "fahrer_id"]
TOUR_ENDPOINTS = ["/api/v1/logistik/tours", "/api/v1/fuhrpark/fahrzeuge", "/api/v1/transporte/fahrer"]
FAHRZEUG_PRIORITY = {
    "kennzeichen": "primary",
    "status": "primary",
    "typ": "secondary",
    "kilometerstand": "secondary",
    "ro_nummer": "tertiary",
    "naechste_inspektion": "tertiary",
}


def _block(name: str) -> str:
    marker = f"export const {name} = "
    start = FALLBACK.index(marker)
    nxt = FALLBACK.find("\nexport const ", start + len(marker))
    return FALLBACK[start:] if nxt < 0 else FALLBACK[start:nxt]


def _first_keys(block: str, keys: list[str]) -> list[int]:
    return [block.index(f"key: '{key}'") for key in keys]


def test_tour_builder_und_fallback_stimmen_ueberein() -> None:
    definition = build_logistik_tourenplanung_screen_definition()
    block = _block("tourenplanungScreen")
    assert definition["id"] == "logistik/tourenplanung"
    assert definition["title"] == "Tourenplanung"
    assert [field["key"] for field in definition["fields"]] == TOUR_FIELDS
    assert _first_keys(block, TOUR_FIELDS) == sorted(_first_keys(block, TOUR_FIELDS))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    summary = [item["key"] for item in definition["summary"]]
    assert summary == ["heute", "geplant", "unterwegs", "abgeschlossen"]
    assert _first_keys(block, summary) == sorted(_first_keys(block, summary))
    endpoints = [source["endpoint"] for source in definition["dataSources"]]
    assert endpoints == TOUR_ENDPOINTS
    for endpoint in TOUR_ENDPOINTS:
        assert endpoint in block
    assert "DEMO-LS-001" not in block
    assert get_screen_definition("logistik/tourenplanung")["id"] == "logistik/tourenplanung"


def test_fahrzeugspalten_haben_dieselbe_prioritaet() -> None:
    definition = build_fuhrpark_fahrzeuge_screen_definition()
    block = _block("fuhrparkFahrzeugeScreen")
    assert definition["title"] == "Fahrzeuge"
    assert definition["tables"][0]["label"] == "Fahrzeuge"
    assert "title: 'Fahrzeuge'" in block
    priorities = {column["key"]: column["priority"] for column in definition["tables"][0]["columns"]}
    assert priorities == FAHRZEUG_PRIORITY
    for key, priority in FAHRZEUG_PRIORITY.items():
        assert f"key: '{key}'" in block
        assert f"priority: '{priority}'" in block


def test_fahrer_zaehlt_touren_aus_demselben_endpunkt() -> None:
    definition = build_transporte_fahrer_screen_definition()
    block = _block("transporteFahrerScreen")
    assert definition["id"] == "transporte/fahrer"
    assert definition["title"] == "Fahrer"
    endpoints = [source["endpoint"] for source in definition["dataSources"]]
    assert "/api/v1/transporte/fahrer" in endpoints
    assert "/api/v1/logistik/tours" in endpoints
    assert "/api/v1/transporte/fahrer" in block
    assert "/api/v1/logistik/tours" in block
    footer = [action["key"] for action in definition["actions"] if action["zone"] == "footer"]
    assert footer[:1] == ["verfuegbar"]
    assert "zone: 'footer'" in block
    assert "DEMO-LS-001" not in block
    assert get_screen_definition("transporte/fahrer")["title"] == "Fahrer"


def test_arbeitsraum_folgt_denselben_listen() -> None:
    definition = build_logistik_tour_fracht_arbeitsraum_screen_definition()
    block = _block("tourFrachtArbeitsraumScreen")
    assert definition["id"] == "logistik/tour-fracht-arbeitsraum"
    assert definition["title"] == "Tour & Fracht"
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    assert [table["key"] for table in definition["tables"]] == ["touren", "fracht", "tarife"]
    assert [source["endpoint"] for source in definition["dataSources"]] == [
        "/api/v1/logistik/tours",
        "/api/v1/logistik/frachtbriefe",
        "/api/v1/logistik/freight-tariffs",
    ]
    for endpoint in ("/api/v1/logistik/tours", "/api/v1/logistik/frachtbriefe", "/api/v1/logistik/freight-tariffs"):
        assert endpoint in block
    assert get_screen_definition("logistik/tour-fracht-arbeitsraum")["title"] == "Tour & Fracht"


def test_frachttabellen_staffel_folgt_der_tabelle() -> None:
    definition = build_logistik_frachttabellen_screen_definition()
    block = _block("frachttabellenScreen")
    felder = ["tabelle_nr", "bezeichnung", "einheit", "waehrung", "staffel", "ab_menge", "frachtsatz_eur", "mindestfracht_eur"]
    assert definition["title"] == "Frachttabellen"
    assert [field["key"] for field in definition["fields"]] == felder
    assert _first_keys(block, felder) == sorted(_first_keys(block, felder))
    assert definition["layout"]["statusPlacement"] == "afterFields"
    assert "statusPlacement: 'afterFields'" in block
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/logistik/frachttabellen"
    assert "/api/v1/logistik/frachttabellen" in block
    assert definition["tables"][0]["columns"][0]["priority"] == "primary"
    assert definition["tables"][0]["columns"][-1]["priority"] == "tertiary"
    assert get_screen_definition("logistik/frachttabellen")["id"] == "logistik/frachttabellen"
