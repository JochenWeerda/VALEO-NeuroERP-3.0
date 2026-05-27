"""
Bank Accounts API - Bankkonto Management (SQLAlchemy)
"""

from typing import Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.repository import BankKontoRepository

router = APIRouter(prefix="/banken", tags=["Banken"])


class BankKontoCreate(BaseModel):
    iban: str = Field(..., description="IBAN")
    bic: str = Field(..., description="BIC/SWIFT")
    bank_name: str = Field(..., description="Bank name")
    kontoart: str = Field(..., description="Account type")
    waehrung: str = Field(default="EUR")
    ist_aktiv: bool = Field(default=True)
    saldo: float = Field(default=0)


class BankKontoUpdate(BaseModel):
    bank_name: Optional[str] = None
    kontoart: Optional[str] = None
    ist_aktiv: Optional[bool] = None
    status: Optional[str] = None
    saldo: Optional[float] = None


def _to_dict(konto) -> dict:
    return {
        "id": konto.id,
        "iban": konto.iban,
        "bic": konto.bic,
        "bank": konto.bank,
        "kontoart": konto.kontoart,
        "saldo": float(konto.saldo or 0),
        "waehrung": konto.waehrung,
        "status": konto.status,
        "ist_aktiv": bool(konto.ist_aktiv),
        "created_at": konto.created_at.isoformat() if konto.created_at else None,
        "updated_at": konto.updated_at.isoformat() if konto.updated_at else None,
    }


@router.get("/konten", response_model=dict, summary="Bankkonten auflisten")
async def list_bankkonten(
    kontoart: Optional[str] = Query(None, description="Filter by account type"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    repo = BankKontoRepository(db)
    items = repo.get_all(skip=offset, limit=limit, kontoart=kontoart, ist_aktiv=ist_aktiv)
    total = repo.count(kontoart=kontoart, ist_aktiv=ist_aktiv)
    return {"items": [_to_dict(i) for i in items], "total": total, "limit": limit, "offset": offset}


@router.get("/konten/{konto_id}", response_model=dict, summary="Bankkonto abrufen")
async def get_bankkonto(konto_id: str, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    konto = repo.get_by_id(konto_id)
    if not konto:
        raise HTTPException(status_code=404, detail="Bankkonto not found")
    return _to_dict(konto)


@router.post("/konten", response_model=dict, status_code=201, summary="Bankkonto anlegen")
async def create_bankkonto(data: BankKontoCreate, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    if repo.get_by_iban(data.iban):
        raise HTTPException(status_code=409, detail="IBAN already exists")

    payload = {
        "iban": data.iban.replace(" ", "").upper(),
        "bic": data.bic.upper(),
        "bank": data.bank_name,
        "kontoart": data.kontoart,
        "saldo": data.saldo,
        "waehrung": data.waehrung,
        "status": "aktiv" if data.ist_aktiv else "inaktiv",
        "ist_aktiv": data.ist_aktiv,
    }
    konto = repo.create(payload)
    return _to_dict(konto)


@router.patch("/konten/{konto_id}", response_model=dict, summary="Bankkonto aktualisieren")
async def update_bankkonto(konto_id: str, data: BankKontoUpdate, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    payload = data.model_dump(exclude_unset=True)
    if "bank_name" in payload:
        payload["bank"] = payload.pop("bank_name")
    konto = repo.update(konto_id, payload)
    if not konto:
        raise HTTPException(status_code=404, detail="Bankkonto not found")
    return _to_dict(konto)


@router.delete("/konten/{konto_id}", status_code=204, response_class=Response, response_model=None, summary="Bankkonto löschen")
async def delete_bankkonto(konto_id: str, db: Session = Depends(get_db)):
    repo = BankKontoRepository(db)
    if not repo.deactivate(konto_id):
        raise HTTPException(status_code=404, detail="Bankkonto not found")


@router.get("/salden", response_model=dict, summary="Salden abrufen")
async def get_salden(db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    return repo.get_salden()


@router.get("/konten/iban-validate", response_model=dict, summary="Iban validieren")
async def validate_iban(iban: str = Query(..., description="IBAN to validate")) -> dict:
    normalized = iban.replace(" ", "").upper()
    is_valid = len(normalized) >= 15 and normalized[:2].isalpha()
    return {
        "iban": iban,
        "valid": is_valid,
        "bic": "UNKNOWN",
        "bank": None,
    }


# ── FinTS/HBCI Online-Banking Endpoints (PSD2 / § 25a KWG) ───────────────────

class UeberweisungRequest(BaseModel):
    auftraggeber_iban: str
    empfaenger_iban: str
    empfaenger_name: str
    betrag: float = Field(..., gt=0)
    verwendungszweck: str = Field(..., max_length=140)
    blz: str = ""
    user_id: str = ""
    pin: str = Field("", description="Nur für einmalige Übertragung — empfohlen: Env-Var FINTS_PIN")


@router.get("/banken/fints/konten", summary="Konten via FinTS/HBCI abrufen",
    response_model=dict
)
async def fints_get_konten(
    blz: str = Query("", description="Bankleitzahl (optional wenn via Env-Var)"),
    user_id: str = Query("", description="Online-Banking Benutzerkennung"),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Liefert Konten und Salden via FinTS/HBCI (HKSAL). Simulator-Modus wenn nicht konfiguriert."""
    from app.services.fints_connector import get_konten
    result = get_konten(blz=blz, user_id=user_id)
    return {
        "erfolg": result.erfolg,
        "fehler": result.fehler,
        "konten": [
            {
                "iban": k.iban, "bic": k.bic, "kontoinhaber": k.kontoinhaber,
                "saldo": float(k.saldo) if k.saldo is not None else None,
                "saldo_datum": str(k.saldo_datum) if k.saldo_datum else None,
            }
            for k in result.konten
        ],
        "modus": result.rohdaten.get("mode", "produktiv") if result.rohdaten else "produktiv",
    }


@router.get("/banken/fints/umsaetze", summary="Kontoumsätze via FinTS/HBCI abrufen (HKKAZ,
    response_model=dict
)")
async def fints_get_umsaetze(
    iban: str = Query(..., description="IBAN des Kontos"),
    von: str = Query(..., description="Von-Datum YYYY-MM-DD"),
    bis: str = Query(..., description="Bis-Datum YYYY-MM-DD"),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Ruft Kontoumsätze ab via FinTS CAMT.052 (HKKAZ/HKCAZ)."""
    from datetime import date as _date
    from app.services.fints_connector import get_umsaetze
    result = get_umsaetze(
        iban=iban,
        von=_date.fromisoformat(von),
        bis=_date.fromisoformat(bis),
    )
    return {
        "erfolg": result.erfolg,
        "fehler": result.fehler,
        "iban": iban,
        "zeitraum": {"von": von, "bis": bis},
        "buchungen": [
            {
                "datum": str(b.datum), "valuta": str(b.valuta),
                "betrag": float(b.betrag), "waehrung": b.waehrung,
                "auftraggeber": b.auftraggeber,
                "verwendungszweck": b.verwendungszweck,
                "end_to_end_id": b.end_to_end_id,
            }
            for b in result.buchungen
        ],
        "anzahl": len(result.buchungen),
        "modus": result.rohdaten.get("mode", "produktiv") if result.rohdaten else "produktiv",
    }


@router.post("/banken/fints/ueberweisung", summary="SEPA-Überweisung via FinTS senden (HKCCM,
    response_model=dict
)")
async def fints_send_ueberweisung(
    body: UeberweisungRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Sendet SEPA-Überweisung über FinTS/HBCI. Erfordert TAN in Produktion."""
    from decimal import Decimal as _Decimal
    from app.services.fints_connector import send_ueberweisung
    result = send_ueberweisung(
        auftraggeber_iban=body.auftraggeber_iban,
        empfaenger_iban=body.empfaenger_iban,
        empfaenger_name=body.empfaenger_name,
        betrag=_Decimal(str(body.betrag)),
        verwendungszweck=body.verwendungszweck,
        blz=body.blz,
        user_id=body.user_id,
        pin=body.pin,
    )
    return {"erfolg": result.erfolg, "fehler": result.fehler, "details": result.rohdaten}


class TanInitRequest(BaseModel):
    auftraggeber_iban: str
    empfaenger_iban: str
    empfaenger_name: str
    betrag: float
    verwendungszweck: str
    tan_verfahren_id: str = ""
    blz: str = ""
    user_id: str = ""
    pin: str = ""


class TanBestaetigenRequest(BaseModel):
    session_token: str
    tan: str
    blz: str = ""
    user_id: str = ""
    pin: str = ""


@router.get("/banken/fints/tan-medien", response_model=dict, summary="Verfügbare TAN-Medien abrufen (ChipTAN/pushTAN)")
async def fints_tan_medien(tenant_id: str = Depends(get_tenant_id)) -> dict:
    """Listet alle konfigurierten TAN-Verfahren des FinTS-Zugangs."""
    from app.services.fints_connector import get_tan_medien
    result = get_tan_medien()
    return {"erfolg": result.erfolg, "fehler": result.fehler, "tan_medien": result.rohdaten}


@router.post("/banken/fints/ueberweisung/tan-initiieren", response_model=dict, summary="Überweisung mit TAN einleiten (Schritt 1)")
async def fints_tan_initiieren(body: TanInitRequest, tenant_id: str = Depends(get_tenant_id)) -> dict:
    """Leitet SEPA-Überweisung ein und gibt TAN-Challenge zurück (ChipTAN/pushTAN Schritt 1)."""
    from decimal import Decimal as _Decimal
    from app.services.fints_connector import initiiere_ueberweisung_mit_tan
    ergebnis, challenge = initiiere_ueberweisung_mit_tan(
        auftraggeber_iban=body.auftraggeber_iban,
        empfaenger_iban=body.empfaenger_iban,
        empfaenger_name=body.empfaenger_name,
        betrag=_Decimal(str(body.betrag)),
        verwendungszweck=body.verwendungszweck,
        blz=body.blz,
        user_id=body.user_id,
        pin=body.pin,
        tan_verfahren_id=body.tan_verfahren_id,
    )
    return {
        "erfolg": ergebnis.erfolg,
        "fehler": ergebnis.fehler,
        "schritt": "challenge" if challenge else "abgeschlossen",
        "challenge": {
            "tan_medium": challenge.tan_medium,
            "challenge_text": challenge.challenge_text,
            "challenge_hhduc": challenge.challenge_hhduc,
            "tan_verfahren": challenge.tan_verfahren,
            "session_token": challenge.session_token,
        } if challenge else None,
    }


@router.post("/banken/fints/ueberweisung/tan-bestaetigen", response_model=dict, summary="TAN bestätigen und Überweisung abschließen (Schritt 2)")
async def fints_tan_bestaetigen(body: TanBestaetigenRequest, tenant_id: str = Depends(get_tenant_id)) -> dict:
    """Bestätigt TAN und schließt die Überweisung ab (ChipTAN/pushTAN Schritt 2)."""
    from app.services.fints_connector import bestaetige_tan
    result = bestaetige_tan(
        session_token=body.session_token,
        tan=body.tan,
        blz=body.blz,
        user_id=body.user_id,
        pin=body.pin,
    )
    return {"erfolg": result.erfolg, "fehler": result.fehler, "details": result.rohdaten}
