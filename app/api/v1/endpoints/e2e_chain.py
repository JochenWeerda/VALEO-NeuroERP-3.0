from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.core.e2e_chain import E2EProcessChain, ChainCompletenessReport

router = APIRouter(prefix="/process/e2e", tags=["process", "e2e", "chain"])

# In-Memory-Store fuer E2E-Ketten
_CHAINS: list[E2EProcessChain] = []


@router.post("/chains", response_model=E2EProcessChain, status_code=201,
             summary="E2E-Prozesskette anlegen")
def create_chain(body: E2EProcessChain) -> E2EProcessChain:
    """Erstellt eine neue E2E-Prozesskette und speichert sie im In-Memory-Store."""
    _CHAINS.append(body)
    return body


@router.get("/chains/{tenant_id}", response_model=list[E2EProcessChain],
            summary="Alle Ketten eines Tenants")
def list_chains(tenant_id: str) -> list[E2EProcessChain]:
    """Gibt alle E2E-Prozessketten fuer den angegebenen Tenant zurueck."""
    return [c for c in _CHAINS if c.tenant_id == tenant_id]


@router.get("/chains/{tenant_id}/completeness", response_model=ChainCompletenessReport,
            summary="Vollstaendigkeitsbericht fuer einen Tenant")
def get_completeness(tenant_id: str) -> ChainCompletenessReport:
    """Gibt einen Vollstaendigkeitsbericht ueber alle E2E-Ketten eines Tenants zurueck."""
    tenant_chains = [c for c in _CHAINS if c.tenant_id == tenant_id]
    return ChainCompletenessReport.build(tenant_id=tenant_id, chains=tenant_chains)


@router.put("/chains/{chain_id}", response_model=E2EProcessChain,
            summary="E2E-Kette aktualisieren")
def update_chain(chain_id: str, body: E2EProcessChain) -> E2EProcessChain:
    """
    Aktualisiert eine bestehende E2E-Prozesskette (z.B. ap_invoice_id nachtraegen).
    chain_id wird mit settlement_id oder contract_id abgeglichen.
    """
    for idx, chain in enumerate(_CHAINS):
        anchor = chain.settlement_id or chain.contract_id
        if anchor == chain_id or (chain.tenant_id == body.tenant_id and anchor == chain_id):
            _CHAINS[idx] = body
            return body
    # Fallback: Kette nicht gefunden → als neue anlegen
    raise HTTPException(status_code=404, detail=f"Chain with id '{chain_id}' not found.")
