"""OP Skonto-Auszifferung — Offene Posten mit Skontoaufteilung ausgleichen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Bei der Auszifferung mit Skonto wird der eingegangene Zahlungsbetrag
  aufgeteilt in:
  1. Zahlungsbetrag (Kontoeingang)
  2. Skontoabzug (Skontokonto / Erlösminderung)

  Der Gesamtbetrag (Zahlung + Skonto) muss dem Rechnungsbetrag entsprechen.

  Fachlich: "Auszifferung mit Skonto aufteilen" ist eine Standard-FIBU-Funktion
  für Warenhändler. Der Skontobetrag wird auf ein separates Skontokonto gebucht.
  Wichtig für korrekte GuV-Darstellung und periodengerechte Buchung.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/fibu/op-auszifferung", tags=["FIBU - OP Skonto-Auszifferung"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SkontoAuszifferungCreate(BaseModel):
    op_id: str
    rechnungsnr: Optional[str] = None
    zahlungsdatum: date
    zahlungsbetrag_eur: Decimal = Field(..., gt=0)
    skonto_betrag_eur: Decimal = Field(default=Decimal("0"), ge=0)
    zahlungsart: Optional[str] = Field(None,
        description="ueberweisung, lastschrift, bar, scheck")
    buchungstext: Optional[str] = None
    fibu_konto: Optional[str] = None
    skonto_konto: Optional[str] = Field(None,
        description="FIBU-Skontokonto (z.B. 8736 SKR03 Erhaltene Skonti)")

    @model_validator(mode="after")
    def validate_betraege(self) -> "SkontoAuszifferungCreate":
        gesamt = self.zahlungsbetrag_eur + self.skonto_betrag_eur
        if gesamt <= 0:
            raise ValueError("Gesamtbetrag muss positiv sein.")
        return self


class SkontoAuszifferungOut(BaseModel):
    id: str
    op_id: str
    rechnungsnr: Optional[str]
    zahlungsdatum: date
    zahlungsbetrag_eur: Decimal
    skonto_betrag_eur: Decimal
    skonto_prozent: Optional[Decimal]
    gesamtbetrag_eur: Decimal
    zahlungsart: Optional[str]
    buchungstext: Optional[str]
    fibu_konto: Optional[str]
    skonto_konto: Optional[str]
    status: str
    storniert: bool
    created_at: datetime


class SkontoBerechnung(BaseModel):
    rechnungsbetrag_eur: Decimal = Field(..., gt=0)
    skonto_prozent: Decimal = Field(..., ge=0, le=100)
    zahlungsdatum: date
    skonto_bis: Optional[date] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/berechnen", summary="Skonto berechne",
    response_model=dict
)
def berechne_skonto(payload: SkontoBerechnung):
    """Skontobetrag aus Rechnungsbetrag und Prozentsatz berechnen.

    Prüft auch ob das Skontodatum noch gültig ist.
    """
    skonto_gueltig = True
    if payload.skonto_bis and payload.zahlungsdatum > payload.skonto_bis:
        skonto_gueltig = False

    skontobetrag = Decimal("0")
    if skonto_gueltig:
        skontobetrag = (payload.rechnungsbetrag_eur * payload.skonto_prozent / 100
                        ).quantize(Decimal("0.01"))

    zahlungsbetrag = payload.rechnungsbetrag_eur - skontobetrag

    return {
        "rechnungsbetrag_eur": float(payload.rechnungsbetrag_eur),
        "skonto_prozent": float(payload.skonto_prozent),
        "skonto_gueltig": skonto_gueltig,
        "skontobetrag_eur": float(skontobetrag),
        "zahlungsbetrag_eur": float(zahlungsbetrag),
        "hinweis": None if skonto_gueltig else
                   f"Skontofrist abgelaufen (Fälligkeit: {payload.skonto_bis})",
    }


@router.get("", response_model=list[SkontoAuszifferungOut], summary="Auszifferungen auflisten")
def list_auszifferungen(
    op_id: Optional[str] = Query(None),
    von_datum: Optional[date] = Query(None),
    bis_datum: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.op_auszifferungen
        WHERE tenant_id = :tid AND NOT storniert
    """
    params: dict = {"tid": tenant_id}
    if op_id:
        sql += " AND op_id = :op_id"
        params["op_id"] = op_id
    if von_datum:
        sql += " AND zahlungsdatum >= :von"
        params["von"] = von_datum
    if bis_datum:
        sql += " AND zahlungsdatum <= :bis"
        params["bis"] = bis_datum
    sql += " ORDER BY zahlungsdatum DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [SkontoAuszifferungOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=SkontoAuszifferungOut, status_code=201, summary="Auszifferung anlegen")
def create_auszifferung(
    payload: SkontoAuszifferungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """OP mit Skonto ausgleichen.

    Bei Skonto > 0 wird die Buchung aufgeteilt:
    - Zahlungsbetrag → Bankkonto/Debitorenkonto
    - Skontobetrag → Skontokonto (Erlösminderung)
    """
    gesamtbetrag = payload.zahlungsbetrag_eur + payload.skonto_betrag_eur
    skonto_prozent = None
    if gesamtbetrag > 0 and payload.skonto_betrag_eur > 0:
        skonto_prozent = (payload.skonto_betrag_eur / gesamtbetrag * 100
                          ).quantize(Decimal("0.0001"))

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.op_auszifferungen
            (id, tenant_id, op_id, rechnungsnr, zahlungsdatum,
             zahlungsbetrag_eur, skonto_betrag_eur, skonto_prozent,
             gesamtbetrag_eur, zahlungsart, buchungstext,
             fibu_konto, skonto_konto, status, storniert)
        VALUES (:id, :tid, :op_id, :rechnungsnr, :zdatum,
                :zbetrag, :skonto, :sprozent,
                :gesamt, :zart, :btext,
                :fibu_kto, :skonto_kto, 'gebucht', false)
    """), {
        "id": new_id, "tid": tenant_id, "op_id": payload.op_id,
        "rechnungsnr": payload.rechnungsnr, "zdatum": payload.zahlungsdatum,
        "zbetrag": payload.zahlungsbetrag_eur, "skonto": payload.skonto_betrag_eur,
        "sprozent": skonto_prozent, "gesamt": gesamtbetrag,
        "zart": payload.zahlungsart, "btext": payload.buchungstext,
        "fibu_kto": payload.fibu_konto, "skonto_kto": payload.skonto_konto,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.op_auszifferungen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return SkontoAuszifferungOut(**dict(row._mapping))


@router.post("/{auszifferung_id}/stornieren", response_model=SkontoAuszifferungOut, summary="Auszifferung storniere")
def storniere_auszifferung(
    auszifferung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Auszifferung stornieren — OP wird wieder geöffnet."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.op_auszifferungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": auszifferung_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Auszifferung nicht gefunden.")
    if row.storniert:
        raise HTTPException(409, "Bereits storniert.")

    db.execute(text("""
        UPDATE domain_shared.op_auszifferungen
        SET storniert = true, status = 'storniert'
        WHERE id = :id
    """), {"id": auszifferung_id})
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.op_auszifferungen WHERE id = :id
    """), {"id": auszifferung_id}).fetchone()
    return SkontoAuszifferungOut(**dict(row._mapping))
