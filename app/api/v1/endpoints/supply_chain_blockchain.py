from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.supply_chain_blockchain import (
    BlockchainNetzwerkProfil,
    SupplyChainBlockchainRequest,
    build_supply_chain_blockchain_envelope,
    dispatch_supply_chain_blockchain_envelope,
    get_blockchain_profile_catalog,
)
from app.core.supply_chain_tracking import LieferkettenPhase, TrackingStatusGesamtlage, TransportModus

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/supply-chain/blockchain", tags=["supply-chain", "blockchain", "integrations"])


class SupplyChainBlockchainPrepareBody(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    lieferung_id: str = Field(..., min_length=1)
    event_id: str = Field(..., min_length=1)
    event_typ: str = Field(..., min_length=1)
    aktuelle_phase: LieferkettenPhase
    gesamtlage: TrackingStatusGesamtlage
    transport_modus: TransportModus
    ort: str = Field(..., min_length=1)
    zeitstempel: datetime
    profil: BlockchainNetzwerkProfil
    route_beschreibung: str | None = None
    eta_iso: str | None = None
    alarm_schwere_max: str | None = None
    quell_system: str = "VALEO_NeuroERP"
    fachobjekt_typ: str = "SUPPLY_CHAIN_EVENT"
    metadaten: dict[str, Any] = Field(default_factory=dict)


class SupplyChainBlockchainDispatchBody(SupplyChainBlockchainPrepareBody):
    endpoint_url: str | None = None
    api_key: str | None = None
    timeout_seconds: float = 10.0


def _to_request(body: SupplyChainBlockchainPrepareBody) -> SupplyChainBlockchainRequest:
    return SupplyChainBlockchainRequest(
        tenant_id=body.tenant_id,
        lieferung_id=body.lieferung_id,
        event_id=body.event_id,
        event_typ=body.event_typ,
        aktuelle_phase=body.aktuelle_phase,
        gesamtlage=body.gesamtlage,
        transport_modus=body.transport_modus,
        ort=body.ort,
        zeitstempel=body.zeitstempel,
        route_beschreibung=body.route_beschreibung,
        eta_iso=body.eta_iso,
        alarm_schwere_max=body.alarm_schwere_max,
        quell_system=body.quell_system,
        fachobjekt_typ=body.fachobjekt_typ,
        metadaten=body.metadaten,
    )


@router.get("/profiles", summary="Supply chain blockchain profiles abrufen",
    response_model=CompatFlexOut
)
async def get_supply_chain_blockchain_profiles() -> dict[str, Any]:
    return {
        "profile_count": len(get_blockchain_profile_catalog()),
        "profiles": get_blockchain_profile_catalog(),
    }


@router.post("/prepare", summary="Supply chain blockchain event prepare",
    response_model=CompatFlexOut
)
async def prepare_supply_chain_blockchain_event(body: SupplyChainBlockchainPrepareBody) -> dict[str, Any]:
    return build_supply_chain_blockchain_envelope(_to_request(body), body.profil).as_dict()


@router.post("/dispatch", summary="Supply chain blockchain event dispatch",
    response_model=CompatFlexOut
)
async def dispatch_supply_chain_blockchain_event(body: SupplyChainBlockchainDispatchBody) -> dict[str, Any]:
    envelope = build_supply_chain_blockchain_envelope(_to_request(body), body.profil)
    result = await dispatch_supply_chain_blockchain_envelope(
        envelope=envelope,
        endpoint_url=body.endpoint_url,
        api_key=body.api_key,
        timeout_seconds=body.timeout_seconds,
    )
    return result.as_dict()
