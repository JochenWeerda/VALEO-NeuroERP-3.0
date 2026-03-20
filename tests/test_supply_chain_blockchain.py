from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.core.supply_chain_blockchain import (
    BlockchainDispatchStatus,
    BlockchainNetzwerkProfil,
    SupplyChainBlockchainRequest,
    build_supply_chain_blockchain_envelope,
    dispatch_supply_chain_blockchain_envelope,
)
from app.core.supply_chain_tracking import LieferkettenPhase, TrackingStatusGesamtlage, TransportModus
from app.main import app

client = TestClient(app)


def _request() -> SupplyChainBlockchainRequest:
    return SupplyChainBlockchainRequest(
        tenant_id="tenant-a",
        lieferung_id="LF-2026-0001",
        event_id="EVT-1",
        event_typ="ETA_UPDATED",
        aktuelle_phase=LieferkettenPhase.TRANSPORT_EINGEHEND,
        gesamtlage=TrackingStatusGesamtlage.LEICHTE_ABWEICHUNG,
        transport_modus=TransportModus.LKW,
        ort="Osnabrueck",
        zeitstempel=datetime(2026, 3, 20, 10, 0, 0),
        route_beschreibung="Hannover -> Osnabrueck -> Muenster",
        eta_iso="2026-03-20T16:00:00",
        alarm_schwere_max="WARNUNG",
        metadaten={"eta_confidence": 82},
    )


def test_build_supply_chain_blockchain_envelope_is_deterministic():
    req = _request()
    envelope_a = build_supply_chain_blockchain_envelope(req, BlockchainNetzwerkProfil.SAP_BTP_LEDGER)
    envelope_b = build_supply_chain_blockchain_envelope(req, BlockchainNetzwerkProfil.SAP_BTP_LEDGER)

    assert envelope_a.anchor_hash == envelope_b.anchor_hash
    assert envelope_a.adapter_payload["businessObjectId"] == "LF-2026-0001"


@pytest.mark.asyncio
async def test_dispatch_without_endpoint_returns_prepared():
    result = await dispatch_supply_chain_blockchain_envelope(
        build_supply_chain_blockchain_envelope(_request(), BlockchainNetzwerkProfil.ORACLE_BLOCKCHAIN_PLATFORM),
        endpoint_url=None,
    )
    assert result.status == BlockchainDispatchStatus.PREPARED


def test_get_profiles_endpoint_returns_catalog():
    response = client.get("/api/v1/supply-chain/blockchain/profiles")
    assert response.status_code == 200
    body = response.json()
    assert body["profile_count"] == 3


def test_prepare_endpoint_returns_profile_specific_payload():
    response = client.post(
        "/api/v1/supply-chain/blockchain/prepare",
        json={
            "tenant_id": "tenant-a",
            "lieferung_id": "LF-2026-0001",
            "event_id": "EVT-1",
            "event_typ": "ETA_UPDATED",
            "aktuelle_phase": "TRANSPORT_EINGEHEND",
            "gesamtlage": "LEICHTE_ABWEICHUNG",
            "transport_modus": "LKW",
            "ort": "Osnabrueck",
            "zeitstempel": "2026-03-20T10:00:00",
            "profil": "HYPERLEDGER_FABRIC",
            "route_beschreibung": "Hannover -> Osnabrueck -> Muenster",
            "eta_iso": "2026-03-20T16:00:00",
            "alarm_schwere_max": "WARNUNG",
            "metadaten": {"eta_confidence": 82},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["profil"] == "HYPERLEDGER_FABRIC"
    assert body["adapter_payload"]["assetType"] == "SUPPLY_CHAIN_EVENT"
    assert body["anchor_hash"]
