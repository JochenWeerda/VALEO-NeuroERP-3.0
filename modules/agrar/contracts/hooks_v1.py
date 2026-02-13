"""
Versioned hook contracts for module integration points (v1).
"""

from dataclasses import asdict, dataclass
from typing import List


HOOK_CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class HookContractV1:
    hook_name: str
    version: str
    producer: str
    consumers: List[str]
    payload_schema_ref: str
    description: str


AGRAR_HOOK_CONTRACTS_V1: List[HookContractV1] = [
    HookContractV1(
        hook_name="agrar.weighing_ticket.created",
        version=HOOK_CONTRACT_VERSION,
        producer="modules.agrar.weighing",
        consumers=["inventory", "compliance", "settlement"],
        payload_schema_ref="modules/agrar/contracts/events_v1.py#WeighingTicketCreatedV1",
        description="Initial hook fired when a weighing ticket is finalized.",
    ),
    HookContractV1(
        hook_name="agrar.contract.allocated",
        version=HOOK_CONTRACT_VERSION,
        producer="modules.agrar.contracts",
        consumers=["settlement", "risk", "reporting"],
        payload_schema_ref="modules/agrar/contracts/events_v1.py#ContractAllocatedV1",
        description="Hook fired when quantity is allocated against a contract.",
    ),
    HookContractV1(
        hook_name="agrar.settlement.issued",
        version=HOOK_CONTRACT_VERSION,
        producer="modules.agrar.settlement",
        consumers=["finance", "portal", "compliance"],
        payload_schema_ref="modules/agrar/contracts/events_v1.py#SettlementIssuedV1",
        description="Hook fired when a self-billing settlement is issued.",
    ),
]


def agrar_hooks_as_dict() -> List[dict]:
    return [asdict(item) for item in AGRAR_HOOK_CONTRACTS_V1]

