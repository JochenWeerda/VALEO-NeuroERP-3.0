"""
Documents Router
API-Endpoints für Belegverwaltung & Folgebeleg-Erstellung
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Callable, Any, List, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import (
    CustomerInquiry, SalesOffer, SalesOrder, SalesDelivery, SalesInvoice, PaymentReceived,
    PurchaseRequest, PurchaseOffer, PurchaseOrder, FollowRequest
)
from .router_helpers import (
    _DB, get_repository, save_to_store, get_from_store, list_from_store, delete_from_store
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/documents", tags=["documents"])


def _enrich_delivery_sustainability(doc_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate and persist nutrient/CO2 totals for sales delivery documents."""
    total_n = 0.0
    total_p2o5 = 0.0
    total_co2e = 0.0

    lines = doc_data.get("lines", [])
    psm_line_count = 0
    missing_mandatory_fields: list[str] = []
    for line in lines:
        qty = float(line.get("qty") or 0.0)
        n_per_unit = float(line.get("nutrientNKgPerUnit") or 0.0)
        p2o5_per_unit = float(line.get("nutrientP2o5KgPerUnit") or 0.0)
        co2e_per_unit = float(line.get("co2eKgPerUnit") or 0.0)

        n_total = round(qty * n_per_unit, 3)
        p2o5_total = round(qty * p2o5_per_unit, 3)
        co2e_total = round(qty * co2e_per_unit, 3)

        line["nutrientNTotalKg"] = n_total
        line["nutrientP2o5TotalKg"] = p2o5_total
        line["co2eTotalKg"] = co2e_total

        is_psm_line = any(
            [
                bool(line.get("bvlZulassungsnummer")),
                bool(line.get("hazardHinweise")),
                bool(line.get("sdsReference")),
            ]
        )
        if is_psm_line:
            psm_line_count += 1
            if not line.get("bvlZulassungsnummer"):
                missing_mandatory_fields.append(f"{line.get('article', 'Position')}: fehlende BVL-Zulassungsnummer")
            if not line.get("sdsReference") and not line.get("hazardHinweise"):
                missing_mandatory_fields.append(f"{line.get('article', 'Position')}: fehlender SDB-/Gefahrhinweis")

        total_n += n_total
        total_p2o5 += p2o5_total
        total_co2e += co2e_total

    doc_data["totalNutrientNKg"] = round(total_n, 3)
    doc_data["totalNutrientP2o5Kg"] = round(total_p2o5, 3)
    doc_data["totalCo2eKg"] = round(total_co2e, 3)

    adr_punkte = float(doc_data.get("adrPunkte") or 0.0)
    sachkunde_status = str(doc_data.get("sachkundeStatus") or "offen")
    sds_mitgeliefert = str(doc_data.get("sdsMitgeliefert") or "offen")
    has_sachkunde_ok = sachkunde_status in ["geprueft", "nicht_erforderlich"]
    has_sds_ok = sds_mitgeliefert in ["ja", "nicht_erforderlich"]

    compliant = True
    if psm_line_count > 0:
        compliant = (
            len(missing_mandatory_fields) == 0
            and has_sachkunde_ok
            and has_sds_ok
            and adr_punkte <= 1000
            and bool(doc_data.get("supplierName"))
        )

    hinweise: list[str] = []
    if psm_line_count > 0 and sachkunde_status == "offen":
        hinweise.append(
            "Hinweis: Bitte einmalig eine Kopie des Sachkundenachweises Pflanzenschutz zeitnah zusenden."
        )
    if psm_line_count > 0 and sds_mitgeliefert == "offen":
        hinweise.append(
            "Hinweis: Sicherheitsdatenblatt (SDB) bei Erstlieferung bereitstellen bzw. nachreichen."
        )
    if psm_line_count > 0 and adr_punkte > 1000:
        hinweise.append("Hinweis: ADR-1000-Punkte-Regel prüfen (Transportkennzeichnung/Anforderungen).")

    doc_data["psmCompliance"] = {
        "psmLineCount": psm_line_count,
        "supplierName": doc_data.get("supplierName"),
        "sachkundeStatus": sachkunde_status,
        "sdsMitgeliefert": sds_mitgeliefert,
        "adrPunkte": adr_punkte,
        "adrWithin1000Rule": adr_punkte <= 1000,
        "missingMandatoryFields": missing_mandatory_fields,
        "hinweise": hinweise,
        "compliant": compliant,
        "recordRetentionYears": 5,
    }

    date_value = str(doc_data.get("date") or "")
    if len(date_value) >= 10:
        try:
            dt = datetime.fromisoformat(date_value[:10])
            doc_data["aufbewahrungBis"] = dt.replace(year=dt.year + 5).date().isoformat()
        except ValueError:
            pass
    return doc_data


def _compute_sales_delivery_sustainability(
    *,
    year: int,
    customer_id: Optional[str],
    db: Session,
) -> dict[str, Any]:
    repo = get_repository(db)
    listed = list_from_store("sales_delivery", skip=0, limit=10_000, repo=repo)
    deliveries = listed.get("data", [])

    filtered: list[dict[str, Any]] = []
    for delivery in deliveries:
        date_str = str(delivery.get("date") or "")
        if not date_str.startswith(f"{year}-"):
            continue
        if customer_id and str(delivery.get("customerId") or "") != customer_id:
            continue
        filtered.append(delivery)

    by_month: dict[str, dict[str, float]] = defaultdict(
        lambda: {"deliveries": 0.0, "n_kg": 0.0, "p2o5_kg": 0.0, "co2e_kg": 0.0}
    )
    total_n = 0.0
    total_p2o5 = 0.0
    total_co2e = 0.0

    for delivery in filtered:
        month = str(delivery.get("date", ""))[:7]
        d_n = float(delivery.get("totalNutrientNKg") or 0.0)
        d_p2o5 = float(delivery.get("totalNutrientP2o5Kg") or 0.0)
        d_co2e = float(delivery.get("totalCo2eKg") or 0.0)

        by_month[month]["deliveries"] += 1
        by_month[month]["n_kg"] += d_n
        by_month[month]["p2o5_kg"] += d_p2o5
        by_month[month]["co2e_kg"] += d_co2e

        total_n += d_n
        total_p2o5 += d_p2o5
        total_co2e += d_co2e

    return {
        "year": year,
        "customerId": customer_id,
        "deliveryCount": len(filtered),
        "totalNutrientNKg": round(total_n, 3),
        "totalNutrientP2o5Kg": round(total_p2o5, 3),
        "totalCo2eKg": round(total_co2e, 3),
        "byMonth": {
            k: {
                "deliveries": int(v["deliveries"]),
                "n_kg": round(v["n_kg"], 3),
                "p2o5_kg": round(v["p2o5_kg"], 3),
                "co2e_kg": round(v["co2e_kg"], 3),
            }
            for k, v in sorted(by_month.items())
        },
    }


# --- CRUD Endpoints ---


@router.post("/customer_inquiry")
async def upsert_customer_inquiry(doc: CustomerInquiry, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Kundenanfrage"""
    try:
        repo = get_repository(db)
        # Status-Transition-Logik
        existing = get_from_store("customer_inquiry", doc.number, repo)
        if existing:
            old_status = existing.get("status", "OFFEN")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "OFFEN": ["IN_BEARBEITUNG"],
                "IN_BEARBEITUNG": ["ANGEBOTEN", "ABGELEHNT"],
                "ANGEBOTEN": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("customer_inquiry", doc.number, doc.model_dump(), repo)
        logger.info(f"Saved customer inquiry: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save customer inquiry: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/sales_offer")
async def upsert_sales_offer(doc: SalesOffer, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Verkaufsangebot"""
    try:
        repo = get_repository(db)
        # Berechne Gesamtbeträge falls nicht gesetzt
        doc_data = doc.model_dump()
        if doc.subtotalNet == 0 and doc.lines:
            doc_data["subtotalNet"] = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc_data["totalTax"] = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price
            )
            doc_data["totalGross"] = doc_data["subtotalNet"] + doc_data["totalTax"]

        # Status-Transition-Logik
        existing = get_from_store("sales_offer", doc.number, repo)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["VERSENDET"],
                "VERSENDET": ["ANGENOMMEN", "ABGELEHNT"],
                "ANGENOMMEN": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("sales_offer", doc.number, doc_data, repo)
        logger.info(f"Saved sales offer: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save sales offer: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/sales_order")
async def upsert_sales_order(doc: SalesOrder, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Verkaufsauftrag"""
    try:
        repo = get_repository(db)
        return save_to_store("sales_order", doc.number, doc.model_dump(), repo)
    except Exception as e:
        logger.error(f"Failed to save sales order: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/sales_delivery")
async def upsert_sales_delivery(doc: SalesDelivery, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Lieferschein"""
    try:
        repo = get_repository(db)
        doc_data = _enrich_delivery_sustainability(doc.model_dump())
        save_to_store("sales_delivery", doc.number, doc_data, repo)
        logger.info(f"Saved sales delivery: {doc.number}")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales delivery: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/sales_invoice")
async def upsert_sales_invoice(doc: SalesInvoice, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Rechnung"""
    try:
        repo = get_repository(db)
        # Berechne Gesamtbeträge falls nicht gesetzt
        doc_data = doc.model_dump()
        if doc.subtotalNet == 0 and doc.lines:
            doc_data["subtotalNet"] = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc_data["totalTax"] = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price
            )
            doc_data["totalGross"] = doc_data["subtotalNet"] + doc_data["totalTax"]

        # Status-Transition-Logik
        existing = get_from_store("sales_invoice", doc.number, repo)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["VERSENDET"],
                "VERSENDET": ["BEZAHLT", "ÜBERFÄLLIG"],
                "BEZAHLT": [],  # Final status
                "ÜBERFÄLLIG": ["BEZAHLT"],  # Kann noch bezahlt werden
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("sales_invoice", doc.number, doc_data, repo)
        logger.info(f"Saved sales invoice: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save sales invoice: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/payment_received")
async def upsert_payment_received(doc: PaymentReceived, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Zahlungseingang"""
    try:
        repo = get_repository(db)
        # Status-Transition-Logik
        existing = get_from_store("payment_received", doc.number, repo)
        if existing:
            old_status = existing.get("status", "EINGEGANGEN")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "EINGEGANGEN": ["VERBUCHT"],
                "VERBUCHT": ["ABGEGLICHEN"],
                "ABGEGLICHEN": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("payment_received", doc.number, doc.model_dump(), repo)
        logger.info(f"Saved payment received: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save payment received: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


# --- Purchase Endpoints ---


@router.post("/purchase_request")
async def upsert_purchase_request(doc: PurchaseRequest, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Einkaufsanfrage"""
    try:
        repo = get_repository(db)
        # Status-Transition-Logik
        existing = get_from_store("purchase_request", doc.number, repo)
        if existing:
            old_status = existing.get("status", "OFFEN")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "OFFEN": ["IN_BEARBEITUNG"],
                "IN_BEARBEITUNG": ["BESTELLT", "ABGELEHNT"],
                "BESTELLT": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("purchase_request", doc.number, doc.model_dump(), repo)
        logger.info(f"Saved purchase request: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save purchase request: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/purchase_offer")
async def upsert_purchase_offer(doc: PurchaseOffer, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Einkaufsangebot"""
    try:
        repo = get_repository(db)
        # Berechne Gesamtbeträge falls nicht gesetzt
        doc_data = doc.model_dump()
        if doc.subtotalNet == 0 and doc.lines:
            doc_data["subtotalNet"] = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc_data["totalTax"] = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price and line.vatRate
            )
            doc_data["totalGross"] = doc_data["subtotalNet"] + doc_data["totalTax"]

        # Status-Transition-Logik
        existing = get_from_store("purchase_offer", doc.number, repo)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["EINGEGANGEN"],
                "EINGEGANGEN": ["ANGENOMMEN", "ABGELEHNT"],
                "ANGENOMMEN": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("purchase_offer", doc.number, doc_data, repo)
        logger.info(f"Saved purchase offer: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save purchase offer: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.post("/purchase_order")
async def upsert_purchase_order(doc: PurchaseOrder, db: Session = Depends(get_db)) -> dict:
    """Erstellt oder aktualisiert Kaufauftrag"""
    try:
        repo = get_repository(db)
        # Berechne Gesamtbeträge falls nicht gesetzt
        doc_data = doc.model_dump()
        if doc.subtotalNet == 0 and doc.lines:
            doc_data["subtotalNet"] = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc_data["totalTax"] = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price and line.vatRate
            )
            doc_data["totalGross"] = doc_data["subtotalNet"] + doc_data["totalTax"]

        # Status-Transition-Logik
        existing = get_from_store("purchase_order", doc.number, repo)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["FREIGEGEBEN"],
                "FREIGEGEBEN": ["TEILGELIEFERT", "VOLLGELIEFERT", "STORNIERT"],
                "TEILGELIEFERT": ["VOLLGELIEFERT", "STORNIERT"],
                "VOLLGELIEFERT": [],  # Final status
                "STORNIERT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        result = save_to_store("purchase_order", doc.number, doc_data, repo)
        logger.info(f"Saved purchase order: {doc.number} (status: {doc.status})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save purchase order: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


# --- GET Endpoints ---


@router.get("/{doc_type}")
async def list_documents(doc_type: str, skip: int = 0, limit: int = 100) -> dict:
    """Holt Liste aller Belege eines Typs"""
    try:
        # Filtere nach Dokumenttyp
        filtered_docs = []
        for key, value in _DB.items():
            # Prüfe ob Dokumentnummer dem Typ entspricht (z.B. "PO-" für purchase_order)
            type_prefixes = {
                "customer_inquiry": ["INQ-"],
                "sales_offer": ["SO-", "ANG-"],
                "sales_order": ["SO-"],
                "sales_delivery": ["DL-"],
                "sales_invoice": ["INV-"],
                "payment_received": ["PAY-"],
                "purchase_request": ["PR-"],
                "purchase_offer": ["POF-"],
                "purchase_order": ["PO-", "EK-"],
            }
            
            prefixes = type_prefixes.get(doc_type, [])
            if any(key.startswith(prefix) for prefix in prefixes) or doc_type in str(value.get("type", "")):
                filtered_docs.append(value)
        
        # Pagination
        total = len(filtered_docs)
        paginated_docs = filtered_docs[skip:skip + limit]
        
        return {
            "ok": True,
            "data": paginated_docs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/{doc_type}/{doc_number}")
async def get_document(doc_type: str, doc_number: str, db: Session = Depends(get_db)) -> dict:
    """Holt einzelnen Beleg nach Typ und Nummer"""
    try:
        repo = get_repository(db)
        doc = get_from_store(doc_type, doc_number, repo)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"ok": True, "data": doc}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.put("/{doc_type}/{doc_number}")
async def update_document(doc_type: str, doc_number: str, doc: dict, db: Session = Depends(get_db)) -> dict:
    """Aktualisiert einen Beleg"""
    try:
        repo = get_repository(db)
        existing = get_from_store(doc_type, doc_number, repo)
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Validiere Status-Transitionen falls Status geändert wird
        old_status = existing.get("status")
        new_status = doc.get("status")
        
        if old_status and new_status and old_status != new_status:
            # Status-Transition-Validierung (vereinfacht - könnte erweitert werden)
            # Die spezifische Validierung erfolgt in den POST-Endpoints
            pass
        
        # Aktualisiere Dokument
        updated_data = {**existing, **doc, "number": doc_number}
        result = save_to_store(doc_type, doc_number, updated_data, repo)
        logger.info(f"Updated document: {doc_number}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update document: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.delete("/{doc_type}/{doc_number}")
async def delete_document(doc_type: str, doc_number: str, db: Session = Depends(get_db)) -> dict:
    """Löscht einen Beleg"""
    try:
        repo = get_repository(db)
        doc = get_from_store(doc_type, doc_number, repo)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Prüfe ob Dokument gelöscht werden kann (z.B. nicht wenn bereits verarbeitet)
        status = doc.get("status", "")
        
        # Finale Status erlauben keine Löschung
        final_statuses = ["BEZAHLT", "VOLLGELIEFERT", "ABGEGLICHEN", "STORNIERT"]
        if status in final_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete document with final status: {status}"
            )
        
        deleted = delete_from_store(doc_type, doc_number, repo)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Deleted document: {doc_number}")
        return {"ok": True, "number": doc_number, "message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.delete("/{doc_type}")
async def bulk_delete_documents(doc_type: str, numbers: List[str] = Query(...)) -> dict:
    """Löscht mehrere Belege gleichzeitig"""
    try:
        deleted = []
        failed = []
        
        for doc_number in numbers:
            if doc_number not in _DB:
                failed.append({"number": doc_number, "error": "Not found"})
                continue
            
            doc = _DB[doc_number]
            status = doc.get("status", "")
            
            # Finale Status erlauben keine Löschung
            final_statuses = ["BEZAHLT", "VOLLGELIEFERT", "ABGEGLICHEN", "STORNIERT"]
            if status in final_statuses:
                failed.append({"number": doc_number, "error": f"Cannot delete with status: {status}"})
                continue
            
            del _DB[doc_number]
            deleted.append(doc_number)
        
        return {
            "ok": True,
            "deleted": deleted,
            "failed": failed,
            "total": len(numbers),
            "deleted_count": len(deleted),
            "failed_count": len(failed)
        }
    except Exception as e:
        logger.error(f"Failed to bulk delete documents: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


# --- Belegfluss-Engine ---

# Flow-Matrix: (from_type, to_type) → Transformation-Function
FLOW: Dict[tuple[str, str], Callable[[dict], dict]] = {
    # Inquiry → Offer
    ("customer_inquiry", "sales_offer"): lambda payload: {
        "number": payload["number"].replace("INQ", "SO"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "validUntil": payload.get("deadline"),  # Verwende Deadline als validUntil
        "deliveryDate": None,
        "deliveryAddress": "",
        "paymentTerms": "net30",
        "notes": f"Aus Anfrage {payload['number']}: {payload.get('notes', '')}",
        "lines": payload.get("lines", []),
        "subtotalNet": 0,
        "totalTax": 0,
        "totalGross": 0,
    },
    # Order → Delivery
    ("sales_order", "delivery"): lambda payload: {
        "number": payload["number"].replace("SO", "DL"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "deliveryAddress": payload.get("deliveryAddress", ""),
        "carrier": "dhl",
        "deliveryDate": payload.get("deliveryDate"),
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
    },
    # Offer → Order
    ("sales_offer", "sales_order"): lambda payload: {
        "number": payload["number"].replace("SO", "SO"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "salesOfferId": payload["number"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "deliveryDate": payload.get("deliveryDate"),
        "deliveryAddress": payload.get("deliveryAddress"),
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "notes": payload.get("notes", ""),
        "lines": payload.get("lines", []),
    },
    # Order → Invoice (direkt)
    ("sales_order", "invoice"): lambda payload: {
        "number": payload["number"].replace("SO", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "dueDate": (datetime.fromisoformat(payload["date"]) + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 0) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 0) / 100))
            for line in payload.get("lines", [])
        ),
    },
    # Delivery → Invoice
    ("sales_delivery", "invoice"): lambda payload: {
        "number": payload["number"].replace("DL", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload.get("sourceOrder"),
        "sourceDelivery": payload["number"],
        "paymentTerms": "net30",
        "dueDate": (datetime.fromisoformat(payload["date"]) + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "ENTWURF",
        "lines": [
            {**line, "price": 0, "vatRate": 19}
            for line in payload.get("lines", [])
        ],
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 19) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 19) / 100))
            for line in payload.get("lines", [])
        ),
    },
    # Purchase Flows
    # Purchase Request → Purchase Offer
    ("purchase_request", "purchase_offer"): lambda payload: {
        "number": payload["number"].replace("PR", "POF"),
        "date": payload["date"],
        "supplierId": payload.get("supplierId", ""),
        "purchaseRequestId": payload["number"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "validUntil": payload.get("deadline"),
        "deliveryDate": None,
        "deliveryAddress": "",
        "paymentTerms": "net30",
        "notes": f"Aus Anfrage {payload['number']}: {payload.get('notes', '')}",
        "lines": payload.get("lines", []),
        "subtotalNet": 0,
        "totalTax": 0,
        "totalGross": 0,
    },
    # Purchase Offer → Purchase Order
    ("purchase_offer", "purchase_order"): lambda payload: {
        "number": payload["number"].replace("POF", "PO"),
        "date": payload["date"],
        "supplierId": payload["supplierId"],
        "purchaseOfferId": payload["number"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "deliveryDate": payload.get("deliveryDate"),
        "deliveryAddress": payload.get("deliveryAddress", ""),
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "notes": payload.get("notes", ""),
        "lines": payload.get("lines", []),
        "subtotalNet": payload.get("subtotalNet", 0),
        "totalTax": payload.get("totalTax", 0),
        "totalGross": payload.get("totalGross", 0),
    },
    # Invoice → PaymentReceived
    ("sales_invoice", "payment_received"): lambda payload: {
        "number": payload["number"].replace("INV", "PAY"),
        "date": payload["date"],
        "salesInvoiceId": payload["number"],
        "amount": payload.get("totalGross", 0),
        "paymentMethod": "Überweisung",
        "bankReference": None,
        "status": "EINGEGANGEN",
        "notes": f"Zahlung für Rechnung {payload['number']}",
    },
}


@router.post("/follow")
async def create_follow_up(req: FollowRequest) -> dict:
    """
    Erstellt Folgebeleg aus Quell-Beleg

    Args:
        req: FollowRequest mit fromType, toType, payload

    Returns:
        Transformierter Folgebeleg
    """
    try:
        flow_key = (req.fromType, req.toType)
        transform_fn = FLOW.get(flow_key)

        if not transform_fn:
            logger.warning(f"Flow not defined: {flow_key}")
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "flow not defined"},
            )

        # Transformation durchführen
        out = transform_fn(req.payload)

        logger.info(
            f"Created follow-up: {req.fromType} → {req.toType} (number: {out.get('number')})"
        )

        return {"ok": True, **out}
    except Exception as e:
        logger.error(f"Failed to create follow-up: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


# --- Lookup-Endpoints (für Autocomplete) ---


@router.get("/customers/search")
async def search_customers(
    q: str = "",
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    """Sucht Kunden (Autocomplete) - Echte DB-Suche"""
    from app.infrastructure.models import BusinessPartner
    from sqlalchemy import or_
    
    if not q or len(q) < 2:
        return {"ok": True, "data": []}
    
    # Suche in name, city, partner_number
    query = db.query(BusinessPartner).filter(
        BusinessPartner.tenant_id == tenant_id,
        BusinessPartner.is_customer == True,
        or_(
            BusinessPartner.name.ilike(f"%{q}%"),
            BusinessPartner.city.ilike(f"%{q}%"),
            BusinessPartner.partner_number.ilike(f"%{q}%")
        )
    ).limit(20)
    
    results = [
        {
            "id": c.id,
            "label": f"{c.name} ({c.city or 'N/A'})" if c.city else c.name,
            "name": c.name,
            "partner_number": c.partner_number,
            "city": c.city,
        }
        for c in query.all()
    ]
    
    return {"ok": True, "data": results}


@router.get("/articles/search")
async def search_articles(
    q: str = "",
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    """Sucht Artikel (Autocomplete) - Echte DB-Suche"""
    from app.infrastructure.models import Article
    from sqlalchemy import or_
    
    if not q or len(q) < 2:
        return {"ok": True, "data": []}
    
    # Suche in name, item_number, ean
    query = db.query(Article).filter(
        Article.tenant_id == tenant_id,
        or_(
            Article.name.ilike(f"%{q}%"),
            Article.item_number.ilike(f"%{q}%"),
            Article.ean.ilike(f"%{q}%")
        )
    ).limit(20)
    
    results = [
        {
            "id": a.id,
            "label": f"{a.name} ({a.item_number})" if a.item_number else a.name,
            "name": a.name,
            "item_number": a.item_number,
            "ean": a.ean,
        }
        for a in query.all()
    ]
    
    return {"ok": True, "data": results}


# --- Due-Date Berechnung ---


@router.post("/due-date/calculate")
async def calculate_due_date(
    data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """Berechnet Fälligkeitsdatum (Due-Date) +30 Tage"""
    from datetime import datetime, timedelta
    
    base_date_str = data.get("base_date")  # YYYY-MM-DD
    tage = data.get("tage", 30)
    
    if base_date_str:
        base_date = datetime.strptime(base_date_str, "%Y-%m-%d").date()
    else:
        base_date = datetime.now().date()
    
    # Berechne Fälligkeitsdatum
    faelligkeitsdatum = base_date + timedelta(days=tage)
    
    return {
        "ok": True,
        "base_date": base_date.isoformat(),
        "tage": tage,
        "faelligkeitsdatum": faelligkeitsdatum.isoformat(),
    }


# --- Analytics Endpoints ---

@router.get("/analytics/sales-performance")
async def get_sales_performance_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Sales Performance Analytics
    - Total revenue
    - Number of orders
    - Average order value
    - Conversion rates
    """
    try:
        # Filter documents by date range if provided
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

        # Calculate metrics
        sales_orders = [d for d in docs if d.get("number", "").startswith("SO")]
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        customer_inquiries = [d for d in docs if d.get("number", "").startswith("INQ")]
        sales_offers = [d for d in docs if d.get("number", "").startswith("SO") and "validUntil" in d]

        total_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices if inv.get("status") == "BEZAHLT")
        total_orders = len(sales_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Conversion rates
        inquiry_to_offer_rate = len(sales_offers) / len(customer_inquiries) * 100 if customer_inquiries else 0
        offer_to_order_rate = len(sales_orders) / len(sales_offers) * 100 if sales_offers else 0
        order_to_invoice_rate = len(sales_invoices) / len(sales_orders) * 100 if sales_orders else 0

        return {
            "ok": True,
            "data": {
                "totalRevenue": total_revenue,
                "totalOrders": total_orders,
                "averageOrderValue": avg_order_value,
                "conversionRates": {
                    "inquiryToOffer": inquiry_to_offer_rate,
                    "offerToOrder": offer_to_order_rate,
                    "orderToInvoice": order_to_invoice_rate
                },
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get sales performance analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/customer-analytics")
async def get_customer_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Customer Analytics
    - Top customers by revenue
    - Customer acquisition trends
    - Customer retention metrics
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]

        # Group by customer
        customer_revenue = defaultdict(float)
        customer_orders = defaultdict(int)

        for inv in sales_invoices:
            customer_id = inv.get("customerId")
            if customer_id:
                customer_revenue[customer_id] += inv.get("totalGross", 0)
                customer_orders[customer_id] += 1

        # Top customers by revenue
        top_customers = sorted(
            [{"customerId": cid, "totalRevenue": rev, "orderCount": customer_orders[cid]}
             for cid, rev in customer_revenue.items()],
            key=lambda x: x["totalRevenue"],
            reverse=True
        )[:10]

        # Customer acquisition (new customers per month)
        customer_first_order = {}
        for inv in sales_invoices:
            cid = inv.get("customerId")
            date = inv.get("date")
            if cid and date:
                if cid not in customer_first_order or date < customer_first_order[cid]:
                    customer_first_order[cid] = date

        acquisition_trends = defaultdict(int)
        for date in customer_first_order.values():
            month = date[:7]  # YYYY-MM
            acquisition_trends[month] += 1

        return {
            "ok": True,
            "data": {
                "topCustomers": top_customers,
                "customerAcquisitionTrends": dict(acquisition_trends),
                "totalUniqueCustomers": len(customer_revenue),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get customer analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/product-analytics")
async def get_product_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Product Analytics
    - Top products by sales volume and revenue
    - Product performance trends
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]

        # Aggregate product data
        product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0.0, "orderCount": 0})

        for inv in sales_invoices:
            for line in inv.get("lines", []):
                article = line.get("article")
                qty = line.get("qty", 0)
                price = line.get("price", 0)

                if article:
                    product_sales[article]["quantity"] += qty
                    product_sales[article]["revenue"] += qty * price
                    product_sales[article]["orderCount"] += 1

        # Top products by revenue
        top_products_revenue = sorted(
            [{"article": art, **data} for art, data in product_sales.items()],
            key=lambda x: x["revenue"],
            reverse=True
        )[:10]

        # Top products by quantity
        top_products_quantity = sorted(
            [{"article": art, **data} for art, data in product_sales.items()],
            key=lambda x: x["quantity"],
            reverse=True
        )[:10]

        return {
            "ok": True,
            "data": {
                "topProductsByRevenue": top_products_revenue,
                "topProductsByQuantity": top_products_quantity,
                "totalUniqueProducts": len(product_sales),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get product analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/financial-analytics")
async def get_financial_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Financial Analytics
    - Revenue breakdown
    - Outstanding payments
    - Payment status overview
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        payments = [d for d in docs if d.get("number", "").startswith("PAY")]

        # Revenue breakdown
        total_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices)
        paid_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices if inv.get("status") == "BEZAHLT")
        outstanding_revenue = total_revenue - paid_revenue

        # Outstanding payments by age
        outstanding_invoices = [inv for inv in sales_invoices if inv.get("status") in ["VERSENDET", "ÜBERFÄLLIG"]]
        current_outstanding = 0
        overdue_30 = 0
        overdue_60 = 0
        overdue_90 = 0

        today = datetime.now().date()
        for inv in outstanding_invoices:
            due_date_str = inv.get("dueDate")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str).date()
                    days_overdue = (today - due_date).days
                    amount = inv.get("totalGross", 0)

                    if days_overdue <= 0:
                        current_outstanding += amount
                    elif days_overdue <= 30:
                        overdue_30 += amount
                    elif days_overdue <= 60:
                        overdue_60 += amount
                    else:
                        overdue_90 += amount
                except ValueError:
                    current_outstanding += inv.get("totalGross", 0)

        # Payment methods distribution
        payment_methods = defaultdict(float)
        for pay in payments:
            method = pay.get("paymentMethod", "Unknown")
            payment_methods[method] += pay.get("amount", 0)

        return {
            "ok": True,
            "data": {
                "revenue": {
                    "total": total_revenue,
                    "paid": paid_revenue,
                    "outstanding": outstanding_revenue
                },
                "outstandingPayments": {
                    "current": current_outstanding,
                    "overdue30Days": overdue_30,
                    "overdue60Days": overdue_60,
                    "overdue90Days": overdue_90
                },
                "paymentMethods": dict(payment_methods),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get financial analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/sales-delivery-sustainability")
async def get_sales_delivery_sustainability(
    year: int = Query(..., ge=2000, le=2100, description="Reporting year (YYYY)"),
    customer_id: Optional[str] = Query(None, description="Optional customer filter"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Aggregated sustainability figures from sales delivery notes.

    Returns totals for N, P2O5 and CO2e to support yearly nutrient and
    sustainability reporting requested by farms and downstream processors.
    """
    try:
        data = _compute_sales_delivery_sustainability(year=year, customer_id=customer_id, db=db)

        return {
            "ok": True,
            "data": data,
        }
    except Exception as e:
        logger.error(f"Failed to aggregate sales delivery sustainability analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/sales-delivery-sustainability/export.csv")
async def export_sales_delivery_sustainability_csv(
    year: int = Query(..., ge=2000, le=2100, description="Reporting year (YYYY)"),
    customer_id: Optional[str] = Query(None, description="Optional customer filter"),
    db: Session = Depends(get_db),
):
    """Export yearly delivery sustainability analytics as CSV."""
    try:
        data = _compute_sales_delivery_sustainability(year=year, customer_id=customer_id, db=db)

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")

        writer.writerow(["Jahr", data["year"]])
        writer.writerow(["Kunde", data["customerId"] or "alle"])
        writer.writerow(["Anzahl Lieferscheine", data["deliveryCount"]])
        writer.writerow(["Summe N (kg)", f"{float(data['totalNutrientNKg']):.3f}"])
        writer.writerow(["Summe P2O5 (kg)", f"{float(data['totalNutrientP2o5Kg']):.3f}"])
        writer.writerow(["Summe CO2e (kg)", f"{float(data['totalCo2eKg']):.3f}"])
        writer.writerow([])
        writer.writerow(["Monat", "Lieferscheine", "N (kg)", "P2O5 (kg)", "CO2e (kg)"])

        by_month = data.get("byMonth", {})
        for month, row in by_month.items():
            writer.writerow([
                month,
                int(row.get("deliveries", 0)),
                f"{float(row.get('n_kg', 0.0)):.3f}",
                f"{float(row.get('p2o5_kg', 0.0)):.3f}",
                f"{float(row.get('co2e_kg', 0.0)):.3f}",
            ])

        payload = io.BytesIO(buffer.getvalue().encode("utf-8-sig"))
        filename = f"sales-delivery-sustainability-{year}.csv"
        if customer_id:
            filename = f"sales-delivery-sustainability-{year}-{customer_id}.csv"

        return StreamingResponse(
            payload,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"Failed to export sales delivery sustainability CSV: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/sales-delivery-sustainability/export.pdf")
async def export_sales_delivery_sustainability_pdf(
    year: int = Query(..., ge=2000, le=2100, description="Reporting year (YYYY)"),
    customer_id: Optional[str] = Query(None, description="Optional customer filter"),
    db: Session = Depends(get_db),
):
    """Export yearly delivery sustainability analytics as PDF."""
    try:
        data = _compute_sales_delivery_sustainability(year=year, customer_id=customer_id, db=db)

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        _, height = A4

        y = height - 20 * mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20 * mm, y, "Jahresreport Lieferschein-Nachhaltigkeit")
        y -= 8 * mm

        c.setFont("Helvetica", 10)
        c.drawString(20 * mm, y, f"Jahr: {data['year']}")
        y -= 5 * mm
        c.drawString(20 * mm, y, f"Kunde: {data['customerId'] or 'alle'}")
        y -= 5 * mm
        c.drawString(20 * mm, y, f"Lieferscheine: {data['deliveryCount']}")
        y -= 7 * mm

        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "Summen")
        y -= 5 * mm

        c.setFont("Helvetica", 10)
        c.drawString(22 * mm, y, f"N gesamt: {float(data['totalNutrientNKg']):.3f} kg")
        y -= 5 * mm
        c.drawString(22 * mm, y, f"P2O5 gesamt: {float(data['totalNutrientP2o5Kg']):.3f} kg")
        y -= 5 * mm
        c.drawString(22 * mm, y, f"CO2e gesamt: {float(data['totalCo2eKg']):.3f} kg")
        y -= 8 * mm

        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "Monat")
        c.drawString(55 * mm, y, "Lieferscheine")
        c.drawString(90 * mm, y, "N (kg)")
        c.drawString(125 * mm, y, "P2O5 (kg)")
        c.drawString(160 * mm, y, "CO2e (kg)")
        y -= 4 * mm
        c.line(20 * mm, y, 190 * mm, y)
        y -= 5 * mm

        c.setFont("Helvetica", 9)
        for month, row in data.get("byMonth", {}).items():
            if y < 20 * mm:
                c.showPage()
                y = height - 20 * mm
                c.setFont("Helvetica-Bold", 10)
                c.drawString(20 * mm, y, "Monat")
                c.drawString(55 * mm, y, "Lieferscheine")
                c.drawString(90 * mm, y, "N (kg)")
                c.drawString(125 * mm, y, "P2O5 (kg)")
                c.drawString(160 * mm, y, "CO2e (kg)")
                y -= 6 * mm
                c.setFont("Helvetica", 9)

            c.drawString(20 * mm, y, str(month))
            c.drawRightString(82 * mm, y, str(int(row.get("deliveries", 0))))
            c.drawRightString(118 * mm, y, f"{float(row.get('n_kg', 0.0)):.3f}")
            c.drawRightString(153 * mm, y, f"{float(row.get('p2o5_kg', 0.0)):.3f}")
            c.drawRightString(188 * mm, y, f"{float(row.get('co2e_kg', 0.0)):.3f}")
            y -= 5 * mm

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        filename = f"sales-delivery-sustainability-{year}.pdf"
        if customer_id:
            filename = f"sales-delivery-sustainability-{year}-{customer_id}.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"Failed to export sales delivery sustainability PDF: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


@router.get("/analytics/trend-analytics")
async def get_trend_analytics(
    period: str = Query("monthly", description="Aggregation period: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Trend Analytics
    - Revenue trends over time
    - Order volume trends
    - Customer acquisition trends
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        sales_orders = [d for d in docs if d.get("number", "").startswith("SO")]
        customer_inquiries = [d for d in docs if d.get("number", "").startswith("INQ")]

        # Group by period
        def get_period_key(date_str: str) -> str:
            date = datetime.fromisoformat(date_str)
            if period == "daily":
                return date.strftime("%Y-%m-%d")
            elif period == "weekly":
                week_start = date - timedelta(days=date.weekday())
                return week_start.strftime("%Y-%W")
            else:  # monthly
                return date.strftime("%Y-%m")

        revenue_trends = defaultdict(float)
        order_trends = defaultdict(int)
        inquiry_trends = defaultdict(int)

        for inv in sales_invoices:
            date = inv.get("date")
            if date:
                key = get_period_key(date)
                revenue_trends[key] += inv.get("totalGross", 0)

        for order in sales_orders:
            date = order.get("date")
            if date:
                key = get_period_key(date)
                order_trends[key] += 1

        for inquiry in customer_inquiries:
            date = inquiry.get("date")
            if date:
                key = get_period_key(date)
                inquiry_trends[key] += 1

        # Sort trends by period
        sorted_revenue = dict(sorted(revenue_trends.items()))
        sorted_orders = dict(sorted(order_trends.items()))
        sorted_inquiries = dict(sorted(inquiry_trends.items()))

        return {
            "ok": True,
            "data": {
                "revenueTrends": sorted_revenue,
                "orderVolumeTrends": sorted_orders,
                "inquiryTrends": sorted_inquiries,
                "periodType": period,
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get trend analytics: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler bei Dokumentverarbeitung")


