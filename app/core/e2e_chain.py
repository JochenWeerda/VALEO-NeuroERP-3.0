from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.core.settlement_compatibility import to_canonical_settlement_aggregate


class E2EChainLink(BaseModel):
    """Ein Glied in der E2E-Prozesskette."""
    aggregate_type: str     # z.B. "contract", "harvest_acceptance"
    canonical_aggregate_type: str | None = None
    aggregate_id: Optional[str] = None
    present: bool = False   # True wenn ID gesetzt
    schema_version: int = 1


class E2EProcessChain(BaseModel):
    """
    Vollstaendige E2E-Kette: Kontrakt → Annahme → Qualitaet → Settlement → Rechnung → Buchung.
    Jede Wave erweitert den bestehenden ProcessReferenceChain um FiBu-Glieder.
    """
    tenant_id: str
    # Agrar-Kern (aus ProcessReferenceChain)
    contract_id: Optional[str] = None
    harvest_acceptance_id: Optional[str] = None
    weighing_ticket_id: Optional[str] = None
    quality_protocol_id: Optional[str] = None
    settlement_id: Optional[str] = None
    charge_id: Optional[str] = None
    # FiBu-Erweiterung (Wave 5)
    ap_invoice_id: Optional[str] = None
    journal_entry_id: Optional[str] = None
    # Meta
    schema_version: int = 1

    def links(self) -> list[E2EChainLink]:
        return [
            E2EChainLink(aggregate_type="contract", aggregate_id=self.contract_id,
                         canonical_aggregate_type="contract",
                         present=bool(self.contract_id)),
            E2EChainLink(aggregate_type="harvest_acceptance", aggregate_id=self.harvest_acceptance_id,
                         canonical_aggregate_type="harvest_acceptance",
                         present=bool(self.harvest_acceptance_id)),
            E2EChainLink(aggregate_type="quality_protocol", aggregate_id=self.quality_protocol_id,
                         canonical_aggregate_type="quality_protocol",
                         present=bool(self.quality_protocol_id)),
            E2EChainLink(aggregate_type="settlement", aggregate_id=self.settlement_id,
                         canonical_aggregate_type=to_canonical_settlement_aggregate("settlement"),
                         present=bool(self.settlement_id)),
            E2EChainLink(aggregate_type="ap_invoice", aggregate_id=self.ap_invoice_id,
                         canonical_aggregate_type="ap_invoice",
                         present=bool(self.ap_invoice_id)),
            E2EChainLink(aggregate_type="journal_entry", aggregate_id=self.journal_entry_id,
                         canonical_aggregate_type="journal_entry",
                         present=bool(self.journal_entry_id)),
        ]

    def completeness_pct(self) -> int:
        """Anteil vorhandener Kettenglieder in Prozent."""
        lnks = self.links()
        return int(len([line_item for line_item in lnks if line_item.present]) * 100 / len(lnks))

    def missing_links(self) -> list[str]:
        return [line_item.aggregate_type for line_item in self.links() if not line_item.present]

    def is_complete(self) -> bool:
        return all(line_item.present for line_item in self.links())


class ChainCompletenessReport(BaseModel):
    """Bericht ueber Vollstaendigkeit aller E2E-Ketten eines Tenants."""
    tenant_id: str
    total_chains: int
    complete_count: int
    incomplete_count: int
    completeness_pct: int
    gaps: list[dict]        # {"chain_anchor": str, "missing": list[str]}
    schema_version: int = 1

    @classmethod
    def build(cls, tenant_id: str, chains: list[E2EProcessChain]) -> "ChainCompletenessReport":
        complete = [c for c in chains if c.is_complete()]
        incomplete = [c for c in chains if not c.is_complete()]
        gaps = [
            {"chain_anchor": c.settlement_id or c.contract_id or "unknown",
             "missing": c.missing_links()}
            for c in incomplete
        ]
        total = len(chains)
        return cls(
            tenant_id=tenant_id,
            total_chains=total,
            complete_count=len(complete),
            incomplete_count=len(incomplete),
            completeness_pct=(len(complete) * 100 // total) if total > 0 else 0,
            gaps=gaps,
        )
