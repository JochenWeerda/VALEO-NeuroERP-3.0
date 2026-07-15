"""Typed API contract for versioned feed analyses (FEED-CORE-019)."""
from __future__ import annotations

import hashlib
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.feed_analysis import AnalysisStatus, AnalysisValueStatus
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_feed_analysis_service import (
    FeedAnalysisConflict,
    FeedAnalysisNotFound,
    FeedingFeedAnalysisService,
)

router = APIRouter(prefix="/feed-analyses", tags=["feeding-feed-analyses"])


class AnalysisOut(BaseModel):
    model_config = ConfigDict(extra="ignore")


class AnalysisValueOut(AnalysisOut):
    id: str
    analysis_id: str
    nutrient_code: str
    original_value: Decimal
    original_unit_code: str
    canonical_value: Decimal
    canonical_unit_code: str
    basis: str
    value_status: AnalysisValueStatus
    method: str | None = None
    confidence: Decimal | None = None
    estimated: bool = False


class AnalysisFindingOut(AnalysisOut):
    id: str
    code: str
    severity: str
    message: str
    nutrient_code: str | None = None
    observed_value: Decimal | None = None
    acknowledged: bool = False


class AnalysisSummaryOut(AnalysisOut):
    id: str
    tenant_id: str
    feed_id: str | None = None
    scope_code: str = "default"
    bezeichnung: str
    probe_nr: str | None = None
    probenart: str | None = None
    labor: str | None = None
    analyse_datum: date | None = None
    status: AnalysisStatus
    is_active: bool
    valid_from: date
    valid_until: date | None = None
    revision: int
    updated_at: datetime | None = None


class AnalysisDetailOut(AnalysisSummaryOut):
    method: str | None = None
    sampled_at: datetime | None = None
    original_document_id: str | None = None
    original_sha256: str | None = None
    released_at: datetime | None = None
    released_by: str | None = None
    values: list[AnalysisValueOut] = Field(default_factory=list)
    findings: list[AnalysisFindingOut] = Field(default_factory=list)


class AnalysisRevisionOut(AnalysisOut):
    id: str
    analysis_id: str
    revision: int
    snapshot: dict
    reason: str
    changed_by: str
    changed_at: datetime


class AnalysisValueIn(BaseModel):
    nutrient_code: str = Field(min_length=1, max_length=80)
    original_value: Decimal = Field(ge=0)
    original_unit_code: str = Field(min_length=1, max_length=80)
    canonical_unit_code: str = Field(min_length=1, max_length=80)
    basis: str = Field(pattern="^(fresh_matter|dry_matter)$")
    value_status: AnalysisValueStatus = AnalysisValueStatus.MEASURED
    method: str | None = Field(default=None, max_length=255)
    detection_limit: Decimal | None = Field(default=None, ge=0)
    confidence: Decimal | None = Field(default=None, ge=0, le=1)
    source_ref: str | None = Field(default=None, max_length=500)


class AnalysisCreateIn(BaseModel):
    id: str | None = None
    feed_id: str | None = None
    scope_code: str = Field(default="default", min_length=1, max_length=80)
    bezeichnung: str = Field(min_length=1, max_length=255)
    probe_nr: str | None = Field(default=None, max_length=50)
    probenart: str | None = Field(default=None, max_length=100)
    labor: str | None = Field(default=None, max_length=255)
    analyse_datum: date | None = None
    method: str | None = Field(default=None, max_length=255)
    sampled_at: datetime | None = None
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None
    original_document_id: str | None = None
    original_sha256: str | None = Field(default=None, pattern="^[0-9a-fA-F]{64}$")
    quelle_datei: str | None = Field(default=None, max_length=500)
    status: AnalysisStatus = AnalysisStatus.DRAFT
    notizen: str | None = None
    values: list[AnalysisValueIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_period(self) -> "AnalysisCreateIn":
        if self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("Gueltigkeitsende liegt vor dem Beginn.")
        return self


class AnalysisValidateIn(BaseModel):
    expected_revision: int = Field(ge=1)


class AnalysisDocumentIn(BaseModel):
    document_id: str = Field(min_length=1, max_length=255)
    sha256: str = Field(pattern="^[0-9a-fA-F]{64}$")
    expected_revision: int = Field(ge=1)


class AnalysisImportPreviewOut(BaseModel):
    filename: str
    sha256: str
    quarantine_status: Literal["preview_only"] = "preview_only"
    confidence: str
    warnings: list[str] = Field(default_factory=list)
    analysis: dict[str, Any]
    values: list[AnalysisValueIn]


class AnalysisTransitionIn(BaseModel):
    target_status: AnalysisStatus
    expected_revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)


class AnalysisActionIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    mode: Literal["validate", "dryRun", "propose", "execute"] = Field(default="execute", alias="_mode")
    audit_reason: str | None = Field(default=None, alias="_auditReason", max_length=500)


def _service(db: Session, tenant_id: str, user: User) -> FeedingFeedAnalysisService:
    return FeedingFeedAnalysisService(db, tenant_id, str(user.get("sub") or "unknown"))


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, FeedAnalysisNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, FeedAnalysisConflict):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.get("", response_model=list[AnalysisSummaryOut], summary="Futteranalysen auflisten")
def list_analyses(status: AnalysisStatus | None = None, feed_id: str | None = None,
                  search: str | None = Query(default=None, max_length=100), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).list_analyses(
        status=status.value if status else None, feed_id=feed_id, search=search,
    )


@router.post("", response_model=AnalysisDetailOut, status_code=201, summary="Futteranalyse anlegen")
def create_analysis(body: AnalysisCreateIn, db: Session = Depends(get_db),
                    tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).create_analysis(body.model_dump())
    except Exception as exc:
        raise _translate(exc) from exc


def _legacy_preview_values(parsed: Any) -> list[AnalysisValueIn]:
    mapping = (
        ("trockensubstanz_os", "dry_matter", "percent", "g_per_kg", "fresh_matter", "measured"),
        ("rohprotein_ts", "crude_protein", "percent", "g_per_kg", "dry_matter", "measured"),
        ("rohfaser_ts", "crude_fiber", "percent", "g_per_kg", "dry_matter", "measured"),
        ("rohfett_ts", "crude_fat", "percent", "g_per_kg", "dry_matter", "measured"),
        ("rohasche_ts", "crude_ash", "percent", "g_per_kg", "dry_matter", "measured"),
        ("andfom_ts", "andfom", "percent", "g_per_kg", "dry_matter", "measured"),
        ("adfom_ts", "adfom", "percent", "g_per_kg", "dry_matter", "measured"),
        ("me_gfe2023_ts", "metabolizable_energy", "MJ_per_kg", "MJ_per_kg", "dry_matter", "calculated"),
        ("nel_ts", "net_energy_lactation", "MJ_per_kg", "MJ_per_kg", "dry_matter", "calculated"),
    )
    values: list[AnalysisValueIn] = []
    for field, code, original_unit, canonical_unit, basis, status in mapping:
        original = getattr(parsed, field, None)
        if original is not None:
            values.append(AnalysisValueIn(
                nutrient_code=code, original_value=Decimal(str(original)), original_unit_code=original_unit,
                canonical_unit_code=canonical_unit, basis=basis, value_status=status,
                method="Laborimport", source_ref=getattr(parsed, "quelle_datei", None),
            ))
    return values


@router.post("/import-preview", response_model=AnalysisImportPreviewOut, summary="Laborbericht sicher vorpruefen")
async def import_preview(file: UploadFile = File(...), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    filename = file.filename or "upload"
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in {"pdf", "csv"}:
        raise HTTPException(status_code=415, detail="Nur PDF- und CSV-Laborberichte werden unterstuetzt.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="Die Importdatei ist leer.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Laborbericht ist groesser als 10 MB.")
    from app.api.v1.endpoints.grundfutter_analysen import parse_lufa_csv, parse_lufa_pdf_text
    if suffix == "csv":
        try:
            csv_text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            csv_text = content.decode("latin-1")
        parsed = parse_lufa_csv(csv_text, filename)
        confidence, warnings = "medium", []
    else:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"PDF konnte nicht sicher gelesen werden: {exc}") from exc
        if not extracted.strip():
            raise HTTPException(status_code=422, detail="PDF enthaelt keinen auswertbaren Textlayer.")
        result = parse_lufa_pdf_text(extracted, filename)
        parsed, confidence, warnings = result.parsed, result.confidence, result.warnings
    return {
        "filename": filename, "sha256": hashlib.sha256(content).hexdigest(),
        "quarantine_status": "preview_only", "confidence": confidence, "warnings": warnings,
        "analysis": {
            "bezeichnung": parsed.bezeichnung, "probe_nr": parsed.probe_nr, "probenart": parsed.probenart,
            "labor": parsed.labor, "analyse_datum": parsed.analyse_datum, "quelle_datei": filename,
        },
        "values": _legacy_preview_values(parsed),
    }


@router.get("/{analysis_id}", response_model=AnalysisDetailOut, summary="Futteranalyse abrufen")
def get_analysis(analysis_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                 user: User = Depends(get_current_user)) -> dict:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).get_analysis(analysis_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/{analysis_id}/history", response_model=list[AnalysisRevisionOut], summary="Analysehistoire abrufen")
def get_history(analysis_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).history(analysis_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/{analysis_id}/values", response_model=list[AnalysisValueOut], summary="Analysewerte abrufen")
def get_values(analysis_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
               user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).values(analysis_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/{analysis_id}/findings", response_model=list[AnalysisFindingOut], summary="Plausibilitaetsbefunde abrufen")
def get_findings(analysis_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                 user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).findings(analysis_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/{analysis_id}/values", response_model=AnalysisValueOut, status_code=201,
             summary="Analysewert erfassen")
def add_value(analysis_id: str, body: AnalysisValueIn, db: Session = Depends(get_db),
              tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).add_value(analysis_id, body.model_dump())
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/{analysis_id}/document-reference", response_model=AnalysisDetailOut,
             summary="Revisionssicheren Originalbeleg referenzieren")
def reference_document(analysis_id: str, body: AnalysisDocumentIn, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).attach_document(
            analysis_id, body.document_id, body.sha256, body.expected_revision,
        )
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/{analysis_id}/validate", response_model=AnalysisDetailOut, summary="Analyse plausibilisieren")
def validate_analysis(analysis_id: str, body: AnalysisValidateIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).validate(analysis_id, body.expected_revision)
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/{analysis_id}/transition", response_model=AnalysisDetailOut, summary="Analysestatus wechseln")
def transition_analysis(analysis_id: str, body: AnalysisTransitionIn, db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    required = APPROVE_ROLES if body.target_status == AnalysisStatus.RELEASED else WRITE_ROLES
    require_roles(user, required)
    try:
        return _service(db, tenant_id, user).transition(
            analysis_id, body.target_status, body.expected_revision, body.reason,
        )
    except Exception as exc:
        raise _translate(exc) from exc


def _run_action(*, analysis_id: str, target: AnalysisStatus, body: AnalysisActionIn,
                service: FeedingFeedAnalysisService) -> dict[str, Any]:
    current = service.get_analysis(analysis_id)
    reason = (body.audit_reason or "").strip()
    if body.mode in {"validate", "dryRun", "propose"}:
        return {
            "success": True, "mode": body.mode, "entityId": analysis_id,
            "proposedChanges": [{"field": "status", "before": current["status"], "after": target.value}],
            "blockingReasons": [finding["message"] for finding in current["findings"]
                                if finding["severity"] == "blocker"],
        }
    if len(reason) < 3:
        raise FeedAnalysisConflict("Ein nachvollziehbarer Auditgrund ist erforderlich.")
    changed = service.transition(analysis_id, target, int(current["revision"]), reason)
    return {"success": True, "mode": "execute", "entityId": analysis_id,
            "status": changed["status"], "revision": changed["revision"]}


@router.post("/{analysis_id}/actions/release", response_model=dict[str, Any], summary="Analyse via ActionRuntime freigeben")
def release_action(analysis_id: str, body: AnalysisActionIn, db: Session = Depends(get_db),
                   tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, APPROVE_ROLES)
    try:
        return _run_action(analysis_id=analysis_id, target=AnalysisStatus.RELEASED, body=body,
                           service=_service(db, tenant_id, user))
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/{analysis_id}/actions/reject", response_model=dict[str, Any], summary="Analyse via ActionRuntime zurueckweisen")
def reject_action(analysis_id: str, body: AnalysisActionIn, db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _run_action(analysis_id=analysis_id, target=AnalysisStatus.REJECTED, body=body,
                           service=_service(db, tenant_id, user))
    except Exception as exc:
        raise _translate(exc) from exc
