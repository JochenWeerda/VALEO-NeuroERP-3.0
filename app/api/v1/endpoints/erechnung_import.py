"""
E-Rechnung Import — ZUGFeRD / XRechnung stub.

POST /erechnung/import                         — upload & detect format
GET  /erechnung/imports                        — list past imports
POST /erechnung/imports/{import_id}/buchen     — book into journal (stub)
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/erechnung", tags=["erechnung"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ERechnungImportResult(BaseModel):
    import_id: str
    format: str            # ZUGFERD_2_1 / XRECHNUNG_3_0 / UNKNOWN
    status: str            # ERKANNT / VALIDIERT / IMPORTIERT / FEHLER
    rechnungsnummer: Optional[str] = None
    lieferant_name: Optional[str] = None
    betrag_netto: Optional[float] = None
    betrag_brutto: Optional[float] = None
    steuer_betrag: Optional[float] = None
    fehler_details: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_format(filename: str, content: bytes) -> str:
    text_content = content.decode("utf-8", errors="replace")
    if filename.lower().endswith(".xml"):
        if "CrossIndustryInvoice" in text_content:
            return "ZUGFERD_2_1"
        if "ubl:Invoice" in text_content:
            return "XRECHNUNG_3_0"
    return "UNKNOWN"


def _extract_first(pattern: str, text_content: str) -> Optional[str]:
    m = re.search(pattern, text_content)
    return m.group(1).strip() if m else None


def _parse_amount(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _parse_zugferd(content: str) -> dict:
    rechnungsnummer = _extract_first(r"<ram:ID>(.*?)</ram:ID>", content)
    lieferant_name = _extract_first(
        r"<ram:SellerTradeParty>.*?<ram:Name>(.*?)</ram:Name>", content
    )
    betrag_netto = _parse_amount(
        _extract_first(r"<ram:TaxBasisTotalAmount[^>]*>(.*?)</ram:TaxBasisTotalAmount>", content)
    )
    steuer_betrag = _parse_amount(
        _extract_first(r"<ram:TaxTotalAmount[^>]*>(.*?)</ram:TaxTotalAmount>", content)
    )
    betrag_brutto = _parse_amount(
        _extract_first(r"<ram:GrandTotalAmount[^>]*>(.*?)</ram:GrandTotalAmount>", content)
    )
    if betrag_netto is not None and steuer_betrag is not None and betrag_brutto is None:
        betrag_brutto = betrag_netto + steuer_betrag
    return dict(
        rechnungsnummer=rechnungsnummer,
        lieferant_name=lieferant_name,
        betrag_netto=betrag_netto,
        betrag_brutto=betrag_brutto,
        steuer_betrag=steuer_betrag,
    )


def _parse_xrechnung(content: str) -> dict:
    rechnungsnummer = _extract_first(r"<cbc:ID>(.*?)</cbc:ID>", content)
    lieferant_name = _extract_first(
        r"<cac:AccountingSupplierParty>.*?<cbc:Name>(.*?)</cbc:Name>", content
    )
    betrag_netto = _parse_amount(
        _extract_first(r"<cbc:TaxExclusiveAmount[^>]*>(.*?)</cbc:TaxExclusiveAmount>", content)
    )
    betrag_brutto = _parse_amount(
        _extract_first(r"<cbc:PayableAmount[^>]*>(.*?)</cbc:PayableAmount>", content)
    )
    steuer_betrag = _parse_amount(
        _extract_first(r"<cbc:TaxAmount[^>]*>(.*?)</cbc:TaxAmount>", content)
    )
    return dict(
        rechnungsnummer=rechnungsnummer,
        lieferant_name=lieferant_name,
        betrag_netto=betrag_netto,
        betrag_brutto=betrag_brutto,
        steuer_betrag=steuer_betrag,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/import", response_model=ERechnungImportResult, status_code=200, summary="Erechnung importieren")
async def import_erechnung(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    import_id = str(uuid4())
    try:
        content_bytes: bytes = await file.read()
        filename = file.filename or ""
        fmt = _detect_format(filename, content_bytes)
        text_content = content_bytes.decode("utf-8", errors="replace")

        extracted: dict = {}
        if fmt == "ZUGFERD_2_1":
            extracted = _parse_zugferd(text_content)
        elif fmt == "XRECHNUNG_3_0":
            extracted = _parse_xrechnung(text_content)

        # Persist import record (best-effort)
        try:
            db.execute(
                text(
                    "INSERT INTO domain_finance.erechnung_imports"
                    " (id, format, status, rechnungsnummer, lieferant_name,"
                    "  betrag_netto, betrag_brutto, steuer_betrag, tenant_id, created_at)"
                    " VALUES (:id, :format, 'ERKANNT', :rechnungsnummer, :lieferant_name,"
                    "  :betrag_netto, :betrag_brutto, :steuer_betrag, :tenant_id, :created_at)"
                ),
                {
                    "id": import_id,
                    "format": fmt,
                    "rechnungsnummer": extracted.get("rechnungsnummer"),
                    "lieferant_name": extracted.get("lieferant_name"),
                    "betrag_netto": extracted.get("betrag_netto"),
                    "betrag_brutto": extracted.get("betrag_brutto"),
                    "steuer_betrag": extracted.get("steuer_betrag"),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow(),
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            # migration_hint: domain_finance.erechnung_imports not yet migrated

        return ERechnungImportResult(
            import_id=import_id,
            format=fmt,
            status="ERKANNT",
            **extracted,
        )
    except Exception as exc:
        return ERechnungImportResult(
            import_id=import_id,
            format="UNKNOWN",
            status="FEHLER",
            fehler_details=str(exc),
        )


@router.get("/imports", response_model=List[ERechnungImportResult], summary="Imports auflisten")
def list_imports(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text(
                "SELECT id AS import_id, format, status, rechnungsnummer,"
                " lieferant_name, betrag_netto, betrag_brutto, steuer_betrag,"
                " NULL AS fehler_details"
                " FROM domain_finance.erechnung_imports"
                " WHERE tenant_id=:tenant_id ORDER BY created_at DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []  # migration_hint: domain_finance.erechnung_imports not yet migrated


@router.post("/imports/{import_id}/buchen", summary="Buchen",
    response_model=CompatFlexOut
)
def buchen(
    import_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    journal_entry_id = str(uuid4())
    try:
        db.execute(
            text(
                "UPDATE domain_finance.erechnung_imports"
                " SET status='IMPORTIERT', journal_entry_id=:journal_entry_id"
                " WHERE id=:import_id AND tenant_id=:tenant_id"
            ),
            {
                "import_id": import_id,
                "journal_entry_id": journal_entry_id,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
    return {"status": "gebucht", "journal_entry_id": journal_entry_id}
