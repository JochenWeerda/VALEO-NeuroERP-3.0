"""NeuroASSIST workflow for data-quality driven ingestion and remediation cases."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _mark_stage(state: dict[str, Any], stage_key: str, detail: str) -> None:
    state["current_stage_key"] = stage_key
    state["stage_transition_log"].append(
        {
            "stage_key": stage_key,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": detail,
        }
    )


def _set_gate(
    state: dict[str, Any],
    *,
    gate_type: str,
    status: str,
    reason: str,
    required_role: str | None = None,
    evidence_refs: list[str] | None = None,
) -> None:
    state["gate_decisions"] = [
        decision for decision in state.get("gate_decisions", []) if decision.get("gate_type") != gate_type
    ]
    state["gate_decisions"].append(
        {
            "gate_type": gate_type,
            "status": status,
            "reason": reason,
            "required_role": required_role,
            "evidence_refs": list(evidence_refs or []),
            "schema_version": 1,
        }
    )


def _summarize_findings(dq_findings: list[dict[str, Any]]) -> tuple[str, list[str]]:
    if not dq_findings:
        return (
            "Keine expliziten DQ-Findings uebergeben; der Fall dient der vorbeugenden Ingestion-Pruefung.",
            ["Ingestion-Kontext vervollstaendigen und Regeln vor Persistenz erneut pruefen."],
        )

    highest_severity = "warnung"
    grouped_fields: list[str] = []
    actions: list[str] = []
    for finding in dq_findings:
        severity = str(finding.get("severity") or finding.get("schweregrad") or "warnung").lower()
        field_name = str(finding.get("feld") or finding.get("field") or "unbekannt")
        if field_name not in grouped_fields:
            grouped_fields.append(field_name)
        if severity in {"error", "fehler", "critical", "kritisch"}:
            highest_severity = "fehler"
        message = str(finding.get("meldung") or finding.get("message") or "DQ-Regel verletzt")
        actions.append(f"{field_name}: {message}")

    summary = (
        f"DQ-Fall mit {len(dq_findings)} Findings ueber {len(grouped_fields)} Felder; "
        f"hoechste Severity: {highest_severity}."
    )
    return summary, actions


async def run_data_quality_assistant(
    *,
    entity_type: str,
    payload_snapshot: dict[str, Any],
    dq_findings: list[dict[str, Any]] | None = None,
    ingestion_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    findings = list(dq_findings or [])
    context = dict(ingestion_context or {})
    state: dict[str, Any] = {
        "entity_type": entity_type,
        "payload_snapshot": dict(payload_snapshot),
        "dq_findings": findings,
        "ingestion_context": context,
        "root_cause_summary": "",
        "remediation_plan": [],
        "current_stage_key": "intake",
        "stage_transition_log": [
            {
                "stage_key": "intake",
                "timestamp": datetime.utcnow().isoformat(),
                "detail": "DQ ingestion run created",
            }
        ],
        "gate_decisions": [],
    }

    _mark_stage(state, "analysis", "Cluster DQ findings and ingestion context")
    summary, actions = _summarize_findings(findings)
    state["root_cause_summary"] = summary
    state["remediation_plan"] = actions

    _mark_stage(state, "verification", "Verify payload completeness against DQ findings")
    dq_status = "blocked" if findings else "allowed"
    _set_gate(
        state,
        gate_type="dq_gate",
        status=dq_status,
        reason=(
            "Persistenz ist blockiert, bis die DQ-Findings fachlich aufgeloest sind."
            if findings
            else "Keine blockierenden DQ-Findings mehr vorhanden."
        ),
        evidence_refs=[entity_type, "dq_validation"],
    )

    _mark_stage(state, "approval", "Prepare remediation handover for ingestion owner")
    if findings:
        _set_gate(
            state,
            gate_type="approval_gate",
            status="deferred",
            reason="Ein Datenverantwortlicher muss die vorgeschlagene DQ-Remediation bestaetigen.",
            required_role="data_steward",
            evidence_refs=[entity_type, "dq_resolution_proposal"],
        )
    else:
        _set_gate(
            state,
            gate_type="approval_gate",
            status="allowed",
            reason="Keine manuelle Freigabe notwendig, da keine blockierenden DQ-Findings offen sind.",
            required_role="data_steward",
            evidence_refs=[entity_type],
        )

    _mark_stage(state, "execution", "Emit structured remediation proposal")
    _mark_stage(state, "closure", "Close DQ assistant run with explainable remediation payload")

    return {
        "entity_type": entity_type,
        "payload_snapshot": state["payload_snapshot"],
        "ingestion_context": context,
        "dq_findings": findings,
        "root_cause_summary": state["root_cause_summary"],
        "remediation_plan": state["remediation_plan"],
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }
