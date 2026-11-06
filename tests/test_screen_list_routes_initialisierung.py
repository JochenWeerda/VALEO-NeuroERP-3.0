"""Listenrouten duerfen nicht von der vorherigen Lazy-Initialisierung abhaengen."""
from app.core import screen_definitions as screens
from app.core import stamm_object_page_parent as stamm
from app.core.screen_definitions_stamm import STAMM_ROUTEN
from scripts import generate_screen_list_routes as generator


def test_kalter_warmer_und_wiederholter_lauf_liefern_dieselben_routen(monkeypatch):
    curated = screens._CURATED_SCREEN_LIST_ROUTE_IDS
    monkeypatch.setattr(screens, "_SCREEN_LIST_ROUTE", {
        key: value for key, value in screens._SCREEN_LIST_ROUTE.items() if key in curated
    })
    registry = dict(screens._SCREEN_DEFINITIONS)
    monkeypatch.setattr(screens, "_SCREEN_DEFINITIONS", registry)
    monkeypatch.setattr(screens, "SCREEN_DEFINITION_BUILDERS", registry)
    monkeypatch.setattr(screens, "_AGENT_SYNONYMS", {key: list(value) for key, value in screens._AGENT_SYNONYMS.items()})
    monkeypatch.setattr(stamm, "_STAMM_REGISTRY_DONE", False)
    cold = generator.erzeugen()
    assert stamm._STAMM_REGISTRY_DONE
    warm = generator.erzeugen()
    again = generator.erzeugen()
    assert cold == warm == again
    assert not set(cold["routen"]) & curated
    for screen_id in ("artikel/stamm", "annahme/waage-1", "admin/users"):
        assert cold["routen"][screen_id] == STAMM_ROUTEN[screen_id]
