"""Response-Schemas fuer die Dokumentenkette (DOM-DOC-004).

SPEC-P1-06 Welle 7: ersetzt ``response_model=dict`` bzw. ``Dict[str, Any]`` in
``document_control.py``, ``docflow_return.py``, ``docflow_followup.py`` und
``doc_nachweisraum_actions.py``.

Ein Modul, weil die vier Dateien eine Fachkette bilden: Belegkontrolle
(Ausnahmen) -> Ruecklauf -> Wiedervorlage -> Nachweisraum/GoBD. Die
Worklist-Huelle (``items``/``total``/``page``/``page_size``) und das
Audit-Muster wiederholen sich darin.

Feldlisten aus ``document_control_service``, ``document_control_projection``,
``docflow_return_service``, ``docflow_followup_service`` und der Migration
``doc_nachweisraum_lifecycle_20260623``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Belegkontrolle (Ausnahmen) ──────────────────────────────────────────────


class ControlExceptionOut(BaseSchema):
    """Zeile aus ``domain_ops.document_control_exceptions``."""

    id: Optional[str] = None
    exception_type: Optional[str] = Field(
        default=None,
        description=(
            "open_purchase_order | missing_inbound_document | "
            "blocked_delivery_note | uninvoiced_delivery_note"
        ),
    )
    status: Optional[str] = Field(
        default=None, description="open | assigned | in_progress | resolved | waived"
    )
    document_ref: Optional[str] = None
    document_number: Optional[str] = None
    partner_ref: Optional[str] = None
    partner_name: Optional[str] = None
    assigned_user: Optional[str] = None
    due_at: Optional[datetime] = None
    source_route: Optional[str] = Field(
        default=None, description="Frontend-Route zum Quellbeleg"
    )
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ControlWorklistOut(BaseSchema):
    """``GET /document-control/exceptions``"""

    items: list[ControlExceptionOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ControlSummaryOut(BaseSchema):
    """``GET /document-control/summary`` — Zaehlung je Ausnahmetyp."""

    open_total: Optional[int] = None
    open_purchase_order: Optional[int] = None
    missing_inbound_document: Optional[int] = None
    blocked_delivery_note: Optional[int] = None
    uninvoiced_delivery_note: Optional[int] = None
    overdue: Optional[int] = None


class ControlRegisteredOut(BaseSchema):
    """``POST /document-control/exceptions``.

    ``duplicate`` kennzeichnet den Idempotenzpfad; ``projection`` setzt nur der
    Projektionslauf (created | refreshed | skipped).
    """

    id: Optional[str] = None
    status: Optional[str] = None
    duplicate: Optional[bool] = None
    projection: Optional[str] = None


class ControlProjectionOut(BaseSchema):
    """``POST /document-control/project`` — Projektion aus den Quellbelegen."""

    tenant_id: Optional[str] = None
    collected: Optional[int] = Field(
        default=None, description="Aus Quellbelegen eingesammelte Kandidaten"
    )
    created: Optional[int] = None
    refreshed: Optional[int] = None
    skipped: Optional[int] = Field(
        default=None, description="Bereits geloeste oder verzichtete Faelle"
    )


class ControlAssignOut(BaseSchema):
    """``POST /document-control/exceptions/{id}/assign``"""

    id: Optional[str] = None
    assigned_user: Optional[str] = None
    status: Optional[str] = None


class ControlTransitionOut(BaseSchema):
    """``POST /document-control/exceptions/{id}/transition``"""

    id: Optional[str] = None
    status: Optional[str] = None


# ── Dokumentenruecklauf ─────────────────────────────────────────────────────


class ReturnCaseOut(BaseSchema):
    """Ruecklauffall mit Belegkopf und optionalem Artefakt."""

    id: Optional[str] = None
    doc_number: Optional[str] = None
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    contact_ref: Optional[str] = None
    assigned_user: Optional[str] = None
    tags: Optional[Any] = None
    shipping_status: Optional[str] = Field(default=None, description="not_sent | sent")
    return_status: Optional[str] = Field(
        default=None, description="expected | received | closed | waived"
    )
    due_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    source_route: Optional[str] = None
    created_at: Optional[datetime] = None
    file_name: Optional[str] = None
    storage_key: Optional[str] = None


class ReturnWorklistOut(BaseSchema):
    """``GET /docflow/returns``"""

    items: list[ReturnCaseOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ReturnSummaryOut(BaseSchema):
    """``GET /docflow/returns/summary``"""

    total: Optional[int] = None
    not_sent: Optional[int] = None
    expected: Optional[int] = None
    received: Optional[int] = None
    overdue: Optional[int] = None


class ReturnCreatedOut(BaseSchema):
    """``POST /docflow/returns``"""

    id: Optional[str] = None
    doc_number: Optional[str] = None
    shipping_status: Optional[str] = None
    return_status: Optional[str] = None


class ReturnTransitionOut(BaseSchema):
    """``POST /docflow/returns/{id}/transition``.

    Der Service setzt je nach ``kind`` entweder ``shipping_status`` oder
    ``return_status`` — der Schluessel ist dynamisch, deshalb beide optional.
    """

    id: Optional[str] = None
    shipping_status: Optional[str] = None
    return_status: Optional[str] = None


class ReturnAuditEntryOut(BaseSchema):
    """Auditzeile eines Ruecklauffalls."""

    id: Optional[str] = None
    action: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None


class ReturnEvidenceOut(BaseSchema):
    """``GET /docflow/returns/{id}/evidence`` — Vorschau und Auditnachweis."""

    id: Optional[str] = None
    doc_number: Optional[str] = None
    source_route: Optional[str] = None
    artifact_id: Optional[str] = None
    file_name: Optional[str] = None
    artifact_type: Optional[str] = None
    content_hash_sha256: Optional[str] = Field(
        default=None, description="Inhaltshash des Artefakts (Nachweiskette)"
    )
    storage_key: Optional[str] = None
    preview_available: Optional[bool] = None
    audit: list[ReturnAuditEntryOut] = Field(default_factory=list)


# ── Bescheide, Rueckmeldungen, Wiedervorlagen ───────────────────────────────


class FollowupOut(BaseSchema):
    """Followup zu einem Vorgang."""

    followup_id: Optional[str] = None
    art: Optional[str] = Field(
        default=None, description="bescheid | rueckmeldung | wiedervorlage"
    )
    betreff: Optional[str] = None
    text: Optional[str] = None
    faellig_am: Optional[str] = None
    status: Optional[str] = Field(default=None, description="offen | erledigt")
    ueberfaellig: Optional[bool] = Field(
        default=None, description="Berechnet gegen das Tagesdatum"
    )
    erledigt_at: Optional[str] = None
    erledigt_von: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class FollowupSummaryOut(BaseSchema):
    """Kopfzahlen der Followups eines Vorgangs."""

    anzahl: Optional[int] = None
    offen: Optional[int] = None
    ueberfaellig: Optional[int] = None


class FollowupListOut(BaseSchema):
    """``GET /docflow/followups``.

    Im Nichttrefferfall sind nur ``found=false`` und ``detail`` gesetzt.
    """

    found: bool = Field(default=False)
    detail: Optional[str] = None
    doc_number: Optional[str] = None
    followups: list[FollowupOut] = Field(default_factory=list)
    summary: Optional[FollowupSummaryOut] = None


class WiedervorlageOut(BaseSchema):
    """Offene Wiedervorlage in der uebergreifenden Worklist."""

    followup_id: Optional[str] = None
    doc_number: Optional[str] = None
    betreff: Optional[str] = None
    faellig_am: Optional[str] = None
    bediener: Optional[str] = None
    ueberfaellig: Optional[bool] = None


class WiedervorlagenListOut(BaseSchema):
    """``GET /docflow/wiedervorlagen``"""

    items: list[WiedervorlageOut] = Field(default_factory=list)


class FollowupCreatedOut(BaseSchema):
    """``POST /docflow/followups``"""

    ok: bool = Field(default=True)
    followup_id: Optional[str] = None
    doc_number: Optional[str] = None
    art: Optional[str] = None


class FollowupCompletedOut(BaseSchema):
    """``POST /docflow/followups/{id}/complete``"""

    ok: bool = Field(default=True)
    followup_id: Optional[str] = None
    status: Optional[str] = None


# ── Nachweisraum und GoBD ───────────────────────────────────────────────────


class NachweisDokumentOut(BaseSchema):
    """Zeile aus ``domain_nachweisraum.nachweisraum_dokumente``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    dokument_typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_typ: Optional[str] = None
    datei_pfad: Optional[str] = None
    version: Optional[int] = None
    status: Optional[str] = Field(default=None, description="EINGEGANGEN und Folgestatus")
    wiedervorlage_datum: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GobdExportOut(BaseSchema):
    """Zeile aus ``domain_nachweisraum.gobd_exporte``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    periode: Optional[str] = None
    anzahl_dokumente: Optional[int] = None
    status: Optional[str] = Field(default=None, description="OFFEN und Folgestatus")
    export_pfad: Optional[str] = None
    fehler_grund: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
