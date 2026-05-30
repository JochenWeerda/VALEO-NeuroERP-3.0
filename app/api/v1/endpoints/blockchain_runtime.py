from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.blockchain_anchor_contracts import (
    BlockchainNetzwerkProfil,
    BlockchainObjektTyp,
    build_blockchain_anchor,
)
from app.core.database import get_db
from app.repositories.blockchain_anchor_repository import BlockchainAnchorRepository

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.blockchain_runtime_schemas import BlockchainRuntimeOut


router = APIRouter(prefix="/blockchain", tags=["blockchain", "audit", "integrations"])


class CreateBlockchainAnchorRequest(BaseModel):
    tenant_id: str
    subject_type: str
    subject_ref: str
    payload: dict[str, Any]
    private_payload: dict[str, Any] | None = None
    network_profile: str = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED.value
    channel_name: str | None = None
    chaincode_name: str | None = None
    private_data_collection: str | None = None
    member_orgs: list[str] | None = None
    remote_source_name: str | None = None
    virtual_table_name: str | None = None
    oauth_credential_ref: str | None = None


@router.post("/anchors", summary="Blockchain anchor anlegen",
    response_model=BlockchainRuntimeOut
)
def create_blockchain_anchor(payload: CreateBlockchainAnchorRequest, db=Depends(get_db)):
    try:
        subject_type = BlockchainObjektTyp(payload.subject_type.strip().upper())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unbekannter subject_type") from exc
    try:
        network_profile = BlockchainNetzwerkProfil(payload.network_profile.strip().upper())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unbekanntes network_profile") from exc

    anchor = build_blockchain_anchor(
        tenant_id=payload.tenant_id,
        subject_type=subject_type,
        subject_ref=payload.subject_ref,
        payload=payload.payload,
        private_payload=payload.private_payload,
        network_profile=network_profile,
        channel_name=payload.channel_name,
        chaincode_name=payload.chaincode_name,
        private_data_collection=payload.private_data_collection,
        member_orgs=payload.member_orgs,
        remote_source_name=payload.remote_source_name,
        virtual_table_name=payload.virtual_table_name,
        oauth_credential_ref=payload.oauth_credential_ref,
    )
    saved = BlockchainAnchorRepository(db).save(anchor)
    return saved.as_dict()


@router.get("/anchors", summary="Blockchain anchors auflisten",
    response_model=BlockchainRuntimeOut
)
def list_blockchain_anchors(
    tenant_id: str | None = None,
    subject_type: str | None = None,
    network_profile: str | None = None,
    limit: int = 50,
    db=Depends(get_db),
):
    items = BlockchainAnchorRepository(db).list(
        tenant_id=tenant_id,
        subject_type=subject_type,
        network_profile=network_profile,
        limit=limit,
    )
    return {
        "items": [item.as_dict() for item in items],
        "total": len(items),
        "filters": {
            "tenant_id": tenant_id,
            "subject_type": subject_type,
            "network_profile": network_profile,
            "limit": limit,
        },
    }


@router.get("/anchors/{anchor_id}", summary="Blockchain anchor abrufen",
    response_model=BlockchainRuntimeOut
)
def get_blockchain_anchor(anchor_id: str, db=Depends(get_db)):
    item = BlockchainAnchorRepository(db).get(anchor_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Anchor nicht gefunden")
    return item.as_dict()
