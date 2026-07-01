"""Mobile-Scan / Barcode-Dispatch API.

POST /scan/barcode — nimmt einen Barcode-String entgegen, ermittelt den Artikel
(EAN/GTIN oder interne Artikelnummer) und gibt Artikel-Info + aktuellen Lagerbestand zurück.
"""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/scan", tags=["scan", "mobile"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class BarcodeScanRequest(BaseModel):
    barcode: str = Field(..., description="Barcode-String (EAN-13, EAN-8, Code128, interne Nr.)")
    barcode_type: Optional[str] = Field(None, description="Typ: ean13|ean8|code128|qr|intern")
    warehouse_id: Optional[str] = Field(None, description="Kontext-Lager für Bestandsinfo")
    action: Optional[str] = Field(
        "info",
        description="Gewünschte Aktion: info|wareneingang|warenausgang|inventur",
    )


class ArtikelInfo(BaseModel):
    artikel_id: str
    artikel_nummer: str
    name: str
    einheit: Optional[str]
    ean: Optional[str]
    charge: Optional[str]
    lagerbestand: Optional[float]
    warehouse_id: Optional[str]
    letzter_einkaufspreis: Optional[float]
    verkaufspreis: Optional[float]


class BarcodeScanResponse(BaseModel):
    scan_id: str
    barcode: str
    barcode_type: Optional[str]
    action: str
    gefunden: bool
    artikel: Optional[ArtikelInfo]
    hinweis: Optional[str]


@router.post(
    "/barcode",
    response_model=BarcodeScanResponse,
    status_code=200,
    summary="Barcode scannen und Artikel identifizieren",
)
async def scan_barcode(
    payload: BarcodeScanRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> BarcodeScanResponse:
    """Barcode-Lookup: sucht Artikel per EAN, Artikelnummer oder internem Code.

    Rückgabe enthält Artikel-Stammdaten + aktuellen Bestand im angegebenen Lager.
    Falls der Artikel nicht gefunden wird, wird `gefunden=False` zurückgegeben
    (kein 404) — das ermöglicht Fremdware-Erkennung im Frontend.
    """
    t_id = tenant_id or DEFAULT_TENANT
    scan_id = str(uuid4())
    barcode = payload.barcode.strip()

    # Suche nach EAN, Artikelnummer oder Name
    artikel_row = db.execute(
        text("""
            SELECT
                id,
                article_number,
                name,
                base_unit,
                ean,
                purchase_price,
                sales_price
            FROM domain_inventory.articles
            WHERE tenant_id = :tenant_id
              AND is_active = TRUE
              AND (
                  ean = :barcode
                  OR article_number = :barcode
                  OR barcode = :barcode
              )
            LIMIT 1
        """),
        {"tenant_id": t_id, "barcode": barcode},
    ).mappings().first()

    if not artikel_row:
        return BarcodeScanResponse(
            scan_id=scan_id,
            barcode=barcode,
            barcode_type=payload.barcode_type,
            action=payload.action or "info",
            gefunden=False,
            artikel=None,
            hinweis=(
                f"Artikel mit Barcode '{barcode}' nicht im Stamm gefunden. "
                "Bitte prüfen ob Fremdware oder neuer Artikel angelegt werden soll."
            ),
        )

    # Bestand im angegebenen Lager ermitteln
    lagerbestand: Optional[float] = None
    if payload.warehouse_id:
        lagerbestand = db.execute(
            text("""
                SELECT COALESCE(SUM(quantity), 0)
                FROM domain_inventory.inventory_stock_movements
                WHERE tenant_id = :tenant_id
                  AND article_id = :article_id
                  AND warehouse_id = :warehouse_id
            """),
            {
                "tenant_id": t_id,
                "article_id": artikel_row["id"],
                "warehouse_id": payload.warehouse_id,
            },
        ).scalar()

    hinweis = None
    if lagerbestand is not None and lagerbestand <= 0 and payload.action in ("warenausgang",):
        hinweis = f"Achtung: Kein Bestand für Artikel {artikel_row['article_number']} in diesem Lager."

    return BarcodeScanResponse(
        scan_id=scan_id,
        barcode=barcode,
        barcode_type=payload.barcode_type,
        action=payload.action or "info",
        gefunden=True,
        artikel=ArtikelInfo(
            artikel_id=artikel_row["id"],
            artikel_nummer=artikel_row["article_number"],
            name=artikel_row["name"],
            einheit=artikel_row["base_unit"],
            ean=artikel_row["ean"],
            charge=None,
            lagerbestand=float(lagerbestand) if lagerbestand is not None else None,
            warehouse_id=payload.warehouse_id,
            letzter_einkaufspreis=float(artikel_row["purchase_price"]) if artikel_row["purchase_price"] else None,
            verkaufspreis=float(artikel_row["sales_price"]) if artikel_row["sales_price"] else None,
        ),
        hinweis=hinweis,
    )
