"""FEED-RECIPE-052 (TDD-Red-Welle 1): bidirektionaler Kundenrezeptur-Kreislauf.

Hinweg: Kundenrezeptur (eigene Artikelnr.) mit append-only Versionen und
Freigabe der Optimal-Rezeptur. Bestellung fixiert IMMER die freigegebene
Version. Ruecklauf: Ist-Lieferung (Mahl-/Mischwagen) wird gegen die fixierte
Version nachkalkuliert. Drift-Schutz: die naechste Bestellung geht wieder von
der Optimal-Rezeptur aus — nie vom letzten Ist. Vor der Implementierung
geschrieben.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


@pytest.mark.parametrize(("method", "path", "body"), [
    ("post", "/feeding/recipes", {"customer_ref": "k-1", "artikel_nr": "A-1",
                                  "name": "Mix", "components": [{"name": "Weizen", "kg_per_t": 500}]}),
    ("get", "/feeding/recipes?customer_ref=k-1", None),
    ("post", "/feeding/recipes/r-1/orders", {"menge_t": 4, "idempotency_key": "o-1"}),
    ("post", "/feeding/recipe-orders/o-1/delivery",
     {"idempotency_key": "d-1", "source": "mixer",
      "components": [{"name": "Weizen", "ist_kg": 2050}]}),
    ("get", "/feeding/recipe-orders/o-1", None),
])
def test_recipe_endpoints_reject_user_without_role(method: str, path: str, body: dict | None) -> None:
    from app.api.v1.endpoints import feeding_recipes
    app = FastAPI()
    app.include_router(feeding_recipes.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = getattr(role_client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

COMPONENTS_V1 = [
    {"name": "Weizen, geschrotet", "kg_per_t": 500.0},
    {"name": "Rapsschrot", "kg_per_t": 350.0},
    {"name": "Mineralfutter", "kg_per_t": 150.0},
]


def _recipe(suffix: str) -> dict[str, Any]:
    response = client.post(f"{ROOT}/feeding/recipes", headers=HEADERS, json={
        "customer_ref": f"kunde-{suffix}", "artikel_nr": f"KA-{suffix}",
        "name": f"Hofmischung {suffix}", "components": COMPONENTS_V1})
    assert response.status_code == 201, response.text
    return response.json()


def test_recipe_is_a_linked_subset_of_a_ration() -> None:
    """Der Kunde bestellt NICHT die ganze Ration — Grund-/Feuchtfutter hat er
    vorraetig. Er verknuepft nur ausgewaehlte Zeilen (Mehle/Schrote/Mineral)
    zu einer Bestellrezeptur; die Herkunft (feed_id, Quell-Ration) bleibt
    nachvollziehbar."""
    suffix = uuid4().hex[:8]
    response = client.post(f"{ROOT}/feeding/recipes", headers=HEADERS, json={
        "customer_ref": f"kunde-{suffix}", "artikel_nr": f"KA-{suffix}",
        "name": f"Kraftfutter-Teilmix {suffix}",
        "source_ration_ref": f"ration-{suffix}",
        "components": [
            {"name": "Weizen, geschrotet", "kg_per_t": 550.0, "feed_id": "dlg_weizen"},
            {"name": "Rapsschrot", "kg_per_t": 450.0, "feed_id": "dlg_raps"},
        ]})
    assert response.status_code == 201, response.text
    recipe = response.json()
    assert recipe["source_ration_ref"] == f"ration-{suffix}"
    components = recipe["latest_components"]
    assert [c["name"] for c in components] == ["Weizen, geschrotet", "Rapsschrot"]
    assert components[0]["feed_id"] == "dlg_weizen"
    # kg_per_t muss in Summe nicht 1000 sein — es ist bewusst eine Teilmischung
    assert sum(c["kg_per_t"] for c in components) == 1000.0


def test_recipe_versions_are_append_only_and_orders_need_approval() -> None:
    suffix = uuid4().hex[:8]
    recipe = _recipe(suffix)
    assert recipe["latest_version_no"] == 1
    assert recipe["approved_version_no"] is None

    # gleiche Kunden-Artikelnummer ist je Kunde eindeutig
    duplicate = client.post(f"{ROOT}/feeding/recipes", headers=HEADERS, json={
        "customer_ref": f"kunde-{suffix}", "artikel_nr": f"KA-{suffix}",
        "name": "Dublette", "components": COMPONENTS_V1})
    assert duplicate.status_code == 409, duplicate.text

    # ohne Freigabe keine Bestellung — klare Meldung
    order = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                        json={"menge_t": 4, "idempotency_key": f"o-{suffix}"})
    assert order.status_code == 409
    assert "freigegeben" in order.json()["detail"].lower()

    approve = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/approve", headers=HEADERS,
                          json={"version_no": 1})
    assert approve.status_code == 200, approve.text
    assert approve.json()["approved_version_no"] == 1


def test_full_cycle_order_delivery_recalc_and_no_drift() -> None:
    suffix = uuid4().hex[:8]
    recipe = _recipe(suffix)
    client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/approve", headers=HEADERS,
                json={"version_no": 1})

    # Bestellung fixiert die freigegebene Version; Soll = kg_per_t × Menge
    order = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                        json={"menge_t": 4, "idempotency_key": f"o1-{suffix}"})
    assert order.status_code == 201, order.text
    first_order = order.json()
    assert first_order["recipe_version_no"] == 1
    soll = {c["name"]: c["soll_kg"] for c in first_order["soll_components"]}
    assert soll["Weizen, geschrotet"] == 2000.0
    assert soll["Rapsschrot"] == 1400.0

    # idempotente Bestellwiederholung
    repeat = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                         json={"menge_t": 4, "idempotency_key": f"o1-{suffix}"})
    assert repeat.status_code == 201 and repeat.json()["id"] == first_order["id"]

    # Ruecklauf: Ist-Mischung mit ueblichen Abweichungen -> Nachkalkulation
    delivery = client.post(f"{ROOT}/feeding/recipe-orders/{first_order['id']}/delivery",
                           headers=HEADERS, json={
                               "idempotency_key": f"d1-{suffix}", "source": "mixer",
                               "components": [
                                   {"name": "Weizen, geschrotet", "ist_kg": 2080.0},
                                   {"name": "Rapsschrot", "ist_kg": 1350.0},
                                   {"name": "Mineralfutter", "ist_kg": 600.0},
                               ]})
    assert delivery.status_code == 201, delivery.text
    recalc = {c["name"]: c for c in delivery.json()["nachkalkulation"]}
    assert recalc["Weizen, geschrotet"]["delta_kg"] == 80.0
    assert recalc["Rapsschrot"]["delta_kg"] == -50.0
    assert recalc["Rapsschrot"]["delta_pct"] == pytest.approx(-3.571, abs=0.01)

    # Kunde kann die Nachkalkulation am Auftrag abrufen
    fetched = client.get(f"{ROOT}/feeding/recipe-orders/{first_order['id']}", headers=HEADERS)
    assert fetched.status_code == 200
    assert fetched.json()["delivery"]["source"] == "mixer"
    assert any(c["delta_kg"] == 80.0 for c in fetched.json()["delivery"]["nachkalkulation"])

    # DRIFT-SCHUTZ: naechste Bestellung geht wieder von der Optimal-Rezeptur aus,
    # nicht vom gelieferten Ist der letzten Mischung.
    second = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                         json={"menge_t": 4, "idempotency_key": f"o2-{suffix}"})
    assert second.status_code == 201, second.text
    soll2 = {c["name"]: c["soll_kg"] for c in second.json()["soll_components"]}
    assert soll2 == soll, "kein Drift: identisches Soll wie die erste Bestellung"

    # Neue Optimal-Version (append-only) + Freigabe wirkt erst auf NEUE Bestellungen
    new_version = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/versions",
                              headers=HEADERS, json={
                                  "expected_latest_version_no": 1,
                                  "components": [
                                      {"name": "Weizen, geschrotet", "kg_per_t": 480.0},
                                      {"name": "Rapsschrot", "kg_per_t": 370.0},
                                      {"name": "Mineralfutter", "kg_per_t": 150.0},
                                  ]})
    assert new_version.status_code == 201, new_version.text
    client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/approve", headers=HEADERS,
                json={"version_no": 2})
    third = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                        json={"menge_t": 4, "idempotency_key": f"o3-{suffix}"})
    assert third.json()["recipe_version_no"] == 2
    # der frueher gelieferte Auftrag bleibt auf seiner fixierten Version
    assert client.get(f"{ROOT}/feeding/recipe-orders/{first_order['id']}",
                      headers=HEADERS).json()["recipe_version_no"] == 1


def test_delivery_rejects_unknown_component_instead_of_guessing() -> None:
    suffix = uuid4().hex[:8]
    recipe = _recipe(suffix)
    client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/approve", headers=HEADERS,
                json={"version_no": 1})
    order = client.post(f"{ROOT}/feeding/recipes/{recipe['id']}/orders", headers=HEADERS,
                        json={"menge_t": 2, "idempotency_key": f"o-{suffix}"}).json()

    response = client.post(f"{ROOT}/feeding/recipe-orders/{order['id']}/delivery",
                           headers=HEADERS, json={
                               "idempotency_key": f"d-{suffix}", "source": "manual",
                               "components": [{"name": "Unbekanntes Futter", "ist_kg": 100.0}]})
    assert response.status_code == 422, response.text
    assert "Unbekanntes Futter" in response.json()["detail"]
