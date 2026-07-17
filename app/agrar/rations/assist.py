"""Deterministische Assistenz-Proposals (FEED-AI-046, Vertrag 11-agenten.md).

Reine Builder-Funktionen ohne Persistenz und ohne Modellaufruf: die Assistenz
verdichtet Ergebnisse der versionierten Rechendienste (FEED-AI-003) in das
Proposal-Schema aus Kap. 11 §3.1. Jede Aussage traegt Evidenzreferenzen und
Unsicherheit; fehlende Daten werden als Annahme benannt, nie geschaetzt
(FEED-AI-009). requires_human_approval ist immer True (FEED-AI-004).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4

RULESET = "GFE_2023_DLG_2025"

# Historientiefe, ab der die Ursachenanalyse als datengestuetzt gilt.
HISTORY_SUFFICIENT_N = 7

# Handlungsrichtungen je Befund-Code (Kap. 9 Berechnungsregeln / DLG 01|2023):
# fachliche Richtungen ohne Zahlenerfindung — Mengen entscheidet der Berater.
_PLAYBOOK: dict[str, str] = {
    "dmi_below_band": "Rationsmenge erhoehen oder schmackhaftere/energiereichere "
                      "Komponenten waehlen, bis die Ziel-TM-Aufnahme erreicht ist.",
    "dmi_above_band": "Gesamtmenge reduzieren oder TM-Band des Bedarfsprofils pruefen.",
    "energy_deficit": "Energiereiche Komponenten (z. B. Maissilage, Getreide) erhoehen "
                      "oder ergaenzen; Grenzen der Positionen pruefen.",
    "energy_surplus": "Energiedichte senken (Grobfutteranteil erhoehen) — Kosten und "
                      "Verfettungsrisiko pruefen.",
    "protein_deficit": "Proteintraeger (z. B. Rapsschrot, Sojaschrot) erhoehen oder "
                       "ergaenzen; sidP-Beitraege der Analysen pruefen.",
    "protein_surplus": "Proteinueberhang reduzieren — N-Effizienz und Harnstoffwerte "
                       "beobachten.",
}


def build_explain_proposal(*, group_id: str, evaluation: dict[str, Any],
                           history_n: int) -> dict[str, Any]:
    """Erklaer-Assistent: Befunde der deterministischen Bewertung als Fakten,
    Abhilfen als Empfehlungen; Datenlage bestimmt die Konfidenz."""
    facts = [{
        "kind": "finding",
        "code": finding["code"],
        "severity": finding["severity"],
        "metric": finding["metric"],
        "message": finding["message"],
        "evidence": f"draft-evaluation:{evaluation['requirement_profile_id']}",
    } for finding in evaluation["findings"]]

    recommendations = [{
        "for_finding": finding["code"],
        "action": finding["remediation"],
        "source": "deterministic_remediation",
    } for finding in evaluation["findings"] if finding.get("remediation")]
    # Fachliches Playbook fuer Kennzahl-Befunde ohne strukturelle Abhilfe —
    # deterministische Handlungsrichtungen, keine erfundenen Zahlenwerte.
    for finding in evaluation["findings"]:
        if finding.get("remediation"):
            continue
        action = _PLAYBOOK.get(finding["code"])
        if action:
            recommendations.append({
                "for_finding": finding["code"],
                "action": action,
                "source": "deterministic_playbook",
            })

    assumptions: list[str] = []
    incomplete = [metric for metric, state in (evaluation.get("coverage") or {}).items()
                  if not state.get("complete", True)]
    if incomplete:
        assumptions.append(
            "Analysewerte unvollstaendig fuer: " + ", ".join(sorted(incomplete))
            + " — Teilsummen nur aus bekannten Beitraegen.")
    if history_n < HISTORY_SUFFICIENT_N:
        assumptions.append(
            f"Controlling-Historie umfasst nur {history_n} Beobachtungen "
            f"(unter {HISTORY_SUFFICIENT_N}) — Ursachenanalyse ohne belastbaren Trendkontext.")

    confidence = "medium" if history_n >= HISTORY_SUFFICIENT_N and not incomplete else "low"

    return {
        "proposal_id": f"prop_{uuid4().hex}",
        "agent": "ration_advisor",
        "objective": "Befunde der Rationsbewertung erklaeren und Abhilfen priorisieren",
        "scope": {"group_id": group_id},
        "facts": facts,
        "assumptions": assumptions,
        "recommendations": recommendations,
        "evidence_refs": [
            f"requirement-profile:{evaluation['requirement_profile_id']}",
            f"controlling-history:n={history_n}",
        ],
        "ruleset": RULESET,
        "confidence": confidence,
        "risks": [],
        "proposed_commands": [],
        "requires_human_approval": True,
    }


def build_measure_proposal(*, findings: list[dict[str, Any]],
                           existing_component_ids: set[str],
                           owner_subject: str) -> dict[str, Any]:
    """Massnahmenvorschlaege als bestaetigungspflichtige Kommandos fuer den
    bestehenden idempotenten Massnahmen-Vertrag — nichts wird committed."""
    commands: list[dict[str, Any]] = []
    for finding in findings:
        if finding.get("severity") not in {"warning", "critical"}:
            continue
        component_id = str(finding.get("actual_component_id") or "")
        if not component_id or component_id in existing_component_ids:
            continue
        feed_name = finding.get("feed_name") or finding.get("feed_id") or "Komponente"
        commands.append({
            "command": "create_actual_measure",
            "endpoint": "/feeding/actuals/measures",
            "payload": {
                "actual_component_id": component_id,
                "title": f"Abweichung {feed_name} pruefen",
                "owner_subject": owner_subject,
                "due_date": str(date.today() + timedelta(days=3)),
                "reason": finding.get("remedy") or finding.get("message")
                or "Abweichung fachlich nachverfolgen.",
                "idempotency_key": f"assist-measure-{component_id}",
            },
            "evidence": {
                "finding_message": finding.get("message"),
                "severity": finding.get("severity"),
                "policy_version": finding.get("policy_version"),
            },
        })

    return {
        "proposal_id": f"prop_{uuid4().hex}",
        "agent": "controlling_agent",
        "objective": "Offene Abweichungsbefunde in nachverfolgbare Massnahmen ueberfuehren",
        "scope": {},
        "facts": [{
            "kind": "finding_count",
            "message": f"{len(commands)} offene Abweichungsbefunde ohne Massnahme.",
        }],
        "assumptions": [],
        "recommendations": [],
        "evidence_refs": [f"deviation-finding:{c['payload']['actual_component_id']}"
                          for c in commands],
        "ruleset": RULESET,
        "confidence": "medium" if commands else "low",
        "risks": [],
        "proposed_commands": commands,
        "requires_human_approval": True,
    }


def build_substitute_candidates(*, source: dict[str, Any],
                                candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Ersatzfuttermittel gleicher Klasse, nach Preis sortiert; fehlende
    Analysen werden als Unsicherheit benannt statt geschaetzt."""
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        price = candidate.get("price_eur_t")
        analysis_complete = bool(candidate.get("has_energy_analysis"))
        rows.append({
            "feed_id": candidate["id"],
            "name": candidate["name"],
            "feed_kind": candidate["feed_kind"],
            "price_eur_t": float(price) if price is not None else None,
            "price_provenance": ("feed-catalog:preis_pro_t" if price is not None else None),
            "analysis_complete": analysis_complete,
            "uncertainty": (None if analysis_complete else
                            "Keine Energie-Analyse hinterlegt — Austauschwirkung "
                            "auf die Ration ist ohne Analyse nicht bewertbar."),
        })
    rows.sort(key=lambda row: (row["price_eur_t"] is None, row["price_eur_t"] or 0.0))
    return {
        "feed_id": source["id"],
        "feed_name": source["name"],
        "feed_kind": source["feed_kind"],
        "restriction": "gleiche Futterklasse (feed_kind), nur freigegebene Futter",
        "candidates": rows,
        "requires_human_approval": True,
    }
