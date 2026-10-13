"""
Tax Keys API
FIBU-TAX-01: Steuerschlüssel-System vervollständigen
"""

from app.auth.finance_roles import finance_admin, finance_write
from typing import List, Optional
from typing import Any
from fastapi import Body, Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
import logging

from ....core.database import get_db
from app.core.read_model_cache import cached_read_model, invalidate_tenant_prefix
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.finance.steuerschluessel import Kontovorschlag, konto_hindernis, kontenvorschlaege, verwendung
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/tax-keys", tags=["finance", "tax"])


class TaxKeyCreate(BaseModel):
    """Schema for creating a tax key"""
    code: str = Field(..., max_length=2, description="Tax key code (1-2 digits)")
    bezeichnung: str = Field(..., max_length=100, description="Tax key description")
    steuersatz: Decimal = Field(..., ge=0, le=100, description="Tax rate in percent")
    ustva_position: str = Field(..., max_length=10, description="UStVA position code")
    ustva_bezeichnung: str = Field(..., max_length=200, description="UStVA description")
    intracom: bool = Field(default=False, description="Intracommunity delivery (EU)")
    export: bool = Field(default=False, description="Export outside EU")
    reverse_charge: bool = Field(default=False, description="Reverse charge mechanism")
    gueltig_von: date = Field(..., description="Valid from date")
    gueltig_bis: Optional[date] = Field(None, description="Valid until date")
    notizen: Optional[str] = Field(None, max_length=500, description="Internal notes")
    debit_account: Optional[str] = Field(None, max_length=20, description="Debit account for tax")
    credit_account: Optional[str] = Field(None, max_length=20, description="Credit account for tax")
    revenue_account: Optional[str] = Field(
        None, max_length=20, description="Erloeskonto fuer Verkaufsbelege; leer = nicht automatisch buchen")
    par_24_ustg: bool = Field(default=False, description="Durchschnittssatz nach Paragraf 24 UStG")
    country: str = Field(default="DE", max_length=2, description="Country code (ISO 3166-1 alpha-2)")
    region: Optional[str] = Field(None, max_length=50, description="Region/state if applicable")
    active: bool = Field(default=True, description="Active status")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) > 2:
            raise ValueError('Code must be 1-2 digits')
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str):
        v = (v or "").strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('country must be ISO 3166-1 alpha-2 (e.g. DE)')
        return v

    @field_validator('gueltig_bis')
    @classmethod
    def validate_valid_until(cls, v, info):
        gueltig_von = info.data.get("gueltig_von")
        if v is not None and gueltig_von is not None and v < gueltig_von:
            raise ValueError('gueltig_bis must be >= gueltig_von')
        return v

    @field_validator('reverse_charge')
    @classmethod
    def validate_reverse_charge_rate(cls, v, info):
        steuersatz = info.data.get("steuersatz")
        if v and steuersatz is not None and Decimal(str(steuersatz)) != Decimal("0"):
            raise ValueError('reverse_charge requires steuersatz = 0')
        return v


class TaxKeyUpdate(BaseModel):
    """Schema for updating a tax key"""
    bezeichnung: Optional[str] = Field(None, max_length=100)
    steuersatz: Optional[Decimal] = Field(None, ge=0, le=100)
    ustva_position: Optional[str] = Field(None, max_length=10)
    ustva_bezeichnung: Optional[str] = Field(None, max_length=200)
    intracom: Optional[bool] = None
    export: Optional[bool] = None
    reverse_charge: Optional[bool] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    notizen: Optional[str] = Field(None, max_length=500)
    debit_account: Optional[str] = Field(None, max_length=20)
    credit_account: Optional[str] = Field(None, max_length=20)
    revenue_account: Optional[str] = Field(None, max_length=20)
    par_24_ustg: Optional[bool] = None
    country: Optional[str] = Field(None, max_length=2)
    region: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('country must be ISO 3166-1 alpha-2 (e.g. DE)')
        return v


class TaxKeyResponse(BaseModel):
    """Response schema for tax key"""
    id: str
    code: str
    bezeichnung: str
    steuersatz: Decimal
    ustva_position: Optional[str]
    ustva_bezeichnung: Optional[str]
    intracom: bool
    export: bool
    reverse_charge: bool
    gueltig_von: date
    gueltig_bis: Optional[date]
    notizen: Optional[str]
    debit_account: Optional[str]
    credit_account: Optional[str]
    country: str
    region: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime
    revenue_account: Optional[str] = None
    par_24_ustg: bool = False
    # Wofuer der Schluessel automatisch bucht (Verkauf, Einkauf) oder warum nicht.
    verwendung: Optional[str] = None


def _oder_leer(wert: Any) -> Optional[str]:
    return str(wert) if wert else None


def _antwort(row: Any) -> TaxKeyResponse:
    """Die Zeile in der Spaltenfolge der Abfragen dieses Moduls."""
    satz = Decimal(str(row[3]))
    return TaxKeyResponse(
        id=str(row[0]), code=str(row[1]), bezeichnung=str(row[2]), steuersatz=satz,
        ustva_position=_oder_leer(row[4]), ustva_bezeichnung=_oder_leer(row[5]),
        intracom=bool(row[6]), export=bool(row[7]), reverse_charge=bool(row[8]),
        gueltig_von=row[9], gueltig_bis=row[10], notizen=_oder_leer(row[11]),
        debit_account=_oder_leer(row[12]), credit_account=_oder_leer(row[13]),
        country=str(row[14]), region=_oder_leer(row[15]), active=bool(row[16]),
        created_at=row[17], updated_at=row[18],
        revenue_account=_oder_leer(row[19]), par_24_ustg=bool(row[20]),
        verwendung=verwendung(str(row[1]), satz, row[13], row[12], row[19], bool(row[8])),
    )


@router.get("", response_model=List[TaxKeyResponse], summary="Tax keys auflisten")
@cached_read_model("tax_keys", ttl=3600)
async def list_tax_keys(
    tenant_id: str = Depends(get_tenant_id),
    active_only: bool = Query(True, description="Show only active tax keys"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    db: Session = Depends(get_db)
):
    """
    List all tax keys.
    """
    try:
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": tenant_id}

        if active_only:
            where_clauses.append("active = true")
        if country:
            where_clauses.append("country = :country")
            params["country"] = country.strip().upper()

        query = text(
            f"""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at, revenue_account, par_24_ustg
            FROM domain_erp.tax_keys
            WHERE {' AND '.join(where_clauses)}
            ORDER BY code
            """  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
        )
        
        rows = db.execute(query, params).fetchall()
        
        return [_antwort(row) for row in rows]
        
    except Exception as e:
        db.rollback()
        logger.error("Error listing tax keys: %s", e, exc_info=True)
        # Ein Ladefehler ist kein leerer Bestand; die leere Liste laege sonst eine Stunde im Cache.
        raise HTTPException(status_code=500, detail="Steuerschlüssel konnten nicht geladen werden.") from e


@router.get("/kontenvorschlaege", response_model=dict[str, List[Kontovorschlag]],
            summary="Konten aus dem Kontenplan je Feld des Steuerschlüssels vorschlagen")
async def list_kontenvorschlaege(
    steuersatz: Optional[str] = Query(None, description="Steuersatz in Prozent; reiht passende Konten nach vorn"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, List[Kontovorschlag]]:
    """Umsatzsteuer-, Vorsteuer- und Erlöskonten des Mandanten, die fachlich nächsten zuerst. Wählt nichts vor."""
    satz: Optional[Decimal] = None
    if steuersatz and steuersatz.strip():
        try:
            satz = Decimal(steuersatz.strip().replace(",", "."))
        except ArithmeticError:
            satz = None  # eine unfertige Eingabe reiht nur nicht; abgelehnt wird beim Speichern
    return kontenvorschlaege(db, tenant_id, satz)


@router.get("/{tax_key_id}", response_model=TaxKeyResponse, summary="Tax key abrufen")
async def get_tax_key(
    tax_key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get a single tax key by ID.
    """
    try:
        query = text("""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at, revenue_account, par_24_ustg
            FROM domain_erp.tax_keys
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "tax_key_id": tax_key_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        return _antwort(row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tax key: {str(e)}")


@router.post("", response_model=TaxKeyResponse, status_code=201, summary="Tax key anlegen", dependencies=[Depends(finance_write)])
async def create_tax_key(
    tax_key: TaxKeyCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a new tax key.
    """
    try:
        # Check if code already exists
        check_query = text("""
            SELECT id FROM domain_erp.tax_keys
            WHERE code = :code AND tenant_id = :tenant_id
        """)
        
        existing = db.execute(check_query, {
            "code": tax_key.code,
            "tenant_id": tenant_id
        }).fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Tax key with code {tax_key.code} already exists")
        
        # Insert new tax key
        tax_key_id = uuid7()
        
        insert_query = text("""
            INSERT INTO domain_erp.tax_keys
            (id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
             intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
             debit_account, credit_account, country, region, active, created_at, updated_at,
             revenue_account, par_24_ustg)
            VALUES
            (:id, :tenant_id, :code, :bezeichnung, :steuersatz, :ustva_position, :ustva_bezeichnung,
             :intracom, :export, :reverse_charge, :gueltig_von, :gueltig_bis, :notizen,
             :debit_account, :credit_account, :country, :region, :active, NOW(), NOW(),
             :revenue_account, :par_24_ustg)
            RETURNING id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                      intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                      debit_account, credit_account, country, region, active,
                      created_at, updated_at, revenue_account, par_24_ustg
        """)
        
        row = db.execute(insert_query, {
            "id": tax_key_id,
            "tenant_id": tenant_id,
            "code": tax_key.code,
            "bezeichnung": tax_key.bezeichnung,
            "steuersatz": tax_key.steuersatz,
            "ustva_position": tax_key.ustva_position,
            "ustva_bezeichnung": tax_key.ustva_bezeichnung,
            "intracom": tax_key.intracom,
            "export": tax_key.export,
            "reverse_charge": tax_key.reverse_charge,
            "gueltig_von": tax_key.gueltig_von,
            "gueltig_bis": tax_key.gueltig_bis,
            "notizen": tax_key.notizen,
            "debit_account": tax_key.debit_account,
            "credit_account": tax_key.credit_account,
            "country": tax_key.country,
            "region": tax_key.region,
            "active": tax_key.active,
            "revenue_account": tax_key.revenue_account,
            "par_24_ustg": tax_key.par_24_ustg,
        }).fetchone()
        
        db.commit()
        invalidate_tenant_prefix("tax_keys", tenant_id)
        
        return _antwort(row)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tax key: {str(e)}")


@router.put("/{tax_key_id}", response_model=TaxKeyResponse, summary="Tax key aktualisieren", dependencies=[Depends(finance_write)])
async def update_tax_key(
    tax_key_id: str,
    tax_key: TaxKeyUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing tax key.
    """
    try:
        current_row = db.execute(
            text(
                """
                SELECT steuersatz, reverse_charge, gueltig_von
                FROM domain_erp.tax_keys
                WHERE id = :tax_key_id AND tenant_id = :tenant_id
                """
            ),
            {"tax_key_id": tax_key_id, "tenant_id": tenant_id},
        ).fetchone()
        if not current_row:
            raise HTTPException(status_code=404, detail="Tax key not found")

        effective_rate = Decimal(str(tax_key.steuersatz if tax_key.steuersatz is not None else current_row[0]))
        effective_reverse = bool(tax_key.reverse_charge if tax_key.reverse_charge is not None else current_row[1])
        effective_from = tax_key.gueltig_von if tax_key.gueltig_von is not None else current_row[2]
        effective_until = tax_key.gueltig_bis

        if effective_reverse and effective_rate != Decimal("0"):
            raise HTTPException(status_code=422, detail="reverse_charge requires steuersatz = 0")
        if effective_until is not None and effective_from is not None and effective_until < effective_from:
            raise HTTPException(status_code=422, detail="gueltig_bis must be >= gueltig_von")

        # Build update query dynamically
        update_fields = []
        params = {"tax_key_id": tax_key_id, "tenant_id": tenant_id}
        
        if tax_key.bezeichnung is not None:
            update_fields.append("bezeichnung = :bezeichnung")
            params["bezeichnung"] = tax_key.bezeichnung
        if tax_key.steuersatz is not None:
            update_fields.append("steuersatz = :steuersatz")
            params["steuersatz"] = tax_key.steuersatz
        if tax_key.ustva_position is not None:
            update_fields.append("ustva_position = :ustva_position")
            params["ustva_position"] = tax_key.ustva_position
        if tax_key.ustva_bezeichnung is not None:
            update_fields.append("ustva_bezeichnung = :ustva_bezeichnung")
            params["ustva_bezeichnung"] = tax_key.ustva_bezeichnung
        if tax_key.intracom is not None:
            update_fields.append("intracom = :intracom")
            params["intracom"] = tax_key.intracom
        if tax_key.export is not None:
            update_fields.append("export = :export")
            params["export"] = tax_key.export
        if tax_key.reverse_charge is not None:
            update_fields.append("reverse_charge = :reverse_charge")
            params["reverse_charge"] = tax_key.reverse_charge
        if tax_key.gueltig_von is not None:
            update_fields.append("gueltig_von = :gueltig_von")
            params["gueltig_von"] = tax_key.gueltig_von
        if tax_key.gueltig_bis is not None:
            update_fields.append("gueltig_bis = :gueltig_bis")
            params["gueltig_bis"] = tax_key.gueltig_bis
        if tax_key.notizen is not None:
            update_fields.append("notizen = :notizen")
            params["notizen"] = tax_key.notizen
        if tax_key.debit_account is not None:
            update_fields.append("debit_account = :debit_account")
            params["debit_account"] = tax_key.debit_account
        if tax_key.credit_account is not None:
            update_fields.append("credit_account = :credit_account")
            params["credit_account"] = tax_key.credit_account
        if tax_key.revenue_account is not None:
            # Leere Angabe nimmt die Einordnung zurueck: Dann wird mit dem Schluessel nicht gebucht.
            update_fields.append("revenue_account = :revenue_account")
            params["revenue_account"] = tax_key.revenue_account.strip() or None
        if tax_key.par_24_ustg is not None:
            update_fields.append("par_24_ustg = :par_24_ustg")
            params["par_24_ustg"] = tax_key.par_24_ustg
        if tax_key.country is not None:
            update_fields.append("country = :country")
            params["country"] = tax_key.country
        if tax_key.region is not None:
            update_fields.append("region = :region")
            params["region"] = tax_key.region
        if tax_key.active is not None:
            update_fields.append("active = :active")
            params["active"] = tax_key.active
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = NOW()")
        
        update_query = text(f"""
            UPDATE domain_erp.tax_keys
            SET {', '.join(update_fields)}
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
            RETURNING id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                      intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                      debit_account, credit_account, country, region, active,
                      created_at, updated_at, revenue_account, par_24_ustg
        """)  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        
        row = db.execute(update_query, params).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        db.commit()
        invalidate_tenant_prefix("tax_keys", tenant_id)
        
        return _antwort(row)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update tax key: {str(e)}")


@router.delete("/{tax_key_id}", status_code=204, response_class=Response, response_model=None, summary="Tax key löschen", dependencies=[Depends(finance_admin)])
async def delete_tax_key(
    tax_key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Delete a tax key (soft delete by setting active=false).
    """
    try:
        update_query = text("""
            UPDATE domain_erp.tax_keys
            SET active = false, updated_at = NOW()
            WHERE id = :tax_key_id AND tenant_id = :tenant_id
        """)
        
        result = db.execute(update_query, {
            "tax_key_id": tax_key_id,
            "tenant_id": tenant_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tax key not found")
        
        db.commit()
        invalidate_tenant_prefix("tax_keys", tenant_id)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tax key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete tax key: {str(e)}")


@router.get("/code/{code}", response_model=TaxKeyResponse, summary="Tax key by code abrufen")
async def get_tax_key_by_code(
    code: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get tax key by code.
    """
    try:
        query = text("""
            SELECT id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung,
                   intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen,
                   debit_account, credit_account, country, region, active,
                   created_at, updated_at, revenue_account, par_24_ustg
            FROM domain_erp.tax_keys
            WHERE code = :code AND tenant_id = :tenant_id AND active = true
            ORDER BY gueltig_von DESC
            LIMIT 1
        """)
        
        row = db.execute(query, {
            "code": code,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Tax key with code {code} not found")
        
        return _antwort(row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax key by code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tax key: {str(e)}")


# ---------------------------------------------------------------------------
# Masken-Kommando (ScreenDefinition finance/steuerschluessel)
# ---------------------------------------------------------------------------

_KONTEN = (("credit_account", "Umsatzsteuerkonto"), ("debit_account", "Vorsteuerkonto"), ("revenue_account", "Erlöskonto"))
_KENNZEICHEN = ("par_24_ustg", "intracom", "export", "reverse_charge", "active")
_FELDTEXT = {
    "bezeichnung": "Bezeichnung", "steuersatz": "Steuersatz", "ustva_position": "UStVA-Kennzahl",
    "ustva_bezeichnung": "UStVA-Text", "credit_account": "Umsatzsteuerkonto", "debit_account": "Vorsteuerkonto",
    "revenue_account": "Erlöskonto", "par_24_ustg": "§ 24 UStG", "intracom": "Innergemeinschaftlich",
    "export": "Ausfuhr", "reverse_charge": "Reverse Charge", "gueltig_von": "Gültig von",
    "gueltig_bis": "Gültig bis", "notizen": "Notizen", "active": "Aktiv",
}
_SPALTEN = tuple(_FELDTEXT)


def _fehler(feld: str, meldung: str) -> dict[str, Any]:
    return {"field": feld, "message": meldung, "severity": "blocking"}


def _lies_eingabe(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Die Eingabe der Maske als Werte der Tabelle. Nichts wird ergaenzt: Ein fehlender Satz ist ein Fehler."""
    fehler: list[dict[str, Any]] = []

    def wort(feld: str) -> Optional[str]:
        roh = payload.get(feld)
        return (str(roh).strip() or None) if roh is not None else None

    def tag(feld: str, name: str) -> Optional[date]:
        roh = wort(feld)
        if roh is None:
            return None
        try:
            return date.fromisoformat(roh[:10])
        except ValueError:
            fehler.append(_fehler(feld, f"{name}: kein gültiges Datum."))
            return None

    werte: dict[str, Any] = {"code": wort("code") or ""}
    if not werte["code"].isdigit() or len(werte["code"]) > 2:
        fehler.append(_fehler("code", "Schlüssel: ein oder zwei Ziffern."))
    werte["bezeichnung"] = wort("bezeichnung")
    if not werte["bezeichnung"] or len(werte["bezeichnung"]) > 100:
        fehler.append(_fehler("bezeichnung", "Bezeichnung angeben (höchstens 100 Zeichen)."))

    satz = wort("steuersatz")
    werte["steuersatz"] = None
    if satz is None:
        fehler.append(_fehler("steuersatz", "Steuersatz angeben; es gibt keinen Vorgabewert."))
    else:
        try:
            werte["steuersatz"] = Decimal(satz.replace(",", "."))
        except ArithmeticError:
            fehler.append(_fehler("steuersatz", "Steuersatz: keine Zahl."))
        else:
            if not Decimal("0") <= werte["steuersatz"] <= Decimal("100"):
                fehler.append(_fehler("steuersatz", "Steuersatz: zwischen 0 und 100."))

    for feld in ("ustva_position", "ustva_bezeichnung", "notizen"):
        werte[feld] = wort(feld)
    for feld, name in _KONTEN:
        werte[feld] = wort(feld)
        if werte[feld] and len(werte[feld]) > 20:
            fehler.append(_fehler(feld, f"{name}: höchstens 20 Zeichen."))
    for feld in _KENNZEICHEN:
        roh = payload.get(feld, feld == "active")
        werte[feld] = roh if isinstance(roh, bool) else str(roh).strip().lower() in ("true", "1", "ja")

    werte["gueltig_von"] = tag("gueltig_von", "Gültig von")
    werte["gueltig_bis"] = tag("gueltig_bis", "Gültig bis")
    if werte["gueltig_von"] is None and not any(f["field"] == "gueltig_von" for f in fehler):
        fehler.append(_fehler("gueltig_von", "Gültig von angeben."))
    if werte["gueltig_von"] and werte["gueltig_bis"] and werte["gueltig_bis"] < werte["gueltig_von"]:
        fehler.append(_fehler("gueltig_bis", "Gültig bis liegt vor Gültig von."))
    if werte["reverse_charge"] and werte["steuersatz"]:
        fehler.append(_fehler("steuersatz", "Reverse Charge verlangt den Steuersatz 0."))
    return werte, fehler


def _bestand(db: Session, tenant_id: str, code: str) -> list[Any]:
    return db.execute(
        text(
            # Spaltenfolge wie _SPALTEN.
            "SELECT id, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung, credit_account, debit_account, "
            "revenue_account, par_24_ustg, intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen, active "
            "FROM domain_erp.tax_keys WHERE tenant_id = :tid AND code = :code"
        ),
        {"tid": tenant_id, "code": code},
    ).fetchall()


def _zeige(wert: Any) -> str:
    if wert is None or wert == "":
        return "–"
    if isinstance(wert, bool):
        return "ja" if wert else "nein"
    if isinstance(wert, Decimal):
        return f"{wert.normalize():f}".replace(".", ",")
    return str(wert)


@router.post("/actions/speichern", response_model=MaskActionResult,
             summary="Steuerschlüssel anlegen oder ändern (Masken-CommandEndpoint)",
             dependencies=[Depends(finance_write)])
async def action_steuerschluessel_speichern(
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MaskActionResult:
    """CE fuer finance/steuerschluessel:speichern. Der Schluessel (code) entscheidet: neu oder Aenderung."""
    code = str(body.get("code") or "").strip() or "neu"

    async def pruefe(pruef_db: Session, payload: dict[str, Any], _entity_id: str, tid: str) -> list[dict[str, Any]]:
        werte, fehler = _lies_eingabe(payload)
        if fehler:
            return fehler
        # Das Konto muss im Kontenplan stehen, bebuchbar sein und der Art nach in das Feld gehoeren.
        hindernisse = [(feld, konto_hindernis(pruef_db, tid, feld, werte[feld])) for feld, _name in _KONTEN if werte[feld]]
        return [_fehler(feld, meldung) for feld, meldung in hindernisse if meldung]

    async def schreibe(schreib_db: Session, payload: dict[str, Any], _entity_id: str, tid: str) -> str:
        werte, _fehlerliste = _lies_eingabe(payload)
        # Je Mandant gibt es einen Schluessel nur einmal (uq_tax_keys_tenant_code). Zwei gleichzeitige
        # Anlagen: Die zweite wartet und aendert dann, statt an der Eindeutigkeit zu scheitern.
        schreib_db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:schluessel))"), {"schluessel": f"tax_keys:{tid}:{werte['code']}"})
        vorhanden = _bestand(schreib_db, tid, werte["code"])
        satz_text = f"{_zeige(werte['steuersatz'])} %"
        if not vorhanden:
            schreib_db.execute(
                text(
                    "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, ustva_position, "
                    "ustva_bezeichnung, credit_account, debit_account, revenue_account, par_24_ustg, intracom, export, "
                    "reverse_charge, gueltig_von, gueltig_bis, notizen, active) "
                    "VALUES (:id, :tid, :code, :bezeichnung, :steuersatz, :ustva_position, :ustva_bezeichnung, "
                    ":credit_account, :debit_account, :revenue_account, :par_24_ustg, :intracom, :export, "
                    ":reverse_charge, :gueltig_von, :gueltig_bis, :notizen, :active)"
                ),
                {**werte, "id": uuid7(), "tid": tid},
            )
            return f"Steuerschlüssel {werte['code']} angelegt: {werte['bezeichnung']}, {satz_text}."
        alt = dict(zip(_SPALTEN, vorhanden[0][1:]))
        geaendert = [
            f"{_FELDTEXT[s]} {_zeige(alt[s])} → {_zeige(werte[s])}"
            for s in _SPALTEN
            if (alt[s] if alt[s] != "" else None) != werte[s]
        ]
        if not geaendert:
            return f"Steuerschlüssel {werte['code']} unverändert."
        schreib_db.execute(
            text(
                "UPDATE domain_erp.tax_keys SET bezeichnung = :bezeichnung, steuersatz = :steuersatz, "
                "ustva_position = :ustva_position, ustva_bezeichnung = :ustva_bezeichnung, "
                "credit_account = :credit_account, debit_account = :debit_account, revenue_account = :revenue_account, "
                "par_24_ustg = :par_24_ustg, intracom = :intracom, export = :export, reverse_charge = :reverse_charge, "
                "gueltig_von = :gueltig_von, gueltig_bis = :gueltig_bis, notizen = :notizen, active = :active, "
                "updated_at = NOW() WHERE id = :id AND tenant_id = :tid"
            ),
            {**werte, "id": vorhanden[0][0], "tid": tid},
        )
        return f"Steuerschlüssel {werte['code']} geändert: {'; '.join(geaendert)}."

    ergebnis = await run_delegated_mask_action(
        db, action_key="speichern", entity_type="tax_key", entity_id=code, tenant_id=tenant_id,
        body=body, check_fn=pruefe, delegate_fn=schreibe, outbox_event_type="finance.tax_key.saved",
    )
    if ergebnis.success and ergebnis.mode == "execute":
        invalidate_tenant_prefix("tax_keys", tenant_id)
    return ergebnis
