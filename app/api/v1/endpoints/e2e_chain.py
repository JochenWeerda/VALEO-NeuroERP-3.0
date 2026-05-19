from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.e2e_chain import E2EProcessChain, ChainCompletenessReport
from app.domains.operations.models import E2EProcessChainDB

router = APIRouter(prefix="/process/e2e", tags=["process", "e2e", "chain"])


def _db_to_chain(row: E2EProcessChainDB) -> E2EProcessChain:
    data = dict(row.chain_data or {})
    data.setdefault("tenant_id", row.tenant_id)
    data.setdefault("settlement_id", row.settlement_id)
    data.setdefault("contract_id", row.contract_id)
    return E2EProcessChain.model_validate(data)


@router.post("/chains", response_model=E2EProcessChain, status_code=201,
             summary="E2E-Prozesskette anlegen")
def create_chain(body: E2EProcessChain, db: Session = Depends(get_db)) -> E2EProcessChain:
    row = E2EProcessChainDB(
        tenant_id=body.tenant_id,
        settlement_id=body.settlement_id,
        contract_id=body.contract_id,
        ernte_annahme_id=body.ernte_annahme_id if hasattr(body, "ernte_annahme_id") else None,
        chain_data=body.model_dump(),
        is_complete=body.is_complete,
        completeness_pct=body.completeness_pct,
    )
    db.add(row)
    db.commit()
    return body


@router.get("/chains/{tenant_id}", response_model=list[E2EProcessChain],
            summary="Alle Ketten eines Tenants")
def list_chains(tenant_id: str, db: Session = Depends(get_db)) -> list[E2EProcessChain]:
    rows = db.query(E2EProcessChainDB).filter(E2EProcessChainDB.tenant_id == tenant_id).all()
    return [_db_to_chain(r) for r in rows]


@router.get("/chains/{tenant_id}/completeness", response_model=ChainCompletenessReport,
            summary="Vollstaendigkeitsbericht fuer einen Tenant")
def get_completeness(tenant_id: str, db: Session = Depends(get_db)) -> ChainCompletenessReport:
    rows = db.query(E2EProcessChainDB).filter(E2EProcessChainDB.tenant_id == tenant_id).all()
    tenant_chains = [_db_to_chain(r) for r in rows]
    return ChainCompletenessReport.build(tenant_id=tenant_id, chains=tenant_chains)


@router.put("/chains/{chain_id}", response_model=E2EProcessChain,
            summary="E2E-Kette aktualisieren")
def update_chain(chain_id: str, body: E2EProcessChain, db: Session = Depends(get_db)) -> E2EProcessChain:
    row = db.query(E2EProcessChainDB).filter(
        (E2EProcessChainDB.settlement_id == chain_id) |
        (E2EProcessChainDB.contract_id == chain_id)
    ).first()
    if not row:
        # Nicht gefunden → neu anlegen (Upsert-Semantik beibehalten)
        row = E2EProcessChainDB(
            tenant_id=body.tenant_id,
            settlement_id=body.settlement_id,
            contract_id=body.contract_id,
            chain_data=body.model_dump(),
            is_complete=body.is_complete,
            completeness_pct=body.completeness_pct,
        )
        db.add(row)
    else:
        row.chain_data = body.model_dump()
        row.is_complete = body.is_complete
        row.completeness_pct = body.completeness_pct
        row.settlement_id = body.settlement_id
        row.contract_id = body.contract_id
    db.commit()
    return body
