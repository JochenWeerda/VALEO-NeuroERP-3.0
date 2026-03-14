"""Wave 9 Paket B - Domain Tests: Ernte-Kampagne und Frontend-Process-Binding."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import uuid

from app.core.ernte_kampagne import (
    ErnteArt,
    ErnteKampagne,
    ErnteKampagneStore,
    KampagnenStatus,
    SchlagErnteziel,
)
from app.core.frontend_process_binding import (
    MaskenCommandBinding,
    MaskenBindingRegistry,
    TriggerEvent,
    build_default_bindings,
)


def make_ziel(
    schlag_id: str = "schlag-1",
    sorte: str = "Aurelia",
    flaeche_ha: float = 10.0,
    ziel_ertrag_t_ha: float = 8.5,
) -> SchlagErnteziel:
    return SchlagErnteziel(
        schlag_id=schlag_id,
        sorte=sorte,
        flaeche_ha=flaeche_ha,
        ziel_ertrag_t_ha=ziel_ertrag_t_ha,
    )


def make_kampagne(
    tenant_id: str = "tenant-a",
    wirtschaftsjahr: int = 2026,
    status: KampagnenStatus = KampagnenStatus.PLANUNG,
) -> ErnteKampagne:
    return ErnteKampagne(
        kampagne_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        wirtschaftsjahr=wirtschaftsjahr,
        ernte_art=ErnteArt.GETREIDE,
        bezeichnung="Ernte 2026",
        schlag_ziele=[make_ziel(), make_ziel("schlag-2", flaeche_ha=5.0, ziel_ertrag_t_ha=7.0)],
        status=status,
    )


def test_schlag_ernteziel_erwartet_gesamt_t():
    ziel = make_ziel(flaeche_ha=12.0, ziel_ertrag_t_ha=7.5)
    assert ziel.erwartet_gesamt_t == 90.0


def test_kampagne_geplante_gesamtmenge_t():
    kampagne = make_kampagne()
    assert kampagne.geplante_gesamtmenge_t == 120.0


def test_kampagne_geplante_gesamtflaeche_ha():
    kampagne = make_kampagne()
    assert kampagne.geplante_gesamtflaeche_ha == 15.0


def test_kampagne_fortschritt_pct_berechnet():
    kampagne = make_kampagne()
    assert kampagne.fortschritt_pct(60.0) == 50.0


def test_kampagne_fortschritt_pct_max_100():
    kampagne = make_kampagne()
    assert kampagne.fortschritt_pct(999.0) == 100.0


def test_kampagne_fortschritt_pct_bei_null_plan():
    kampagne = make_kampagne()
    kampagne.schlag_ziele = []
    assert kampagne.fortschritt_pct(10.0) == 0.0


def test_kampagne_starten_setzt_status():
    kampagne = make_kampagne()
    kampagne.kampagne_starten()
    assert kampagne.status == KampagnenStatus.AKTIV
    assert kampagne.gestartet_am is not None


def test_kampagne_abschliessen_setzt_status():
    kampagne = make_kampagne(status=KampagnenStatus.AKTIV)
    kampagne.kampagne_abschliessen()
    assert kampagne.status == KampagnenStatus.ABGESCHLOSSEN
    assert kampagne.abgeschlossen_am is not None


def test_kampagne_archivieren_setzt_status():
    kampagne = make_kampagne(status=KampagnenStatus.ABGESCHLOSSEN)
    kampagne.archivieren()
    assert kampagne.status == KampagnenStatus.ARCHIVIERT


def test_kampagne_starten_ungueltig():
    kampagne = make_kampagne(status=KampagnenStatus.AKTIV)
    import pytest
    with pytest.raises(ValueError):
        kampagne.kampagne_starten()


def test_kampagne_abschliessen_ungueltig():
    kampagne = make_kampagne(status=KampagnenStatus.PLANUNG)
    import pytest
    with pytest.raises(ValueError):
        kampagne.kampagne_abschliessen()


def test_kampagne_store_add_get():
    store = ErnteKampagneStore()
    kampagne = make_kampagne()
    store.add(kampagne)
    assert store.get(kampagne.kampagne_id) is kampagne


def test_kampagne_store_aktive():
    store = ErnteKampagneStore()
    store.add(make_kampagne(status=KampagnenStatus.AKTIV))
    store.add(make_kampagne(status=KampagnenStatus.PLANUNG))
    assert len(store.aktive("tenant-a")) == 1


def test_kampagne_store_by_wirtschaftsjahr():
    store = ErnteKampagneStore()
    store.add(make_kampagne(wirtschaftsjahr=2026))
    store.add(make_kampagne(wirtschaftsjahr=2027))
    assert len(store.by_wirtschaftsjahr("tenant-a", 2026)) == 1


def test_binding_registry_add_and_lookup():
    registry = MaskenBindingRegistry()
    binding = MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="A001",
        masken_name="AP-Invoice-Genehmigung",
        command_name="ApproveAPInvoice",
        trigger_event=TriggerEvent.ON_FREIGABE_CLICK,
        required_preconditions=["status"],
    )
    registry.add(binding)
    assert registry.by_masken_id("A001")[0].command_name == "ApproveAPInvoice"
    assert registry.by_command("ApproveAPInvoice")[0].masken_id == "A001"


def test_binding_registry_alle_masken_ids_eindeutig():
    registry = build_default_bindings()
    ids = registry.alle_masken_ids()
    assert "A001" in ids
    assert len(ids) == len(set(ids))


def test_default_bindings_decken_ap_invoice():
    registry = build_default_bindings()
    bindings = registry.by_masken_id("A001")
    command_names = {binding.command_name for binding in bindings}
    assert {"ApproveAPInvoice", "RejectAPInvoice", "PostAPInvoice"} <= command_names


def test_default_bindings_decken_payment_run():
    registry = build_default_bindings()
    bindings = registry.by_command("ExecutePaymentRun")
    assert bindings[0].masken_id == "C001"


def test_default_bindings_schema_version():
    registry = build_default_bindings()
    assert registry.schema_version == 1
    assert all(binding.schema_version == 1 for binding in registry.bindings)


def test_default_bindings_count():
    registry = build_default_bindings()
    assert len(registry.bindings) >= 8


def test_api_ernte_kampagne_create_and_list():
    from app.api.v1.endpoints.ernte_kampagne_api import router as ernte_router

    app = FastAPI()
    app.include_router(ernte_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=True)

    create_resp = client.post(
        "/api/v1/ernte-kampagnen",
        json={
            "tenant_id": "tenant-a",
            "wirtschaftsjahr": 2026,
            "ernte_art": "getreide",
            "bezeichnung": "Ernte 2026",
            "schlag_ziele": [
                {"schlag_id": "s1", "sorte": "Aurelia", "flaeche_ha": 10.0, "ziel_ertrag_t_ha": 8.5}
            ],
        },
    )
    assert create_resp.status_code == 201
    kampagne_id = create_resp.json()["kampagne_id"]

    list_resp = client.get("/api/v1/ernte-kampagnen/tenant/tenant-a")
    assert list_resp.status_code == 200
    assert any(item["kampagne_id"] == kampagne_id for item in list_resp.json())


def test_api_ernte_kampagne_start_and_finish():
    from app.api.v1.endpoints.ernte_kampagne_api import router as ernte_router

    app = FastAPI()
    app.include_router(ernte_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=True)

    create_resp = client.post(
        "/api/v1/ernte-kampagnen",
        json={
            "tenant_id": "tenant-a",
            "wirtschaftsjahr": 2026,
            "ernte_art": "getreide",
            "bezeichnung": "Ernte 2026",
            "schlag_ziele": [
                {"schlag_id": "s1", "sorte": "Aurelia", "flaeche_ha": 10.0, "ziel_ertrag_t_ha": 8.5}
            ],
        },
    )
    kampagne_id = create_resp.json()["kampagne_id"]

    start_resp = client.post(f"/api/v1/ernte-kampagnen/{kampagne_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "aktiv"

    finish_resp = client.post(f"/api/v1/ernte-kampagnen/{kampagne_id}/abschliessen")
    assert finish_resp.status_code == 200
    assert finish_resp.json()["status"] == "abgeschlossen"
