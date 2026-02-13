from datetime import datetime

from modules.agrar.contracts.events_v1 import (
    ContractAllocatedV1,
    SettlementIssuedV1,
    WeighingTicketCreatedV1,
)
from modules.agrar.contracts.hooks_v1 import AGRAR_HOOK_CONTRACTS_V1


def test_weighing_ticket_contract_has_stable_event_type():
    event = WeighingTicketCreatedV1(
        event_id="evt-1",
        aggregate_id="wt-1",
        tenant_id="tenant-1",
        occurred_at=datetime.utcnow(),
        ticket_number="WT-10001",
        gross_weight_kg=42000,
        tare_weight_kg=12000,
        net_weight_kg=30000,
    )
    assert event.event_type == "agrar.weighing_ticket.created"
    assert event.event_version == "1.0.0"


def test_contract_allocated_contract_is_fixed_schema():
    payload = ContractAllocatedV1(
        event_id="evt-2",
        aggregate_id="alloc-1",
        tenant_id="tenant-1",
        occurred_at=datetime.utcnow(),
        contract_id="ctr-1",
        contract_number="K-2026-001",
        allocation_quantity_kg=25000,
        remaining_quantity_kg=75000,
        pricing_model="follow",
    )
    assert payload.event_type == "agrar.contract.allocated"
    assert payload.pricing_model in {"fixed", "follow", "pool"}


def test_settlement_contract_and_hooks_are_consistent():
    settlement = SettlementIssuedV1(
        event_id="evt-3",
        aggregate_id="set-1",
        tenant_id="tenant-1",
        occurred_at=datetime.utcnow(),
        settlement_id="set-1",
        settlement_number="GS-2026-001",
        base_quantity_kg=30000,
        billable_quantity_kg=29000,
        gross_amount=7250.0,
        deductions_amount=180.5,
        net_amount=7069.5,
    )
    assert settlement.event_type == "agrar.settlement.issued"
    assert any(hook.hook_name == settlement.event_type for hook in AGRAR_HOOK_CONTRACTS_V1)

