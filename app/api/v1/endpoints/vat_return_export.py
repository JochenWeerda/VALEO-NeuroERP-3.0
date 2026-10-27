"""
VAT Return Export API
FIBU-TAX-02: USt-Voranmeldung

Ablauf einer Anmeldung: berechnet -> geprueft -> freigegeben -> uebermittelt. Jeder Schritt speichert den geprueften
Bearbeiter (Token), nie einen Namen aus dem Rumpf.

Die Zahlen kommen aus ``app.finance.ustva.berechne``: gebuchte Salden der Konten, die die Steuerschluessel nennen.
Bis 27.10.2026 erkannte diese Datei Erloes- und Aufwandskonten am ersten Zeichen der Konto-UUID, rechnete pauschal
19 %, lieferte immer null und meldete Fehler als null; ``submit`` setzte ``submitted`` mit einer erfundenen
ELSTER-Referenz, ohne dass irgendetwas uebermittelt wurde.

Eine Uebermittlung an ELSTER (ERiC) ist nicht angebunden. Uebermittelt wird im ELSTER-Portal; ``submit`` haelt sie
mit dem Transferticket fest, das ELSTER dafuer vergibt. Ohne Ticket keine Uebermittlung.
"""

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.schemas.vat_return_export_schemas import VatReturnExportOut
from app.auth.finance_roles import finance_admin, finance_read, finance_write
from app.core.akteur import gepruefter_akteur_aus_request
from app.core.explainability import ExplainabilityView
from app.core.policy_decisions import PolicyOverrideResolution
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.finance.ustva import UStVAStand, berechne

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vat-return", tags=["finance", "tax", "vat"])

#: Spalten einer Anmeldung, in dieser Reihenfolge gelesen — Zuordnung ueber den Namen, nie ueber die Position.
_SPALTEN = (
    "id, period, return_type, taxpayer_name, tax_id, vat_id, total_sales_net, total_input_tax, total_output_tax, "
    "vat_payable, positions, status, calculated_at, calculated_by, validated_at, validated_by, approved_at, "
    "approved_by, submitted_at, submitted_by, elster_transferticket, notes, created_at, updated_at"
)
TOLERANZ = Decimal("0.01")


class VATReturnResponse(BaseModel):
    """Response schema for VAT return"""
    id: str
    period: str
    return_type: str
    taxpayer_name: Optional[str]
    tax_id: Optional[str]
    vat_id: Optional[str]
    total_sales_net: Decimal
    total_input_tax: Decimal
    total_output_tax: Decimal
    vat_payable: Decimal
    positions: List[Dict[str, Any]]
    status: str  # calculated, validated, approved, submitted
    calculated_at: Optional[datetime]
    calculated_by: Optional[str] = None
    validated_at: Optional[datetime]
    validated_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    submitted_at: Optional[datetime]
    submitted_by: Optional[str] = None
    #: Transferticket der ELSTER-Uebermittlung — die einzige ELSTER-Referenz, die es gibt.
    elster_reference: Optional[str] = None
    approval_status: str | None = None
    approval_can_submit: bool = False
    approval_override_resolution: PolicyOverrideResolution | None = None
    approval_explainability: ExplainabilityView | None = None
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VATReturnCalculationRequest(BaseModel):
    """Request to calculate VAT return from journal entries"""
    period: str = Field(..., description="Zeitraum YYYY-MM oder YYYY-Q1 bis YYYY-Q4")
    tenant_id: Optional[str] = Field(default=None)


class VATReturnSubmitRequest(BaseModel):
    """Festhalten einer im ELSTER-Portal erfolgten Uebermittlung."""
    transferticket: str = Field(..., min_length=5, max_length=50, description="Transferticket aus ELSTER")


class VATReturnVorberechnung(BaseModel):
    """Vorberechnung (nicht gespeichert)."""
    zeitraum: str
    umsatz_netto: float = Field(0, description="Summe der Bemessungsgrundlagen")
    umsatzsteuer: float = Field(0, description="Umsatzsteuer laut Hauptbuch")
    vorsteuer: float = Field(0, description="Abziehbare Vorsteuer laut Hauptbuch")
    zahllast: float = Field(0, description="Kennzahl 83: positiv Zahlung, negativ Erstattung")
    positionen: List[Dict[str, Any]] = Field(default_factory=list, description="Kennzahlen")
    klaerungen: List[str] = Field(default_factory=list, description="Was sich nicht eindeutig zuordnen laesst")
    offene_entwuerfe: int = Field(0, description="Ungebuchte Buchungsentwuerfe im Zeitraum")


def _resolve_vat_request_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="VAT return request belongs to a different tenant")
    return tenant_id


def _nicht_verfuegbar(db: Session, exc: Exception) -> HTTPException:
    db.rollback()
    logger.error("UStVA: Datenbankfehler: %s", exc)
    return HTTPException(status_code=503, detail="UStVA ist vorübergehend nicht verfügbar.")


def _stand(db: Session, tenant_id: str, zeitraum: str) -> UStVAStand:
    try:
        return berechne(db, tenant_id, zeitraum)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc


def _positionen(stand: UStVAStand) -> list[dict[str, Any]]:
    return [k.model_dump(mode="json") for k in stand.kennzahlen]


def _build_vat_return_response(row: Any, *, positions_data: Optional[list[dict[str, Any]]] = None) -> VATReturnResponse:
    """Antwort aus einer Zeile mit den Spalten ``_SPALTEN`` (Mapping)."""
    r = dict(row)
    status = str(r["status"])
    if positions_data is None:
        roh = r.get("positions")
        positions_data = json.loads(roh) if isinstance(roh, str) else list(roh or [])
    can_submit = status == "approved"
    return VATReturnResponse(
        id=str(r["id"]),
        period=str(r["period"]),
        return_type=str(r["return_type"]),
        taxpayer_name=r.get("taxpayer_name"),
        tax_id=r.get("tax_id"),
        vat_id=r.get("vat_id"),
        total_sales_net=Decimal(str(r["total_sales_net"])),
        total_input_tax=Decimal(str(r["total_input_tax"])),
        total_output_tax=Decimal(str(r["total_output_tax"])),
        vat_payable=Decimal(str(r["vat_payable"])),
        positions=positions_data,
        status=status,
        calculated_at=r.get("calculated_at"),
        calculated_by=r.get("calculated_by"),
        validated_at=r.get("validated_at"),
        validated_by=r.get("validated_by"),
        approved_at=r.get("approved_at"),
        approved_by=r.get("approved_by"),
        submitted_at=r.get("submitted_at"),
        submitted_by=r.get("submitted_by"),
        elster_reference=r.get("elster_transferticket"),
        approval_status=status,
        approval_can_submit=can_submit,
        approval_override_resolution=PolicyOverrideResolution(
            rule_id="finance.vat_return.submission",
            effective_scope="global",
            effective_scope_key="vat-return",
            effective_enabled=True,
            effective_params={"status": status},
            applied_reason="UStVA-Freigabe für Einreichung.",
            applied_source="vat-return-export",
        ),
        approval_explainability=ExplainabilityView(
            status="allowed" if can_submit or status == "submitted" else "approval-required",
            summary=(
                "USt-Voranmeldung ist übermittelt." if status == "submitted"
                else "USt-Voranmeldung kann übermittelt werden." if can_submit
                else "USt-Voranmeldung benötigt Prüfung und Freigabe."
            ),
            rule_id="finance.vat_return.submission",
            source_scope="global",
        ),
        notes=r.get("notes"),
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


def _lies(db: Session, return_id: str, tenant_id: str, *, sperren: bool = False) -> dict[str, Any]:
    sql = f"SELECT {_SPALTEN} FROM domain_erp.vat_returns WHERE id = :return_id AND tenant_id = :tenant_id"  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
    if sperren:
        sql += " FOR UPDATE"
    try:
        row = db.execute(text(sql), {"return_id": return_id, "tenant_id": tenant_id}).mappings().first()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    if not row:
        raise HTTPException(status_code=404, detail="VAT return not found")
    return dict(row)


def _abweichungen(gespeichert: dict[str, Any], stand: UStVAStand) -> list[dict[str, Any]]:
    """Was zwischen gespeicherter Anmeldung und aktuellem Hauptbuch abweicht — Summen und Kennzahlen."""
    differences = []
    for feld, neu in (
        ("total_sales_net", stand.umsatz_netto), ("total_output_tax", stand.umsatzsteuer),
        ("total_input_tax", stand.vorsteuer), ("vat_payable", stand.zahllast),
    ):
        alt = Decimal(str(gespeichert[feld]))
        if abs(alt - neu) >= TOLERANZ:
            differences.append({"field": feld, "vat_return": float(alt), "gl_total": float(neu),
                                "difference": float(neu - alt)})
    roh = gespeichert.get("positions")
    alt_kz = {p["kennzahl"]: p for p in (json.loads(roh) if isinstance(roh, str) else list(roh or []))
              if isinstance(p, dict) and "kennzahl" in p}
    neu_kz = {p["kennzahl"]: p for p in _positionen(stand)}
    for kz in sorted(set(alt_kz) | set(neu_kz)):
        for wert in ("bemessungsgrundlage", "steuer"):
            a = Decimal(str((alt_kz.get(kz) or {}).get(wert) or 0))
            n = Decimal(str((neu_kz.get(kz) or {}).get(wert) or 0))
            if abs(a - n) >= TOLERANZ:
                differences.append({"field": f"kennzahl_{kz}_{wert}", "vat_return": float(a), "gl_total": float(n),
                                    "difference": float(n - a)})
    return differences


@router.get("/vorberechnung", response_model=VATReturnVorberechnung, summary="Ustva vorberechnung", dependencies=[Depends(finance_read)])
async def vorberechnung_ustva(
    zeitraum: str = Query(..., description="Zeitraum im Format YYYY-MM oder YYYY-QN"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Vorberechnung der UStVA aus dem Hauptbuch, ohne eine Anmeldung anzulegen. Ein Lesefehler ist 503, keine Null."""
    stand = _stand(db, tenant_id, zeitraum)
    return VATReturnVorberechnung(
        zeitraum=zeitraum,
        umsatz_netto=float(stand.umsatz_netto),
        umsatzsteuer=float(stand.umsatzsteuer),
        vorsteuer=float(stand.vorsteuer),
        zahllast=float(stand.zahllast),
        positionen=_positionen(stand),
        klaerungen=stand.klaerungen,
        offene_entwuerfe=stand.offene_entwuerfe,
    )


@router.post("/calculate", response_model=VATReturnResponse, summary="Vat return berechnen", dependencies=[Depends(finance_write)])
async def calculate_vat_return(
    request: VATReturnCalculationRequest,
    http_request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Anmeldung aus dem Hauptbuch anlegen. Mit offenen Klaerungen wird nichts angelegt (422)."""
    effective_tenant_id = _resolve_vat_request_tenant(request.tenant_id, tenant_id)
    akteur = gepruefter_akteur_aus_request(http_request)
    stand = _stand(db, effective_tenant_id, request.period)
    if stand.klaerungen:
        raise HTTPException(status_code=422, detail={"message": "Die Voranmeldung ist nicht eindeutig.",
                                                     "klaerungen": stand.klaerungen})
    try:
        firma = db.execute(
            text("SELECT name FROM domain_shared.tenants WHERE id = :tid"), {"tid": effective_tenant_id}
        ).scalar()
        row = db.execute(
            text(f"""
                INSERT INTO domain_erp.vat_returns
                (id, tenant_id, period, return_type, taxpayer_name, tax_id, vat_id,
                 total_sales_net, total_input_tax, total_output_tax, vat_payable,
                 positions, status, calculated_at, calculated_by, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :period, :return_type, :taxpayer_name, NULL, NULL,
                 :total_sales_net, :total_input_tax, :total_output_tax, :vat_payable,
                 CAST(:positions AS jsonb), 'calculated', NOW(), :akteur, NOW(), NOW())
                RETURNING {_SPALTEN}
            """),  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
            {
                "id": uuid7(),
                "tenant_id": effective_tenant_id,
                "period": request.period,
                "return_type": "quarterly" if "-Q" in request.period else "monthly",
                "taxpayer_name": firma,
                "total_sales_net": stand.umsatz_netto,
                "total_input_tax": stand.vorsteuer,
                "total_output_tax": stand.umsatzsteuer,
                "vat_payable": stand.zahllast,
                "positions": json.dumps(_positionen(stand)),
                "akteur": akteur,
            },
        ).mappings().one()
        db.commit()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    return _build_vat_return_response(row)


@router.get("/{return_id}", response_model=VATReturnResponse, summary="Vat return abrufen", dependencies=[Depends(finance_read)])
async def get_vat_return(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    return _build_vat_return_response(_lies(db, return_id, tenant_id))


@router.get("/export/{return_id}", summary="Vat return download exportieren",
    response_model=VatReturnExportOut, dependencies=[Depends(finance_read)])
async def export_vat_return_download(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alias fuer /{return_id}/elster-xml."""
    return await export_elster_xml(return_id, tenant_id, db)


@router.get("/{return_id}/elster-xml", summary="Elster xml exportieren",
    response_model=VatReturnExportOut, dependencies=[Depends(finance_read)])
async def export_elster_xml(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Kennzahlen der Anmeldung als XML (Datenaustausch, z. B. Steuerberatung) — keine signierte ERiC-Uebermittlung."""
    from app.elster import build_ustva_elster_xml

    vat_return = await get_vat_return(return_id, tenant_id, db)
    xml_bytes = build_ustva_elster_xml(
        period=vat_return.period,
        taxpayer_name=vat_return.taxpayer_name or "",
        tax_id=vat_return.tax_id,
        vat_id=vat_return.vat_id,
        positions=vat_return.positions,
        vat_payable=vat_return.vat_payable,
    )
    return Response(
        content=xml_bytes,
        media_type="application/xml; charset=ISO-8859-15",
        headers={"Content-Disposition": f'attachment; filename="UStVA_{vat_return.period}.xml"'},
    )


@router.post("/{return_id}/validate", summary="Vat return validieren",
    response_model=VatReturnExportOut, dependencies=[Depends(finance_write)])
async def validate_vat_return(
    return_id: str,
    http_request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Anmeldung gegen das aktuelle Hauptbuch pruefen. Gueltig nur ohne Abweichung, Klaerung und offene Entwuerfe."""
    akteur = gepruefter_akteur_aus_request(http_request)
    gespeichert = _lies(db, return_id, tenant_id, sperren=True)
    if gespeichert["status"] not in ("calculated", "validated"):
        raise HTTPException(status_code=409, detail=f"Anmeldung ist bereits {gespeichert['status']}.")
    stand = _stand(db, tenant_id, gespeichert["period"])
    differences = _abweichungen(gespeichert, stand)
    hindernisse = list(stand.klaerungen)
    if stand.offene_entwuerfe:
        hindernisse.append(f"{stand.offene_entwuerfe} Buchungsentwürfe im Zeitraum sind nicht gebucht.")
    is_valid = not differences and not hindernisse
    try:
        if is_valid:
            db.execute(
                text("""
                    UPDATE domain_erp.vat_returns
                    SET status = 'validated', validated_at = NOW(), validated_by = :akteur, updated_at = NOW()
                    WHERE id = :return_id AND tenant_id = :tenant_id
                """),
                {"return_id": return_id, "tenant_id": tenant_id, "akteur": akteur},
            )
            db.commit()
        else:
            db.rollback()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    return {
        "valid": is_valid,
        "differences": differences,
        "hindernisse": hindernisse,
        "message": "Anmeldung stimmt mit dem Hauptbuch überein." if is_valid
        else "Anmeldung weicht vom Hauptbuch ab oder der Zeitraum ist nicht abgeschlossen.",
    }


@router.get("", response_model=List[VATReturnResponse], summary="Vat returns auflisten", dependencies=[Depends(finance_read)])
async def list_vat_returns(
    period: Optional[str] = Query(None, description="Filter by period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Anmeldungen des Mandanten. Ein Lesefehler ist 503, keine leere Liste."""
    sql = f"SELECT {_SPALTEN} FROM domain_erp.vat_returns WHERE tenant_id = :tenant_id"  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if period:
        sql += " AND period = :period"
        params["period"] = period
    sql += " ORDER BY period DESC, created_at DESC"
    try:
        rows = db.execute(text(sql), params).mappings().all()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    return [_build_vat_return_response(row) for row in rows]


@router.post("/{return_id}/approve", response_model=VATReturnResponse, summary="Vat return genehmigen", dependencies=[Depends(finance_admin)])
async def approve_vat_return(
    return_id: str,
    http_request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Freigabe einer geprueften Anmeldung. Hat sich das Hauptbuch seit der Pruefung geaendert: 409."""
    akteur = gepruefter_akteur_aus_request(http_request)
    gespeichert = _lies(db, return_id, tenant_id, sperren=True)
    if gespeichert["status"] != "validated":
        raise HTTPException(status_code=409, detail="Nur eine geprüfte Anmeldung kann freigegeben werden.")
    stand = _stand(db, tenant_id, gespeichert["period"])
    if _abweichungen(gespeichert, stand) or stand.klaerungen or stand.offene_entwuerfe:
        db.rollback()
        raise HTTPException(status_code=409, detail="Das Hauptbuch hat sich seit der Prüfung geändert; bitte neu berechnen.")
    try:
        db.execute(
            text("""
                UPDATE domain_erp.vat_returns
                SET status = 'approved', approved_at = NOW(), approved_by = :akteur, updated_at = NOW()
                WHERE id = :return_id AND tenant_id = :tenant_id
            """),
            {"return_id": return_id, "tenant_id": tenant_id, "akteur": akteur},
        )
        db.commit()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    return _build_vat_return_response(_lies(db, return_id, tenant_id))


@router.post("/{return_id}/submit", response_model=VATReturnResponse, summary="Vat return einreichen", dependencies=[Depends(finance_admin)])
async def submit_vat_return(
    return_id: str,
    request: VATReturnSubmitRequest,
    http_request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Haelt die im ELSTER-Portal erfolgte Uebermittlung mit ihrem Transferticket fest. Uebermittelt selbst nichts."""
    akteur = gepruefter_akteur_aus_request(http_request)
    gespeichert = _lies(db, return_id, tenant_id, sperren=True)
    if gespeichert["status"] != "approved":
        raise HTTPException(status_code=409, detail="Nur eine freigegebene Anmeldung kann als übermittelt gelten.")
    try:
        db.execute(
            text("""
                UPDATE domain_erp.vat_returns
                SET status = 'submitted', submitted_at = :jetzt, submitted_by = :akteur,
                    elster_transferticket = :ticket, updated_at = NOW()
                WHERE id = :return_id AND tenant_id = :tenant_id
            """),
            {"return_id": return_id, "tenant_id": tenant_id, "akteur": akteur,
             "ticket": request.transferticket.strip(), "jetzt": datetime.now(timezone.utc)},
        )
        db.commit()
    except SQLAlchemyError as exc:
        raise _nicht_verfuegbar(db, exc) from exc
    return _build_vat_return_response(_lies(db, return_id, tenant_id))
