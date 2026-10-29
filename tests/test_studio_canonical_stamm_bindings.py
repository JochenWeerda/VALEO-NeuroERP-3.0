"""Vertrag fuer die drei lesbaren kanonischen Studio-Stamm-Bindungen."""

from __future__ import annotations

from app.api.v1.endpoints.artikel_mengeneinheiten import MengeneinheitCreate, MengeneinheitOut
from app.api.v1.endpoints.hausbankenstamm import HausbankCreate, HausbankOut, router as hausbank_router
from app.api.v1.endpoints.individuelle_artikelnummern import (
    IndivArtikelNrOut,
    router as individuelle_nummern_router,
)
from app.api.v1.endpoints.artikel_mengeneinheiten import router as mengeneinheiten_router
from app.core.screen_definitions_stamm import (
    build_stammdaten_hausbank_stamm,
    build_stammdaten_individuelle_artikelnummer_stamm,
    build_stammdaten_mengeneinheit_stamm,
)


def _field_keys(definition: dict) -> set[str]:
    return {field["key"] for field in definition["tabs"][0]["fields"]}


def _action(definition: dict, key: str = "edit") -> dict:
    return next(action for action in definition["actions"] if action["key"] == key)


def _methods(router, path: str) -> set[str]:
    return {
        method
        for route in router.routes
        if getattr(route, "path", None) == path
        for method in (getattr(route, "methods", None) or set())
    }


def test_hausbank_definition_matches_get_and_put_contract() -> None:
    definition = build_stammdaten_hausbank_stamm()
    endpoint = "/api/v1/stammdaten/hausbanken/{entity_id}"
    action = _action(definition)

    assert definition["identityField"] == "bank_nr"
    assert definition["dataSources"][0] == {"key": "entity", "endpoint": endpoint}
    assert _methods(hausbank_router, "/stammdaten/hausbanken/{bank_nr}") == {"GET", "PUT", "DELETE"}
    assert _field_keys(definition) <= set(HausbankOut.model_fields)
    assert {field["key"] for field in action["inputFields"]} == set(HausbankCreate.model_fields)
    assert action["commandEndpoint"] == endpoint
    assert action["method"] == "PUT"
    assert action["permission"] == "finance.hausbank.update"


def test_mengeneinheit_definition_matches_detail_and_full_update_contract() -> None:
    definition = build_stammdaten_mengeneinheit_stamm()
    endpoint = "/api/v1/artikel/mengeneinheiten/stamm/{entity_id}"
    action = _action(definition)

    assert definition["identityField"] == "einheit_kuerzel"
    assert definition["dataSources"][0] == {"key": "entity", "endpoint": endpoint}
    assert _methods(mengeneinheiten_router, "/artikel/mengeneinheiten/stamm/{einheit_kuerzel}") == {"GET", "PUT", "DELETE"}
    assert _field_keys(definition) <= set(MengeneinheitOut.model_fields)
    assert {field["key"] for field in action["inputFields"]} == set(MengeneinheitCreate.model_fields)
    assert action["commandEndpoint"] == endpoint
    assert action["method"] == "PUT"
    assert action["permission"] == "stammdaten.mengeneinheit.update"


def test_individuelle_artikelnummer_is_read_only_until_update_contract_exists() -> None:
    definition = build_stammdaten_individuelle_artikelnummer_stamm()
    endpoint = "/api/v1/artikel/individuelle-nummern/{entity_id}"
    action = _action(definition)

    assert definition["identityField"] == "id"
    assert definition["dataSources"][0] == {"key": "entity", "endpoint": endpoint}
    assert _methods(individuelle_nummern_router, "/artikel/individuelle-nummern/{indiv_id}") == {"GET", "DELETE"}
    assert _field_keys(definition) <= set(IndivArtikelNrOut.model_fields)
    assert action["disabled"] is True
    assert "keine Aktualisierung" in action["stubReason"]
    assert "commandEndpoint" not in action
