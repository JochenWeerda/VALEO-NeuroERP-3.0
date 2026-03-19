"""
Compliance Copilot Workflow
AI-Agent to ensure regulatory compliance (PSM, ENNI, TRACES, etc.)
"""

from typing import Annotated, List, TypedDict, Dict, Any
import operator
from datetime import datetime, timedelta

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

import logging

logger = logging.getLogger(__name__)


# State Definition
class ComplianceCopilotState(TypedDict):
    """State for compliance checking workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    entity_type: str  # "customer", "article", "transaction"
    entity_id: str
    entity_data: Dict[str, Any]
    compliance_checks: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    risk_score: float  # 0-1
    current_stage_key: str
    stage_transition_log: List[Dict[str, Any]]
    gate_decisions: List[Dict[str, Any]]


def _mark_stage(state: ComplianceCopilotState, stage_key: str, detail: str) -> None:
    state["current_stage_key"] = stage_key
    state["stage_transition_log"].append(
        {
            "stage_key": stage_key,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": detail,
        }
    )


def _set_policy_gate(state: ComplianceCopilotState, status: str, reason: str) -> None:
    state["gate_decisions"] = [
        decision for decision in state.get("gate_decisions", []) if decision.get("gate_type") != "policy_gate"
    ]
    state["gate_decisions"].append(
        {
            "gate_type": "policy_gate",
            "status": status,
            "reason": reason,
            "required_role": None,
            "schema_version": 1,
        }
    )


# Compliance Check Definitions
COMPLIANCE_RULES = {
    "psm": {
        "name": "Pflanzenschutzmittel-Gesetz",
        "applies_to": ["customer", "article"],
        "checks": [
            "sachkundenachweis_required",
            "verkaufsdokumentation",
            "bvl_reporting"
        ]
    },
    "explosivstoff": {
        "name": "Explosivstoff-Verordnung (Düngemittel)",
        "applies_to": ["customer", "article"],
        "checks": [
            "erlaubnispflichtig",
            "lagerung_dokumentiert",
            "mengenbegrenzung"
        ]
    },
    "enni": {
        "name": "ENNI Düngemittel-Reporting",
        "applies_to": ["transaction"],
        "checks": [
            "enni_export_complete",
            "npk_calculation_correct",
            "quarterly_reporting"
        ]
    },
    "traces": {
        "name": "TRACES-NT Intra-EU",
        "applies_to": ["transaction"],
        "checks": [
            "traces_notification",
            "veterinary_certificate",
            "eu_compliant"
        ]
    }
}


# Workflow Nodes
def identify_applicable_rules(state: ComplianceCopilotState) -> dict:
    """Identify which compliance rules apply to this entity."""
    _mark_stage(state, "analysis", "Identify applicable compliance rules")
    logger.info(
        f"Identifying compliance rules for {state['entity_type']}..."
    )
    
    applicable_checks = []
    
    for rule_id, rule in COMPLIANCE_RULES.items():
        if state["entity_type"] in rule["applies_to"]:
            applicable_checks.append({
                "rule_id": rule_id,
                "rule_name": rule["name"],
                "checks": rule["checks"]
            })
    
    logger.info(f"Found {len(applicable_checks)} applicable rule sets")
    
    return {
        "compliance_checks": applicable_checks,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
    }


def run_compliance_checks(state: ComplianceCopilotState) -> dict:
    """Execute compliance checks."""
    logger.info("Running compliance checks...")
    _mark_stage(state, "analysis", "Run compliance checks")
    
    violations = []
    entity_data = state["entity_data"]
    
    for check in state["compliance_checks"]:
        rule_id = check["rule_id"]
        
        # PSM Check
        if rule_id == "psm" and state["entity_type"] == "customer":
            if not entity_data.get("psm_sachkundenachweis"):
                violations.append({
                    "rule": "PSM Sachkundenachweis",
                    "severity": "high",
                    "message": "Kunde hat keinen PSM-Sachkundenachweis "
                               "hinterlegt",
                    "action": "Nachweis anfordern oder PSM-Verkauf sperren"
                })
        
        # Explosivstoff Check
        if rule_id == "explosivstoff" and state["entity_type"] == "article":
            if entity_data.get("category") == "Düngemittel":
                if not entity_data.get("explosivstoff_konform"):
                    violations.append({
                        "rule": "Explosivstoff-VO",
                        "severity": "critical",
                        "message": "Düngemittel ohne Konformitätsnachweis",
                        "action": "Konformitätsprüfung durchführen"
                    })
        
        # ENNI Check
        if rule_id == "enni" and state["entity_type"] == "transaction":
            if not entity_data.get("enni_export_done"):
                violations.append({
                    "rule": "ENNI Export",
                    "severity": "medium",
                    "message": "Düngemittel-Transaktion nicht an ENNI "
                               "gemeldet",
                    "action": "ENNI-Export durchführen"
                })
    
    # Calculate risk score
    risk_score = min(len(violations) * 0.25, 1.0)
    
    logger.info(f"Found {len(violations)} violations (risk: {risk_score})")
    
    _mark_stage(state, "proposal", "Build compliance findings and risk proposal")
    _set_policy_gate(
        state,
        "blocked" if violations else "allowed",
        "Policy findings require follow-up before approval." if violations else "No blocking compliance findings detected.",
    )

    return {
        "violations": violations,
        "risk_score": risk_score,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }


def generate_recommendations(state: ComplianceCopilotState) -> dict:
    """Generate recommendations based on violations."""
    _mark_stage(state, "closure", "Generate compliance recommendations and close run")
    recommendations = []
    
    if not state["violations"]:
        recommendations.append("✅ Keine Compliance-Verstöße gefunden")
        return {
            "recommendations": recommendations,
            "current_stage_key": state["current_stage_key"],
            "stage_transition_log": state["stage_transition_log"],
            "gate_decisions": state["gate_decisions"],
        }
    
    critical = [v for v in state["violations"] if v["severity"] == "critical"]
    high = [v for v in state["violations"] if v["severity"] == "high"]
    
    if critical:
        recommendations.append(
            f"🚨 {len(critical)} kritische Verstöße müssen "
            f"SOFORT behoben werden"
        )
    
    if high:
        recommendations.append(
            f"⚠️ {len(high)} schwere Verstöße innerhalb "
            f"7 Tagen beheben"
        )
    
    # Specific actions
    for violation in state["violations"]:
        recommendations.append(f"• {violation['rule']}: {violation['action']}")
    
    return {
        "recommendations": recommendations,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }


# Build Workflow
def build_compliance_workflow():
    """Build the compliance checking workflow."""
    workflow = StateGraph(ComplianceCopilotState)
    
    workflow.add_node("identify_rules", identify_applicable_rules)
    workflow.add_node("run_checks", run_compliance_checks)
    workflow.add_node("generate_recs", generate_recommendations)
    
    workflow.set_entry_point("identify_rules")
    workflow.add_edge("identify_rules", "run_checks")
    workflow.add_edge("run_checks", "generate_recs")
    workflow.add_edge("generate_recs", END)
    
    return workflow.compile()


# Execute workflow
async def check_compliance(
    entity_type: str,
    entity_id: str,
    entity_data: Dict[str, Any]
) -> dict:
    """Execute compliance checking workflow."""
    workflow = build_compliance_workflow()
    
    initial_state = ComplianceCopilotState(
        messages=[HumanMessage(content="Check Compliance")],
        entity_type=entity_type,
        entity_id=entity_id,
        entity_data=entity_data,
        compliance_checks=[],
        violations=[],
        recommendations=[],
        risk_score=0.0,
        current_stage_key="intake",
        stage_transition_log=[
            {
                "stage_key": "intake",
                "timestamp": datetime.utcnow().isoformat(),
                "detail": "Compliance workflow run created",
            }
        ],
        gate_decisions=[],
    )
    
    result = workflow.invoke(initial_state)
    
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "violations": result["violations"],
        "risk_score": result["risk_score"],
        "recommendations": result["recommendations"],
        "checked_at": datetime.utcnow().isoformat(),
        "current_stage_key": result["current_stage_key"],
        "stage_transition_log": result["stage_transition_log"],
        "gate_decisions": result["gate_decisions"],
    }

