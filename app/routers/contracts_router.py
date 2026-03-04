"""
Verträge-API für Frontend contracts-v2.
Angebunden an AgrarContract (domain_inventory), Rahmenvertrag (domain_ops) und ContractAmendment (domain_shared).
Liefert das von der Maske erwartete Format { items: [...] } in camelCase.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models import AgrarContract, ContractAmendment, AmendmentTemplate
from app.domains.operations.repository import RahmenvertragRepository
from app.domains.operations.models import KonContract

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


class AmendmentCreate(BaseModel):
    contractId: Optional[str] = Field(None, alias="contractId")
    tenantId: Optional[str] = Field(None, alias="tenantId")
    type: str = Field("amendment")
    reason: str = Field(..., min_length=10)
    changes: dict[str, Any] = Field(default_factory=dict)
    createdBy: Optional[str] = Field(None, alias="createdBy")

    model_config = {"populate_by_name": True}


def _dt_iso(d: Optional[datetime]) -> str:
    if d is None:
        return ""
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def _agrar_to_item(c: AgrarContract) -> dict[str, Any]:
    """AgrarContract → Frontend-Contract (camelCase)."""
    valid_from = getattr(c, "valid_from", None)
    valid_until = getattr(c, "valid_until", None)
    return {
        "id": c.id,
        "sourceType": "agrar",
        "contractNo": c.contract_number,
        "type": getattr(c, "contract_type", "sell"),
        "commodity": getattr(c, "article_id", ""),
        "counterpartyId": c.partner_id,
        "status": c.status,
        "qty": {
            "contracted": float(c.total_quantity_kg) if c.total_quantity_kg is not None else 0,
            "unit": "kg",
        },
        "deliveryWindow": {
            "from": _dt_iso(valid_from),
            "to": _dt_iso(valid_until),
        },
        "createdAt": _dt_iso(getattr(c, "created_at", None)),
        "updatedAt": _dt_iso(getattr(c, "updated_at", None)),
    }


def _rahmen_to_item(v: Any) -> dict[str, Any]:
    """Rahmenvertrag → Frontend-Contract (camelCase)."""
    laufzeit = getattr(v, "laufzeit_bis", None)
    return {
        "id": v.id,
        "sourceType": "rahmen",
        "contractNo": v.nummer,
        "type": getattr(v, "typ", ""),
        "commodity": getattr(v, "artikel_id", "") or getattr(v, "artikel", ""),
        "counterpartyId": getattr(v, "partner_id", ""),
        "status": getattr(v, "status", "aktiv"),
        "qty": {
            "contracted": float(v.menge) if getattr(v, "menge", None) is not None else 0,
            "unit": "Stk",
        },
        "deliveryWindow": {
            "from": "",
            "to": _dt_iso(laufzeit) if laufzeit else "",
        },
        "createdAt": _dt_iso(getattr(v, "created_at", None)),
        "updatedAt": _dt_iso(getattr(v, "updated_at", None)),
    }


def _amendment_to_item(a: ContractAmendment) -> dict[str, Any]:
    """ContractAmendment → Frontend-Amendment (camelCase)."""
    return {
        "id": a.id,
        "contractId": a.contract_id,
        "type": a.type or "",
        "reason": a.reason or "",
        "status": a.status or "pending",
        "changes": a.changes if isinstance(a.changes, dict) else {},
        "createdAt": _dt_iso(getattr(a, "created_at", None)),
    }


def _template_to_item(t: AmendmentTemplate) -> dict[str, Any]:
    """AmendmentTemplate → Frontend (camelCase)."""
    return {
        "id": t.id,
        "code": t.code,
        "name": t.name,
        "description": t.description or "",
        "bodyMarkdown": t.body_markdown or "",
        "sectionsSchema": t.sections_schema if isinstance(t.sections_schema, dict) else {},
        "isActive": getattr(t, "is_active", True),
        "createdAt": _dt_iso(getattr(t, "created_at", None)),
    }


# --- Amendment-Templates (vor /{contract_id} definieren) ---

@router.get("/amendment-templates")
async def list_amendment_templates(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, alias="activeOnly"),
) -> dict[str, Any]:
    """Liste aller Nachtrag-Vorlagen (z. B. EHB/EB-Nachtrag)."""
    q = db.query(AmendmentTemplate)
    if active_only:
        q = q.filter(AmendmentTemplate.is_active.is_(True))
    items = q.order_by(AmendmentTemplate.code).all()
    return {"items": [_template_to_item(t) for t in items]}


@router.get("/amendment-templates/{code}")
async def get_amendment_template(
    code: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Eine Vorlage nach Code (z. B. EHBEB_NACHTRAG)."""
    t = db.query(AmendmentTemplate).filter(AmendmentTemplate.code == code).first()
    if not t:
        raise HTTPException(status_code=404, detail="Amendment template not found")
    return _template_to_item(t)


def _kon_to_item(k: KonContract) -> dict[str, Any]:
    return {
        "id": k.contract_id,
        "sourceType": "kon",
        "contractNo": k.contract_no,
        "type": k.contract_type,
        "commodity": "",
        "counterpartyId": k.party_id,
        "status": (k.status or "OFFEN").lower(),
        "qty": {
            "contracted": float(k.total_quantity) if k.total_quantity is not None else 0,
            "unit": k.unit or "kg",
        },
        "deliveryWindow": {
            "from": _dt_iso(k.valid_from),
            "to": _dt_iso(k.valid_to),
        },
        "createdAt": _dt_iso(getattr(k, "created_at", None)),
        "updatedAt": _dt_iso(getattr(k, "updated_at", None)),
    }


@router.get("")
async def list_contracts(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    Liste Verträge: AgrarContract (tenant) + Rahmenvertrag, einheitlich für contracts-v2.
    """
    items: list[dict[str, Any]] = []

    # AgrarContract (domain_inventory)
    q = db.query(AgrarContract).filter(AgrarContract.tenant_id == tenant_id)
    if status:
        q = q.filter(AgrarContract.status == status)
    for c in q.order_by(AgrarContract.created_at.desc()).limit(limit).all():
        items.append(_agrar_to_item(c))

    # Valeo Kontrakte (domain_ops)
    kq = db.query(KonContract).filter(KonContract.tenant_id == tenant_id)
    if status:
        kq = kq.filter(KonContract.status == status.upper())
    for k in kq.order_by(KonContract.updated_at.desc()).limit(limit).all():
        items.append(_kon_to_item(k))

    # Rahmenverträge (domain_ops) – begrenzt hinzufügen, damit Gesamtlimit ungefähr eingehalten wird
    repo = RahmenvertragRepository(db)
    rahmen = repo.get_all(limit=limit, status=status)
    for v in rahmen:
        items.append(_rahmen_to_item(v))

    # Nach updatedAt/createdAt sortieren (neueste zuerst)
    items.sort(
        key=lambda x: (x.get("updatedAt") or x.get("createdAt") or ""),
        reverse=True,
    )
    return {"items": items[:limit]}


@router.get("/{contract_id}")
async def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Einzelvertrag nach ID (Agrar oder Rahmenvertrag)."""
    if contract_id.startswith("RV-"):
        repo = RahmenvertragRepository(db)
        vertrag = repo.get_by_id(contract_id)
        if not vertrag:
            raise HTTPException(status_code=404, detail="Contract not found")
        return _rahmen_to_item(vertrag)

    kon = (
        db.query(KonContract)
        .filter(KonContract.contract_id == contract_id, KonContract.tenant_id == tenant_id)
        .first()
    )
    if kon:
        return _kon_to_item(kon)

    contract = (
        db.query(AgrarContract)
        .filter(AgrarContract.id == contract_id, AgrarContract.tenant_id == tenant_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return _agrar_to_item(contract)


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Vertrag löschen (Rahmenvertrag) oder 404 (Agrar-Storno über cancel)."""
    if contract_id.startswith("RV-"):
        repo = RahmenvertragRepository(db)
        if not repo.delete(contract_id):
            raise HTTPException(status_code=404, detail="Contract not found")
        return {"ok": True}

    contract = (
        db.query(AgrarContract)
        .filter(AgrarContract.id == contract_id, AgrarContract.tenant_id == tenant_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    db.delete(contract)
    db.commit()
    return {"ok": True}


@router.post("/{contract_id}/cancel")
async def cancel_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Vertrag stornieren (Status auf cancelled bzw. storniert)."""
    if contract_id.startswith("RV-"):
        repo = RahmenvertragRepository(db)
        vertrag = repo.get_by_id(contract_id)
        if not vertrag:
            raise HTTPException(status_code=404, detail="Contract not found")
        vertrag.status = "storniert"
        db.commit()
        db.refresh(vertrag)
        return _rahmen_to_item(vertrag)

    contract = (
        db.query(AgrarContract)
        .filter(AgrarContract.id == contract_id, AgrarContract.tenant_id == tenant_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract.status = "cancelled"
    db.commit()
    db.refresh(contract)
    return _agrar_to_item(contract)


@router.get("/{contract_id}/amendments")
async def list_amendments(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Änderungshistorie zu einem Vertrag (ContractAmendment)."""
    rows = (
        db.query(ContractAmendment)
        .filter(
            ContractAmendment.contract_id == contract_id,
            ContractAmendment.tenant_id == tenant_id,
        )
        .order_by(ContractAmendment.created_at.desc())
        .all()
    )
    return {"items": [_amendment_to_item(a) for a in rows]}


@router.post("/{contract_id}/amendments")
async def create_amendment(
    contract_id: str,
    body: AmendmentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Amendment anlegen und zurückgeben (camelCase)."""
    tid = body.tenantId or tenant_id
    if len(body.reason.strip()) < 10:
        raise HTTPException(status_code=400, detail="reason must be at least 10 characters")
    amendment = ContractAmendment(
        id=uuid7(),
        contract_id=contract_id,
        type=body.type or "amendment",
        reason=body.reason.strip(),
        status="pending",
        changes=body.changes or {},
        tenant_id=tid,
        created_by=body.createdBy,
    )
    db.add(amendment)
    db.commit()
    db.refresh(amendment)
    return _amendment_to_item(amendment)
