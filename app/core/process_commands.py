"""
Shared process command catalog for the Wave-1 kernel path.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.settlement_compatibility import (
    CANONICAL_SETTLEMENT_AGGREGATE,
    CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
)


class ProcessCommandDefinition(BaseModel):
    command_id: str = Field(min_length=3)
    aggregate: str = Field(min_length=1)
    canonical_aggregate: str | None = None
    canonical_process_definition_key: str | None = None
    intent: str = Field(min_length=1)
    mutating: bool = True
    idempotent: bool = False
    ui_surfaces: list[str] = Field(default_factory=list)
    backend_endpoints: list[str] = Field(default_factory=list)
    result_model: str | None = None
    error_model: str | None = None


DEFAULT_PROCESS_COMMANDS: list[ProcessCommandDefinition] = [
    ProcessCommandDefinition(
        command_id="contract.create",
        aggregate="contract",
        intent="Kontrakt anlegen",
        ui_surfaces=["contracts", "agrar/contracts"],
        backend_endpoints=["POST /api/v1/agrar/contracts/"],
        result_model="AgrarContractOut",
    ),
    ProcessCommandDefinition(
        command_id="contract.update",
        aggregate="contract",
        intent="Kontrakt ändern oder stornieren",
        ui_surfaces=["contracts", "agrar/contracts"],
        backend_endpoints=["PATCH /api/v1/agrar/contracts/{contract_id}"],
        result_model="AgrarContractOut",
    ),
    ProcessCommandDefinition(
        command_id="contract.allocate",
        aggregate="contract",
        intent="Kontraktmenge zuordnen",
        ui_surfaces=["annahme", "contracts"],
        backend_endpoints=["POST /api/v1/agrar/contracts/{contract_id}/allocations"],
        result_model="ContractAllocationOut",
    ),
    ProcessCommandDefinition(
        command_id="acceptance.register",
        aggregate="acceptance",
        intent="LKW oder Anlieferung registrieren",
        ui_surfaces=["annahme/lkw-registrierung"],
        backend_endpoints=["POST /api/v1/annahme/upload", "POST /api/v1/annahme/lkw-registrierung"],
    ),
    ProcessCommandDefinition(
        command_id="acceptance.capture",
        aggregate="acceptance",
        intent="Annahme erfassen oder fortschreiben",
        ui_surfaces=["ernte-annahme-erfassung", "workflow-sandbox"],
        backend_endpoints=["POST /api/v1/harvest-acceptance/", "PUT /api/v1/harvest-acceptance/{acceptance_id}"],
    ),
    ProcessCommandDefinition(
        command_id="acceptance.release",
        aggregate="acceptance",
        intent="Annahme freigeben",
        ui_surfaces=["ernte-annahme-erfassung", "annahme/warteschlange"],
        backend_endpoints=["POST /api/v1/harvest-acceptance/{acceptance_id}/release"],
    ),
    ProcessCommandDefinition(
        command_id="quality.record",
        aggregate="quality-protocol",
        intent="Qualitätsprotokoll erfassen oder aktualisieren",
        ui_surfaces=["annahme/qualitaets-check"],
        backend_endpoints=["POST /api/v1/agrar/quality-protocols", "PUT /api/v1/agrar/quality-protocols/{protocol_id}"],
    ),
    ProcessCommandDefinition(
        command_id="quality.finalize",
        aggregate="quality-protocol",
        intent="Qualitätsprotokoll finalisieren",
        ui_surfaces=["annahme/qualitaets-check"],
        backend_endpoints=["POST /api/v1/agrar/quality-protocols/{protocol_id}/finalize"],
    ),
    ProcessCommandDefinition(
        command_id="settlement.preview",
        aggregate="settlement",
        canonical_aggregate=CANONICAL_SETTLEMENT_AGGREGATE,
        canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
        intent="Abrechnung oder Billing vorrechnen",
        mutating=False,
        idempotent=True,
        ui_surfaces=["annahme/abrechnung"],
        backend_endpoints=["POST /api/v1/agrar/settlements/preview", "POST /api/v1/agrar/settlements/billing-weight/preview"],
        result_model="SettlementPreview",
    ),
    ProcessCommandDefinition(
        command_id="settlement.create",
        aggregate="settlement",
        canonical_aggregate=CANONICAL_SETTLEMENT_AGGREGATE,
        canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
        intent="Settlement anlegen",
        ui_surfaces=["annahme/abrechnung"],
        backend_endpoints=["POST /api/v1/agrar/settlements", "POST /api/v1/harvest-acceptance/{acceptance_id}/calculate"],
        result_model="SettlementOut",
    ),
    ProcessCommandDefinition(
        command_id="settlement.post",
        aggregate="settlement",
        canonical_aggregate=CANONICAL_SETTLEMENT_AGGREGATE,
        canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
        intent="Settlement nach FIBU buchen",
        ui_surfaces=["annahme/abrechnung"],
        backend_endpoints=["POST /api/v1/agrar/settlements/{settlement_id}/post-fibu"],
    ),
    ProcessCommandDefinition(
        command_id="workflow.simulate",
        aggregate="workflow-definition",
        intent="Prozessvariante gegen Stichtag simulieren",
        mutating=False,
        idempotent=True,
        ui_surfaces=["workflow/workflow-sandbox"],
        backend_endpoints=["POST /api/v1/admin/workflow-sandbox/preview"],
        result_model="WorkflowSandboxPreviewOut",
    ),
    ProcessCommandDefinition(
        command_id="policy.evaluate",
        aggregate="policy-decision",
        intent="Policy-Entscheidung mit Explainability berechnen",
        mutating=False,
        idempotent=True,
        ui_surfaces=["policy-manager", "freigabe-ui"],
        backend_endpoints=[],
        result_model="PolicyDecisionView",
    ),
]


def get_process_command_catalog() -> list[ProcessCommandDefinition]:
    return list(DEFAULT_PROCESS_COMMANDS)
