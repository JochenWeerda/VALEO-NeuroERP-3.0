"""Lohnabrechnung — Brutto-Netto-Preview und Monats-Closeout.

Herausgenommen aus `personal.py` am 06.10.2026 (Godfile-Ratsche). Die Rechnung
selbst liegt wie bisher in `app/services/lohn_service.py`; hier stehen nur die
Wege und ihre Vertraege.

Der Code ist **unveraendert** uebernommen. Grundlage und Vorbehalt bleiben
dieselben: § 38 EStG, SGB IV; produktiv massgeblich sind amtlicher BMF-PAP,
DATEV-/Steuerberaterfreigabe und freigegebene SV-Parameter.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/personal", tags=["personal", "hr", "lohn"])


class LohnBerechnungRequest(BaseModel):
    brutto: float = Field(..., gt=0, description="Monatliches Bruttogehalt EUR")
    steuerklasse: int = Field(..., ge=1, le=6)
    hat_kinder: bool = False
    kinder_freibetraege: float = Field(0.0, ge=0)
    kirchensteuersatz: float = Field(0.09, ge=0, le=0.12, description="0,08 oder 0,09")
    zusatzbeitrag_kv: float = Field(0.029, ge=0, le=0.05, description="Individueller KV-Zusatzbeitrag")
    jahr: int = Field(2026, ge=2025, le=2100)


class LohnBerechnungResponse(BaseModel):
    eingabe: dict[str, Any]
    ergebnis: dict[str, Any]
    hinweis: str
    beitragsgrundlagen: dict[str, float]


class PayrollCloseoutEmployeeIn(BaseModel):
    employeeRef: str = Field(..., min_length=1, max_length=120)
    gross: float = Field(..., gt=0)
    taxClass: int = Field(..., ge=1, le=6)
    hasChildren: bool = False
    childAllowances: float = Field(0.0, ge=0)
    churchTaxRate: float = Field(0.09, ge=0, le=0.12)
    healthAdditionalRate: float | None = Field(default=None, ge=0, le=0.05)
    costCenter: str | None = Field(default=None, max_length=80)
    personnelNumber: str | None = Field(default=None, max_length=80)


class PayrollCloseoutPreviewIn(BaseModel):
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    employees: list[PayrollCloseoutEmployeeIn] = Field(..., min_length=1)


class PayrollCloseoutPreviewOut(BaseModel):
    period: str
    parameterVersion: str
    status: str
    totals: dict[str, float]
    lines: list[dict[str, Any]]
    blockers: list[dict[str, str]]
    externalGates: list[str]


@router.post(
    "/lohn/berechnung",
    summary="Brutto-Netto-Berechnung als Payroll-Preview",
    response_model=LohnBerechnungResponse,
)
async def berechne_lohn(
    payload: LohnBerechnungRequest,
    tenant_id: str = Depends(get_tenant_id),  # noqa: ARG001 - mandantenpflichtiger Payroll-Kontext
) -> dict:
    from app.services.lohn_service import berechne_netto

    ergebnis = berechne_netto(
        brutto=payload.brutto,
        steuerklasse=payload.steuerklasse,
        hat_kinder=payload.hat_kinder,
        kinder_freibetraege=payload.kinder_freibetraege,
        kirchensteuersatz=payload.kirchensteuersatz,
        zusatzbeitrag_kv=payload.zusatzbeitrag_kv,
        year=payload.jahr,
    )
    return {
        "eingabe": payload.model_dump(),
        "ergebnis": ergebnis.as_dict(),
        "hinweis": "Preview-Berechnung. Produktiv massgeblich sind amtlicher BMF-PAP, DATEV-/Steuerberaterfreigabe und freigegebene SV-Parameter.",
        "beitragsgrundlagen": {
            "bbg_kv_monat": 5812.50,
            "bbg_rv_monat": 8450.00,
            "grundfreibetrag_monat": 1008.0,
        },
    }


@router.post(
    "/lohn/closeout-preview",
    summary="Payroll Monats-Closeout als DATEV-/FIBU-Uebergabevertrag vorbereiten",
    response_model=PayrollCloseoutPreviewOut,
)
async def preview_payroll_closeout(
    payload: PayrollCloseoutPreviewIn,
    tenant_id: str = Depends(get_tenant_id),  # noqa: ARG001 - Payroll bleibt mandantenpflichtig.
) -> dict:
    from decimal import Decimal

    from app.services.lohn_service import PayrollEmployeeInput, build_payroll_closeout

    try:
        closeout = build_payroll_closeout(
            payload.period,
            [
                PayrollEmployeeInput(
                    employee_ref=row.employeeRef,
                    gross=Decimal(str(row.gross)),
                    tax_class=row.taxClass,
                    has_children=row.hasChildren,
                    child_allowances=Decimal(str(row.childAllowances)),
                    church_tax_rate=Decimal(str(row.churchTaxRate)),
                    health_additional_rate=None if row.healthAdditionalRate is None else Decimal(str(row.healthAdditionalRate)),
                    cost_center=row.costCenter,
                    personnel_number=row.personnelNumber,
                )
                for row in payload.employees
            ],
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return closeout.as_dict()
