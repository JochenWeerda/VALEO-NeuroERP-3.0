"""
Settlement E2E-Referenzkette — Wave 21 AP6

Vollstaendige, maschinell pruefbare Referenzkette:
Kontrakt → Annahme → Charge → Qualitaet → Settlement → JournalEntry

Schliesst Gap 001 (E2E ohne Medienbruch):
Alle Referenzen sind explizit, keine losen Sonder-IDs,
jede Luecke ist als fehlendes Feld pruefbar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


E2E_SCHEMA_VERSION = 1


@dataclass
class E2ESettlementReference:
    """
    Vollstaendige Referenzkette fuer einen Settlement-Vorgang.

    Jedes Feld entspricht einem Aggregat der kanonischen Prozesskette.
    Fehlende Referenzen (None) sind explizit benannte Luecken.
    """

    settlement_id: str
    tenant_id: str

    # Prozesskette aufwaerts
    kontrakt_id: Optional[str] = None          # Ursprungs-Kontrakt
    annahme_id: Optional[str] = None           # Wareneingangs-/Annahme-ID
    charge_id: Optional[str] = None            # Chargen-ID (Lot)
    qualitaet_id: Optional[str] = None         # Qualitaetsprotokoll-ID
    journal_entry_id: Optional[str] = None     # FiBu-Buchungssatz-ID (nach Verbuchung)

    # Prozessmetadaten
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: int = E2E_SCHEMA_VERSION

    @property
    def complete(self) -> bool:
        """True wenn alle Pflichtreferenzen vorhanden sind (inkl. Buchung)."""
        return all([
            self.kontrakt_id,
            self.annahme_id,
            self.charge_id,
            self.qualitaet_id,
            self.settlement_id,
            self.journal_entry_id,
        ])

    @property
    def missing_refs(self) -> list[str]:
        """Gibt Liste der fehlenden Referenz-Felder zurueck."""
        gaps = []
        if not self.kontrakt_id:
            gaps.append("kontrakt_id")
        if not self.annahme_id:
            gaps.append("annahme_id")
        if not self.charge_id:
            gaps.append("charge_id")
        if not self.qualitaet_id:
            gaps.append("qualitaet_id")
        if not self.journal_entry_id:
            gaps.append("journal_entry_id")
        return gaps

    @property
    def coverage_pct(self) -> float:
        """Prozentualer Abdeckungsgrad der E2E-Kette (0-100)."""
        total = 5  # kontrakt, annahme, charge, qualitaet, journal
        filled = total - len(self.missing_refs)
        return round(filled / total * 100, 1)

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "kontrakt_id": self.kontrakt_id,
            "annahme_id": self.annahme_id,
            "charge_id": self.charge_id,
            "qualitaet_id": self.qualitaet_id,
            "journal_entry_id": self.journal_entry_id,
            "complete": self.complete,
            "missing_refs": self.missing_refs,
            "coverage_pct": self.coverage_pct,
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }


@dataclass
class E2EReferenceValidationResult:
    settlement_id: str
    valid: bool
    missing_refs: list[str]
    coverage_pct: float
    schema_version: int = E2E_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "valid": self.valid,
            "missing_refs": self.missing_refs,
            "coverage_pct": self.coverage_pct,
            "schema_version": self.schema_version,
        }


def build_e2e_reference(
    settlement_id: str,
    tenant_id: str,
    *,
    kontrakt_id: Optional[str] = None,
    annahme_id: Optional[str] = None,
    charge_id: Optional[str] = None,
    qualitaet_id: Optional[str] = None,
    journal_entry_id: Optional[str] = None,
) -> E2ESettlementReference:
    """Baut eine E2E-Referenzkette aus den bekannten Referenzen."""
    return E2ESettlementReference(
        settlement_id=settlement_id,
        tenant_id=tenant_id,
        kontrakt_id=kontrakt_id,
        annahme_id=annahme_id,
        charge_id=charge_id,
        qualitaet_id=qualitaet_id,
        journal_entry_id=journal_entry_id,
    )


def validate_e2e_reference(ref: E2ESettlementReference) -> E2EReferenceValidationResult:
    """Prueft die Vollstaendigkeit der E2E-Kette."""
    return E2EReferenceValidationResult(
        settlement_id=ref.settlement_id,
        valid=ref.complete,
        missing_refs=ref.missing_refs,
        coverage_pct=ref.coverage_pct,
    )
