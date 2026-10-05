"""SPEC-P1-06 Welle 7: Dokumentenkette (DOM-DOC-004) und Inventur-/PLC-Bereich."""

from datetime import datetime

import pytest

from app.api.v1.endpoints import agri_plc_stub as plc_module
from app.api.v1.endpoints import doc_nachweisraum_actions as nachweis_module
from app.api.v1.endpoints import docflow_followup as followup_module
from app.api.v1.endpoints import docflow_return as return_module
from app.api.v1.endpoints import document_control as control_module
from app.api.v1.endpoints import inventory_auxiliary as aux_module
from app.api.v1.schemas import docflow_bundle_schemas as doc
from app.api.v1.schemas import inventory_bundle_schemas as inv

pytestmark = pytest.mark.unit

WELLE7_MODULE = [
    control_module,
    return_module,
    followup_module,
    nachweis_module,
    aux_module,
    plc_module,
]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize("module", WELLE7_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        text = str(model)
        if (
            model is None
            or model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


# ── Belegkontrolle ──────────────────────────────────────────────────────────


def test_belegausnahme_und_worklist():
    ausnahme = {
        "id": "e1",
        "exception_type": "uninvoiced_delivery_note",
        "status": "assigned",
        "document_ref": "LS-1",
        "document_number": "LS-2026-001",
        "partner_ref": "K-1",
        "partner_name": "Hof Meyer",
        "assigned_user": "u1",
        "due_at": datetime(2026, 9, 1),
        "source_route": "/verkauf/lieferscheine/1",
        "notes": None,
        "created_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 2),
    }
    _assert_kein_feldverlust(doc.ControlExceptionOut, ausnahme)
    _assert_kein_feldverlust(
        doc.ControlWorklistOut,
        {"items": [ausnahme], "total": 1, "page": 1, "page_size": 25},
    )
    _assert_kein_feldverlust(
        doc.ControlSummaryOut,
        {
            "open_total": 5,
            "open_purchase_order": 1,
            "missing_inbound_document": 2,
            "blocked_delivery_note": 1,
            "uninvoiced_delivery_note": 1,
            "overdue": 3,
        },
    )


def test_belegausnahme_kennt_idempotenz_und_projektion():
    """register liefert duplicate, der Projektionslauf zusaetzlich projection."""
    _assert_kein_feldverlust(
        doc.ControlRegisteredOut,
        {"id": "e1", "status": "open", "duplicate": False},
        "Registriert(neu)",
    )
    dumped = _assert_kein_feldverlust(
        doc.ControlRegisteredOut,
        {"id": "e1", "status": "open", "duplicate": False, "projection": "created"},
        "Registriert(projiziert)",
    )
    assert dumped["projection"] == "created"
    _assert_kein_feldverlust(
        doc.ControlProjectionOut,
        {"tenant_id": "t", "collected": 12, "created": 3, "refreshed": 4, "skipped": 5},
    )
    _assert_kein_feldverlust(
        doc.ControlAssignOut, {"id": "e1", "assigned_user": "u1", "status": "assigned"}
    )
    _assert_kein_feldverlust(doc.ControlTransitionOut, {"id": "e1", "status": "resolved"})


# ── Dokumentenruecklauf ─────────────────────────────────────────────────────


def test_ruecklauf_worklist_und_nachweis():
    fall = {
        "id": "r1",
        "doc_number": "RE-2026-001",
        "subject_type": "kunde",
        "subject_ref": "K-1",
        "contact_ref": "c1",
        "assigned_user": "u1",
        "tags": ["urgent"],
        "shipping_status": "sent",
        "return_status": "expected",
        "due_at": datetime(2026, 9, 1),
        "sent_at": datetime(2026, 8, 2),
        "returned_at": None,
        "source_route": "/verkauf/rechnungen/1",
        "created_at": datetime(2026, 8, 1),
        "file_name": "rechnung.pdf",
        "storage_key": "s3://bucket/key",
    }
    _assert_kein_feldverlust(doc.ReturnCaseOut, fall)
    _assert_kein_feldverlust(
        doc.ReturnWorklistOut, {"items": [fall], "total": 1, "page": 1, "page_size": 25}
    )
    _assert_kein_feldverlust(
        doc.ReturnSummaryOut,
        {"total": 10, "not_sent": 2, "expected": 5, "received": 3, "overdue": 1},
    )
    dumped = _assert_kein_feldverlust(
        doc.ReturnEvidenceOut,
        {
            "id": "r1",
            "doc_number": "RE-2026-001",
            "source_route": "/verkauf/rechnungen/1",
            "artifact_id": "a1",
            "file_name": "rechnung.pdf",
            "artifact_type": "pdf",
            "content_hash_sha256": "abc123",
            "storage_key": "s3://bucket/key",
            "preview_available": True,
            "audit": [
                {
                    "id": "au1",
                    "action": "created",
                    "old_value": None,
                    "new_value": "expected",
                    "actor": "u1",
                    "reason": "Ruecklauf angelegt",
                    "created_at": datetime(2026, 8, 1),
                }
            ],
        },
    )
    # Der Inhaltshash ist der Kern des Nachweises.
    assert dumped["content_hash_sha256"] == "abc123"
    assert dumped["audit"][0]["new_value"] == "expected"


def test_ruecklauf_transition_hat_einen_dynamischen_schluessel():
    """Der Service setzt je nach kind shipping_status ODER return_status."""
    versand = _assert_kein_feldverlust(
        doc.ReturnTransitionOut, {"id": "r1", "shipping_status": "sent"}, "Transition(Versand)"
    )
    assert versand["return_status"] is None
    ruecklauf = _assert_kein_feldverlust(
        doc.ReturnTransitionOut, {"id": "r1", "return_status": "received"}, "Transition(Ruecklauf)"
    )
    assert ruecklauf["shipping_status"] is None
    _assert_kein_feldverlust(
        doc.ReturnCreatedOut,
        {
            "id": "r1",
            "doc_number": "RE-2026-001",
            "shipping_status": "not_sent",
            "return_status": "expected",
        },
    )


# ── Followups und Wiedervorlagen ────────────────────────────────────────────


def test_followups_und_wiedervorlagen():
    followup = {
        "followup_id": "f1",
        "art": "wiedervorlage",
        "betreff": "Nachfassen",
        "text": None,
        "faellig_am": "2026-08-20",
        "status": "offen",
        "ueberfaellig": True,
        "erledigt_at": None,
        "erledigt_von": None,
        "created_at": "2026-08-01T00:00:00",
        "created_by": "KIM",
    }
    dumped = _assert_kein_feldverlust(
        doc.FollowupListOut,
        {
            "found": True,
            "doc_number": "RE-2026-001",
            "followups": [followup],
            "summary": {"anzahl": 1, "offen": 1, "ueberfaellig": 1},
        },
    )
    # ueberfaellig wird gegen das Tagesdatum berechnet, ist keine Spalte.
    assert dumped["followups"][0]["ueberfaellig"] is True

    nichttreffer = doc.FollowupListOut.model_validate(
        {"found": False, "detail": "Dokument nicht gefunden."}
    ).model_dump()
    assert nichttreffer["found"] is False

    _assert_kein_feldverlust(
        doc.WiedervorlagenListOut,
        {
            "items": [
                {
                    "followup_id": "f1",
                    "doc_number": "RE-2026-001",
                    "betreff": "Nachfassen",
                    "faellig_am": "2026-08-20",
                    "bediener": "KIM",
                    "ueberfaellig": True,
                }
            ]
        },
    )
    _assert_kein_feldverlust(
        doc.FollowupCreatedOut,
        {"ok": True, "followup_id": "f1", "doc_number": "RE-2026-001", "art": "wiedervorlage"},
    )
    _assert_kein_feldverlust(
        doc.FollowupCompletedOut, {"ok": True, "followup_id": "f1", "status": "erledigt"}
    )


# ── Nachweisraum und GoBD ───────────────────────────────────────────────────


def test_nachweisraum_und_gobd():
    _assert_kein_feldverlust(
        doc.NachweisDokumentOut,
        {
            "id": "d1",
            "tenant_id": "t",
            "dokument_typ": "bescheid",
            "bezeichnung": "Foerderbescheid",
            "referenz_id": "V-1",
            "referenz_typ": "vorgang",
            "datei_pfad": "/archiv/d1.pdf",
            "version": 2,
            "status": "EINGEGANGEN",
            "wiedervorlage_datum": "2026-09-01",
            "operator": "system",
            "created_at": datetime(2026, 8, 1),
            "updated_at": None,
        },
    )
    _assert_kein_feldverlust(
        doc.GobdExportOut,
        {
            "id": "g1",
            "tenant_id": "t",
            "periode": "2026-Q3",
            "anzahl_dokumente": 120,
            "status": "OFFEN",
            "export_pfad": None,
            "fehler_grund": None,
            "operator": "system",
            "created_at": datetime(2026, 8, 1),
            "updated_at": None,
        },
    )


# ── Inventur-Hilfsstapel ────────────────────────────────────────────────────


def test_hilfsstapel_und_summary():
    stapel = {
        "id": "b1",
        "inventory_count_id": "c1",
        "batch_type": "differenz",
        "status": "generated",
        "source_hash": "abc",
        "line_count": 40,
        "difference_count": 3,
        "preliminary_value": 1234.56,
        "maker": "u1",
        "checker": None,
        "source_route": "/lager/inventur/1",
        "notes": None,
        "created_at": datetime(2026, 8, 1),
        "updated_at": None,
    }
    _assert_kein_feldverlust(inv.AuxiliaryBatchOut, stapel)
    _assert_kein_feldverlust(
        inv.AuxiliaryBatchPageOut,
        {"items": [stapel], "total": 1, "page": 1, "page_size": 50},
    )
    _assert_kein_feldverlust(
        inv.AuxiliarySummaryOut,
        {"generated": 2, "reviewed": 1, "approved": 0, "applied": 5, "with_differences": 3},
    )
    # Idempotenzpfad liefert weniger Felder als die Neuanlage.
    knapp = _assert_kein_feldverlust(
        inv.AuxiliaryBatchCreatedOut,
        {"id": "b1", "status": "generated", "duplicate": True, "source_hash": "abc"},
        "Anlage(idempotent)",
    )
    assert knapp["line_count"] is None
    _assert_kein_feldverlust(
        inv.AuxiliaryBatchCreatedOut,
        {
            "id": "b1",
            "status": "generated",
            "duplicate": False,
            "source_hash": "abc",
            "line_count": 40,
            "difference_count": 3,
            "preliminary_value": 1234.56,
        },
        "Anlage(neu)",
    )
    _assert_kein_feldverlust(inv.AuxiliaryTransitionOut, {"id": "b1", "status": "approved"})


# ── PLC ─────────────────────────────────────────────────────────────────────


def test_plc_antworten():
    _assert_kein_feldverlust(
        inv.PlcIngestOut,
        {
            "ok": True,
            "device_id": "plc-1",
            "received": 10,
            "processed": 8,
            "skipped_bad_quality": 2,
        },
    )
    _assert_kein_feldverlust(
        inv.PlcSiloLevelOut,
        {
            "ok": True,
            "cell_id": "z1",
            "cell_code": "Z-01",
            "level_pct": 62.5,
            "estimated_stock_kg": 125000.0,
            "temperature_celsius": 14.2,
            "qs_status": "freigegeben",
        },
    )
    _assert_kein_feldverlust(
        inv.PlcDeviceStatusOut, {"ok": True, "device_id": "plc-1", "status": "online"}
    )
    dumped = _assert_kein_feldverlust(
        inv.PlcInfoOut,
        {
            "stub": True,
            "version": "WM-AGRI-PLC-005",
            "endpoints": ["POST /plc/ingest — Batch OPC-UA/PLC Datenpunkte"],
            "production_extensions": ["asyncua OPC-UA client (asyncio polling loop)"],
        },
    )
    # 'stub: true' ist die Aussage dieses Endpunkts und darf nicht wegfallen.
    assert dumped["stub"] is True
