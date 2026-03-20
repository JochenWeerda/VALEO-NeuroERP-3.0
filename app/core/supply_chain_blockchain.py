"""
Supply Chain Blockchain Interface
Externe Ledger-/Blockchain-Schnittstelle fuer Lieferkettenprozesse.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import httpx

from app.core.supply_chain_tracking import LieferkettenPhase, TrackingStatusGesamtlage, TransportModus


class BlockchainNetzwerkProfil(str, Enum):
    SAP_BTP_LEDGER = "SAP_BTP_LEDGER"
    ORACLE_BLOCKCHAIN_PLATFORM = "ORACLE_BLOCKCHAIN_PLATFORM"
    HYPERLEDGER_FABRIC = "HYPERLEDGER_FABRIC"


class BlockchainDispatchStatus(str, Enum):
    PREPARED = "PREPARED"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SupplyChainBlockchainRequest:
    lieferung_id: str
    tenant_id: str
    event_id: str
    event_typ: str
    aktuelle_phase: LieferkettenPhase
    gesamtlage: TrackingStatusGesamtlage
    transport_modus: TransportModus
    ort: str
    zeitstempel: datetime
    route_beschreibung: str | None = None
    eta_iso: str | None = None
    alarm_schwere_max: str | None = None
    quell_system: str = "VALEO_NeuroERP"
    fachobjekt_typ: str = "SUPPLY_CHAIN_EVENT"
    metadaten: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SupplyChainBlockchainEnvelope:
    profil: BlockchainNetzwerkProfil
    anchor_hash: str
    external_reference: str
    canonical_payload: dict[str, Any]
    adapter_payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "profil": self.profil.value,
            "anchor_hash": self.anchor_hash,
            "external_reference": self.external_reference,
            "canonical_payload": self.canonical_payload,
            "adapter_payload": self.adapter_payload,
        }


@dataclass(frozen=True)
class SupplyChainBlockchainDispatchResult:
    status: BlockchainDispatchStatus
    envelope: SupplyChainBlockchainEnvelope
    endpoint: str | None = None
    response_status_code: int | None = None
    response_body: dict[str, Any] | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "endpoint": self.endpoint,
            "response_status_code": self.response_status_code,
            "response_body": self.response_body,
            "error": self.error,
            "envelope": self.envelope.as_dict(),
        }


def get_blockchain_profile_catalog() -> list[dict[str, Any]]:
    return [
        {
            "profil": BlockchainNetzwerkProfil.SAP_BTP_LEDGER.value,
            "branchenstandard": "sap",
            "zielbild": "SAP-nahe Business Event Anchors fuer BTP-/Ledger-Adapter",
        },
        {
            "profil": BlockchainNetzwerkProfil.ORACLE_BLOCKCHAIN_PLATFORM.value,
            "branchenstandard": "oracle",
            "zielbild": "Oracle Blockchain Platform Event Payload fuer revisionsfaehige Lieferkettenevents",
        },
        {
            "profil": BlockchainNetzwerkProfil.HYPERLEDGER_FABRIC.value,
            "branchenstandard": "fabric",
            "zielbild": "Fabric Chaincode Event/Asset Payload fuer permissioned Netzwerke",
        },
    ]


def _canonical_payload(req: SupplyChainBlockchainRequest) -> dict[str, Any]:
    return {
        "tenant_id": req.tenant_id,
        "lieferung_id": req.lieferung_id,
        "event_id": req.event_id,
        "event_typ": req.event_typ,
        "fachobjekt_typ": req.fachobjekt_typ,
        "aktuelle_phase": req.aktuelle_phase.value,
        "gesamtlage": req.gesamtlage.value,
        "transport_modus": req.transport_modus.value,
        "ort": req.ort,
        "zeitstempel": req.zeitstempel.isoformat(),
        "route_beschreibung": req.route_beschreibung,
        "eta_iso": req.eta_iso,
        "alarm_schwere_max": req.alarm_schwere_max,
        "quell_system": req.quell_system,
        "metadaten": req.metadaten,
    }


def _hash_payload(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _build_adapter_payload(
    req: SupplyChainBlockchainRequest,
    profil: BlockchainNetzwerkProfil,
    anchor_hash: str,
) -> dict[str, Any]:
    if profil == BlockchainNetzwerkProfil.SAP_BTP_LEDGER:
        return {
            "businessObjectType": req.fachobjekt_typ,
            "businessObjectId": req.lieferung_id,
            "businessEventId": req.event_id,
            "eventType": req.event_typ,
            "tenantId": req.tenant_id,
            "phase": req.aktuelle_phase.value,
            "status": req.gesamtlage.value,
            "anchorHash": anchor_hash,
            "sourceSystem": req.quell_system,
            "recordedAt": req.zeitstempel.isoformat(),
            "location": req.ort,
            "transportMode": req.transport_modus.value,
            "routeDescription": req.route_beschreibung,
            "metadata": req.metadaten,
        }
    if profil == BlockchainNetzwerkProfil.ORACLE_BLOCKCHAIN_PLATFORM:
        return {
            "recordType": req.fachobjekt_typ,
            "recordId": req.event_id,
            "deliveryId": req.lieferung_id,
            "tenantId": req.tenant_id,
            "eventType": req.event_typ,
            "currentPhase": req.aktuelle_phase.value,
            "overallStatus": req.gesamtlage.value,
            "sha256": anchor_hash,
            "sourceSystem": req.quell_system,
            "timestamp": req.zeitstempel.isoformat(),
            "location": req.ort,
            "transportMode": req.transport_modus.value,
            "eta": req.eta_iso,
            "severity": req.alarm_schwere_max,
            "metadata": req.metadaten,
        }
    return {
        "assetType": req.fachobjekt_typ,
        "assetId": req.event_id,
        "deliveryId": req.lieferung_id,
        "tenantId": req.tenant_id,
        "channel": "supply-chain",
        "eventType": req.event_typ,
        "phase": req.aktuelle_phase.value,
        "status": req.gesamtlage.value,
        "hash": anchor_hash,
        "sourceSystem": req.quell_system,
        "eventTimestamp": req.zeitstempel.isoformat(),
        "location": req.ort,
        "transportMode": req.transport_modus.value,
        "privateData": {
            "eta": req.eta_iso,
            "routeDescription": req.route_beschreibung,
            "maxSeverity": req.alarm_schwere_max,
            "metadata": req.metadaten,
        },
    }


def build_supply_chain_blockchain_envelope(
    req: SupplyChainBlockchainRequest,
    profil: BlockchainNetzwerkProfil,
) -> SupplyChainBlockchainEnvelope:
    canonical_payload = _canonical_payload(req)
    anchor_hash = _hash_payload(canonical_payload)
    external_reference = f"{req.tenant_id}:{req.lieferung_id}:{req.event_id}"
    adapter_payload = _build_adapter_payload(req, profil, anchor_hash)
    return SupplyChainBlockchainEnvelope(
        profil=profil,
        anchor_hash=anchor_hash,
        external_reference=external_reference,
        canonical_payload=canonical_payload,
        adapter_payload=adapter_payload,
    )


async def dispatch_supply_chain_blockchain_envelope(
    envelope: SupplyChainBlockchainEnvelope,
    endpoint_url: str | None,
    api_key: str | None = None,
    timeout_seconds: float = 10.0,
) -> SupplyChainBlockchainDispatchResult:
    if not endpoint_url:
        return SupplyChainBlockchainDispatchResult(
            status=BlockchainDispatchStatus.PREPARED,
            endpoint=None,
            envelope=envelope,
        )

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                endpoint_url,
                json={
                    "reference": envelope.external_reference,
                    "profile": envelope.profil.value,
                    "payload": envelope.adapter_payload,
                },
                headers=headers,
            )
        try:
            parsed = response.json()
            body = parsed if isinstance(parsed, dict) else {"data": parsed}
        except ValueError:
            body = {"raw": response.text}
        return SupplyChainBlockchainDispatchResult(
            status=BlockchainDispatchStatus.DISPATCHED if response.is_success else BlockchainDispatchStatus.FAILED,
            endpoint=endpoint_url,
            response_status_code=response.status_code,
            response_body=body,
            error=None if response.is_success else f"upstream returned {response.status_code}",
            envelope=envelope,
        )
    except Exception as exc:  # pragma: no cover
        return SupplyChainBlockchainDispatchResult(
            status=BlockchainDispatchStatus.FAILED,
            endpoint=endpoint_url,
            error=str(exc),
            envelope=envelope,
        )
