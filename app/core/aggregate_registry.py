"""
Aggregate Ownership Register — maschinenlesbarer Vertrag

Jedes Aggregat hat:
- einen klaren fachlichen Besitzer (business_domain)
- die zulässigen Commands (Referenz auf build_core_command_catalog)
- Read-Model-Schlüssel (Referenz auf finance_read_models / projection registry)
- zulässige Agent-Tools
- den kanonischen E2E-Kettenplatz (e2e_chain.py)

Regel: Read Models, APIs und Agent-Tools mappen IMMER von diesem Register aus.
Neue Features müssen an ein registriertes Aggregat anschliessen oder ein neues
Aggregat explizit hier eintragen — kein konkurrierendes Schattenmodell erlaubt.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class AggregateDefinition(BaseModel):
    """Verbindlicher Vertrag für ein Aggregat im System."""
    aggregate_type: str
    business_domain: str            # fachlicher Besitzer z.B. "finance", "agrar"
    description: str
    allowed_commands: list[str]     # command_name aus build_core_command_catalog()
    read_model_keys: list[str]      # Projektionsschlüssel aus finance_read_models
    agent_tools: list[str]          # zulässige Agent-Tool-IDs
    e2e_chain_position: Optional[int] = None   # Reihenfolge in E2EProcessChain.links()
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Kanonisches Register
# ---------------------------------------------------------------------------

_AGGREGATE_REGISTRY: list[AggregateDefinition] = [
    AggregateDefinition(
        aggregate_type="ap_invoice",
        business_domain="finance",
        description="Kreditorenrechnung — Kernbeleg im Rechnungseingangsworkflow",
        allowed_commands=["ApproveAPInvoice", "RejectAPInvoice", "PostAPInvoice"],
        read_model_keys=["ap-invoice-cockpit"],
        agent_tools=["ap_invoice_lookup", "ap_invoice_approval_check"],
        e2e_chain_position=5,
    ),
    AggregateDefinition(
        aggregate_type="harvest_acceptance",
        business_domain="agrar",
        description="Ernte-Annahme — Wareneingang aus Landhandel-Prozesskette",
        allowed_commands=["FinalizeHarvestAcceptance"],
        read_model_keys=[],
        agent_tools=["harvest_acceptance_lookup"],
        e2e_chain_position=2,
    ),
    AggregateDefinition(
        aggregate_type="quality_protocol",
        business_domain="agrar",
        description="Qualitätsprotokoll — Laborergebnis zur Ernte-Annahme",
        allowed_commands=["ReleaseQualityProtocol"],
        read_model_keys=[],
        agent_tools=["quality_protocol_lookup"],
        e2e_chain_position=3,
    ),
    AggregateDefinition(
        aggregate_type="agrar_settlement",
        business_domain="agrar",
        description="Agrar-Abrechnung — Preisermittlung und Abschluss zur Annahme",
        allowed_commands=["CreateAgrarSettlement", "FinalizeAgrarSettlement"],
        read_model_keys=[],
        agent_tools=["settlement_lookup"],
        e2e_chain_position=4,
    ),
    AggregateDefinition(
        aggregate_type="payment_run",
        business_domain="finance",
        description="Zahlungslauf — Kreditoren-Sammellauf; ausschliesslich Human-Kontrolle",
        allowed_commands=["ExecutePaymentRun"],
        read_model_keys=["payment-run-cockpit"],
        agent_tools=[],          # blockiert: requires_human_confirmation
        e2e_chain_position=None,
    ),
    AggregateDefinition(
        aggregate_type="direct_debit_run",
        business_domain="finance",
        description="Lastschriftlauf — SEPA-Debitoren-Sammellauf; ausschliesslich Human-Kontrolle",
        allowed_commands=["ExecuteDirectDebit"],
        read_model_keys=[],
        agent_tools=[],          # blockiert: requires_human_confirmation
        e2e_chain_position=None,
    ),
    AggregateDefinition(
        aggregate_type="purchase_order",
        business_domain="einkauf",
        description="Einkaufsbestellung aus dispositionellem Bestellvorschlag oder manueller Beschaffung",
        allowed_commands=["CreatePurchaseOrder"],
        read_model_keys=[],
        agent_tools=["purchase_order_lookup"],
        e2e_chain_position=None,
    ),
    AggregateDefinition(
        aggregate_type="contract",
        business_domain="agrar",
        description="Agrar-Kontrakt — Wurzelbeleg der E2E-Prozesskette",
        allowed_commands=[],
        read_model_keys=[],
        agent_tools=["contract_lookup"],
        e2e_chain_position=1,
    ),
    AggregateDefinition(
        aggregate_type="journal_entry",
        business_domain="finance",
        description="Buchungssatz — FiBu-Abschluss der E2E-Prozesskette",
        allowed_commands=[],
        read_model_keys=[],
        agent_tools=["journal_entry_lookup"],
        e2e_chain_position=6,
    ),
]

_REGISTRY_INDEX: dict[str, AggregateDefinition] = {
    agg.aggregate_type: agg for agg in _AGGREGATE_REGISTRY
}


# ---------------------------------------------------------------------------
# Öffentliche API
# ---------------------------------------------------------------------------

def get_aggregate_registry() -> list[AggregateDefinition]:
    """Gibt das vollständige Aggregate-Register zurück."""
    return list(_AGGREGATE_REGISTRY)


def get_aggregate_definition(aggregate_type: str) -> AggregateDefinition:
    """
    Gibt die Definition eines Aggregats zurück.
    Wirft KeyError wenn das Aggregat nicht registriert ist — kein stilles None.
    """
    if aggregate_type not in _REGISTRY_INDEX:
        raise KeyError(
            f"Aggregat '{aggregate_type}' ist nicht im Register. "
            "Neues Aggregat muss explizit in aggregate_registry.py eingetragen werden."
        )
    return _REGISTRY_INDEX[aggregate_type]


def get_aggregates_by_domain(domain: str) -> list[AggregateDefinition]:
    """Alle Aggregate eines fachlichen Besitzers."""
    return [agg for agg in _AGGREGATE_REGISTRY if agg.business_domain == domain]


def get_read_model_owner(read_model_key: str) -> AggregateDefinition | None:
    """Welches Aggregat ist Besitzer dieses Read-Model-Schlüssels?"""
    for agg in _AGGREGATE_REGISTRY:
        if read_model_key in agg.read_model_keys:
            return agg
    return None


def get_command_owner(command_name: str) -> AggregateDefinition | None:
    """Welches Aggregat ist Besitzer dieses Commands?"""
    for agg in _AGGREGATE_REGISTRY:
        if command_name in agg.allowed_commands:
            return agg
    return None


def validate_command_aggregate_consistency(
    command_name: str, aggregate_type: str
) -> bool:
    """
    Prüft ob ein Command zum angegebenen Aggregat-Typ passt.
    Gibt True zurück wenn konsistent, False wenn Fehlanpassung.
    """
    owner = get_command_owner(command_name)
    if owner is None:
        return False
    return owner.aggregate_type == aggregate_type
