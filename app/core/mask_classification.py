"""
UI-Maskenklassifizierung A/B/C — Wave 3 AP1

Klassifiziert alle Prozessmasken nach ihrer Kritikalitaet:
  A = Kernprozess-Masken (direkte Prozessschritte, Freigabe, Settlement)
  B = Unterstuetzende Masken (Kontrakte, Stammdaten, Qualitaet)
  C = Reporting- und Admin-Masken (Cockpits, Berichte, Konfiguration)
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MaskClass(str, Enum):
    A = "A"   # Kernprozess — direkte Auswirkung auf Buchung, Freigabe, Settlement
    B = "B"   # Unterstuetzend — Datenerfassung, Workflow-Vorbereitung
    C = "C"   # Reporting/Admin — Auswertung, Konfiguration, Stammdaten


class MaskDomain(str, Enum):
    FINANCE = "finance"
    AGRAR = "agrar"
    EINKAUF = "einkauf"
    VERKAUF = "verkauf"
    LAGER = "lager"
    CRM = "crm"
    ADMIN = "admin"
    COMPLIANCE = "compliance"


class ExplainabilityRequirement(str, Enum):
    REQUIRED = "required"       # Maske MUSS Explainability-Block zeigen
    RECOMMENDED = "recommended" # Sollte Explainability zeigen wenn vorhanden
    OPTIONAL = "optional"       # Explainability optional


class MaskClassification(BaseModel):
    """Klassifizierung einer einzelnen ERP-Maske."""

    mask_id: str                          # eindeutige ID, z.B. "finance/ap-invoice-form"
    route: str                            # Frontend-Route, z.B. "/finance/ap/invoices/new"
    label: str                            # Anzeigename
    domain: MaskDomain
    mask_class: MaskClass
    process_key: str | None = None        # zugehoeriger Prozess, z.B. "ap_approval"
    explainability: ExplainabilityRequirement = ExplainabilityRequirement.OPTIONAL
    requires_approval_ui: bool = False    # zeigt Freigabe-/Ablehnen-Buttons
    gobd_relevant: bool = False           # GoBD-Pflicht: Audit-Trail vorhanden?
    wave1_contract: bool = False          # nutzt Wave-1-Contract (semantic_status etc.)
    notes: str | None = None
    schema_version: int = 1


class MaskRegistry(BaseModel):
    """Vollstaendiges Register aller klassifizierten Masken."""

    masks: list[MaskClassification] = Field(default_factory=list)
    schema_version: int = 1

    def get_by_class(self, mask_class: MaskClass) -> list[MaskClassification]:
        return [m for m in self.masks if m.mask_class == mask_class]

    def get_by_domain(self, domain: MaskDomain) -> list[MaskClassification]:
        return [m for m in self.masks if m.domain == domain]

    def get(self, mask_id: str) -> MaskClassification | None:
        return next((m for m in self.masks if m.mask_id == mask_id), None)

    def class_a_without_wave1_contract(self) -> list[MaskClassification]:
        """Klasse-A-Masken, die noch keinen Wave-1-Contract haben — technische Schulden."""
        return [m for m in self.masks if m.mask_class == MaskClass.A and not m.wave1_contract]


# ---------------------------------------------------------------------------
# Produktives Masken-Register fuer VALEO NeuroERP 3.0
# ---------------------------------------------------------------------------

def build_mask_registry() -> MaskRegistry:
    """Liefert das vollstaendige klassifizierte Masken-Register."""

    masks = [
        # ── KLASSE A: Kernprozess-Masken ────────────────────────────────────

        MaskClassification(
            mask_id="finance/ap-invoice-form",
            route="/finance/ap/invoices/new",
            label="Eingangsrechnung erfassen",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.A,
            process_key="ap_approval",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="finance/ap-invoices-list",
            route="/finance/ap/invoices",
            label="Eingangsrechnungen Liste",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.A,
            process_key="ap_approval",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="finance/zahlungslauf-kreditoren",
            route="/finance/zahlungslauf-kreditoren",
            label="Zahlungslauf Kreditoren",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.A,
            process_key="payment_run",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="finance/lastschriften-debitoren",
            route="/finance/lastschriften-debitoren",
            label="Lastschriften Debitoren",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.A,
            process_key="direct_debit",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="finance/abschluss",
            route="/finance/abschluss",
            label="Periodenabschluss-Arbeitsplatz",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.A,
            process_key="closing_checklist",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="annahme/abrechnung",
            route="/annahme/abrechnung",
            label="Ernte-Annahme Abrechnung",
            domain=MaskDomain.AGRAR,
            mask_class=MaskClass.A,
            process_key="harvest_acceptance",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="annahme/qualitaets-check",
            route="/annahme/qualitaets-check",
            label="Qualitaetspruefung Annahme",
            domain=MaskDomain.AGRAR,
            mask_class=MaskClass.A,
            process_key="quality_protocol",
            explainability=ExplainabilityRequirement.REQUIRED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),

        # ── KLASSE B: Unterstuetzende Masken ────────────────────────────────

        MaskClassification(
            mask_id="einkauf/rechnungseingang",
            route="/einkauf/rechnungseingang",
            label="Rechnungseingang",
            domain=MaskDomain.EINKAUF,
            mask_class=MaskClass.B,
            process_key="ap_approval",
            explainability=ExplainabilityRequirement.RECOMMENDED,
            requires_approval_ui=False,
            gobd_relevant=True,
            wave1_contract=False,
            notes="Vorstufe zur AP-Invoice-Erfassung",
        ),
        MaskClassification(
            mask_id="finance/mahnwesen",
            route="/finance/mahnwesen",
            label="Mahnwesen",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.B,
            explainability=ExplainabilityRequirement.RECOMMENDED,
            gobd_relevant=True,
            wave1_contract=False,
        ),
        MaskClassification(
            mask_id="finance/ustva",
            route="/export/ustva",
            label="UStVA Voranmeldung",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.B,
            process_key="vat_return",
            explainability=ExplainabilityRequirement.RECOMMENDED,
            requires_approval_ui=True,
            gobd_relevant=True,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="agrar/kontrakte",
            route="/agrar/kontrakte",
            label="Agrar-Kontrakte",
            domain=MaskDomain.AGRAR,
            mask_class=MaskClass.B,
            explainability=ExplainabilityRequirement.OPTIONAL,
            gobd_relevant=True,
            wave1_contract=False,
        ),
        MaskClassification(
            mask_id="workflow/sandbox",
            route="/workflow/sandbox",
            label="Workflow-Sandbox",
            domain=MaskDomain.ADMIN,
            mask_class=MaskClass.B,
            explainability=ExplainabilityRequirement.RECOMMENDED,
            wave1_contract=True,
        ),
        MaskClassification(
            mask_id="policy-manager",
            route="/policy-manager",
            label="Policy-Manager",
            domain=MaskDomain.ADMIN,
            mask_class=MaskClass.B,
            explainability=ExplainabilityRequirement.REQUIRED,
            wave1_contract=True,
        ),

        # ── KLASSE C: Reporting und Admin ───────────────────────────────────

        MaskClassification(
            mask_id="finance/index",
            route="/finance",
            label="Finance Uebersicht",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.C,
            explainability=ExplainabilityRequirement.OPTIONAL,
            wave1_contract=True,
            notes="Cockpit — Read-Model-Daten",
        ),
        MaskClassification(
            mask_id="finance/reports",
            route="/finance/reports",
            label="Finanzberichte",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.C,
            gobd_relevant=True,
            wave1_contract=False,
        ),
        MaskClassification(
            mask_id="finance/audit-trail",
            route="/finance/audit-trail",
            label="GoBD Audit-Trail",
            domain=MaskDomain.FINANCE,
            mask_class=MaskClass.C,
            gobd_relevant=True,
            wave1_contract=False,
        ),
        MaskClassification(
            mask_id="admin/compliance-dashboard",
            route="/admin/compliance",
            label="Compliance-Dashboard",
            domain=MaskDomain.COMPLIANCE,
            mask_class=MaskClass.C,
            explainability=ExplainabilityRequirement.OPTIONAL,
            wave1_contract=False,
        ),
        MaskClassification(
            mask_id="agrar/feldbuch",
            route="/agrar/feldbuch",
            label="Feldbuch",
            domain=MaskDomain.AGRAR,
            mask_class=MaskClass.C,
            wave1_contract=False,
        ),
    ]

    return MaskRegistry(masks=masks)
