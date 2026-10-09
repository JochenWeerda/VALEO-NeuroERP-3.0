"""Authenticated ERP adapters; a catalog entry alone never enables execution."""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Any, Literal
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.actual_measures import DeviationPolicyError
from app.agrar.rations.feed_analysis import AnalysisStatus
from app.agrar.rations.lifecycle import RationStatus, TransitionError, validate_transition
from app.api.v1.endpoints.reklamation_api import (
    ReklamationTransitionRequest,
    _query_reklamation,
    transition_status,
)
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.reklamation import ReklamationsStatus, ReklamationZustandsmaschine
from app.services import crm_lead_service
from app.services.crm_kontakt_service import CrmKontaktService
from app.services.document_allocation_service import LineToRegister
from app.services.einkauf_compat_service import EinkaufCompatService, _NICHT_BESTELLBAR
from app.services.feeding_actual_measure_service import (
    ActualMeasureConflict,
    FeedingActualMeasureService,
)
from app.services.feeding_feed_analysis_service import (
    FeedAnalysisConflict,
    FeedAnalysisNotFound,
    FeedingFeedAnalysisService,
)
from app.services.feeding_supply_service import (
    FeedingSupplyConflict,
    FeedingSupplyNotFound,
    FeedingSupplyService,
)
from app.services.inventory_correction_service import CorrectionError, storno_korrektur
from app.services.inventory_movement_direction import signed_quantity
from app.services.inventory_stock_balance import current_stock
from app.services.calendar_projection_service import CalendarProjectionService
from app.services.mask_action_runtime_service import _write_audit
from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from app.services.mobile_sync_service import MobileSyncService
from app.services.procurement_service import ProcurementService
from app.services.production_control_service import ProductionControlService
from app.services.rations_lifecycle_service import (
    RationLifecycleConflict,
    RationLifecycleNotFound,
    RationLifecycleService,
)
from app.services.sales_invoice_service import (
    InvoiceCreationError,
    SalesInvoiceService,
    SourceLine,
)
from app.services.wareneingang_avis_service import (
    WareneingangAvisError,
    buche_wareneingang_aus_avis,
    pruefe_wareneingang,
)

_RATION_MCP_TARGETS: dict[str, RationStatus] = {
    "submit_review": RationStatus.IN_REVIEW,
    "approve": RationStatus.APPROVED,
    "schedule": RationStatus.SCHEDULED,
    "activate": RationStatus.ACTIVE,
    "retire": RationStatus.RETIRED,
    "archive": RationStatus.ARCHIVED,
}


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_name: str
    parameters: dict[str, Any]
    mode: Literal["validate", "dryRun", "propose", "execute"] = "dryRun"
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=200)


class ContactLogInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kunden_nr: str = Field(min_length=1, max_length=20)
    kanal: Literal["telefon", "email", "besuch", "post"]
    ergebnis: str = Field(min_length=1, max_length=10000)
    wiedervorlage_datum: date | None = None


class ActivityCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kunden_nr: str = Field(min_length=1, max_length=20)
    betreff: str = Field(min_length=1, max_length=200)
    typ: Literal["Anruf", "Besuch", "E-Mail", "Aufgabe", "Meeting", "Sonstiges"]
    datum: date | None = None
    notiz: str | None = Field(default=None, max_length=10000)
    verantwortlich: str | None = Field(default=None, max_length=100)


class LeadQualifyInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lead_id: str = Field(min_length=1, max_length=64)
    customer_id: str | None = Field(default=None, max_length=64)
    kunden_nr: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def _require_customer_ref(self) -> LeadQualifyInput:
        if not (self.customer_id or self.kunden_nr):
            raise ValueError("customer_id or kunden_nr is required")
        return self


class BestellungStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    bestellung_id: str = Field(min_length=1, max_length=64)


class BestellungVersendenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    bestellung_id: str = Field(min_length=1, max_length=64)
    versand_art: Literal["email", "fax", "edi", "post", "manuell"] = "email"
    empfaenger: str | None = Field(default=None, max_length=200)


class AngebotBestellenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    angebot_id: str = Field(min_length=1, max_length=64)


class AnlieferavisWareneingangInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    avis_id: str = Field(min_length=1, max_length=64)
    lager_id: str = Field(min_length=1, max_length=64)
    lieferschein_nr: str = Field(min_length=1, max_length=80)


class StockMovementStornierenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    movement_id: str = Field(min_length=1, max_length=64)
    begruendung: str | None = Field(default=None, max_length=500)


class RationTransitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ration_id: str = Field(min_length=1, max_length=80)
    action_key: Literal[
        "submit_review", "approve", "schedule", "activate", "retire", "archive",
    ]
    reason: str | None = Field(default=None, max_length=2000)
    feeding_start: datetime | None = None
    expected_status: str | None = Field(default=None, max_length=40)


class FeedingSupplyHandoffInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    plan_version_id: str = Field(min_length=1, max_length=80)
    feed_id: str = Field(min_length=1, max_length=160)
    reason: str = Field(min_length=10, max_length=2000)
    horizon_days: int = Field(default=30, ge=1, le=365)
    safety_pct: float = Field(default=10, ge=0, le=100)


class FeedingActualMeasureInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    actual_component_id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=3, max_length=240)
    reason: str = Field(min_length=10, max_length=2000)
    due_date: date
    owner_subject: str | None = Field(default=None, max_length=160)


class FeedingConfigureThresholdInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    feed_class: Literal[
        "forage", "concentrate", "mineral", "additive", "byproduct", "liquid", "other"
    ]
    warning_pct: Decimal = Field(gt=0, le=100)
    critical_pct: Decimal = Field(gt=0, le=100)
    valid_from: date
    reason: str = Field(min_length=10, max_length=1000)


class FeedAnalysisTransitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    analysis_id: str = Field(min_length=1, max_length=80)
    action_key: Literal["release", "reject"]
    reason: str = Field(min_length=3, max_length=2000)


class ReklamationAbschliessenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reklamation_id: str = Field(min_length=1, max_length=80)
    kommentar: str | None = Field(default=None, max_length=2000)


class ProduktionControlSyncInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reason: str = Field(min_length=3, max_length=500)


class PlanungCalendarReprojectInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    horizon_days: int = Field(default=120, ge=1, le=366)


class MobileSyncProcessPendingInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    limit: int = Field(default=50, ge=1, le=500)
    reason: str = Field(default="MCP MDE-Verarbeitung", min_length=3, max_length=500)


class SanctionsCheckInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=240)
    scope: Literal["customers", "personal", "manual"]
    entity_ref: str | None = Field(default=None, max_length=120)


class FrachttabelleAnlegenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    tabelle_nr: str = Field(min_length=1, max_length=20)
    bezeichnung: str = Field(min_length=1, max_length=240)
    einheit: str | None = Field(default=None, max_length=20)
    waehrung: str = Field(default="EUR", min_length=1, max_length=3)


class BonusCalculateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    report_id: Literal["bonus-by-customer", "bonus-by-article-group"]
    from_date: date
    to_date: date
    rate_pct: Decimal = Field(gt=0, le=100)
    reason: str = Field(min_length=3, max_length=500)


class QueryImportSignedInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bundle: dict[str, Any]
    reason: str = Field(min_length=5, max_length=500)


class TourAnlegenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    date: datetime | None = None
    vehicle_id: str | None = Field(default=None, max_length=64)
    driver_id: str | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=2000)
    delivery_note_ref: str | None = Field(default=None, max_length=80)
    reason: str = Field(min_length=3, max_length=500)


class BestellungSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    bestellung_id: str = Field(min_length=1, max_length=64)
    lieferdatum_wunsch: date | None = None
    lieferdatum_zugesagt: date | None = None
    ladetermin: date | None = None
    ladetermin_ab: date | None = None
    versand_art: Literal["email", "fax", "edi", "post", "telefon", "manuell"] | None = None
    unsere_referenz: str | None = Field(default=None, max_length=120)
    ihre_referenz: str | None = Field(default=None, max_length=120)
    notiz: str | None = Field(default=None, max_length=4000)
    reason: str = Field(min_length=3, max_length=500)


class BewerbungSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    applicant_name: str = Field(min_length=1, max_length=200)
    applicant_email: str = Field(min_length=3, max_length=200)
    position_title: str | None = Field(default=None, max_length=200)
    source: str | None = Field(default=None, max_length=80)
    reason: str = Field(min_length=3, max_length=500)


class EinwilligungAnlegenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    wortlaut: str = Field(min_length=1, max_length=20000)
    erstellt_durch: str | None = Field(default=None, max_length=120)
    reason: str = Field(min_length=3, max_length=500)


class PostfachSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kennung: str = Field(min_length=1, max_length=80)
    absender_email: str = Field(min_length=3, max_length=200)
    anbieter: Literal["ionos", "google", "microsoft", "smtp", "alias"] = "smtp"
    anmeldung: Literal["passwort", "oauth2"] = "passwort"
    bezeichnung: str | None = Field(default=None, max_length=200)
    absender_name: str | None = Field(default=None, max_length=200)
    postfach_id: str | None = Field(default=None, max_length=64)
    passwort: str | None = Field(default=None, max_length=500)
    smtp_host: str | None = Field(default=None, max_length=200)
    smtp_port: int | None = Field(default=None, ge=1, le=65535)
    reason: str = Field(min_length=3, max_length=500)


class OnboardingSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    employee_ref: str = Field(min_length=1, max_length=120)
    checklist_id: str = Field(min_length=1, max_length=64)
    assigned_by: str | None = Field(default=None, max_length=120)
    due_date: str | None = Field(default=None, max_length=40)
    reason: str = Field(min_length=3, max_length=500)


class QualifikationSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    employee_ref: str = Field(min_length=1, max_length=120)
    role_code: str = Field(min_length=1, max_length=80)
    qualification_level: str = Field(default="basic", max_length=40)
    skills: list[str] | None = None
    valid_until: str | None = Field(default=None, max_length=40)
    reason: str = Field(min_length=3, max_length=500)


class SchulungSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    employee_ref: str = Field(min_length=1, max_length=120)
    course_id: str = Field(min_length=1, max_length=64)
    assigned_by: str | None = Field(default=None, max_length=120)
    due_date: str | None = Field(default=None, max_length=40)
    reason: str = Field(min_length=3, max_length=500)


class FahrzeugSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kennzeichen: str = Field(min_length=2, max_length=20)
    typ: str = Field(min_length=2, max_length=50)
    id: str | None = Field(default=None, max_length=64)
    reason: str = Field(min_length=3, max_length=500)


class FahrzeugLoeschenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    fahrzeug_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=3, max_length=500)


class TerminartSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    terminart: str = Field(min_length=2, max_length=120)
    id: str | None = Field(default=None, max_length=64)
    intervall_monate: int = Field(default=0, ge=0, le=1200)
    intervall_km: int = Field(default=0, ge=0, le=2_000_000)
    reason: str = Field(min_length=3, max_length=500)


class FuhrparkRechnungSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    rechnungs_nr: str = Field(min_length=3, max_length=80)
    datum: str = Field(min_length=4, max_length=40)
    betrag_eur: float = Field(ge=0)
    id: str | None = Field(default=None, max_length=64)
    fahrzeug_kennzeichen: str | None = Field(default=None, max_length=30)
    sachkonto: str | None = Field(default=None, max_length=40)
    kostenart: str | None = Field(default=None, max_length=120)
    notiz: str | None = None
    reason: str = Field(min_length=3, max_length=500)


class AusgehendesDokumentSpeichernInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    beleg_typ: str = Field(min_length=2, max_length=120)
    id: str | None = Field(default=None, max_length=64)
    formular: str | None = Field(default=None, max_length=80)
    ziel_modul: str | None = Field(default=None, max_length=255)
    beschreibung: str | None = None
    aktiv: bool = True
    reason: str = Field(min_length=3, max_length=500)


_FEED_ANALYSIS_TARGETS: dict[str, AnalysisStatus] = {
    "release": AnalysisStatus.RELEASED,
    "reject": AnalysisStatus.REJECTED,
}


class InvoiceProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lieferschein_nr: str = Field(min_length=1, max_length=40)
    rechnungsdatum: date


class InvoicePostInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    proposal_id: str = Field(min_length=1, max_length=36)


class ApInvoiceProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    invoice_id: str = Field(min_length=1, max_length=64)


class ApInvoiceFreigebenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    proposal_id: str = Field(min_length=1, max_length=36)


class InventurOpeningProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    count_id: str = Field(min_length=1, max_length=64)
    reason: str | None = Field(default=None, max_length=500)


class CustomerOpenInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kunden_nr: str = Field(min_length=1, max_length=64)


class CustomerSearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    query: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=20, ge=1, le=50)


class OrderStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    auftrag_nr: str = Field(min_length=1, max_length=64)


class OpenItemsListInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    typ: Literal["forderung", "verbindlichkeit"]
    faellig_bis: date | None = None
    limit: int = Field(default=50, ge=1, le=200)


class LotTraceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lot_id: str = Field(min_length=1, max_length=100)


class CellStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    cell_code: str = Field(min_length=1, max_length=64)


class DocumentSearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    dokument_id: str | None = Field(default=None, max_length=64)
    beleg_ref: str | None = Field(default=None, max_length=120)
    dokument_typ: str | None = Field(default=None, max_length=64)
    von: date | None = None
    bis: date | None = None
    limit: int = Field(default=20, ge=1, le=100)


class GobdExportStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    export_id: str = Field(min_length=1, max_length=64)


class ComplianceGateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    gate_typ: Literal["elster", "datev", "tse", "auditor", "all"] | None = None


class AgrarContractInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kontrakt_id: str = Field(min_length=1, max_length=64)


class WeighingTicketListInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ticket_id: str | None = Field(default=None, max_length=64)
    partie_id: str | None = Field(default=None, max_length=64)
    von: date | None = None
    bis: date | None = None
    limit: int = Field(default=50, ge=1, le=200)


class LagerBestandInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    artikel_id: str = Field(min_length=1, max_length=64)
    lager_id: str | None = Field(default=None, max_length=64)


class InventurStatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lager_id: str | None = Field(default=None, max_length=64)


class BestellungListInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    status: Literal["offen", "teilgeliefert", "abgeschlossen"] | None = None
    limit: int = Field(default=50, ge=1, le=200)


class ProposalListInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    status: Literal["pending", "approved", "rejected", "expired"] | None = None
    limit: int = Field(default=20, ge=1, le=100)


_PO_STATUS_FILTER = {
    "offen": ("open", "offen", "draft", "freigegeben", "bestellt", "ordered"),
    "teilgeliefert": ("partial", "teilgeliefert", "partially_delivered", "teilweise"),
    "abgeschlossen": ("closed", "completed", "abgeschlossen", "geliefert", "posted", "cancelled", "storniert"),
}


_CUSTOMER_SCREEN_ID = "crm/customer-360"
_CUSTOMER_ROUTE_PREFIX = "/crm/customers"
_ORDER_SCREEN_ID = "sales/sales-order"
_ORDER_ROUTE_PREFIX = "/sales/order-editor"
_LOT_SCREEN_ID = "charge/stamm"
_LOT_ROUTE_PREFIX = "/charge/stamm"
_CELL_SCREEN_ID = "lager/silo-cell"
_CELL_ROUTE_PREFIX = "/lager/silo-zellen"
_PO_SCREEN_ID = "einkauf/purchase-order"
_PO_ROUTE_PREFIX = "/einkauf/bestellung"
_DMS_SCREEN_ID = "docflow/nachweisraum"
_DMS_ROUTE_PREFIX = "/docflow/nachweisraum"
_GOBD_SCREEN_ID = "docflow/gobd-export"
_GOBD_ROUTE_PREFIX = "/docflow/gobd-export"
_AGRAR_CONTRACT_SCREEN_ID = "agrar/kontrakte"
_AGRAR_CONTRACT_ROUTE_PREFIX = "/agrar/kontrakt"
_WEIGHING_SCREEN_ID = "waage/wiegeschein"
_WEIGHING_ROUTE_PREFIX = "/waage/wiegeschein"
_STOCK_SCREEN_ID = "lager/article-stock"
_STOCK_ROUTE_PREFIX = "/lager/artikel"
_BILLABLE_DELIVERY_STATUSES = ("posted", "printed", "gebucht")
_ORDER_NEXT_STEP = {
    "open": "Auftrag bestätigen",
    "confirmed": "Lieferschein erstellen",
    "in_delivery": "Auftrag abschließen",
    "completed": "Keine Aktion — Auftrag abgeschlossen",
    "cancelled": "Keine Aktion — Auftrag storniert",
}
_ORDER_TERMINAL_STATUSES = frozenset({"completed", "cancelled", "storniert"})
_OPEN_ITEM_KONTO_TYP = {
    "forderung": "debitoren",
    "verbindlichkeit": "kreditoren",
}


# Nie aus Tool-Parametern akzeptieren — nur Token/Claims.
_FORBIDDEN_PARAMETER_IDENTITY_KEYS = frozenset({
    "tenant_id",
    "mandanten_id",
    "bediener",
    "approval_granted",
})


def _tenant_from_claims(raw: object) -> str | None:
    """Mandanten-ID nur aus verifiziertem Token — nie aus Tool-Parametern.

    Akzeptiert ``tenant_id`` (kanonisch) und ``mandanten_id`` (Alias in manchen
    IdP-Claims). Ein Client-Parameter ``mandanten_id`` bleibt durch
    ``extra=forbid`` und den zentralen Parameter-Guard abgewiesen.
    """
    from app.auth.tenant import tenant_from_claims

    return tenant_from_claims(raw)


def _reject_identity_parameters(parameters: dict[str, Any]) -> None:
    """Top-Level-Identitaetsfelder in Tool-Parametern hart ablehnen (422)."""
    if not isinstance(parameters, dict):
        raise HTTPException(422, "Tool parameters must be an object")
    hit = sorted(_FORBIDDEN_PARAMETER_IDENTITY_KEYS.intersection(parameters))
    if hit:
        raise HTTPException(
            422,
            "Identity or approval fields are not allowed in tool parameters: "
            + ", ".join(hit),
        )


def _customer_in_tenant(db: Session, *, kunden_nr: str, tenant: str) -> dict | None:
    """Operativer CRM-Stamm des authentifizierten Mandanten (kein Cross-Tenant-Fallback)."""
    return db.execute(text("""
        SELECT id::text AS id,
               company_name AS name,
               customer_number AS kunden_nr,
               business_partner_id::text AS business_partner_id
        FROM domain_crm.customers
        WHERE tenant_id::text = :tenant
          AND (customer_number = :customer OR id::text = :customer)
        FOR SHARE
    """), {"customer": kunden_nr, "tenant": tenant}).mappings().first()


def _scalar_or_default(db: Session, sql: str, params: dict, key: str, default: Any) -> Any:
    """Best-effort aggregate read; missing tables/columns yield the default after rollback."""
    try:
        row = db.execute(text(sql), params).mappings().first()
        if not row or row.get(key) is None:
            return default
        return row[key]
    except Exception:
        db.rollback()
        return default


def _first_or_none(db: Session, sql: str, params: dict) -> dict | None:
    """Best-effort single-row read; missing tables/columns yield None after rollback."""
    try:
        row = db.execute(text(sql), params).mappings().first()
        return dict(row) if row else None
    except Exception:
        db.rollback()
        return None


def _rows_or_empty(db: Session, sql: str, params: dict) -> list[dict]:
    try:
        return [dict(row) for row in db.execute(text(sql), params).mappings().all()]
    except Exception:
        db.rollback()
        return []


def execute_mcp_tool(db: Session, request: ToolExecutionRequest, user: dict, tenant_header: str | None) -> dict:
    """Use the verified identity, never a tenant or actor from tool arguments."""
    actor = user.get("sub")
    tenant = _tenant_from_claims(user.get("raw"))
    if not isinstance(actor, str) or not actor.strip() or not isinstance(tenant, str) or not tenant.strip():
        raise HTTPException(403, "Verified subject and tenant_id claims are required")
    if len(actor) > 120 or len(tenant) > 64:
        raise HTTPException(403, "Identity claims exceed the ERP field limits")
    if tenant_header is not None and tenant_header != tenant:
        raise HTTPException(403, "Tenant header does not match the verified token")
    _reject_identity_parameters(request.parameters)
    try:
        tool = mcp_tool_registry_service.get_tool(request.tool_name)
    except KeyError as exc:
        raise HTTPException(404, "Unknown ERP tool") from exc
    if tool["scope"] not in user.get("scopes", []):
        raise HTTPException(403, "Required tool scope is missing")
    # A catalog flag or a client boolean never posts. Only an explicit adapter may write.
    if request.tool_name == "crm.customer.search":
        return _search_customers(db, request, actor, tenant)
    if request.tool_name == "crm.customer.summary360":
        return _customer_summary360(db, request, actor, tenant)
    if request.tool_name == "crm.customer.open":
        return _open_customer(db, request, actor, tenant)
    if request.tool_name == "crm.contact.log":
        return _log_contact(db, request, actor, tenant)
    if request.tool_name == "crm.activity.create":
        return _create_activity(db, request, actor, tenant)
    if request.tool_name == "crm.lead.qualify":
        return _qualify_lead(db, request, actor, tenant)
    if request.tool_name == "sales.order.status":
        return _order_status(db, request, actor, tenant)
    if request.tool_name == "sales.invoice.propose":
        return _propose_invoice(db, request, actor, tenant)
    if request.tool_name == "sales.invoice.post":
        return _post_invoice(db, request, actor, tenant)
    if request.tool_name == "finance.ap_invoice.propose":
        return _propose_ap_freigabe(db, request, actor, tenant)
    if request.tool_name == "finance.ap_invoice.freigeben":
        return _freigeben_ap_invoice(db, request, actor, tenant)
    if request.tool_name == "fibu.open_items.list":
        return _list_open_items(db, request, actor, tenant)
    if request.tool_name == "fibu.dunning.status":
        return _dunning_status(db, request, actor, tenant)
    if request.tool_name == "wms.lot.trace":
        return _lot_trace(db, request, actor, tenant)
    if request.tool_name == "wms.cell.status":
        return _cell_status(db, request, actor, tenant)
    if request.tool_name == "dms.document.search":
        return _document_search(db, request, actor, tenant)
    if request.tool_name == "dms.gobd.export_status":
        return _gobd_export_status(db, request, actor, tenant)
    if request.tool_name == "compliance.gate.status":
        return _compliance_gate_status(db, request, actor, tenant)
    if request.tool_name == "compliance.sanctions.check":
        return _sanctions_check(db, request, actor, tenant)
    if request.tool_name == "logistik.frachttabelle.anlegen":
        return _frachttabelle_anlegen(db, request, actor, tenant)
    if request.tool_name == "logistik.fahrzeug.speichern":
        return _fahrzeug_speichern(db, request, actor, tenant)
    if request.tool_name == "logistik.fahrzeug.loeschen":
        return _fahrzeug_loeschen(db, request, actor, tenant)
    if request.tool_name == "logistik.terminart.speichern":
        return _terminart_speichern(db, request, actor, tenant)
    if request.tool_name == "logistik.rechnung.speichern":
        return _fuhrpark_rechnung_speichern(db, request, actor, tenant)
    if request.tool_name == "logistik.ausgehendes_dokument.speichern":
        return _ausgehendes_dokument_speichern(db, request, actor, tenant)
    if request.tool_name == "reporting.bonus.calculate":
        return _bonus_calculate(db, request, actor, tenant)
    if request.tool_name == "reporting.query.import_signed":
        return _query_import_signed(db, request, actor, tenant)
    if request.tool_name == "logistik.tour.anlegen":
        return _tour_anlegen(db, request, actor, tenant)
    if request.tool_name == "einkauf.bestellung.speichern":
        return _bestellung_speichern(db, request, actor, tenant)
    if request.tool_name == "hr.bewerbung.speichern":
        return _bewerbung_speichern(db, request, actor, tenant)
    if request.tool_name == "hr.einwilligung.anlegen":
        return _einwilligung_anlegen(db, request, actor, tenant)
    if request.tool_name == "hr.onboarding.speichern":
        return _onboarding_speichern(db, request, actor, tenant)
    if request.tool_name == "hr.qualifikation.speichern":
        return _qualifikation_speichern(db, request, actor, tenant)
    if request.tool_name == "hr.schulung.speichern":
        return _schulung_speichern(db, request, actor, tenant)
    if request.tool_name == "admin.postfach.speichern":
        return _postfach_speichern(db, request, actor, tenant)
    if request.tool_name == "agrar.contract.get":
        return _agrar_contract_get(db, request, actor, tenant)
    if request.tool_name == "agrar.weighing_ticket.list":
        return _weighing_ticket_list(db, request, actor, tenant)
    if request.tool_name == "agrar.ration.transition":
        return _ration_transition(db, request, actor, tenant)
    if request.tool_name == "agrar.feeding.supply_handoff":
        return _feeding_supply_handoff(db, request, actor, tenant)
    if request.tool_name == "agrar.feeding.actual_measure":
        return _feeding_actual_measure(db, request, actor, tenant)
    if request.tool_name == "agrar.feeding.configure_threshold":
        return _feeding_configure_threshold(db, request, actor, tenant)
    if request.tool_name == "agrar.feed_analysis.transition":
        return _feed_analysis_transition(db, request, actor, tenant)
    if request.tool_name == "qualitaet.reklamation.abschliessen":
        return _reklamation_abschliessen(db, request, actor, tenant)
    if request.tool_name == "produktion.control.sync":
        return _produktion_control_sync(db, request, actor, tenant)
    if request.tool_name == "planung.calendar.reproject":
        return _planung_calendar_reproject(db, request, actor, tenant)
    if request.tool_name == "mobile.sync.process_pending":
        return _mobile_sync_process_pending(db, request, actor, tenant)
    if request.tool_name == "lager.bestand.get":
        return _lager_bestand_get(db, request, actor, tenant)
    if request.tool_name == "lager.inventur.status":
        return _inventur_status(db, request, actor, tenant)
    if request.tool_name == "lager.inventur.propose_opening":
        return _propose_inventur_opening(db, request, actor, tenant)
    if request.tool_name == "einkauf.bestellung.list":
        return _bestellung_list(db, request, actor, tenant)
    if request.tool_name == "einkauf.bestellung.status":
        return _bestellung_status(db, request, actor, tenant)
    if request.tool_name == "einkauf.bestellung.versenden":
        return _bestellung_versenden(db, request, actor, tenant)
    if request.tool_name == "einkauf.angebot.bestellen":
        return _angebot_bestellen(db, request, actor, tenant)
    if request.tool_name == "einkauf.anlieferavis.wareneingang":
        return _anlieferavis_wareneingang(db, request, actor, tenant)
    if request.tool_name == "lager.stock_movement.stornieren":
        return _stock_movement_stornieren(db, request, actor, tenant)
    if request.tool_name == "agent.proposal.list":
        return _proposal_list(db, request, actor, tenant)
    raise HTTPException(501, "No verified execution adapter is connected for this tool")


def _advisory_lock(db: Session, tenant: str, tool_name: str, idempotency_key: str) -> None:
    lock_bytes = hashlib.sha256(json.dumps([tenant, tool_name, idempotency_key]).encode()).digest()[:8]
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})


def _replay_or_none(db: Session, tenant: str, tool_name: str, key: str, actor: str, fingerprint: str) -> dict | None:
    previous = db.execute(text("""
        SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
        WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
    """), {"tenant": tenant, "tool": tool_name, "key": key}).mappings().first()
    if not previous:
        return None
    if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
        raise HTTPException(409, "Idempotency key is already bound to another request")
    result = previous["result"]
    if isinstance(result, str):
        result = json.loads(result)
    db.rollback()
    return {**result, "replayed": True}


def _store_execution(
    db: Session, *, tenant: str, tool: str, key: str, actor: str, fingerprint: str, result: dict
) -> None:
    db.execute(text("""
        INSERT INTO public.mcp_tool_executions
            (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
        VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
    """), {
        "tenant": tenant, "tool": tool, "key": key, "actor": actor,
        "hash": fingerprint, "result": json.dumps(result),
    })


def _city_from_address(address: object) -> str | None:
    if isinstance(address, dict):
        city = address.get("city")
        return str(city).strip() if city else None
    if isinstance(address, str) and address.strip():
        try:
            parsed = json.loads(address)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        if isinstance(parsed, dict) and parsed.get("city"):
            return str(parsed["city"]).strip()
    return None


def _search_customers(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Tenant-scoped customer search (UI combobox parity). Read-only."""
    del actor
    try:
        search = CustomerSearchInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid customer search parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "crm.customer.search does not support propose")
    term = search.query.strip()
    like = f"{term}%"
    contains = f"%{term}%"
    try:
        rows = db.execute(text("""
            SELECT id::text AS id,
                   customer_number AS kunden_nr,
                   company_name AS name,
                   address
            FROM domain_crm.customers
            WHERE tenant_id::text = :tenant
              AND (
                    company_name ILIKE :contains
                 OR customer_number ILIKE :contains
                 OR CAST(address AS text) ILIKE :contains
              )
            ORDER BY
              CASE
                WHEN customer_number ILIKE :like THEN 0
                WHEN company_name ILIKE :like THEN 1
                ELSE 2
              END,
              company_name ASC NULLS LAST
            LIMIT :lim
        """), {
            "tenant": tenant,
            "like": like,
            "contains": contains,
            "lim": search.limit,
        }).mappings().all()
        items = []
        for row in rows:
            customer_id = str(row["id"])
            kunden_nr = str(row["kunden_nr"] or "")
            name = str(row["name"] or kunden_nr)
            items.append({
                "customer_id": customer_id,
                "kunden_nr": kunden_nr,
                "name": name,
                "ort": _city_from_address(row["address"]),
                "segment": None,
                "route_path": f"{_CUSTOMER_ROUTE_PREFIX}/{customer_id}",
                "screen_id": _CUSTOMER_SCREEN_ID,
            })
        result = {
            "success": True,
            "mode": request.mode,
            "items": items,
            "count": len(items),
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _order_next_step(status: str) -> str:
    return _ORDER_NEXT_STEP.get(status, "Status prüfen")


def _reject_propose(tool_name: str, mode: str) -> None:
    if mode == "propose":
        raise HTTPException(422, f"{tool_name} does not support propose")


def _document_search(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = DocumentSearchInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid document search parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    params: dict[str, Any] = {
        "tenant": tenant,
        "lim": opened.limit,
        "dok": opened.dokument_id,
        "beleg": opened.beleg_ref,
        "typ": opened.dokument_typ,
        "von": opened.von.isoformat() if opened.von else None,
        "bis": opened.bis.isoformat() if opened.bis else None,
    }
    try:
        rows = _rows_or_empty(db, """
            SELECT id::text AS dokument_id,
                   COALESCE(bezeichnung, '') AS titel,
                   COALESCE(status, '') AS status,
                   created_at::text AS erstellt_am
            FROM domain_nachweisraum.nachweisraum_dokumente
            WHERE tenant_id::text = :tenant
              AND (
                    :dok IS NULL
                    OR id::text = :dok
                    OR bezeichnung = :dok
                    OR referenz_id = :dok
              )
              AND (:beleg IS NULL OR referenz_id = :beleg OR referenz_typ = :beleg)
              AND (:typ IS NULL OR dokument_typ = :typ)
              AND (:von IS NULL OR created_at::date >= CAST(:von AS date))
              AND (:bis IS NULL OR created_at::date <= CAST(:bis AS date))
            ORDER BY created_at DESC NULLS LAST
            LIMIT :lim
        """, params)
        items = []
        for r in rows:
            dok_id = str(r.get("dokument_id") or "")
            items.append({
                "dokument_id": dok_id,
                "titel": str(r.get("titel") or ""),
                "status": str(r.get("status") or ""),
                "erstellt_am": (str(r["erstellt_am"]) if r.get("erstellt_am") is not None else None),
                "route_path": f"{_DMS_ROUTE_PREFIX}/{dok_id}" if dok_id else None,
                "screen_id": _DMS_SCREEN_ID,
            })
        if opened.dokument_id and not items:
            raise HTTPException(404, "Document not found in the authenticated tenant")
        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _gobd_export_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = GobdExportStatusInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid GoBD export status parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    try:
        row = _first_or_none(db, """
            SELECT id::text AS export_id,
                   COALESCE(status, '') AS status,
                   COALESCE(anzahl_dokumente, 0)::int AS dokument_anzahl,
                   COALESCE(fehler_grund, export_pfad, periode) AS pruefprotokoll
            FROM domain_nachweisraum.gobd_exporte
            WHERE tenant_id::text = :tenant
              AND id::text = :export_id
            LIMIT 1
        """, {"tenant": tenant, "export_id": opened.export_id})
        if not row:
            raise HTTPException(404, "GoBD export not found in the authenticated tenant")
        export_id = str(row["export_id"])
        result = {
            "success": True,
            "mode": request.mode,
            "export_id": export_id,
            "status": str(row.get("status") or ""),
            "dokument_anzahl": int(row.get("dokument_anzahl") or 0),
            "pruefprotokoll": (str(row["pruefprotokoll"]) if row.get("pruefprotokoll") is not None else None),
            "route_path": f"{_GOBD_ROUTE_PREFIX}/{export_id}",
            "screen_id": _GOBD_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _compliance_gate_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Honest gate signals from existing domain tables — never invents approvals."""
    del actor
    try:
        opened = ComplianceGateInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid compliance gate parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    wanted = opened.gate_typ or "all"
    try:
        items: list[dict[str, Any]] = []

        def _add(gate_typ: str, gate_id: str, status: str, faellig: str | None = None) -> None:
            if wanted not in ("all", gate_typ):
                return
            items.append({
                "gate_id": gate_id,
                "gate_typ": gate_typ,
                "status": status,
                "faellig_am": faellig,
            })

        elster = _first_or_none(db, """
            SELECT id::text AS gate_id, COALESCE(status, 'keine_daten') AS status
            FROM domain_finance.ebilanz_exports
            WHERE tenant_id::text = :tenant
            ORDER BY erstellt_am DESC NULLS LAST, id
            LIMIT 1
        """, {"tenant": tenant})
        _add("elster", str(elster["gate_id"]) if elster else "elster",
             str(elster["status"]) if elster else "keine_daten")

        datev = _first_or_none(db, """
            SELECT id::text AS gate_id, COALESCE(status, 'keine_daten') AS status
            FROM domain_nachweisraum.gobd_exporte
            WHERE tenant_id::text = :tenant
            ORDER BY created_at DESC NULLS LAST, id
            LIMIT 1
        """, {"tenant": tenant})
        _add("datev", str(datev["gate_id"]) if datev else "datev-gobd",
             str(datev["status"]) if datev else "keine_daten")

        tse = _first_or_none(db, """
            SELECT id::text AS gate_id, COALESCE(status, 'keine_daten') AS status
            FROM domain_inventory.tse_devices
            WHERE tenant_id::text = :tenant
            ORDER BY id
            LIMIT 1
        """, {"tenant": tenant})
        if tse is None:
            tse = _first_or_none(db, """
                SELECT id::text AS gate_id, COALESCE(notice_status, status, 'keine_daten') AS status
                FROM public.pos_fiscal_notices
                WHERE tenant_id::text = :tenant
                ORDER BY created_at DESC NULLS LAST, id
                LIMIT 1
            """, {"tenant": tenant})
        _add("tse", str(tse["gate_id"]) if tse else "tse",
             str(tse["status"]) if tse else "keine_daten")

        auditor = _first_or_none(db, """
            SELECT id::text AS gate_id, COALESCE(status, 'keine_daten') AS status
            FROM domain_nachweisraum.gobd_exporte
            WHERE tenant_id::text = :tenant
              AND COALESCE(status, '') IN ('ABGESCHLOSSEN', 'PRUEFBEREIT', 'EXPORTIERT', 'fertig')
            ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST, id
            LIMIT 1
        """, {"tenant": tenant})
        _add("auditor", str(auditor["gate_id"]) if auditor else "auditor-gobd",
             str(auditor["status"]) if auditor else "keine_daten")

        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _sanctions_check(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: sanctions check via existing list + protocol helpers."""
    try:
        opened = SanctionsCheckInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid compliance.sanctions.check parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.sanctions_compliance import (
            match_sanctions_name,
            persist_sanctions_check,
        )

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed

        treffer, status, empfehlung = match_sanctions_name(db, opened.name)
        treffer_payload = [t.model_dump() for t in treffer]
        if request.mode != "execute":
            db.rollback()
            return {
                "success": True,
                "mode": request.mode,
                "status": status,
                "empfehlung": empfehlung,
                "treffer": treffer_payload,
                "proposedChanges": parameters,
            }

        check_id = persist_sanctions_check(
            db,
            tenant_id=tenant,
            name=opened.name,
            status=status,
            scope=opened.scope,
            entity_ref=opened.entity_ref,
            checked_by=actor,
            commit=False,
        )
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="sanctions_check",
            entity_id=check_id,
            audit_reason="MCP sanctions check",
            idempotency_key=request.idempotency_key,
            summary=f"Sanktionspruefung {opened.scope}: {status} fuer {opened.name} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "status": status,
            "empfehlung": empfehlung,
            "treffer": treffer_payload,
            "check_id": check_id,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _frachttabelle_anlegen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: create freight table in authenticated tenant."""
    try:
        opened = FrachttabelleAnlegenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.frachttabelle.anlegen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.logistik_frachttabellen import insert_frachttabelle

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed

        if request.mode != "execute":
            existing = db.execute(text("""
                SELECT id FROM domain_shared.logistik_frachttabellen
                WHERE tenant_id = :tid AND tabelle_nr = :nr
            """), {"tid": tenant, "nr": opened.tabelle_nr}).fetchone()
            db.rollback()
            if existing:
                raise HTTPException(409, f"Frachttabelle {opened.tabelle_nr} bereits vorhanden.")
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": parameters,
            }

        row = insert_frachttabelle(
            db,
            tenant_id=tenant,
            tabelle_nr=opened.tabelle_nr,
            bezeichnung=opened.bezeichnung,
            einheit=opened.einheit,
            waehrung=opened.waehrung,
            commit=False,
        )
        entity_id = str(row["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="frachttabelle",
            entity_id=entity_id,
            audit_reason="MCP frachttabelle anlegen",
            idempotency_key=request.idempotency_key,
            summary=f"Frachttabelle {opened.tabelle_nr} angelegt by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "id": entity_id,
            "tabelle_nr": opened.tabelle_nr,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _fahrzeug_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: Fahrzeug upsert in authenticated tenant."""
    try:
        opened = FahrzeugSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.fahrzeug.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.fuhrpark import upsert_fahrzeug

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {"kennzeichen": opened.kennzeichen, "typ": opened.typ}
        if opened.id:
            payload["id"] = opened.id
        if request.mode != "execute":
            upsert_fahrzeug(db, tenant, payload, validate_only=True)
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = upsert_fahrzeug(db, tenant, payload, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="fuhrpark_fahrzeug", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Fahrzeug {opened.kennzeichen} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "fahrzeug_id": entity_id, "kennzeichen": opened.kennzeichen,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _fahrzeug_loeschen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: delete Fahrzeug in authenticated tenant."""
    try:
        opened = FahrzeugLoeschenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.fahrzeug.loeschen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.fuhrpark import delete_fahrzeug_tenant
        from app.domains.operations.repository import FahrzeugRepository

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if request.mode != "execute":
            if not FahrzeugRepository(db).get_by_id(tenant, opened.fahrzeug_id):
                raise HTTPException(404, "Fahrzeug not found")
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        deleted_id = delete_fahrzeug_tenant(db, tenant, opened.fahrzeug_id, commit=False)
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="fuhrpark_fahrzeug", entity_id=deleted_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Fahrzeug {deleted_id} geloescht by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "fahrzeug_id": deleted_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _terminart_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: Terminart upsert in authenticated tenant."""
    try:
        opened = TerminartSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.terminart.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.fuhrpark import upsert_terminart

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "terminart": opened.terminart,
            "intervall_monate": opened.intervall_monate,
            "intervall_km": opened.intervall_km,
        }
        if opened.id:
            payload["id"] = opened.id
        if request.mode != "execute":
            upsert_terminart(db, tenant, payload, validate_only=True)
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = upsert_terminart(db, tenant, payload, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="fuhrpark_terminart", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Terminart {opened.terminart} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "terminart_id": entity_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _fuhrpark_rechnung_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: Fuhrpark-Rechnung upsert in authenticated tenant."""
    try:
        opened = FuhrparkRechnungSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.rechnung.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.fuhrpark import upsert_rechnung

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "rechnungs_nr": opened.rechnungs_nr,
            "datum": opened.datum,
            "betrag_eur": opened.betrag_eur,
            "fahrzeug_kennzeichen": opened.fahrzeug_kennzeichen,
            "sachkonto": opened.sachkonto,
            "kostenart": opened.kostenart,
            "notiz": opened.notiz,
        }
        if opened.id:
            payload["id"] = opened.id
        if request.mode != "execute":
            upsert_rechnung(db, tenant, payload, validate_only=True)
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = upsert_rechnung(db, tenant, payload, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="fuhrpark_rechnung", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Rechnung {opened.rechnungs_nr} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "rechnung_id": entity_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _ausgehendes_dokument_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: ausgehendes Dokument upsert in authenticated tenant."""
    try:
        opened = AusgehendesDokumentSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.ausgehendes_dokument.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.fuhrpark import upsert_ausgehendes_dokument

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "beleg_typ": opened.beleg_typ,
            "formular": opened.formular,
            "ziel_modul": opened.ziel_modul,
            "beschreibung": opened.beschreibung,
            "aktiv": opened.aktiv,
        }
        if opened.id:
            payload["id"] = opened.id
        if request.mode != "execute":
            upsert_ausgehendes_dokument(db, tenant, payload, validate_only=True)
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = upsert_ausgehendes_dokument(db, tenant, payload, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="fuhrpark_ausgehendes_dokument", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Dokument {opened.beleg_typ} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "dokument_id": entity_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bonus_calculate(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: calculate immutable bonus run via L3ReportCatalogService."""
    try:
        opened = BonusCalculateInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid reporting.bonus.calculate parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.services.l3_report_catalog_service import L3ReportCatalogService, ReportCatalogError

        svc = L3ReportCatalogService(db, tenant)
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        try:
            svc.validate_bonus_run_params(
                report_id=opened.report_id,
                from_date=opened.from_date,
                to_date=opened.to_date,
                rate_pct=opened.rate_pct,
                reason=opened.reason,
            )
        except ReportCatalogError as exc:
            raise HTTPException(422, str(exc)) from exc
        if request.mode != "execute":
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        created = svc.create_bonus_run(
            report_id=opened.report_id,
            from_date=opened.from_date,
            to_date=opened.to_date,
            rate_pct=opened.rate_pct,
            actor=actor,
            reason=opened.reason,
        )
        run_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="bonus_run",
            entity_id=run_id,
            audit_reason="MCP bonus calculate",
            idempotency_key=request.idempotency_key,
            summary=f"Bonuslauf {opened.report_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "run_id": run_id,
            "lines": created.get("lines"),
            "total_bonus": float(created.get("total_bonus") or 0),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _query_import_signed(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: import HMAC-signed query definition."""
    try:
        opened = QueryImportSignedInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid reporting.query.import_signed parameters") from exc
    parameters = {"reason": opened.reason, "bundle_keys": sorted(opened.bundle.keys())}
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(
        json.dumps({"reason": opened.reason, "bundle": opened.bundle}, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()
    try:
        from app.core.config import settings
        from app.services.query_center_service import QueryCenterError, QueryCenterService

        svc = QueryCenterService(db, tenant, signing_key=settings.SECRET_KEY)
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        try:
            preview = svc.preview_import_signed(opened.bundle)
        except QueryCenterError as exc:
            raise HTTPException(422, str(exc)) from exc
        if request.mode != "execute":
            db.rollback()
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {**parameters, **preview},
            }
        saved = svc.import_signed(opened.bundle, actor=actor, reason=opened.reason)
        def_id = str(saved.get("id") or "")
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="query_definition",
            entity_id=def_id or tenant,
            audit_reason="MCP query import signed",
            idempotency_key=request.idempotency_key,
            summary=f"Abfrage importiert {preview.get('name')} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "definition_id": def_id,
            "name": preview.get("name"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _tour_anlegen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: create logistics tour in authenticated tenant."""
    try:
        opened = TourAnlegenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid logistik.tour.anlegen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.logistics_tours import insert_tour

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        stops: list[dict[str, Any]] = []
        if opened.delivery_note_ref:
            stops.append({"delivery_note_ref": opened.delivery_note_ref, "stop_order": 0})
        if request.mode != "execute":
            if opened.delivery_note_ref:
                from app.api.v1.endpoints.logistics_tours import _lookup_sales_delivery_note

                if _lookup_sales_delivery_note(db, opened.delivery_note_ref, tenant) is None:
                    raise HTTPException(404, "Delivery note not found in the authenticated tenant")
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        row = insert_tour(
            db,
            tenant_id=tenant,
            date_value=opened.date,
            vehicle_id=opened.vehicle_id,
            driver_id=opened.driver_id,
            notes=opened.notes,
            stops=stops,
            commit=False,
        )
        tour_id = str(row["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="logistics_tour",
            entity_id=tour_id,
            audit_reason=opened.reason,
            idempotency_key=request.idempotency_key,
            summary=f"Tour angelegt by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "tour_id": tour_id,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bestellung_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: update PO header fields in authenticated tenant."""
    try:
        opened = BestellungSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid einkauf.bestellung.speichern parameters") from exc
    parameters = opened.model_dump(mode="json", exclude_none=True)
    patch = {
        k: v for k, v in parameters.items()
        if k not in ("bestellung_id", "reason") and v is not None
    }
    if not patch:
        raise HTTPException(422, "At least one purchase-order header field is required")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        resolved = db.execute(text("""
            SELECT id::text AS id, bestellnummer, status
            FROM domain_einkauf.bestellungen
            WHERE tenant_id::text = :tenant
              AND (id::text = :bid OR bestellnummer = :bid)
            FOR SHARE
            LIMIT 1
        """), {"tenant": tenant, "bid": opened.bestellung_id}).mappings().first()
        if not resolved:
            raise HTTPException(404, "Purchase order not found in the authenticated tenant")
        bestellung_id = str(resolved["id"])
        if request.mode != "execute":
            db.rollback()
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "bestellung_id": bestellung_id,
                    "bestellnummer": resolved.get("bestellnummer"),
                    "status": resolved.get("status"),
                    "patch": patch,
                },
            }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            updated = ProcurementService(child, tenant).update_bestellung(bestellung_id, patch)
        audit_id = _write_audit(
            db,
            tenant_id=tenant,
            action_key=request.tool_name,
            entity_type="einkauf_bestellung",
            entity_id=bestellung_id,
            audit_reason=opened.reason,
            idempotency_key=request.idempotency_key,
            summary=f"Bestellung {resolved.get('bestellnummer') or bestellung_id} gespeichert by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "bestellung_id": bestellung_id,
            "bestellnummer": resolved.get("bestellnummer"),
            "status": updated.get("status"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(404, "Purchase order not found in the authenticated tenant") from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bewerbung_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: create HR application in authenticated tenant."""
    try:
        opened = BewerbungSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid hr.bewerbung.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.schemas.personal_bewerbung_schemas import BewerbungIn
        from app.core.uuid7 import uuid7
        from app.services import bewerbung_service as dienst

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = BewerbungIn(
            applicant_name=opened.applicant_name,
            applicant_email=opened.applicant_email,
            position_title=opened.position_title,
            source=opened.source,
        )
        if request.mode != "execute":
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        created = dienst.anlegen(db, tenant, str(uuid7()), payload)
        app_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="hr_application", entity_id=app_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Bewerbung {opened.applicant_name} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "application_id": app_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _einwilligung_anlegen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: immutable consent text version in authenticated tenant."""
    try:
        opened = EinwilligungAnlegenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid hr.einwilligung.anlegen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.core.uuid7 import uuid7
        from app.services import bewerbung_einwilligung_service as einwilligung

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if request.mode != "execute":
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": {
                "wortlaut": opened.wortlaut[:120], "erstellt_durch": opened.erstellt_durch or actor,
            }}
        created = einwilligung.erklaerung_anlegen(
            db, tenant, str(uuid7()), opened.wortlaut, opened.erstellt_durch or actor,
        )
        entity_id = str(created.get("id") or created.get("fassung") or "")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="hr_consent_text", entity_id=entity_id or tenant,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Einwilligungsfassung by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "erklaerung_id": entity_id, "fassung": created.get("fassung"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _onboarding_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: onboarding run in authenticated tenant (checklist tenant-bound)."""
    try:
        opened = OnboardingSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid hr.onboarding.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.training import insert_onboarding_run

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "checklist_id": opened.checklist_id,
            "employee_ref": opened.employee_ref,
            "assigned_by": opened.assigned_by or actor,
            "due_date": opened.due_date,
            "status": "not_started",
            "progress_percent": 0,
            "state": {},
        }
        if request.mode != "execute":
            from app.api.v1.endpoints.training import _require_tenant_row

            _require_tenant_row(
                db,
                "SELECT id FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id",
                {"tenant_id": tenant, "id": opened.checklist_id},
                not_found_detail="Checklist not found",
            )
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = insert_onboarding_run(db, tenant, payload)
        run_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="hr_onboarding_run", entity_id=run_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Onboarding-Lauf {opened.employee_ref} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "run_id": run_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _qualifikation_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: qualification profile in authenticated tenant."""
    try:
        opened = QualifikationSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid hr.qualifikation.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.training import insert_qualification

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "employee_ref": opened.employee_ref,
            "role_code": opened.role_code,
            "qualification_level": opened.qualification_level,
            "skills": opened.skills or [],
            "valid_until": opened.valid_until,
        }
        if request.mode != "execute":
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = insert_qualification(db, tenant, payload)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="hr_qualification", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Qualifikation {opened.employee_ref}/{opened.role_code} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "qualification_id": entity_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _schulung_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: training assignment in authenticated tenant (course tenant-bound)."""
    try:
        opened = SchulungSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid hr.schulung.speichern parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.api.v1.endpoints.training import _require_tenant_row, insert_assignment

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        payload = {
            "course_id": opened.course_id,
            "employee_ref": opened.employee_ref,
            "assigned_by": opened.assigned_by or actor,
            "due_date": opened.due_date,
            "status": "assigned",
        }
        if request.mode != "execute":
            _require_tenant_row(
                db,
                "SELECT id FROM domain_hr.training_courses WHERE tenant_id=:tenant_id AND id=:id",
                {"tenant_id": tenant, "id": opened.course_id},
                not_found_detail="Course not found",
            )
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": payload}
        created = insert_assignment(db, tenant, payload)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="hr_training_assignment", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Schulung {opened.employee_ref} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "assignment_id": entity_id, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _postfach_speichern(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Mask-parity write: create/update mailbox in authenticated tenant (no password in audit)."""
    try:
        opened = PostfachSpeichernInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid admin.postfach.speichern parameters") from exc
    # Fingerprint ohne Klartext-Passwort.
    parameters = opened.model_dump(mode="json", exclude={"passwort"})
    parameters["hat_passwort"] = bool(opened.passwort)
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        from app.services import mailkonto_service as konto

        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if opened.postfach_id:
            try:
                konto.lesen(db, tenant, opened.postfach_id)
            except konto.MailkontoFehler as exc:
                raise HTTPException(404, "Mailbox not found in the authenticated tenant") from exc
        if request.mode != "execute":
            db.rollback()
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        saved = konto.speichern(
            db,
            tenant,
            opened.model_dump(exclude={"reason", "postfach_id"}),
            postfach_id=opened.postfach_id,
            von=actor,
        )
        entity_id = str(saved["id"])
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="mailkonto", entity_id=entity_id,
            audit_reason=opened.reason, idempotency_key=request.idempotency_key,
            summary=f"Postfach {opened.kennung} gespeichert by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "postfach_id": entity_id, "kennung": opened.kennung, "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _agrar_contract_get(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = AgrarContractInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar contract parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    try:
        row = _first_or_none(db, """
            SELECT id::text AS kontrakt_id,
                   article_id::text AS ware,
                   (COALESCE(total_quantity_kg, 0) / 1000.0)::float AS menge_t,
                   fixed_price::float AS preis_eur,
                   COALESCE(status, '') AS status
            FROM domain_inventory.agrar_contracts
            WHERE tenant_id::text = :tenant
              AND (id::text = :kid OR contract_number = :kid)
            LIMIT 1
        """, {"tenant": tenant, "kid": opened.kontrakt_id})
        if not row:
            raise HTTPException(404, "Agrar contract not found in the authenticated tenant")
        kontrakt_id = str(row["kontrakt_id"])
        result = {
            "success": True,
            "mode": request.mode,
            "kontrakt_id": kontrakt_id,
            "ware": (str(row["ware"]) if row.get("ware") is not None else None),
            "menge_t": round(float(row.get("menge_t") or 0.0), 3),
            "preis_eur": (round(float(row["preis_eur"]), 2) if row.get("preis_eur") is not None else None),
            "status": str(row.get("status") or ""),
            "route_path": f"{_AGRAR_CONTRACT_ROUTE_PREFIX}/{kontrakt_id}",
            "screen_id": _AGRAR_CONTRACT_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _weighing_ticket_list(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = WeighingTicketListInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid weighing ticket list parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    params: dict[str, Any] = {
        "tenant": tenant,
        "lim": opened.limit,
        "ticket": opened.ticket_id,
        "partie": opened.partie_id,
        "von": opened.von.isoformat() if opened.von else None,
        "bis": opened.bis.isoformat() if opened.bis else None,
    }
    try:
        rows = _rows_or_empty(db, """
            SELECT id::text AS ticket_id,
                   COALESCE(contract_id::text, reference_doc, '') AS partie_id,
                   COALESCE(gross_weight, 0)::float AS brutto_kg,
                   COALESCE(net_weight, billing_weight, 0)::float AS netto_kg,
                   COALESCE(weighing_date, created_at)::text AS erstellt_am
            FROM domain_inventory.weighing_tickets
            WHERE tenant_id::text = :tenant
              AND (:ticket IS NULL OR id::text = :ticket)
              AND (
                    :partie IS NULL
                 OR contract_id::text = :partie
                 OR reference_doc = :partie
              )
              AND (:von IS NULL OR COALESCE(weighing_date, created_at)::date >= CAST(:von AS date))
              AND (:bis IS NULL OR COALESCE(weighing_date, created_at)::date <= CAST(:bis AS date))
            ORDER BY COALESCE(weighing_date, created_at) DESC NULLS LAST
            LIMIT :lim
        """, params)
        items = []
        for r in rows:
            tid = str(r.get("ticket_id") or "")
            items.append({
                "ticket_id": tid,
                "partie_id": str(r.get("partie_id") or ""),
                "brutto_kg": round(float(r.get("brutto_kg") or 0.0), 3),
                "netto_kg": round(float(r.get("netto_kg") or 0.0), 3),
                "erstellt_am": (str(r["erstellt_am"]) if r.get("erstellt_am") is not None else None),
                "route_path": f"{_WEIGHING_ROUTE_PREFIX}/{tid}" if tid else None,
                "screen_id": _WEIGHING_SCREEN_ID,
            })
        if opened.ticket_id and not items:
            raise HTTPException(404, "Weighing ticket not found in the authenticated tenant")
        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _lager_bestand_get(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = LagerBestandInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid stock parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    # lager_id accepted for API shape; article stock columns are not warehouse-partitioned.
    _ = opened.lager_id
    try:
        row = _first_or_none(db, """
            SELECT id::text AS artikel_id,
                   COALESCE(current_stock, 0)::float AS menge,
                   COALESCE(unit, 'Stk') AS einheit,
                   COALESCE(reserved_stock, 0)::float AS reserviert,
                   COALESCE(
                       available_stock,
                       COALESCE(current_stock, 0) - COALESCE(reserved_stock, 0),
                       0
                   )::float AS verfuegbar
            FROM domain_inventory.articles
            WHERE tenant_id::text = :tenant
              AND deleted_at IS NULL
              AND (id::text = :aid OR article_number = :aid)
            LIMIT 1
        """, {"tenant": tenant, "aid": opened.artikel_id})
        if not row:
            raise HTTPException(404, "Article not found in the authenticated tenant")
        artikel_id = str(row["artikel_id"])
        result = {
            "success": True,
            "mode": request.mode,
            "artikel_id": artikel_id,
            "menge": round(float(row.get("menge") or 0.0), 3),
            "einheit": str(row.get("einheit") or "Stk"),
            "reserviert": round(float(row.get("reserviert") or 0.0), 3),
            "verfuegbar": round(float(row.get("verfuegbar") or 0.0), 3),
            "route_path": f"{_STOCK_ROUTE_PREFIX}/{artikel_id}",
            "screen_id": _STOCK_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


_INVENTUR_OPENING_ROUTE = "/lager/inventur-nebenlaeufe"
_INVENTUR_OPENING_SCREEN = "lager/inventur-nebenlaeufe"


def _inventur_opening_preview(db: Session, count_id: str, tenant: str) -> dict[str, Any]:
    """Read-only snapshot from inventory_counts + lines (same source as auxiliary create)."""
    count = db.execute(text("""
        SELECT c.id::text AS count_id,
               c.warehouse_id::text AS warehouse_id,
               COALESCE(c.status, '') AS status
          FROM domain_inventory.inventory_counts c
         WHERE c.id::text = :id AND c.tenant_id::text = :tenant
         FOR SHARE OF c
    """), {"id": count_id, "tenant": tenant}).mappings().first()
    if not count:
        raise HTTPException(404, "Inventur not found in the authenticated tenant")
    agg = db.execute(text("""
        SELECT COUNT(*)::int AS line_count,
               COALESCE(SUM(CASE
                 WHEN ABS(COALESCE(l.counted_qty, 0) - COALESCE(l.expected_qty, 0)) >= 0.001
                 THEN 1 ELSE 0 END), 0)::int AS difference_count,
               COALESCE(SUM(
                 COALESCE(l.counted_qty, 0) * COALESCE(a.purchase_price, 0)
               ), 0)::float AS preliminary_value
          FROM domain_inventory.inventory_count_lines l
          LEFT JOIN domain_inventory.articles a
            ON a.id = l.article_id AND a.tenant_id::text = l.tenant_id::text
         WHERE l.inventory_count_id::text = :id AND l.tenant_id::text = :tenant
    """), {"id": count_id, "tenant": tenant}).mappings().first() or {}
    return {
        "count_id": str(count["count_id"]),
        "warehouse_id": (str(count["warehouse_id"]) if count.get("warehouse_id") else None),
        "status": str(count.get("status") or ""),
        "line_count": int(agg.get("line_count") or 0),
        "difference_count": int(agg.get("difference_count") or 0),
        "preliminary_value": round(float(agg.get("preliminary_value") or 0.0), 2),
        "batch_type": "opening_balance",
        "route_path": _INVENTUR_OPENING_ROUTE,
        "screen_id": _INVENTUR_OPENING_SCREEN,
        "source_route": f"/lager/inventur?count={count['count_id']}",
    }


def _propose_inventur_opening(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Store a pending Bestandsvortrag proposal. Never creates or applies a batch."""
    try:
        opened = InventurOpeningProposeInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid inventur opening propose parameters") from exc
    if request.mode == "execute":
        raise HTTPException(
            501,
            "Inventur opening booking is not an MCP execution; no CommandEndpoint — human UI only",
        )
    parameters = opened.model_dump(mode="json")
    if request.mode == "propose" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "propose requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "propose":
            lock_bytes = hashlib.sha256(
                json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()
            ).digest()[:8]
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})
            previous = db.execute(text("""
                SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
                WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
            """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key}).mappings().first()
            if previous:
                if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                    raise HTTPException(409, "Idempotency key is already bound to another request")
                result = previous["result"]
                if isinstance(result, str):
                    result = json.loads(result)
                db.rollback()
                return {**result, "replayed": True}
        preview = _inventur_opening_preview(db, opened.count_id, tenant)
        if request.mode != "propose":
            return {"success": True, "mode": request.mode, "booked": False, **preview}
        proposal_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        rationale = (opened.reason or "").strip() or "MCP lager.inventur.propose_opening"
        db.execute(text("""
            INSERT INTO public.agent_proposals
                (proposal_id, tenant_id, action_type, risk_level, approval_status,
                 context_snapshot, rationale, idempotency_key, created_at)
            VALUES
                (:id, :tenant, 'inventur_opening', 'high', 'pending',
                 CAST(:snapshot AS json), :rationale, :key, :now)
        """), {
            "id": proposal_id,
            "tenant": tenant,
            "snapshot": json.dumps({
                "context_summary": f"Bestandsvortrag Inventur {preview['count_id']}",
                "proposed_action": (
                    "Bestandsvortrag vorschlagen — kein Booking; "
                    "Uebernahme nur ueber menschliche UI (Vier-Augen)"
                ),
                "human_approval_required": True,
                "audit_events": [{"event": "proposal_created", "occurred_at": now}],
                "actor_id": actor,
                "payload_hash": fingerprint,
                **preview,
            }),
            "rationale": rationale[:500],
            "key": hashlib.sha256(f"{tenant}|{request.tool_name}|{request.idempotency_key}".encode()).hexdigest(),
            "now": now,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="inventur_opening_proposal", entity_id=proposal_id,
            audit_reason="MCP inventur opening proposal", idempotency_key=request.idempotency_key,
            summary=f"Inventur opening proposal for {opened.count_id} by {actor}",
        )
        result = {
            "success": True, "mode": "propose", "replayed": False, "booked": False,
            "entwurf_id": proposal_id, "approval_status": "pending", "auditEntryId": audit_id,
            **preview,
        }
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {
            "tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
            "actor": actor, "hash": fingerprint, "result": json.dumps(result),
        })
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _inventur_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = InventurStatusInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid inventur status parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    params = {"tenant": tenant, "lager": opened.lager_id}
    try:
        offen = int(_scalar_or_default(db, """
            SELECT COUNT(*)::int AS offene_inventuren
            FROM domain_inventory.inventory_counts
            WHERE tenant_id::text = :tenant
              AND COALESCE(status, '') NOT IN ('posted', 'approved', 'closed', 'abgeschlossen')
              AND (:lager IS NULL OR warehouse_id::text = :lager)
        """, params, "offene_inventuren", 0) or 0)
        differenzen = float(_scalar_or_default(db, """
            SELECT COALESCE(SUM(
                     ABS(COALESCE(l.counted_qty, 0) - COALESCE(l.expected_qty, 0))
                     * COALESCE(a.purchase_price, 0)
                   ), 0)::float AS differenzen_eur
            FROM domain_inventory.inventory_count_lines l
            JOIN domain_inventory.inventory_counts c
              ON c.id = l.inventory_count_id AND c.tenant_id::text = l.tenant_id::text
            LEFT JOIN domain_inventory.articles a
              ON a.id = l.article_id AND a.tenant_id::text = l.tenant_id::text
            WHERE l.tenant_id::text = :tenant
              AND COALESCE(c.status, '') NOT IN ('posted', 'approved', 'closed', 'abgeschlossen')
              AND (:lager IS NULL OR c.warehouse_id::text = :lager)
        """, params, "differenzen_eur", 0.0) or 0.0)
        letzter = _scalar_or_default(db, """
            SELECT COALESCE(approved_at, updated_at, created_at)::text AS letzter_abschluss
            FROM domain_inventory.inventory_counts
            WHERE tenant_id::text = :tenant
              AND COALESCE(status, '') IN ('posted', 'approved', 'closed', 'abgeschlossen')
              AND (:lager IS NULL OR warehouse_id::text = :lager)
            ORDER BY COALESCE(approved_at, updated_at, created_at) DESC NULLS LAST
            LIMIT 1
        """, params, "letzter_abschluss", None)
        result = {
            "success": True,
            "mode": request.mode,
            "offene_inventuren": offen,
            "differenzen_eur": round(differenzen, 2),
            "letzter_abschluss": str(letzter) if letzter is not None else None,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bestellung_list(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = BestellungListInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid purchase order list parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    statuses = list(_PO_STATUS_FILTER.get(opened.status, ())) if opened.status else None
    params: dict[str, Any] = {"tenant": tenant, "lim": opened.limit, "statuses": statuses}
    try:
        rows = _rows_or_empty(db, """
            SELECT b.id::text AS bestellung_id,
                   COALESCE(l.firmenname, b.lieferant_id::text, '') AS lieferant,
                   COALESCE(b.status, '') AS status,
                   b.lieferdatum_wunsch::text AS liefertermin,
                   COALESCE(b.brutto_summe, b.netto_summe, 0)::float AS wert_eur
            FROM domain_einkauf.bestellungen b
            LEFT JOIN domain_einkauf.lieferanten l
              ON l.id = b.lieferant_id AND l.tenant_id::text = b.tenant_id::text
            WHERE b.tenant_id::text = :tenant
              AND (:statuses IS NULL OR LOWER(COALESCE(b.status, '')) = ANY(:statuses))
            ORDER BY b.bestelldatum DESC NULLS LAST, b.created_at DESC NULLS LAST
            LIMIT :lim
        """, params)
        items = []
        for r in rows:
            bid = str(r.get("bestellung_id") or "")
            items.append({
                "bestellung_id": bid,
                "lieferant": str(r.get("lieferant") or ""),
                "status": str(r.get("status") or ""),
                "liefertermin": (str(r["liefertermin"]) if r.get("liefertermin") is not None else None),
                "wert_eur": round(float(r.get("wert_eur") or 0.0), 2),
                "route_path": f"{_PO_ROUTE_PREFIX}/{bid}" if bid else None,
                "screen_id": _PO_SCREEN_ID,
            })
        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bestellung_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Tenant-scoped purchase order status + canonical mask route. Read-only."""
    del actor
    try:
        opened = BestellungStatusInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid purchase order status parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "einkauf.bestellung.status does not support propose")
    try:
        row = db.execute(text("""
            SELECT b.id::text AS bestellung_id,
                   COALESCE(b.bestellnummer, b.id::text) AS bestellnummer,
                   COALESCE(b.status, '') AS status,
                   COALESCE(l.firmenname, b.lieferant_id::text, '') AS lieferant
            FROM domain_einkauf.bestellungen b
            LEFT JOIN domain_einkauf.lieferanten l
              ON l.id = b.lieferant_id AND l.tenant_id::text = b.tenant_id::text
            WHERE b.tenant_id::text = :tenant
              AND (b.id::text = :bid OR b.bestellnummer = :bid)
            LIMIT 1
        """), {"tenant": tenant, "bid": opened.bestellung_id}).mappings().first()
        if not row:
            raise HTTPException(404, "Purchase order not found in the authenticated tenant")
        bestellung_id = str(row["bestellung_id"])
        result = {
            "success": True,
            "mode": request.mode,
            "bestellung_id": bestellung_id,
            "bestellnummer": str(row.get("bestellnummer") or opened.bestellung_id),
            "status": str(row.get("status") or ""),
            "lieferant": str(row.get("lieferant") or ""),
            "route_path": f"{_PO_ROUTE_PREFIX}/{bestellung_id}",
            "screen_id": _PO_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _proposal_list(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    del actor
    try:
        opened = ProposalListInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid proposal list parameters") from exc
    _reject_propose(request.tool_name, request.mode)
    params = {"tenant": tenant, "lim": opened.limit, "status": opened.status}
    try:
        rows = _rows_or_empty(db, """
            SELECT proposal_id::text AS proposal_id,
                   COALESCE(action_type, '') AS action_type,
                   COALESCE(approval_status, '') AS approval_status,
                   created_at::text AS created_at
            FROM public.agent_proposals
            WHERE tenant_id::text = :tenant
              AND (:status IS NULL OR approval_status = :status)
            ORDER BY created_at DESC NULLS LAST
            LIMIT :lim
        """, params)
        items = [{
            "proposal_id": str(r.get("proposal_id") or ""),
            "action_type": str(r.get("action_type") or ""),
            "approval_status": str(r.get("approval_status") or ""),
            "created_at": (str(r["created_at"]) if r.get("created_at") is not None else None),
        } for r in rows]
        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _cell_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Silocell fill level, material, QS and flush flag. Read-only — no transfer/QS write."""
    del actor
    try:
        opened = CellStatusInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid cell status parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "wms.cell.status does not support propose")
    params = {"cell": opened.cell_code, "tenant": tenant}
    try:
        cell = _first_or_none(db, """
            SELECT id::text AS id,
                   cell_code,
                   COALESCE(current_stock_kg, 0)::float AS current_stock_kg,
                   COALESCE(qs_status, 'frei') AS qs_status,
                   current_material_id::text AS current_material
            FROM domain_inventory.silo_cells
            WHERE tenant_id::text = :tenant
              AND COALESCE(is_active, true) = true
              AND (cell_code = :cell OR id::text = :cell)
            LIMIT 1
        """, params)
        if not cell:
            raise HTTPException(404, "Silo cell not found in the authenticated tenant")

        qs = str(cell.get("qs_status") or "frei")
        flush_edge = _scalar_or_default(db, """
            SELECT TRUE AS flush_required
            FROM domain_inventory.material_flow_edges e
            JOIN domain_inventory.material_flow_nodes n
              ON n.id = e.to_node_id
             AND n.tenant_id::text = e.tenant_id::text
            WHERE e.tenant_id::text = :tenant
              AND e.flush_required = true
              AND n.ref_type = 'silo_cell'
              AND n.ref_id = :cell_id
            LIMIT 1
        """, {"tenant": tenant, "cell_id": str(cell["id"])}, "flush_required", None)
        flush_required = bool(flush_edge) or qs == "reinigung"

        material = cell.get("current_material")
        cell_id = str(cell["id"])
        result = {
            "success": True,
            "mode": request.mode,
            "cell_id": cell_id,
            "cell_code": str(cell.get("cell_code") or opened.cell_code),
            "current_stock_kg": round(float(cell.get("current_stock_kg") or 0.0), 3),
            "qs_status": qs,
            "current_material": str(material) if material is not None else None,
            "flush_required": flush_required,
            "route_path": f"{_CELL_ROUTE_PREFIX}/{cell_id}",
            "screen_id": _CELL_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _lot_trace(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """WMS lot trace from silo_lots (preferred) or inventory_lots. Read-only."""
    del actor
    try:
        opened = LotTraceInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid lot trace parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "wms.lot.trace does not support propose")
    params = {"lot": opened.lot_id, "tenant": tenant}
    try:
        silo = _first_or_none(db, """
            SELECT id::text AS id,
                   virtual_lot_number,
                   article_id::text AS artikel_id,
                   COALESCE(quantity_tons, 0)::float AS quantity_tons,
                   COALESCE(status, '') AS status
            FROM domain_inventory.silo_lots
            WHERE tenant_id::text = :tenant
              AND (id::text = :lot OR virtual_lot_number = :lot)
            LIMIT 1
        """, params)

        if silo:
            lot_id = str(silo["id"])
            menge_kg = round(float(silo.get("quantity_tons") or 0.0) * 1000.0, 3)
            status = str(silo.get("status") or "")
            cell = _scalar_or_default(db, """
                SELECT cell_code AS silozelle
                FROM domain_inventory.silo_cells
                WHERE tenant_id::text = :tenant
                  AND current_lot_id = :lot_id
                  AND COALESCE(is_active, true) = true
                ORDER BY updated_at DESC NULLS LAST
                LIMIT 1
            """, {"tenant": tenant, "lot_id": lot_id}, "silozelle", None)
            qs = _scalar_or_default(db, """
                SELECT qs_status
                FROM domain_inventory.silo_cells
                WHERE tenant_id::text = :tenant
                  AND current_lot_id = :lot_id
                  AND COALESCE(is_active, true) = true
                ORDER BY updated_at DESC NULLS LAST
                LIMIT 1
            """, {"tenant": tenant, "lot_id": lot_id}, "qs_status", None)
            movements = _rows_or_empty(db, """
                SELECT movement_type AS typ,
                       (COALESCE(quantity_tons, 0) * 1000)::float AS menge_kg,
                       note AS notiz,
                       created_at::text AS zeit
                FROM domain_inventory.silo_lot_movements
                WHERE tenant_id::text = :tenant
                  AND silo_lot_id::text = :lot_id
                ORDER BY created_at DESC NULLS LAST
                LIMIT 50
            """, {"tenant": tenant, "lot_id": lot_id})
            result = {
                "success": True,
                "mode": request.mode,
                "lot_id": lot_id,
                "artikel_id": (str(silo["artikel_id"]) if silo.get("artikel_id") is not None else None),
                "menge_kg": menge_kg,
                "status": status,
                "qs_status": str(qs) if qs is not None else status,
                "silozelle": str(cell) if cell is not None else None,
                "bewegungen": [
                    {
                        "typ": str(row.get("typ") or ""),
                        "menge_kg": round(float(row.get("menge_kg") or 0.0), 3),
                        "notiz": (str(row["notiz"]) if row.get("notiz") is not None else None),
                        "zeit": (str(row["zeit"]) if row.get("zeit") is not None else None),
                    }
                    for row in movements
                ],
                "route_path": f"{_LOT_ROUTE_PREFIX}/{lot_id}",
                "screen_id": _LOT_SCREEN_ID,
            }
            db.rollback()
            return result

        inv = _first_or_none(db, """
            SELECT id::text AS id,
                   article_id::text AS artikel_id,
                   COALESCE(current_qty, 0)::float AS current_qty,
                   COALESCE(unit, 'kg') AS unit,
                   COALESCE(status, '') AS status,
                   warehouse_id::text AS warehouse_id
            FROM domain_inventory.inventory_lots
            WHERE tenant_id::text = :tenant
              AND (id::text = :lot OR lot_number = :lot)
            LIMIT 1
        """, params)
        if not inv:
            raise HTTPException(404, "Lot not found in the authenticated tenant")

        lot_id = str(inv["id"])
        qty = float(inv.get("current_qty") or 0.0)
        unit = str(inv.get("unit") or "kg").lower()
        menge_kg = round(qty * 1000.0, 3) if unit in ("t", "to", "ton", "tons", "tonne", "tonnen") else round(qty, 3)
        status = str(inv.get("status") or "")
        qs = _scalar_or_default(db, """
            SELECT qs_status
            FROM domain_inventory.inventory_lots
            WHERE id::text = :lot_id AND tenant_id::text = :tenant
            LIMIT 1
        """, {"lot_id": lot_id, "tenant": tenant}, "qs_status", None)
        movements = _rows_or_empty(db, """
            SELECT movement_type AS typ,
                   COALESCE(quantity, 0)::float AS menge_kg,
                   reference_type AS notiz,
                   created_at::text AS zeit
            FROM domain_inventory.inventory_lot_movements
            WHERE lot_id::text = :lot_id
              AND (tenant_id IS NULL OR tenant_id::text = :tenant)
            ORDER BY created_at DESC NULLS LAST
            LIMIT 50
        """, {"tenant": tenant, "lot_id": lot_id})
        result = {
            "success": True,
            "mode": request.mode,
            "lot_id": lot_id,
            "artikel_id": (str(inv["artikel_id"]) if inv.get("artikel_id") is not None else None),
            "menge_kg": menge_kg,
            "status": status,
            "qs_status": str(qs) if qs is not None else status,
            "silozelle": None,
            "bewegungen": [
                {
                    "typ": str(row.get("typ") or ""),
                    "menge_kg": round(float(row.get("menge_kg") or 0.0), 3),
                    "notiz": (str(row["notiz"]) if row.get("notiz") is not None else None),
                    "zeit": (str(row["zeit"]) if row.get("zeit") is not None else None),
                }
                for row in movements
            ],
            "route_path": f"{_LOT_ROUTE_PREFIX}/{lot_id}",
            "screen_id": _LOT_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _dunning_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Customer dunning snapshot from open items + notices. Read-only — no dunning run."""
    del actor
    try:
        opened = CustomerOpenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid dunning status parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "fibu.dunning.status does not support propose")
    try:
        customer = _customer_in_tenant(db, kunden_nr=opened.kunden_nr, tenant=tenant)
        if not customer:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        customer_id = str(customer["id"])
        kunden_nr = str(customer["kunden_nr"] or opened.kunden_nr)
        params = {"tenant": tenant, "cid": customer_id, "nr": kunden_nr or None}

        op_level = int(_scalar_or_default(db, """
            SELECT COALESCE(MAX(COALESCE(mahn_stufe, 0)), 0)::int AS mahnstufe
            FROM domain_erp.offene_posten
            WHERE tenant_id::text = :tenant
              AND konto_typ = 'debitoren'
              AND COALESCE(op_status, '') NOT IN ('bezahlt', 'storniert', 'ausgeziffert')
              AND (
                    konto_nr = :nr
                 OR kunde_id::text = :cid
                 OR debtor_id::text = :cid
                 OR (:nr IS NOT NULL AND (
                        kunde_id::text = :nr OR debtor_id::text = :nr
                    ))
              )
        """, params, "mahnstufe", 0) or 0)

        gesamt_offen = float(_scalar_or_default(db, """
            SELECT COALESCE(SUM(COALESCE(offen, 0)), 0)::float AS gesamt_offen_eur
            FROM domain_erp.offene_posten
            WHERE tenant_id::text = :tenant
              AND konto_typ = 'debitoren'
              AND COALESCE(op_status, '') NOT IN ('bezahlt', 'storniert', 'ausgeziffert')
              AND (
                    konto_nr = :nr
                 OR kunde_id::text = :cid
                 OR debtor_id::text = :cid
                 OR (:nr IS NOT NULL AND (
                        kunde_id::text = :nr OR debtor_id::text = :nr
                    ))
              )
        """, params, "gesamt_offen_eur", 0.0) or 0.0)

        notices = _rows_or_empty(db, """
            SELECT dunning_date::text AS letzte_mahnung,
                   COALESCE(dunning_level, 0)::int AS dunning_level
            FROM domain_erp.dunning_notices
            WHERE tenant_id::text = :tenant
              AND (debtor_id::text = :cid OR (:nr IS NOT NULL AND debtor_id::text = :nr))
            ORDER BY dunning_date DESC NULLS LAST, dunning_level DESC
            LIMIT 1
        """, params)
        notice_level = 0
        letzte: str | None = None
        if notices:
            notice_level = int(notices[0].get("dunning_level") or 0)
            raw_date = notices[0].get("letzte_mahnung")
            letzte = str(raw_date) if raw_date is not None else None

        result = {
            "success": True,
            "mode": request.mode,
            "customer_id": customer_id,
            "kunden_nr": kunden_nr,
            "mahnstufe": max(op_level, notice_level),
            "letzte_mahnung": letzte,
            "gesamt_offen_eur": round(gesamt_offen, 2),
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _list_open_items(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """List open AR/AP items for the authenticated tenant. Read-only — no close/post."""
    del actor
    try:
        opened = OpenItemsListInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid open items list parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "fibu.open_items.list does not support propose")
    konto_typ = _OPEN_ITEM_KONTO_TYP[opened.typ]
    params: dict[str, Any] = {
        "tenant": tenant,
        "konto_typ": konto_typ,
        "lim": opened.limit,
        "faellig_bis": opened.faellig_bis.isoformat() if opened.faellig_bis else None,
    }
    try:
        rows = _rows_or_empty(db, """
            SELECT
                rechnungsnr AS beleg_nr,
                COALESCE(konto_nr, kunde_id::text) AS kunden_nr,
                COALESCE(offen, 0)::float AS betrag_eur,
                faelligkeit::text AS faellig_am,
                COALESCE(mahn_stufe, 0)::text AS mahnstatus
            FROM domain_erp.offene_posten
            WHERE tenant_id::text = :tenant
              AND konto_typ = :konto_typ
              AND COALESCE(op_status, '') NOT IN ('bezahlt', 'storniert', 'ausgeziffert')
              AND COALESCE(offen, 0) > 0
              AND (:faellig_bis IS NULL OR faelligkeit <= CAST(:faellig_bis AS date))
            ORDER BY faelligkeit ASC NULLS LAST, rechnungsnr ASC
            LIMIT :lim
        """, params)
        items = []
        for row in rows:
            items.append({
                "beleg_nr": str(row.get("beleg_nr") or ""),
                "kunden_nr": (str(row["kunden_nr"]) if row.get("kunden_nr") is not None else None),
                "betrag_eur": round(float(row.get("betrag_eur") or 0.0), 2),
                "faellig_am": (str(row["faellig_am"]) if row.get("faellig_am") is not None else None),
                "mahnstatus": str(row.get("mahnstatus") or "0"),
            })
        result = {
            "success": True,
            "mode": request.mode,
            "typ": opened.typ,
            "items": items,
            "count": len(items),
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _order_status(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Tenant-scoped sales order lifecycle status. Read-only."""
    del actor
    try:
        opened = OrderStatusInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid order status parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "sales.order.status does not support propose")
    try:
        order = db.execute(text("""
            SELECT id::text AS id,
                   order_number AS auftrag_nr,
                   COALESCE(status, 'open') AS status
            FROM domain_crm.sales_orders
            WHERE tenant_id::text = :tenant
              AND deleted_at IS NULL
              AND (order_number = :ref OR id::text = :ref)
            FOR SHARE
        """), {"tenant": tenant, "ref": opened.auftrag_nr}).mappings().first()
        if not order:
            raise HTTPException(404, "Sales order not found in the authenticated tenant")
        status_value = str(order["status"] or "open")
        if status_value in _ORDER_TERMINAL_STATUSES:
            offene_positionen = 0
        else:
            offene_positionen = int(_scalar_or_default(db, """
                SELECT COUNT(*)::int AS offene_positionen
                FROM domain_crm.sales_order_items
                WHERE order_id::text = :oid
                  AND tenant_id::text = :tenant
                  AND COALESCE(quantity, 0) > 0
            """, {"oid": order["id"], "tenant": tenant}, "offene_positionen", 0) or 0)
        order_id = str(order["id"])
        result = {
            "success": True,
            "mode": request.mode,
            "order_id": order_id,
            "auftrag_nr": str(order["auftrag_nr"] or opened.auftrag_nr),
            "status": status_value,
            "offene_positionen": offene_positionen,
            "naechster_schritt": _order_next_step(status_value),
            "route_path": f"{_ORDER_ROUTE_PREFIX}/{order_id}",
            "screen_id": _ORDER_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _customer_summary360(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Compact 360 summary for agents — same aggregates as CRM screen-summary, tenant-strict.

    Identity uses domain_crm.customers only (no public.kunden fallback from UI helpers).
    """
    del actor
    try:
        opened = CustomerOpenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid customer summary360 parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "crm.customer.summary360 does not support propose")
    try:
        customer = _customer_in_tenant(db, kunden_nr=opened.kunden_nr, tenant=tenant)
        if not customer:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        customer_id = str(customer["id"])
        kunden_nr = str(customer["kunden_nr"] or opened.kunden_nr)
        name = str(customer["name"] or kunden_nr)
        params = {"cid": customer_id, "nr": kunden_nr or None, "tenant": tenant, "kunde": name}

        offene_auftraege = int(_scalar_or_default(db, """
            SELECT COUNT(*)::int AS offene_auftraege
            FROM domain_crm.sales_orders
            WHERE (
                    customer_id::text = :cid
                 OR (:nr IS NOT NULL AND customer_id::text = :nr)
                  )
              AND tenant_id::text = :tenant
              AND deleted_at IS NULL
              AND COALESCE(status, '') NOT IN ('cancelled', 'completed', 'storniert')
        """, params, "offene_auftraege", 0) or 0)

        op_saldo = float(_scalar_or_default(db, """
            SELECT COALESCE(SUM(offen), 0)::float AS op_saldo_eur
            FROM domain_erp.offene_posten
            WHERE (
                    kunde_id::text = :cid
                 OR debtor_id::text = :cid
                 OR (:nr IS NOT NULL AND (
                        kunde_id::text = :nr OR debtor_id::text = :nr
                    ))
                  )
              AND tenant_id::text = :tenant
              AND COALESCE(op_status, '') NOT IN ('bezahlt', 'storniert')
        """, params, "op_saldo_eur", 0.0) or 0.0)

        contacts = _rows_or_empty(db, """
            SELECT id::text AS id,
                   type AS kanal,
                   title AS betreff,
                   COALESCE(date, created_at)::text AS erfasst_am
            FROM domain_crm.activities
            WHERE customer = :kunde
              AND tenant_id::text = :tenant
            ORDER BY COALESCE(date, created_at) DESC NULLS LAST
            LIMIT 5
        """, {"kunde": name, "tenant": tenant})

        segment = None
        partner_id = customer.get("business_partner_id")
        if partner_id:
            segment = _scalar_or_default(db, """
                SELECT marketing_segment AS segment
                FROM domain_crm.business_partners
                WHERE partner_id::text = :pid
                  AND tenant_id::text = :tenant
                LIMIT 1
            """, {"pid": partner_id, "tenant": tenant}, "segment", None)
            if segment is not None:
                segment = str(segment)

        result = {
            "success": True,
            "mode": request.mode,
            "customer_id": customer_id,
            "kunden_nr": kunden_nr,
            "name": name,
            "offene_auftraege": offene_auftraege,
            "op_saldo_eur": round(op_saldo, 2),
            "letzte_kontakte": contacts,
            "segment": segment,
            "route_path": f"{_CUSTOMER_ROUTE_PREFIX}/{customer_id}",
            "screen_id": _CUSTOMER_SCREEN_ID,
        }
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _open_customer(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Resolve a tenant-scoped customer and return the canonical mask route.

    Read-only: neither dryRun nor execute persist MCP execution rows or mutate CRM.
    """
    del actor  # identity already verified by execute_mcp_tool
    try:
        opened = CustomerOpenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid customer open parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "crm.customer.open does not support propose")
    try:
        customer = _customer_in_tenant(db, kunden_nr=opened.kunden_nr, tenant=tenant)
        if not customer:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        customer_id = str(customer["id"])
        kunden_nr = str(customer["kunden_nr"] or opened.kunden_nr)
        name = str(customer["name"] or kunden_nr)
        result = {
            "success": True,
            "mode": request.mode,
            "customer_id": customer_id,
            "kunden_nr": kunden_nr,
            "name": name,
            "route_path": f"{_CUSTOMER_ROUTE_PREFIX}/{customer_id}",
            "screen_id": _CUSTOMER_SCREEN_ID,
        }
        db.rollback()  # release FOR SHARE; no writes
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _log_contact(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    try:
        contact = ContactLogInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid contact log parameters") from exc
    parameters = contact.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            # Serializes identical keys across processes, including the first call.
            lock_bytes = hashlib.sha256(json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()).digest()[:8]
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})
            previous = db.execute(text("""
                SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
                WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
            """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key}).mappings().first()
            if previous:
                if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                    raise HTTPException(409, "Idempotency key is already bound to another request")
                result = previous["result"]
                if isinstance(result, str):
                    result = json.loads(result)
                db.rollback()  # Release the transaction lock without another write.
                return {**result, "replayed": True}
        exists = db.execute(text("""SELECT 1 FROM public.kunden k
            JOIN domain_crm.business_partners bp ON bp.partner_id = CAST(k.business_partner_id AS text)
            WHERE k.kunden_nr=:customer AND bp.tenant_id=:tenant FOR SHARE OF k, bp"""),
                            {"customer": contact.kunden_nr, "tenant": tenant}).first()
        if not exists:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        # The existing UI service commits. A child Session confines that commit to
        # a SAVEPOINT so the contact, audit and replay record remain atomic.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            saved = CrmKontaktService(child, tenant).create({
                "kunden_nr": contact.kunden_nr, "art": contact.kanal,
                "notiz": contact.ergebnis, "wiedervorlage": parameters["wiedervorlage_datum"],
                "bediener": actor,
            })
        audit_id = _write_audit(db, tenant_id=tenant, action_key=request.tool_name,
                               entity_type="customer_contact", entity_id=saved["id"],
                               audit_reason="MCP contact log", idempotency_key=request.idempotency_key,
                               summary=f"Contact logged by {actor}")
        result = {"success": True, "mode": "execute", "replayed": False,
                  "kontakt_id": saved["id"], "erfasst_am": saved["created_at"], "auditEntryId": audit_id}
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
                 "actor": actor, "hash": fingerprint, "result": json.dumps(result)})
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _money(totals: Any, key: str) -> float:
    if isinstance(totals, str):
        totals = json.loads(totals)
    if not isinstance(totals, dict) or totals.get(key) is None:
        raise HTTPException(409, "Delivery note has no stored totals")
    return round(float(totals[key]), 2)


_AP_INVOICE_ROUTE_PREFIX = "/finance/ap-invoice"
_AP_INVOICE_SCREEN_ID = "finance/ap-invoice"
_AP_FREIGABE_ACTION_TYPE = "ap_invoice_freigabe"
_AP_FREIGABE_BLOCKED_STATUSES = frozenset({
    "FREIGEGEBEN", "VERBUCHT", "BEZAHLT", "ABGELEHNT", "posted", "approved", "paid",
})


def _load_ap_invoice(db: Session, invoice_id: str, tenant: str) -> dict[str, Any]:
    """Tenant-scoped AP invoice from the document store (same path as mask freigeben)."""
    from app.api.v1.endpoints.ap_approval_workflow import _ensure_invoice_tenant_access
    from app.documents.router_helpers import get_from_store, get_repository

    return _ensure_invoice_tenant_access(
        get_from_store("ap_invoice", invoice_id, get_repository(db)),
        tenant,
    )


def _ap_invoice_preview(invoice: dict[str, Any], invoice_id: str) -> dict[str, Any]:
    status = str(invoice.get("status") or invoice.get("semantic_status") or "")
    brutto = invoice.get("totalGross")
    if brutto is None:
        brutto = invoice.get("brutto")
    try:
        brutto_eur = round(float(brutto), 2) if brutto is not None else None
    except (TypeError, ValueError):
        brutto_eur = None
    return {
        "invoice_id": invoice_id,
        "invoice_number": str(invoice.get("number") or invoice_id),
        "status": status,
        "brutto_eur": brutto_eur,
        "route_path": f"{_AP_INVOICE_ROUTE_PREFIX}/{invoice_id}",
        "screen_id": _AP_INVOICE_SCREEN_ID,
    }


def _propose_ap_freigabe(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Store a pending AP-freigabe proposal. Never calls the freigeben endpoint."""
    try:
        opened = ApInvoiceProposeInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid AP invoice propose parameters") from exc
    if request.mode == "execute":
        raise HTTPException(501, "AP freigabe is not an MCP execution on propose; use finance.ap_invoice.freigeben")
    parameters = opened.model_dump(mode="json")
    if request.mode == "propose" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "propose requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "propose":
            lock_bytes = hashlib.sha256(
                json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()
            ).digest()[:8]
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})
            previous = db.execute(text("""
                SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
                WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
            """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key}).mappings().first()
            if previous:
                if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                    raise HTTPException(409, "Idempotency key is already bound to another request")
                result = previous["result"]
                if isinstance(result, str):
                    result = json.loads(result)
                db.rollback()
                return {**result, "replayed": True}
        invoice = _load_ap_invoice(db, opened.invoice_id, tenant)
        preview = _ap_invoice_preview(invoice, opened.invoice_id)
        status_upper = str(preview["status"] or "").upper()
        if status_upper in {s.upper() for s in _AP_FREIGABE_BLOCKED_STATUSES}:
            raise HTTPException(409, f"AP invoice status {preview['status']} cannot be proposed for freigabe")
        if request.mode != "propose":
            return {"success": True, "mode": request.mode, "approved": False, **preview}
        proposal_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        db.execute(text("""
            INSERT INTO public.agent_proposals
                (proposal_id, tenant_id, action_type, risk_level, approval_status,
                 context_snapshot, rationale, idempotency_key, created_at)
            VALUES
                (:id, :tenant, 'ap_invoice_freigabe', 'high', 'pending',
                 CAST(:snapshot AS json), :rationale, :key, :now)
        """), {
            "id": proposal_id,
            "tenant": tenant,
            "snapshot": json.dumps({
                "context_summary": f"AP-Freigabe {preview['invoice_number']}",
                "proposed_action": "Eingangsrechnung freigeben (nach menschlicher Freigabe)",
                "human_approval_required": True,
                "audit_events": [{"event": "proposal_created", "occurred_at": now}],
                "invoice_id": opened.invoice_id,
                "actor_id": actor,
                "payload_hash": fingerprint,
                **preview,
            }),
            "rationale": "MCP finance.ap_invoice.propose",
            "key": hashlib.sha256(f"{tenant}|{request.tool_name}|{request.idempotency_key}".encode()).hexdigest(),
            "now": now,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="ap_invoice_proposal", entity_id=proposal_id,
            audit_reason="MCP AP freigabe proposal", idempotency_key=request.idempotency_key,
            summary=f"AP freigabe proposal for {opened.invoice_id} by {actor}",
        )
        result = {
            "success": True, "mode": "propose", "replayed": False, "approved": False,
            "entwurf_id": proposal_id, "approval_status": "pending", "auditEntryId": audit_id,
            **preview,
        }
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {
            "tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
            "actor": actor, "hash": fingerprint, "result": json.dumps(result),
        })
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _freigeben_ap_invoice(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Call the real AP freigeben CommandEndpoint only after an approved proposal."""
    try:
        payload = ApInvoiceFreigebenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid AP invoice freigeben parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "finance.ap_invoice.freigeben does not accept propose; use finance.ap_invoice.propose")
    parameters = payload.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        proposal = db.execute(text("""
            SELECT proposal_id, action_type, approval_status, risk_level,
                   context_snapshot, execution_result
            FROM public.agent_proposals
            WHERE proposal_id=:id AND tenant_id=:tenant
            FOR UPDATE OF agent_proposals
        """), {"id": payload.proposal_id, "tenant": tenant}).mappings().first()
        if not proposal:
            raise HTTPException(404, "Proposal not found in the authenticated tenant")
        if proposal["action_type"] != _AP_FREIGABE_ACTION_TYPE:
            raise HTTPException(409, "Proposal is not an AP freigabe proposal")
        if proposal["approval_status"] != "approved":
            raise HTTPException(409, "Proposal is not approved")
        if proposal["execution_result"] is not None:
            existing = proposal["execution_result"]
            if isinstance(existing, str):
                existing = json.loads(existing)
            if isinstance(existing, dict) and existing.get("invoice_id"):
                if request.mode != "execute":
                    return {
                        "success": True, "mode": request.mode, "approved": False,
                        "already_executed": True,
                        **{k: existing[k] for k in ("invoice_id", "invoice_number", "status") if k in existing},
                    }
                raise HTTPException(409, "Proposal was already executed")
        snapshot = proposal["context_snapshot"] or {}
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        if not isinstance(snapshot, dict):
            raise HTTPException(409, "Proposal snapshot is unusable")
        invoice_id = snapshot.get("invoice_id")
        if not isinstance(invoice_id, str) or not invoice_id.strip():
            raise HTTPException(409, "Proposal snapshot lacks invoice_id")
        invoice = _load_ap_invoice(db, invoice_id, tenant)
        preview = _ap_invoice_preview(invoice, invoice_id)
        preview["proposal_id"] = payload.proposal_id
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "approved": False, **preview}
        from app.api.v1.endpoints.ap_invoices import approve_ap_invoice

        user = {"sub": actor}
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            asyncio.run(
                approve_ap_invoice(
                    invoice_id,
                    approved_by=None,
                    db=child,
                    tenant_id=tenant,
                    user=user,
                )
            )
        refreshed = _load_ap_invoice(db, invoice_id, tenant)
        final_preview = _ap_invoice_preview(refreshed, invoice_id)
        execution_result = {
            "invoice_id": invoice_id,
            "invoice_number": final_preview["invoice_number"],
            "status": final_preview["status"],
            "executed_by": actor,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        db.execute(text("""
            UPDATE public.agent_proposals
            SET execution_result = CAST(:result AS json)
            WHERE proposal_id = :id AND tenant_id = :tenant
        """), {"result": json.dumps(execution_result), "id": payload.proposal_id, "tenant": tenant})
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="ap_invoice", entity_id=invoice_id,
            audit_reason="MCP AP freigabe from approved proposal",
            idempotency_key=request.idempotency_key,
            summary=f"AP freigabe {invoice_id} from proposal {payload.proposal_id} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False, "approved": True,
            "proposal_id": payload.proposal_id, "auditEntryId": audit_id,
            "fibu_journal": False,
            **final_preview,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _propose_invoice(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Store a pending invoice proposal. This call never posts an invoice."""
    try:
        invoice = InvoiceProposeInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid invoice proposal parameters") from exc
    if request.mode == "execute":
        raise HTTPException(501, "Invoice posting is not an MCP execution")
    parameters = invoice.model_dump(mode="json")
    if request.mode == "propose" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "propose requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "propose":
            lock_bytes = hashlib.sha256(
                json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()
            ).digest()[:8]
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})
            previous = db.execute(text("""
                SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
                WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
            """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key}).mappings().first()
            if previous:
                if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                    raise HTTPException(409, "Idempotency key is already bound to another request")
                result = previous["result"]
                if isinstance(result, str):
                    result = json.loads(result)
                db.rollback()
                return {**result, "replayed": True}
        note = db.execute(text("""
            SELECT n.id, n.status, n.totals,
                   (SELECT COUNT(*) FROM domain_sales.delivery_note_positions p
                    WHERE p.delivery_note_id = n.id) AS positionen
            FROM domain_sales.delivery_notes n
            WHERE n.tenant_id=:tenant AND n.delivery_note_number=:nr
            FOR SHARE OF n
        """), {"tenant": tenant, "nr": invoice.lieferschein_nr}).mappings().first()
        if not note:
            raise HTTPException(404, "Delivery note not found in the authenticated tenant")
        if note["status"] not in _BILLABLE_DELIVERY_STATUSES:
            raise HTTPException(409, "Delivery note is not ready to invoice")
        preview = {
            "betrag_netto": _money(note["totals"], "netto"),
            "mwst": _money(note["totals"], "mwst"),
            "positionen": int(note["positionen"] or 0),
        }
        if request.mode != "propose":
            return {"success": True, "mode": request.mode, "posted": False, **preview}
        proposal_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        db.execute(text("""
            INSERT INTO public.agent_proposals
                (proposal_id, tenant_id, action_type, risk_level, approval_status,
                 context_snapshot, rationale, idempotency_key, created_at)
            VALUES
                (:id, :tenant, 'rechnung_vorschlag', 'high', 'pending',
                 CAST(:snapshot AS json), :rationale, :key, :now)
        """), {
            "id": proposal_id,
            "tenant": tenant,
            "snapshot": json.dumps({
                "context_summary": f"Lieferschein {invoice.lieferschein_nr}",
                "proposed_action": "Rechnung vorschlagen, nicht buchen",
                "human_approval_required": True,
                "audit_events": [{"event": "proposal_created", "occurred_at": now}],
                "lieferschein_nr": invoice.lieferschein_nr,
                "rechnungsdatum": parameters["rechnungsdatum"],
                "actor_id": actor,
                "payload_hash": fingerprint,
                **preview,
            }),
            "rationale": "MCP sales.invoice.propose",
            "key": hashlib.sha256(f"{tenant}|{request.tool_name}|{request.idempotency_key}".encode()).hexdigest(),
            "now": now,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="sales_invoice_proposal", entity_id=proposal_id,
            audit_reason="MCP invoice proposal", idempotency_key=request.idempotency_key,
            summary=f"Invoice proposal for {invoice.lieferschein_nr} by {actor}",
        )
        result = {
            "success": True, "mode": "propose", "replayed": False, "posted": False,
            "entwurf_id": proposal_id, "approval_status": "pending", "auditEntryId": audit_id,
            **preview,
        }
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {
            "tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
            "actor": actor, "hash": fingerprint, "result": json.dumps(result),
        })
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _create_activity(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    try:
        activity = ActivityCreateInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid activity parameters") from exc
    parameters = activity.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        customer = _customer_in_tenant(db, kunden_nr=activity.kunden_nr, tenant=tenant)
        if not customer:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        activity_id = str(uuid4())
        now = datetime.now(timezone.utc)
        verantwortlich = (activity.verantwortlich or actor)[:100]
        db.execute(text("""
            INSERT INTO domain_crm.activities
              (id, type, title, customer, contact_person, date, status, assigned_to, description, tenant_id)
            VALUES
              (:aid, :typ, :titel, :kunde, :person, :datum, 'offen', :verantwortlich, :notiz, :tid)
        """), {
            "aid": activity_id,
            "typ": activity.typ[:20],
            "titel": activity.betreff[:200],
            "kunde": str(customer["name"] or customer["kunden_nr"] or activity.kunden_nr)[:100],
            "person": verantwortlich,
            "datum": parameters["datum"] or now.date().isoformat(),
            "verantwortlich": verantwortlich,
            "notiz": activity.notiz,
            "tid": tenant,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="crm_activity", entity_id=activity_id,
            audit_reason="MCP activity create", idempotency_key=request.idempotency_key,
            summary=f"Activity '{activity.betreff}' by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "activity_id": activity_id, "erfasst_am": now.isoformat(), "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _resolve_customer_id(db: Session, *, tenant: str, customer_id: str | None, kunden_nr: str | None) -> str:
    if customer_id:
        row = db.execute(text("""
            SELECT id::text AS id FROM domain_crm.customers
            WHERE tenant_id::text = :tenant AND id::text = :cid AND deleted_at IS NULL
            FOR SHARE
        """), {"tenant": tenant, "cid": customer_id}).mappings().first()
        if not row:
            raise HTTPException(422, "Customer not found in the authenticated tenant")
        return str(row["id"])
    assert kunden_nr is not None
    customer = _customer_in_tenant(db, kunden_nr=kunden_nr, tenant=tenant)
    if not customer:
        raise HTTPException(422, "Customer not found in the authenticated tenant")
    return str(customer["id"])


def _qualify_lead(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Qualify lead → opportunity via crm_lead_service (same path as mask action)."""
    try:
        opened = LeadQualifyInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid lead qualify parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        customer_id = _resolve_customer_id(
            db, tenant=tenant, customer_id=opened.customer_id, kunden_nr=opened.kunden_nr,
        )
        crm_lead_service.qualification_inputs(db, tenant, opened.lead_id, customer_id, lock=False)
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {**parameters, "customer_id": customer_id},
            }
        opportunity_id = crm_lead_service.qualify(db, tenant, opened.lead_id, customer_id)
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="crm_lead", entity_id=opened.lead_id,
            audit_reason="MCP lead qualify", idempotency_key=request.idempotency_key,
            summary=f"Lead {opened.lead_id} qualified → opportunity {opportunity_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "lead_id": opened.lead_id,
            "opportunity_id": opportunity_id,
            "customer_id": customer_id,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _bestellung_versenden(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Send purchase order via ProcurementService (email/fax/edi/manual) — no obligo journal."""
    try:
        opened = BestellungVersendenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid purchase order send parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        resolved = db.execute(text("""
            SELECT id::text AS id, bestellnummer, status
            FROM domain_einkauf.bestellungen
            WHERE tenant_id::text = :tenant
              AND (id::text = :bid OR bestellnummer = :bid)
            FOR SHARE
            LIMIT 1
        """), {"tenant": tenant, "bid": opened.bestellung_id}).mappings().first()
        if not resolved:
            raise HTTPException(404, "Purchase order not found in the authenticated tenant")
        bestellung_id = str(resolved["id"])
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "bestellung_id": bestellung_id,
                    "bestellnummer": resolved.get("bestellnummer"),
                    "status": resolved.get("status"),
                },
            }
        # ProcurementService commits; confine to SAVEPOINT so audit/replay stay atomic.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            sent = ProcurementService(child, tenant).versende_bestellung_svc(
                bestellung_id, opened.versand_art, opened.empfaenger,
            )
        versand = sent.get("versand") if isinstance(sent, dict) else None
        versand_status = (
            str(versand.get("status")) if isinstance(versand, dict) and versand.get("status") is not None
            else "gesendet"
        )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="einkauf_bestellung", entity_id=bestellung_id,
            audit_reason="MCP purchase order send", idempotency_key=request.idempotency_key,
            summary=f"Bestellung {sent.get('bestellnummer') or bestellung_id} versandt ({opened.versand_art}) by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "bestellung_id": bestellung_id,
            "bestellnummer": sent.get("bestellnummer"),
            "versand_status": versand_status,
            "versand_art": opened.versand_art,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(404, "Purchase order not found in the authenticated tenant") from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _ration_transition(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Ration lifecycle step via RationLifecycleService (mask agrar/ration:*)."""
    try:
        opened = RationTransitionInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar.ration.transition parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    target = _RATION_MCP_TARGETS[opened.action_key]
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        detail = RationLifecycleService(db, tenant, actor).get_ration(
            opened.ration_id, include_audit=False,
        )
        version_id = str(detail["latest_version_id"])
        current_status = str(detail["latest_status"])
        expected = RationStatus(opened.expected_status or current_status)
        if expected.value != current_status:
            raise HTTPException(
                409,
                f"Status conflict: expected {expected.value}, current {current_status}",
            )
        try:
            validate_transition(
                expected, target, reason=opened.reason, feeding_start=opened.feeding_start,
            )
        except TransitionError as exc:
            raise HTTPException(422, str(exc)) from exc
        blockers = int(detail.get("latest_readiness_blockers") or 0)
        if (
            target in {RationStatus.APPROVED, RationStatus.ACTIVE}
            and blockers > 0
            and not (opened.reason or "").startswith("OVERRIDE:")
        ):
            raise HTTPException(
                422,
                f"Readiness blocks this step ({blockers} finding(s)); use reason starting with OVERRIDE:",
            )
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "version_id": version_id,
                    "from_status": current_status,
                    "to_status": target.value,
                },
            }
        # Service commits; confine to SAVEPOINT for audit/replay atomicity.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            result_row = RationLifecycleService(child, tenant, actor).transition(
                version_id=version_id,
                target=target,
                expected_status=expected,
                reason=opened.reason,
                feeding_start=opened.feeding_start,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="agrar_ration", entity_id=opened.ration_id,
            audit_reason="MCP ration lifecycle transition", idempotency_key=request.idempotency_key,
            summary=(
                f"Ration {opened.ration_id} version {version_id}: "
                f"{current_status}→{target.value} ({opened.action_key}) by {actor}"
            ),
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "ration_id": opened.ration_id,
            "version_id": version_id,
            "from_status": current_status,
            "to_status": target.value,
            "action_key": opened.action_key,
            "superseded_version_ids": result_row.get("superseded_version_ids") or [],
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except RationLifecycleNotFound as exc:
        db.rollback()
        raise HTTPException(404, "Ration not found in the authenticated tenant") from exc
    except (RationLifecycleConflict, TransitionError) as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _feeding_supply_handoff(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Procurement handoff from feed readiness (mask agrar/feed-readiness:create_handoff)."""
    try:
        opened = FeedingSupplyHandoffInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar.feeding.supply_handoff parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        svc = FeedingSupplyService(db, tenant, actor)
        projection = next(
            (
                row
                for row in svc.project(
                    horizon_days=opened.horizon_days,
                    safety_pct=opened.safety_pct,
                    subject=actor,
                    unrestricted=True,
                )
                if row["plan_version_id"] == opened.plan_version_id
                and row["feed_id"] == opened.feed_id
            ),
            None,
        )
        if not projection:
            raise HTTPException(404, "Current plan demand not found for this tenant")
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "group_id": projection.get("group_id"),
                    "shortage_kg": projection.get("shortage_kg"),
                    "suggested_order_kg": projection.get("suggested_order_kg"),
                },
            }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            row = FeedingSupplyService(child, tenant, actor).create_handoff(
                plan_version_id=opened.plan_version_id,
                feed_id=opened.feed_id,
                horizon_days=opened.horizon_days,
                safety_pct=opened.safety_pct,
                idempotency_key=request.idempotency_key,  # type: ignore[arg-type]
                reason=opened.reason,
                subject=actor,
                unrestricted=True,
            )
        handoff_id = str(row.get("id") or "")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="feeding_supply_handoff", entity_id=handoff_id,
            audit_reason="MCP feeding supply handoff", idempotency_key=request.idempotency_key,
            summary=f"Handoff {handoff_id} plan={opened.plan_version_id} feed={opened.feed_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "handoff_id": handoff_id,
            "plan_version_id": opened.plan_version_id,
            "feed_id": opened.feed_id,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except FeedingSupplyNotFound as exc:
        db.rollback()
        raise HTTPException(404, str(exc)) from exc
    except FeedingSupplyConflict as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _feeding_actual_measure(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Create measure from feeding deviation (mask agrar/feeding-actuals:create_measure)."""
    try:
        opened = FeedingActualMeasureInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar.feeding.actual_measure parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        group_ids = [
            str(row["id"])
            for row in db.execute(
                text("SELECT id::text AS id FROM domain_agrar.feeding_groups WHERE tenant_id = :tid"),
                {"tid": tenant},
            ).mappings().all()
        ]
        measure_svc = FeedingActualMeasureService(db, tenant, actor)
        finding = next(
            (
                item
                for item in measure_svc.findings(group_ids=group_ids)
                if item["actual_component_id"] == opened.actual_component_id
            ),
            None,
        )
        if not finding or finding.get("severity") not in {"warning", "critical"}:
            raise HTTPException(422, "No actionable deviation finding for this component")
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "group_id": finding.get("group_id"),
                    "severity": finding.get("severity"),
                },
            }
        payload = {
            "actual_component_id": opened.actual_component_id,
            "title": opened.title,
            "owner_subject": opened.owner_subject or actor,
            "due_date": opened.due_date,
            "reason": opened.reason,
            "idempotency_key": request.idempotency_key,
        }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            row = FeedingActualMeasureService(child, tenant, actor).create_measure(
                payload, group_ids=group_ids,
            )
        measure_id = str(row.get("id") or "")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="feeding_actual_measure", entity_id=measure_id,
            audit_reason="MCP feeding actual measure", idempotency_key=request.idempotency_key,
            summary=f"Measure {measure_id} for component {opened.actual_component_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "measure_id": measure_id,
            "actual_component_id": opened.actual_component_id,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except ActualMeasureConflict as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _feeding_configure_threshold(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Create deviation policy version (mask agrar/feeding-actuals:configure_threshold)."""
    try:
        opened = FeedingConfigureThresholdInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar.feeding.configure_threshold parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        try:
            from app.agrar.rations.actual_measures import validate_thresholds
            validate_thresholds(opened.warning_pct, opened.critical_pct)
        except DeviationPolicyError as exc:
            raise HTTPException(422, str(exc)) from exc
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": parameters,
            }
        payload = {
            "feed_class": opened.feed_class,
            "warning_pct": opened.warning_pct,
            "critical_pct": opened.critical_pct,
            "valid_from": opened.valid_from,
            "reason": opened.reason,
        }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            row = FeedingActualMeasureService(child, tenant, actor).create_policy(payload)
        policy_id = str(row.get("id") or "")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="feeding_deviation_policy", entity_id=policy_id,
            audit_reason="MCP feeding threshold configure", idempotency_key=request.idempotency_key,
            summary=(
                f"Policy {opened.feed_class} v{row.get('version')} "
                f"warn={opened.warning_pct} crit={opened.critical_pct} by {actor}"
            ),
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "policy_id": policy_id,
            "feed_class": opened.feed_class,
            "version": row.get("version"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except DeviationPolicyError as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _feed_analysis_transition(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Release or reject feed analysis (mask futtermittel/analyse:release|reject)."""
    try:
        opened = FeedAnalysisTransitionInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid agrar.feed_analysis.transition parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    target = _FEED_ANALYSIS_TARGETS[opened.action_key]
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        current = FeedingFeedAnalysisService(db, tenant, actor).get_analysis(opened.analysis_id)
        from_status = str(current.get("status") or "")
        revision = int(current.get("revision") or 0)
        blockers = [
            f.get("message") for f in (current.get("findings") or [])
            if f.get("severity") == "blocker"
        ]
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "from_status": from_status,
                    "to_status": target.value,
                    "revision": revision,
                    "blockingReasons": blockers,
                },
            }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            changed = FeedingFeedAnalysisService(child, tenant, actor).transition(
                opened.analysis_id, target, revision, opened.reason,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="grundfutter_analyse", entity_id=opened.analysis_id,
            audit_reason="MCP feed analysis transition", idempotency_key=request.idempotency_key,
            summary=(
                f"Analysis {opened.analysis_id}: {from_status}→{changed.get('status')} "
                f"({opened.action_key}) by {actor}"
            ),
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "analysis_id": opened.analysis_id,
            "from_status": from_status,
            "to_status": str(changed.get("status") or target.value),
            "revision": changed.get("revision"),
            "action_key": opened.action_key,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except FeedAnalysisNotFound as exc:
        db.rollback()
        raise HTTPException(404, "Feed analysis not found in the authenticated tenant") from exc
    except FeedAnalysisConflict as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _reklamation_abschliessen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Close quality complaint (mask qualitaet/reklamation:abschliessen)."""
    try:
        opened = ReklamationAbschliessenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid qualitaet.reklamation.abschliessen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        try:
            zeile = _query_reklamation(db, opened.reklamation_id, tenant)
        except HTTPException as exc:
            if exc.status_code == 404:
                raise HTTPException(404, "Complaint not found in the authenticated tenant") from exc
            raise
        from_status = str(zeile.status)
        try:
            ReklamationZustandsmaschine.pruefe_statuswechsel(
                ReklamationsStatus(from_status), ReklamationsStatus.GESCHLOSSEN,
            )
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "from_status": from_status,
                    "to_status": ReklamationsStatus.GESCHLOSSEN.value,
                },
            }
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            transition_status(
                opened.reklamation_id,
                ReklamationTransitionRequest(
                    neuer_status=ReklamationsStatus.GESCHLOSSEN.value,
                    aktor_id=actor,
                    kommentar=opened.kommentar,
                ),
                db=child,
                tenant_id=tenant,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="reklamation", entity_id=opened.reklamation_id,
            audit_reason="MCP complaint close", idempotency_key=request.idempotency_key,
            summary=f"Reklamation {opened.reklamation_id} geschlossen by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "reklamation_id": opened.reklamation_id,
            "status": ReklamationsStatus.GESCHLOSSEN.value,
            "from_status": from_status,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _produktion_control_sync(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Sync production orders into Leitstand (mask produktion/produktionsleitstand:sync)."""
    try:
        opened = ProduktionControlSyncInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid produktion.control.sync parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            stats = ProductionControlService(child, tenant).sync_production_orders(
                actor=actor, reason=opened.reason,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="production_control", entity_id=tenant,
            audit_reason="MCP production control sync", idempotency_key=request.idempotency_key,
            summary=f"Produktionsleitstand sync ({stats.get('synchronized')} rows) by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "synchronized": stats.get("synchronized"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _planung_calendar_reproject(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Reproject planning calendar (mask planung/kalender:reproject)."""
    try:
        opened = PlanungCalendarReprojectInput.model_validate(request.parameters or {})
    except ValidationError as exc:
        raise HTTPException(422, "Invalid planung.calendar.reproject parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            stats = CalendarProjectionService(child).reproject(
                tenant, horizon_days=opened.horizon_days,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="planung_kalender", entity_id=tenant,
            audit_reason="MCP calendar reproject", idempotency_key=request.idempotency_key,
            summary=f"Kalender reproject horizon={opened.horizon_days} projected={stats.get('projected')} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "projected": stats.get("projected"),
            "horizon_days": opened.horizon_days,
            "sources": stats.get("sources"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _mobile_sync_process_pending(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Process pending MDE queue events (mask schnittstelle/mde-inbox:process_pending)."""
    try:
        opened = MobileSyncProcessPendingInput.model_validate(request.parameters or {})
    except ValidationError as exc:
        raise HTTPException(422, "Invalid mobile.sync.process_pending parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            stats = MobileSyncService(child, tenant).process_pending(
                limit=opened.limit, actor=actor, reason=opened.reason,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="mobile_event_queue", entity_id=tenant,
            audit_reason="MCP mobile sync process", idempotency_key=request.idempotency_key,
            summary=(
                f"MDE queue processed={stats.get('processed')} failed={stats.get('failed')} "
                f"by {actor}"
            ),
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "processed": stats.get("processed"),
            "failed": stats.get("failed"),
            "skipped": stats.get("skipped"),
            "total": stats.get("total"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _angebot_bestellen(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Convert supplier quote → purchase order (same path as mask einkauf/angebot:bestellen)."""
    try:
        opened = AngebotBestellenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid angebot.bestellen parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        svc = EinkaufCompatService(db, tenant)
        row = svc._load_angebot_raw_row(opened.angebot_id)
        if row is None:
            raise HTTPException(404, "Offer not found in the authenticated tenant")
        m = row._mapping
        angebot_id = str(m.get("id"))
        status = str(m.get("status") or "").upper()
        if status in _NICHT_BESTELLBAR:
            raise HTTPException(409, f"Offer status {status} cannot be ordered")
        pos_count = db.execute(
            text("SELECT COUNT(*) FROM einkauf_angebote_positionen WHERE angebot_id = :id"),
            {"id": angebot_id},
        ).scalar()
        if not pos_count:
            raise HTTPException(422, "Offer without positions cannot be ordered")
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "angebot_id": angebot_id,
                    "angebots_nummer": m.get("angebots_nummer"),
                    "status": m.get("status"),
                    "positionen": int(pos_count),
                },
            }
        # convert_angebot_to_order commits; confine to SAVEPOINT for audit/replay atomicity.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            ergebnis = asyncio.run(
                EinkaufCompatService(child, tenant).convert_angebot_to_order(angebot_id)
            )
        bestellung_id = str(ergebnis.get("purchaseOrderId") or "")
        bestellnummer = ergebnis.get("purchaseOrderNumber")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="einkauf_angebot", entity_id=angebot_id,
            audit_reason="MCP offer to purchase order", idempotency_key=request.idempotency_key,
            summary=f"Angebot {angebot_id} → Bestellung {bestellnummer or bestellung_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "angebot_id": angebot_id,
            "bestellung_id": bestellung_id,
            "bestellnummer": bestellnummer,
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(404, "Offer not found in the authenticated tenant") from exc
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _anlieferavis_wareneingang(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Book goods receipt from delivery advice — inventory only, no FIBU journal."""
    try:
        opened = AnlieferavisWareneingangInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid anlieferavis.wareneingang parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        try:
            offen = pruefe_wareneingang(
                db, opened.avis_id, tenant, opened.lager_id, opened.lieferschein_nr,
            )
        except WareneingangAvisError as exc:
            raise HTTPException(422, str(exc)) from exc
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "positionen_offen": len(offen),
                },
            }
        # Service commits; confine to SAVEPOINT so audit/replay stay atomic.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            ergebnis = buche_wareneingang_aus_avis(
                child, opened.avis_id, tenant, opened.lager_id, opened.lieferschein_nr, operator=actor,
            )
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="einkauf_anlieferavis", entity_id=opened.avis_id,
            audit_reason="MCP goods receipt from delivery advice", idempotency_key=request.idempotency_key,
            summary=(
                f"Wareneingang Avis {opened.avis_id} → Bestellung {ergebnis.get('bestellnummer')} "
                f"({ergebnis.get('positionen')} Pos.) by {actor}"
            ),
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "avis_id": opened.avis_id,
            "bestellung_id": ergebnis.get("bestellung_id"),
            "bestellnummer": ergebnis.get("bestellnummer"),
            "positionen": ergebnis.get("positionen"),
            "lieferschein_nr": ergebnis.get("lieferschein_nr"),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except WareneingangAvisError as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _stock_movement_stornieren(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Reverse a stock movement via Gegenbuchung (mask lager/stock-movement:stornieren)."""
    try:
        opened = StockMovementStornierenInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid stock_movement.stornieren parameters") from exc
    parameters = opened.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        zeile = db.execute(
            text(
                "SELECT id::text AS id, movement_type, quantity, source_document_type, "
                "article_id, warehouse_id "
                "FROM domain_inventory.inventory_stock_movements "
                "WHERE id = :id AND tenant_id = :tid FOR SHARE"
            ),
            {"id": opened.movement_id, "tid": tenant},
        ).mappings().first()
        if zeile is None:
            raise HTTPException(404, "Stock movement not found in the authenticated tenant")
        if str(zeile["source_document_type"] or "").upper() == "STORNO":
            raise HTTPException(422, "A storno cannot be reversed again")
        wirkung = signed_quantity(zeile["movement_type"], float(zeile["quantity"] or 0))
        if wirkung == 0:
            raise HTTPException(422, "Movement is stock-neutral; nothing to reverse")
        bestand = current_stock(
            db, tenant_id=tenant, article_id=str(zeile["article_id"]),
            warehouse_id=str(zeile["warehouse_id"]),
        )
        if bestand - wirkung < 0:
            raise HTTPException(422, "Reversal would make stock negative")
        if request.mode != "execute":
            return {
                "success": True,
                "mode": request.mode,
                "proposedChanges": {
                    **parameters,
                    "movement_id": zeile["id"],
                    "movement_type": zeile["movement_type"],
                    "quantity": float(zeile["quantity"] or 0),
                    "stock_effect": wirkung,
                },
            }
        try:
            ergebnis = storno_korrektur(db, opened.movement_id, tenant, bemerkung=opened.begruendung)
        except CorrectionError as exc:
            raise HTTPException(422, str(exc)) from exc
        storno_id = str(ergebnis.get("id") or "")
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="inventory_stock_movement", entity_id=opened.movement_id,
            audit_reason="MCP stock movement storno", idempotency_key=request.idempotency_key,
            summary=f"Storno {storno_id} für Bewegung {opened.movement_id} by {actor}",
        )
        result = {
            "success": True,
            "mode": "execute",
            "replayed": False,
            "movement_id": opened.movement_id,
            "storno_movement_id": storno_id,
            "movement_type": ergebnis.get("movement_type"),
            "quantity": float(ergebnis.get("quantity") or 0),
            "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except CorrectionError as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _invoice_sources_from_positions(ls_id: str, positions: list[dict]) -> list[SourceLine]:
    sources: list[SourceLine] = []
    for pos in positions:
        zeile = LineToRegister.from_mapping(pos)
        if not zeile.line_id or not zeile.unit:
            continue
        sources.append(SourceLine(
            document_type="delivery_note",
            document_id=ls_id,
            line_id=zeile.line_id,
            article_id=zeile.article_id,
            article_number=pos.get("artikel_nr"),
            description=pos.get("bezeichnung"),
            quantity=Decimal(str(zeile.quantity or 0)),
            unit=str(zeile.unit),
            unit_price=Decimal(str(pos.get("netto_preis") or 0)),
            vat_rate=(
                Decimal(str(pos["mwst_prozent"]))
                if pos.get("mwst_prozent") is not None
                else None
            ),
        ))
    return sources


def _post_invoice(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Create a sales invoice draft from an approved proposal. Never skips human approval."""
    try:
        payload = InvoicePostInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid invoice post parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "sales.invoice.post does not accept propose; use sales.invoice.propose")
    parameters = payload.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        proposal = db.execute(text("""
            SELECT proposal_id, action_type, approval_status, risk_level,
                   context_snapshot, execution_result
            FROM public.agent_proposals
            WHERE proposal_id=:id AND tenant_id=:tenant
            FOR UPDATE OF agent_proposals
        """), {"id": payload.proposal_id, "tenant": tenant}).mappings().first()
        if not proposal:
            raise HTTPException(404, "Proposal not found in the authenticated tenant")
        if proposal["action_type"] != "rechnung_vorschlag":
            raise HTTPException(409, "Proposal is not an invoice proposal")
        if proposal["approval_status"] != "approved":
            raise HTTPException(409, "Proposal is not approved")
        if proposal["execution_result"] is not None:
            existing = proposal["execution_result"]
            if isinstance(existing, str):
                existing = json.loads(existing)
            if isinstance(existing, dict) and existing.get("invoice_id"):
                if request.mode != "execute":
                    return {
                        "success": True, "mode": request.mode, "posted": False,
                        "already_executed": True,
                        **{k: existing[k] for k in ("invoice_id", "invoice_number", "status") if k in existing},
                    }
                raise HTTPException(409, "Proposal was already executed")
        snapshot = proposal["context_snapshot"] or {}
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        if not isinstance(snapshot, dict):
            raise HTTPException(409, "Proposal snapshot is unusable")
        lieferschein_nr = snapshot.get("lieferschein_nr")
        rechnungsdatum_raw = snapshot.get("rechnungsdatum")
        if not isinstance(lieferschein_nr, str) or not lieferschein_nr.strip():
            raise HTTPException(409, "Proposal snapshot lacks lieferschein_nr")
        try:
            rechnungsdatum = date.fromisoformat(str(rechnungsdatum_raw))
        except (TypeError, ValueError) as exc:
            raise HTTPException(409, "Proposal snapshot lacks a valid rechnungsdatum") from exc
        preview = {
            "proposal_id": payload.proposal_id,
            "lieferschein_nr": lieferschein_nr,
            "rechnungsdatum": rechnungsdatum.isoformat(),
            "betrag_netto": snapshot.get("betrag_netto"),
            "mwst": snapshot.get("mwst"),
            "positionen": snapshot.get("positionen"),
        }
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "posted": False, **preview}
        note = db.execute(text("""
            SELECT n.id, n.status, n.customer_id, n.delivery_note_number
            FROM domain_sales.delivery_notes n
            WHERE n.tenant_id=:tenant AND n.delivery_note_number=:nr
            FOR UPDATE OF n
        """), {"tenant": tenant, "nr": lieferschein_nr}).mappings().first()
        if not note:
            raise HTTPException(404, "Delivery note not found in the authenticated tenant")
        if note["status"] not in _BILLABLE_DELIVERY_STATUSES:
            raise HTTPException(409, "Delivery note is not ready to invoice")
        positions = [
            dict(row) for row in db.execute(text("""
                SELECT p.*
                FROM domain_sales.delivery_note_positions p
                JOIN domain_sales.delivery_notes n ON n.id = p.delivery_note_id
                WHERE p.delivery_note_id = :id
                  AND n.tenant_id = :tenant
                ORDER BY p.pos_nr
            """), {"id": note["id"], "tenant": tenant}).mappings().all()
        ]
        sources = _invoice_sources_from_positions(str(note["id"]), positions)
        invoice_number = f"RE-{note['delivery_note_number'] or str(note['id'])[:8]}"
        try:
            with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
                ergebnis = SalesInvoiceService(child, tenant).create_from_sources(
                    invoice_number=invoice_number,
                    customer_id=str(note.get("customer_id") or ""),
                    invoice_date=rechnungsdatum,
                    sources=sources,
                    reason="rechnung_aus_lieferschein_mcp",
                    user_id=actor,
                    note=f"MCP post from proposal {payload.proposal_id}",
                )
        except InvoiceCreationError as exc:
            raise HTTPException(409, str(exc)) from exc
        invoice_id = str(ergebnis.invoice.id)
        db.execute(text("""
            UPDATE domain_sales.delivery_notes
            SET status = 'invoiced', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant
        """), {"id": note["id"], "tenant": tenant})
        execution_result = {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "status": "entwurf",
            "executed_by": actor,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        db.execute(text("""
            UPDATE public.agent_proposals
            SET execution_result = CAST(:result AS json)
            WHERE proposal_id = :id AND tenant_id = :tenant
        """), {"result": json.dumps(execution_result), "id": payload.proposal_id, "tenant": tenant})
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="sales_invoice", entity_id=invoice_id,
            audit_reason="MCP invoice post from approved proposal",
            idempotency_key=request.idempotency_key,
            summary=f"Invoice {invoice_number} from proposal {payload.proposal_id} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False, "posted": False,
            "invoice_id": invoice_id, "invoice_number": invoice_number, "status": "entwurf",
            "proposal_id": payload.proposal_id, "auditEntryId": audit_id,
            "fibu_journal": False,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc
