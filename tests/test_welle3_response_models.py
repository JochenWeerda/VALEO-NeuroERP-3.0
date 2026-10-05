"""SPEC-P1-06 Welle 3: getypte response_model fuer Lieferkette, Rations-Lebenszyklus,
Ist-Fuetterung und Operator-Agent.

Die Feldproben laufen gegen DDL- bzw. servicegetreue Beispielzeilen, weil alle
vier Bereiche eine laufende Datenbank braeuchten. Die fachlichen Endpunkttests
(``test_rations_lifecycle_api`` und Geschwister) decken den DB-Pfad ab.
"""

from datetime import date, datetime

import pytest

from app.api.v1.endpoints import feeding_actual as feeding_module
from app.api.v1.endpoints import operator_agent as agent_module
from app.api.v1.endpoints import rations_lifecycle as rations_module
from app.api.v1.endpoints import supply_chain as chain_module
from app.api.v1.schemas import feeding_actual_schemas as fa
from app.api.v1.schemas import operator_agent_schemas as oa
from app.api.v1.schemas import rations_lifecycle_schemas as rl
from app.api.v1.schemas import supply_chain_schemas as sc

pytestmark = pytest.mark.unit


# Reine Downloads liefern eine CSV-Response statt JSON und haben deshalb
# zurecht kein response_model.
REINE_DOWNLOADS = {"/feeding/actuals/export.csv"}


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize(
    "module",
    [chain_module, rations_module, feeding_module, agent_module],
    ids=["supply_chain", "rations_lifecycle", "feeding_actual", "operator_agent"],
)
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if path in REINE_DOWNLOADS:
            continue
        # list[EchtesSchema].__name__ ist ebenfalls "list" — nur die Textform
        # unterscheidet den generischen Container vom nackten Typ.
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


# ── Lieferkette ─────────────────────────────────────────────────────────────


@pytest.fixture
def kettenknoten():
    return {
        "stage": "wiegung",
        "label": "Wiegung",
        "ref": "WG-1",
        "ref_id": "1",
        "status": "ok",
        "menge_kg": 1000.0,
        "zeitpunkt": "2026-08-01",
        "facts": {"brutto_kg": 1200.0, "kennzeichen": "XX", "allokation": "allocated"},
    }


@pytest.fixture
def kettenereignis():
    return {
        "id": "e",
        "ticket_id": "t",
        "stage": "lager",
        "ref_type": "silo_lot",
        "ref_id": "l",
        "ref_label": "L1",
        "event_type": "storniert",
        "status_from": "active",
        "status_to": "storniert",
        "menge_kg": -5.0,
        "abweichung_grund": "Grund",
        "payload": {"x": 1},
        "bediener": "KIM",
        "source": "manual",
        "occurred_at": "2026-08-01T00:00:00",
        "created_at": "2026-08-01T00:00:00",
    }


def test_kettenknoten_behaelt_die_stufenspezifischen_facts(kettenknoten):
    """``facts`` ist je Stufe anders belegt und muss unveraendert durchgehen."""
    dumped = _assert_kein_feldverlust(sc.ChainNodeOut, kettenknoten)
    assert dumped["facts"]["kennzeichen"] == "XX"
    assert dumped["facts"]["allokation"] == "allocated"


def test_kettenereignis_deckt_die_service_spaltenliste_ab(kettenereignis):
    _assert_kein_feldverlust(sc.ChainEventOut, kettenereignis)


def test_traceability_behaelt_alle_ebenen(kettenknoten, kettenereignis):
    daten = {
        "found": True,
        "ticket_id": "t",
        "ticket_nr": "WG-1",
        "kette": [kettenknoten],
        "mengen_konsistenz": [
            {
                "von": "Wiegung",
                "nach": "Lager",
                "menge_von_kg": 1000.0,
                "menge_nach_kg": 990.0,
                "differenz_kg": -10.0,
                "differenz_pct": -1.0,
                "abweichung": False,
                "hinweis": "innerhalb Toleranz",
            }
        ],
        "luecken": [{"stufe": "annahme", "schwere": "warnung", "text": "fehlt"}],
        "ereignisse": [kettenereignis],
        "kanon_status": {"status": "offen", "rang": 0},
        "summary": {
            "stufen": 1,
            "vollstaendig": False,
            "hat_mengen_abweichung": False,
            "offene_luecken": 1,
            "status": "offen",
        },
    }
    dumped = _assert_kein_feldverlust(sc.TraceabilityOut, daten)
    assert dumped["kette"][0]["facts"]["brutto_kg"] == 1200.0
    assert dumped["mengen_konsistenz"][0]["differenz_pct"] == -1.0
    assert dumped["ereignisse"][0]["payload"] == {"x": 1}


def test_traceability_traegt_den_nichttrefferfall():
    dumped = sc.TraceabilityOut.model_validate(
        {"found": False, "detail": "Kein Wiegeschein zur Eingabe aufloesbar."}
    ).model_dump()
    assert dumped["found"] is False
    assert dumped["detail"].startswith("Kein Wiegeschein")


def test_lot_aktionen_und_storno(kettenereignis):
    _assert_kein_feldverlust(
        sc.LotActionOut,
        {"ok": True, "lot": "L1", "status": "gesperrt", "event": kettenereignis},
        "LotActionOut(sperre)",
    )
    # Nur die Schwundbuchung fuehrt bestand_kg.
    _assert_kein_feldverlust(
        sc.LotActionOut,
        {"ok": True, "lot": "L1", "bestand_kg": 900.0, "event": kettenereignis},
        "LotActionOut(schwund)",
    )
    _assert_kein_feldverlust(
        sc.ChainCancelOut,
        {
            "ok": True,
            "ticket_id": "t",
            "ticket_nr": "WG-1",
            "stornierte_lots": ["L1"],
            "status": "storniert",
            "event": kettenereignis,
        },
    )


def test_sync_und_event_ack_tragen_beide_zweige(kettenereignis):
    _assert_kein_feldverlust(sc.ChainSyncOut, {"synced": 2, "total": 5, "ticket_id": "t"})
    _assert_kein_feldverlust(
        sc.ChainSyncOut,
        {"synced": 0, "detail": "Ticket nicht aufloesbar."},
        "ChainSyncOut(fehler)",
    )
    _assert_kein_feldverlust(sc.ChainEventAckOut, {"ok": True, "event": kettenereignis})
    _assert_kein_feldverlust(
        sc.ChainEventAckOut,
        {"ok": False, "detail": "Ticket nicht aufloesbar."},
        "ChainEventAckOut(fehler)",
    )


# ── Rations-Lebenszyklus ────────────────────────────────────────────────────


@pytest.fixture
def rationsversion():
    return {
        "id": "v",
        "tenant_id": "t",
        "ration_id": "r",
        "version_no": 1,
        "source": "solver",
        "comment": None,
        "snapshot": {"readiness": {"status": "ok", "blocker_count": 0}},
        "snapshot_checksum": "abc",
        "based_on_version_id": None,
        "created_by": "u",
        "created_at": datetime(2026, 8, 1),
        "status": "draft",
        "feeding_start": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "approved_by": None,
        "approved_at": None,
        "activated_by": None,
        "activated_at": None,
        "retired_by": None,
        "retired_at": None,
        "archived_by": None,
        "archived_at": None,
    }


def test_neue_version_liefert_die_versionszeile_nicht_das_rationsdetail():
    """Regressionsklammer fuer einen Fehler aus dieser Welle.

    ``create_version`` gibt die neue Versionszeile zurueck, nicht das
    Rations-Detail. Mit RationDetailOut fiel ``version_no`` aus der Antwort und
    der Lebenszyklus-Endpunkttest brach.
    """
    modelle = _response_models(rations_module)
    assert (
        modelle[("/lifecycle/rations/{ration_id}/versions", "POST")] is rl.RationVersionOut
    ), "POST versions muss die Versionszeile liefern"
    assert modelle[("/lifecycle/rations", "POST")] is rl.RationDetailOut


def test_rationsversion_behaelt_lebenszyklus_stempel(rationsversion):
    dumped = _assert_kein_feldverlust(rl.RationVersionOut, rationsversion)
    assert dumped["snapshot"]["readiness"]["status"] == "ok"


def test_rationsdetail_behaelt_versionen_audit_und_latest_felder(rationsversion):
    audit = {
        "id": "a",
        "tenant_id": "t",
        "ration_id": "r",
        "version_id": "v",
        "event_type": "status_transition",
        "from_status": "draft",
        "to_status": "in_review",
        "actor": "u",
        "reason": None,
        "delta": {"version_no": 1},
        "occurred_at": datetime(2026, 8, 1),
    }
    daten = {
        "id": "r",
        "tenant_id": "t",
        "group_id": "g",
        "name": "R1",
        "description": None,
        "created_by": "u",
        "created_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 1),
        "group_name": "G",
        "animal_count": 100,
        "feeding_system": "TMR",
        "location": "Stall 1",
        "versions": [rationsversion],
        "audit": [audit],
        "latest_version_id": "v",
        "latest_version_no": 1,
        "latest_status": "draft",
        "latest_feeding_start": None,
        "latest_readiness_status": "ok",
        "latest_readiness_blockers": 0,
        "latest_readiness_warnings": 0,
    }
    dumped = _assert_kein_feldverlust(rl.RationDetailOut, daten)
    assert dumped["audit"][0]["delta"] == {"version_no": 1}
    assert dumped["versions"][0]["version_no"] == 1


def test_statuswechsel_behaelt_abgeloeste_versionen():
    daten = {
        "version_id": "v",
        "tenant_id": "t",
        "ration_id": "r",
        "group_id": "g",
        "status": "active",
        "feeding_start": datetime(2026, 8, 1),
        "reviewed_by": "u",
        "reviewed_at": datetime(2026, 8, 1),
        "approved_by": "u",
        "approved_at": datetime(2026, 8, 1),
        "activated_by": "u",
        "activated_at": datetime(2026, 8, 1),
        "retired_by": None,
        "retired_at": None,
        "archived_by": None,
        "archived_at": None,
        "updated_at": datetime(2026, 8, 1),
        "version_no": 2,
        "snapshot_checksum": "abc",
        "superseded_version_ids": ["v0"],
    }
    dumped = _assert_kein_feldverlust(rl.RationTransitionOut, daten)
    assert dumped["superseded_version_ids"] == ["v0"]


def test_aktive_ration_behaelt_den_snapshot():
    daten = {
        "ration_id": "r",
        "name": "R1",
        "group_id": "g",
        "group_name": "G",
        "animal_count": 100,
        "version_id": "v",
        "version_no": 1,
        "snapshot": {"result": {"status": "optimal"}},
        "snapshot_checksum": "abc",
        "feeding_start": datetime(2026, 8, 1),
        "activated_at": datetime(2026, 8, 1),
    }
    dumped = _assert_kein_feldverlust(rl.ActiveRationOut, daten)
    assert dumped["snapshot"]["result"]["status"] == "optimal"


# ── Ist-Fuetterung ──────────────────────────────────────────────────────────


@pytest.fixture
def komponente():
    return {
        "id": "c",
        "tenant_id": "t",
        "actual_record_id": "ar",
        "instruction_id": "i",
        "feed_id": "f",
        "feed_name": "Silage",
        "target_kg": 10.0,
        "actual_kg": 9.0,
        "delta_kg": -1.0,
        "delta_pct": -10.0,
        "value_consequences": {"cost": {"delta_eur": -1.2}, "nutrients": []},
    }


def test_ist_datensatz_behaelt_komponenten_und_folgen(komponente):
    daten = {
        "id": "ar",
        "tenant_id": "t",
        "plan_version_id": "pv",
        "group_id": "g",
        "feeding_at": datetime(2026, 8, 1),
        "source": "manual",
        "source_ref": "x",
        "cause_class": "normal",
        "comment": None,
        "context": {},
        "supersedes_id": None,
        "idempotency_key": "k",
        "request_hash": "h",
        "recorded_by": "u",
        "recorded_at": datetime(2026, 8, 1),
        "group_name": "G",
        "plan_version_no": 2,
        "components": [komponente],
    }
    dumped = _assert_kein_feldverlust(fa.ActualRecordOut, daten)
    assert dumped["components"][0]["value_consequences"]["cost"]["delta_eur"] == -1.2


def test_befund_traegt_beide_auspraegungen():
    """Ohne konfigurierte Schwelle liefert der Service nur den Identitaetsteil."""
    ohne_policy = {
        "actual_component_id": "c",
        "actual_record_id": "ar",
        "plan_version_id": "pv",
        "group_id": "g",
        "feed_id": "f",
        "feed_name": "Silage",
        "severity": "unconfigured",
        "message": "Keine explizite Schwelle konfiguriert.",
        "feed_class": "other",
        "policy_id": None,
    }
    _assert_kein_feldverlust(fa.DeviationFindingOut, ohne_policy, "Befund(unconfigured)")

    bewertet = {
        **ohne_policy,
        "policy_id": "p",
        "severity": "warning",
        "feed_class": "roughage",
        "policy_version": 1,
        "target_kg": 10.0,
        "actual_kg": 9.0,
        "delta_kg": -1.0,
        "delta_pct": -10.0,
        "threshold_pct": 5.0,
        "remedy": "Dosierung pruefen.",
    }
    dumped = _assert_kein_feldverlust(fa.DeviationFindingOut, bewertet, "Befund(bewertet)")
    assert dumped["threshold_pct"] == 5.0


def test_massnahme_behaelt_versionsfelder_aus_dem_join():
    daten = {
        "id": "m",
        "tenant_id": "t",
        "actual_record_id": "ar",
        "actual_component_id": "c",
        "group_id": "g",
        "finding": {"severity": "warning"},
        "title": "T",
        "owner_subject": "u",
        "due_date": date(2026, 9, 1),
        "version": 2,
        "status": "in_progress",
        "reason": "r",
        "idempotency_key": "k",
        "request_hash": "h",
        "created_by": "u",
        "created_at": datetime(2026, 8, 1),
        "reminder_date": date(2026, 8, 25),
        "escalation_status": "attention",
        "effectiveness": "partial",
        "effectiveness_result": "teilweise",
        "changed_by": "u",
        "changed_at": datetime(2026, 8, 1),
    }
    dumped = _assert_kein_feldverlust(fa.ActualMeasureOut, daten)
    assert dumped["escalation_status"] == "attention"


def test_policy_und_komponentensicht(komponente):
    _assert_kein_feldverlust(
        fa.DeviationPolicyOut,
        {
            "id": "p",
            "tenant_id": "t",
            "feed_class": "roughage",
            "version": 1,
            "warning_pct": 5.0,
            "critical_pct": 10.0,
            "valid_from": date(2026, 1, 1),
            "reason": "r",
            "created_by": "u",
            "created_at": datetime(2026, 8, 1),
        },
    )
    _assert_kein_feldverlust(
        fa.ActualComponentRowOut,
        {
            "id": "c",
            "actual_record_id": "ar",
            "plan_version_id": "pv",
            "plan_version_no": 2,
            "group_id": "g",
            "group_name": "G",
            "feeding_at": datetime(2026, 8, 1),
            "cause_class": "normal",
            "comment": None,
            "source": "manual",
            "feed_id": "f",
            "feed_name": "Silage",
            "target_kg": 10.0,
            "actual_kg": 9.0,
            "delta_kg": -1.0,
            "delta_pct": -10.0,
            "cost_delta_eur": -1.2,
            "nutrient_delta_summary": "NEL: -0.5 MJ",
            "missing_value_summary": None,
        },
    )
    _assert_kein_feldverlust(fa.ActualComponentOut, komponente)


# ── Operator-Agent ──────────────────────────────────────────────────────────


def test_agent_kontext_behaelt_risikovertrag_und_freien_kontext():
    daten = {
        "tenant_id": "t",
        "action_type": "mahnung_vorschlag",
        "risk_level": "high",
        "human_approval_required": True,
        "context": {"gesamt_offen_eur": 1234.56, "empfohlene_mahnstufe": 1},
        "retrieved_at": "2026-08-01T00:00:00",
        "hinweis": "Kontext-Abfrage - kein Schreibzugriff.",
    }
    dumped = _assert_kein_feldverlust(oa.AgentContextOut, daten)
    # Risikostufe und Freigabepflicht sind der Sicherheitsvertrag.
    assert dumped["risk_level"] == "high"
    assert dumped["human_approval_required"] is True
    assert dumped["context"]["empfohlene_mahnstufe"] == 1


def test_agent_proposal_behaelt_alle_to_dict_felder():
    daten = {
        "proposal_id": "p",
        "tenant_id": "t",
        "action_type": "a",
        "risk_level": "low",
        "human_approval_required": False,
        "context_summary": {"x": 1},
        "proposed_action": {"y": 2},
        "rationale": "r",
        "approval_status": "pending",
        "created_at": "2026-08-01T00:00:00",
        "approved_by": None,
        "approved_at": None,
        "rejection_reason": None,
        "audit_event_count": 2,
    }
    dumped = _assert_kein_feldverlust(oa.AgentProposalOut, daten)
    assert dumped["audit_event_count"] == 2


def test_agent_summary_und_ausfuehrung():
    _assert_kein_feldverlust(
        oa.AgentProposalSummaryOut,
        {
            "tenant_id": "t",
            "total_proposals": 3,
            "by_status": {"pending": 1, "approved": 2},
            "pending_high_risk": 1,
        },
    )
    dumped = _assert_kein_feldverlust(
        oa.AgentExecutionOut,
        {
            "proposal_id": "p",
            "action_type": "a",
            "executed_by": "u",
            "executed_at": "2026-08-01T00:00:00",
            "result": {"simulated": True, "outbox_event": "crm.angebot.nachgefasst"},
        },
    )
    assert dumped["result"]["outbox_event"] == "crm.angebot.nachgefasst"
