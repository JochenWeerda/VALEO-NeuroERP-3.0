"""
Audit-Evidence-Modell — Wave 3 AP2

Verknuepft Audit-Log-Eintraege mit DMS-Dokumenten (Paperless-ngx)
und OCR-Belegnachweisen fuer GoBD-konforme Dokumentation.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSourceSystem(str, Enum):
    PAPERLESS_NGX = "paperless_ngx"   # DMS: Paperless-ngx
    UPLOAD = "upload"                  # direkter Datei-Upload
    OCR_PIPELINE = "ocr_pipeline"     # automatisierte OCR-Extraktion
    EDI = "edi"                        # elektronischer Datenaustausch
    EMAIL = "email"                    # E-Mail-Anhang
    SCAN = "scan"                      # manueller Scan


class EvidenceType(str, Enum):
    INVOICE_SCAN = "invoice_scan"           # gescannte Eingangsrechnung
    DELIVERY_NOTE = "delivery_note"         # Lieferschein
    WEIGHING_TICKET = "weighing_ticket"     # Wiegebon
    QUALITY_LAB_REPORT = "quality_lab_report"  # Laborausdruck
    APPROVAL_CONFIRMATION = "approval_confirmation"  # Freigabebeleg
    CONTRACT_DOCUMENT = "contract_document"  # Vertragsdokument
    PAYMENT_PROOF = "payment_proof"         # Zahlungsnachweis
    SEPA_MANDATE = "sepa_mandate"           # SEPA-Mandat
    CUSTOMS_DOCUMENT = "customs_document"   # Zolldokument
    CORRECTION_NOTE = "correction_note"     # Korrekturbeleg


class EvidenceReference(BaseModel):
    """Referenz auf ein externes Dokument als Beleg fuer einen Auditvorgang."""

    evidence_id: str
    source_system: EvidenceSourceSystem
    evidence_type: EvidenceType
    external_id: str                          # ID im Quellsystem (z.B. Paperless doc_id)
    filename: str | None = None
    page_count: int | None = None
    ocr_confidence: float | None = None       # 0.0-1.0 OCR-Qualitaet
    verified: bool = False                    # manuell geprueft?
    verified_by: str | None = None
    verified_at: str | None = None
    schema_version: int = 1


class AuditEvidenceEntry(BaseModel):
    """Verknuepfung eines Audit-Log-Eintrags mit einem oder mehreren Belegen."""

    audit_entry_id: str                       # Fremdschluessel zum Audit-Log
    tenant_id: str
    aggregate_type: str                       # z.B. "ap_invoice", "harvest_acceptance"
    aggregate_id: str
    action: str                               # z.B. "approved", "posted", "released"
    evidence_refs: list[EvidenceReference] = Field(default_factory=list)
    gobd_compliant: bool = False              # True wenn mind. 1 verif. Beleg vorhanden
    schema_version: int = 1

    def add_evidence(self, ref: EvidenceReference) -> None:
        self.evidence_refs.append(ref)
        # GoBD-konform wenn mind. 1 verifizierter Beleg vorhanden
        self.gobd_compliant = any(r.verified for r in self.evidence_refs)

    def primary_evidence(self) -> EvidenceReference | None:
        """Gibt den ersten verifizierten Beleg zurueck, sonst den ersten verfuegbaren."""
        verified = [r for r in self.evidence_refs if r.verified]
        return verified[0] if verified else (self.evidence_refs[0] if self.evidence_refs else None)


class DocumentEvidencePolicy(BaseModel):
    """Richtlinie welche Vorgaenge zwingend einen Dokumentenbeleg benoetigen."""

    tenant_id: str
    required_evidence_for: list[str] = Field(default_factory=list)
    # z.B. ["ap_invoice.approved", "harvest_acceptance.released", "payment_run.executed"]
    gobd_retention_check: bool = True         # prueft Aufbewahrungsfristen
    ocr_min_confidence: float = 0.75          # Mindest-OCR-Qualitaet fuer automatische Anerkennung
    schema_version: int = 1

    def requires_evidence(self, aggregate_type: str, action: str) -> bool:
        key = f"{aggregate_type}.{action}"
        return key in self.required_evidence_for


def build_default_evidence_policy(tenant_id: str) -> DocumentEvidencePolicy:
    """GoBD-konforme Standard-Belegpflicht fuer Landhandel."""
    return DocumentEvidencePolicy(
        tenant_id=tenant_id,
        required_evidence_for=[
            "ap_invoice.approved",
            "ap_invoice.posted",
            "payment_run.executed",
            "harvest_acceptance.released",
            "closing_checklist.closed",
        ],
        gobd_retention_check=True,
        ocr_min_confidence=0.75,
    )
