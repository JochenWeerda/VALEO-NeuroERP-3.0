"""SPEC-P1-06 Welle 4: getypte response_model fuer Abrechnungsstapel,
AI-Engineering-Metriken, Workflow-Cockpit (DB) und Kontraktaktionen.

Die Mock-freien Bereiche (AI-Metriken) werden gegen den echten Service geprobt;
die DB-gestuetzten gegen DDL-getreue Beispielzeilen.
"""

from datetime import datetime

import pytest

from app.api.v1.endpoints import ai_engineering_metrics as metrics_module
from app.api.v1.endpoints import billing_batch as billing_module
from app.api.v1.endpoints import kontrakt_actions as kontrakt_module
from app.api.v1.endpoints import wf_cockpit_persist as cockpit_module
from app.api.v1.schemas import ai_engineering_metrics_schemas as am
from app.api.v1.schemas import billing_batch_schemas as bb
from app.api.v1.schemas import kontrakt_actions_schemas as ka
from app.api.v1.schemas import wf_cockpit_persist_schemas as wf
from app.services.ai_engineering_metrics_service import ai_engineering_metrics_service

pytestmark = pytest.mark.unit


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize(
    "module",
    [billing_module, metrics_module, cockpit_module, kontrakt_module],
    ids=["billing_batch", "ai_engineering_metrics", "wf_cockpit_persist", "kontrakt_actions"],
)
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        # dict[str, int] ist ein echter Typ (Mapping mit dynamischen Schluesseln)
        # und wird bewusst nicht als schwach gewertet — nur bare dict/list/Any
        # und dict[str, Any] zaehlen.
        text = str(model)
        if (
            model is None
            or model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def test_owner_distribution_bleibt_ein_echtes_mapping():
    """Dynamische Schluessel (Eigentuemernamen) lassen sich nicht als Modell
    mit festen Feldern abbilden — dict[str, int] ist hier die genaue Form."""
    modelle = _response_models(metrics_module)
    assert modelle[("/ai-engineering/metrics/owner-distribution", "GET")] == dict[str, int]


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


# ── AI-Engineering-Metriken: gegen den echten Service ────────────────────────


def test_metriken_schemas_gegen_den_echten_service():
    _assert_kein_feldverlust(
        am.CycleTimeSummaryOut, ai_engineering_metrics_service.cycle_time_summary()
    )
    _assert_kein_feldverlust(
        am.CoverageSummaryOut, ai_engineering_metrics_service.coverage_summary()
    )
    _assert_kein_feldverlust(
        am.GateBlockerSummaryOut, ai_engineering_metrics_service.gate_blocker_summary()
    )
    _assert_kein_feldverlust(
        am.ReworkIndicatorOut, ai_engineering_metrics_service.rework_indicator()
    )
    _assert_kein_feldverlust(
        am.MetricsDashboardOut, ai_engineering_metrics_service.full_dashboard()
    )
    slices = ai_engineering_metrics_service.slice_metrics()
    if slices:
        _assert_kein_feldverlust(am.SliceMetricOut, slices[0])


def test_coverage_traegt_den_fehlerzweig():
    """Ohne coverage.xml liefert der Service nur ``status`` mit einem Hinweis."""
    dumped = am.CoverageSummaryOut.model_validate(
        {"status": "coverage.xml nicht gefunden - pytest --cov zuerst ausfuehren"}
    ).model_dump()
    assert dumped["status"].startswith("coverage.xml")
    assert dumped["total_files"] is None


# ── Workflow-Cockpit ────────────────────────────────────────────────────────


def test_cockpit_instanz_traegt_beide_migrationsformen():
    """Zwei Migrationen legen wf_cockpit_instances unterschiedlich an.

    ``wf_cockpit_persist_20260625`` fuehrt ``created_at``, die Reparatur
    ``feed_qs_wf_cockpit_repair_20260626`` zusaetzlich ``started_at`` und
    ``finished_at``. Der Detail-Endpunkt liest ``SELECT *`` — das Schema muss
    beide Saetze tragen, sonst verliert es je nach Installation Felder.
    """
    kanonisch = {
        "id": "i1",
        "tenant_id": "t",
        "process_key": "o2c",
        "status": "failed",
        "correlation_id": "c1",
        "idempotency_key": "k",
        "business_object_ref": "SO-1",
        "current_step": "invoice",
        "audit_ref": "a1",
        "active_blocker_count": 1,
        "replayable": True,
        "created_at": "2026-08-01T00:00:00",
        "updated_at": "2026-08-02T00:00:00",
    }
    _assert_kein_feldverlust(wf.CockpitInstanceOut, kanonisch, "Instanz(kanonisch)")

    repariert = {
        **kanonisch,
        "started_at": "2026-08-01T00:00:00",
        "finished_at": None,
    }
    _assert_kein_feldverlust(wf.CockpitInstanceOut, repariert, "Instanz(Reparatur)")


def test_cockpit_blocker_traegt_beide_migrationsformen():
    kanonisch = {
        "id": "b1",
        "blocker_type": "BLOCKED_EXTERNAL_GATE",
        "message": "Steuerberater-Freigabe fehlt",
        "external_system": "DATEV",
        "retryable": True,
        "resolved": False,
        "since": "2026-08-01T00:00:00",
        "resolved_at": None,
    }
    _assert_kein_feldverlust(wf.CockpitBlockerOut, kanonisch, "Blocker(kanonisch)")

    repariert = {
        **kanonisch,
        "reason": "Freigabe fehlt",
        "context": {"gate": "datev"},
        "resolved_by": None,
        "created_at": "2026-08-01T00:00:00",
    }
    dumped = _assert_kein_feldverlust(
        wf.CockpitBlockerOut, repariert, "Blocker(Reparatur)"
    )
    assert dumped["context"] == {"gate": "datev"}


def test_cockpit_detail_und_dead_letter():
    ereignis = {
        "id": "e1",
        "kind": "domain_event",
        "message": "Schritt fehlgeschlagen",
        "source": "workflow-cockpit",
        "payload": {"step": "invoice"},
        "occurred_at": "2026-08-01T00:00:00",
    }
    detail = {
        "id": "i1",
        "tenant_id": "t",
        "process_key": "o2c",
        "status": "failed",
        "correlation_id": "c1",
        "created_at": "2026-08-01T00:00:00",
        "updated_at": "2026-08-02T00:00:00",
        "events": [ereignis],
        "blockers": [],
    }
    dumped = _assert_kein_feldverlust(wf.CockpitInstanceDetailOut, detail)
    assert dumped["events"][0]["payload"] == {"step": "invoice"}

    _assert_kein_feldverlust(
        wf.DeadLetterViewOut,
        {
            "tenant_id": "t",
            "dead_letter_count": 1,
            "items": [
                {
                    "id": "i1",
                    "process_key": "o2c",
                    "status": "failed",
                    "correlation_id": "c1",
                    "current_step": "invoice",
                    "updated_at": "2026-08-02T00:00:00",
                    "replayable": True,
                    "open_blocker_count": 2,
                }
            ],
        },
    )


def test_cockpit_aktionsantworten():
    assert wf.InstanceUpsertOut.model_validate(
        {"process_instance_id": "i1", "ok": True}
    ).model_dump() == {"process_instance_id": "i1", "ok": True}
    assert wf.BlockerResolvedOut.model_validate(
        {"blocker_id": "b1", "resolved": True}
    ).model_dump() == {"blocker_id": "b1", "resolved": True}
    for status in ("retry_pending", "compensated"):
        assert wf.InstanceStatusOut.model_validate(
            {"process_instance_id": "i1", "status": status}
        ).model_dump()["status"] == status


# ── Abrechnungsstapel ───────────────────────────────────────────────────────


def test_stapel_und_positionen():
    _assert_kein_feldverlust(
        bb.BatchOut,
        {
            "id": "b1",
            "batch_number": "BB-2026-001",
            "batch_type": "sammelrechnung",
            "status": "validated",
            "description": "August",
            "maker": "u1",
            "checker": None,
            "currency": "EUR",
            "total_lines": 10,
            "processed_lines": 0,
            "failed_lines": 1,
            "total_amount": 1234.56,
            "created_at": datetime(2026, 8, 1),
            "updated_at": datetime(2026, 8, 2),
        },
    )
    _assert_kein_feldverlust(
        bb.BatchLineOut,
        {
            "id": "l1",
            "batch_id": "b1",
            "source_type": "lieferschein",
            "source_ref": "LS-1",
            "source_number": "LS-2026-001",
            "source_route": "/verkauf/lieferscheine/1",
            "evidence_route": "/dokumente/1",
            "amount": 123.45,
            "status": "failed",
            "validation_error": "Kunde gesperrt",
            "retry_count": 1,
            "processed_at": None,
            "created_at": datetime(2026, 8, 1),
        },
    )


def test_stapel_aktionen_tragen_ihre_zusatzfelder():
    """validate/execute liefern mehr als release/retry — ein Schema, optionale Felder."""
    _assert_kein_feldverlust(
        bb.BatchActionOut, {"id": "b1", "status": "validated", "failed_lines": 2},
        "Aktion(validate)",
    )
    dumped = _assert_kein_feldverlust(
        bb.BatchActionOut,
        {"id": "b1", "status": "partial_failed", "processed_lines": 8, "failed_lines": 2},
        "Aktion(execute)",
    )
    assert dumped["processed_lines"] == 8
    schlank = _assert_kein_feldverlust(
        bb.BatchActionOut, {"id": "b1", "status": "released"}, "Aktion(release)"
    )
    assert schlank["failed_lines"] is None


def test_stapel_summary_und_anlage():
    _assert_kein_feldverlust(
        bb.BatchSummaryOut,
        {
            "draft": 1,
            "validated": 2,
            "released": 0,
            "running": 0,
            "partial_failed": 1,
            "failed_lines": 3,
        },
    )
    _assert_kein_feldverlust(
        bb.BatchCreatedOut,
        {
            "id": "b1",
            "batch_number": "BB-2026-001",
            "status": "draft",
            "total_lines": 10,
            "total_amount": 1234.56,
        },
    )


# ── Kontraktaktionen ────────────────────────────────────────────────────────


def test_kontrakt_lifecycle_fixing_settlement():
    _assert_kein_feldverlust(
        ka.KontraktLifecycleOut,
        {
            "id": "k1",
            "kontrakt_id": "K-1",
            "tenant_id": "t",
            "kontrakt_nr": "KT-2026-001",
            "artikel_id": "A1",
            "menge_t": 500.0,
            "preis_eur_t": 210.5,
            "lieferant_id": "L1",
            "periode": "2026-Q3",
            "status": "ENTWURF",
            "created_at": datetime(2026, 8, 1),
            "updated_at": None,
        },
    )
    _assert_kein_feldverlust(
        ka.KontraktFixingOut,
        {
            "id": "f1",
            "kontrakt_id": "K-1",
            "tenant_id": "t",
            "fixing_datum": "2026-08-01",
            "fixing_preis_eur_t": 215.0,
            "menge_t": 100.0,
            "markt": "KASSA",
            "referenz": "MATIF",
            "operator": "u1",
            "created_at": datetime(2026, 8, 1),
        },
    )
    dumped = _assert_kein_feldverlust(
        ka.KontraktFixingSummaryOut,
        {
            "kontrakt_id": "K-1",
            "gefixte_menge_t": 100.0,
            "offene_menge_t": 400.0,
            "avg_fixing_preis_eur_t": 215.0,
            "anzahl_fixings": 1,
            "vollstaendig_gefixt": False,
        },
    )
    assert dumped["offene_menge_t"] == 400.0
    _assert_kein_feldverlust(
        ka.KontraktSettlementOut,
        {
            "id": "s1",
            "kontrakt_id": "K-1",
            "tenant_id": "t",
            "lieferung_datum": "2026-08-15",
            "gelieferte_menge_t": 50.0,
            "abrechnungspreis_eur_t": 212.0,
            "netto_eur": 10600.0,
            "referenz": "LS-1",
            "status": "OFFEN",
            "storno_grund": "",
            "operator": "u1",
            "created_at": datetime(2026, 8, 15),
            "updated_at": None,
        },
    )
