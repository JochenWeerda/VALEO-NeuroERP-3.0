"""
Credit Memos and Debit Memos API
PROC-PAY-02: Lieferantengutschriften / Belastungen
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
import logging
import uuid

from app.core.database import get_db
from app.documents.router_helpers import get_repository, save_to_store, get_from_store, list_from_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/einkauf", tags=["procurement", "ap", "memos"])


# Pydantic Models
class MemoItem(BaseModel):
    """Memo Position"""
    productId: Optional[str] = None
    productName: str
    quantity: float
    unit: str = "Stk"
    unitPrice: float
    netAmount: float
    taxRate: float = 19.0
    taxAmount: float
    grossAmount: float
    reason: Optional[str] = None


class CreditMemoCreate(BaseModel):
    """Request-Modell für Credit Memo Erstellung"""
    supplierId: str = Field(..., description="Lieferanten-ID")
    invoiceId: Optional[str] = Field(None, description="Referenz-Rechnung (optional)")
    memoDate: str = Field(..., description="Gutschriftsdatum (YYYY-MM-DD)")
    reason: str = Field(..., min_length=10, description="Grund für Gutschrift (min. 10 Zeichen)")
    notes: Optional[str] = None
    items: List[MemoItem] = Field(..., min_items=1, description="Gutschrifts-Positionen")


class DebitMemoCreate(BaseModel):
    """Request-Modell für Debit Memo Erstellung"""
    supplierId: str = Field(..., description="Lieferanten-ID")
    invoiceId: Optional[str] = Field(None, description="Referenz-Rechnung (optional)")
    memoDate: str = Field(..., description="Belastungsdatum (YYYY-MM-DD)")
    reason: str = Field(..., min_length=10, description="Grund für Belastung (min. 10 Zeichen)")
    notes: Optional[str] = None
    items: List[MemoItem] = Field(..., min_items=1, description="Belastungs-Positionen")


class SettlementRequest(BaseModel):
    """Request-Modell für Verrechnung"""
    invoiceIds: List[str] = Field(..., min_items=1, description="Rechnungs-IDs zur Verrechnung")


class CreditMemoResponse(BaseModel):
    """Response-Modell für Credit Memo"""
    id: str
    number: str
    supplierId: str
    supplierName: str
    invoiceId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    memoDate: str
    netAmount: float
    taxAmount: float
    grossAmount: float
    status: str
    reason: str
    notes: Optional[str] = None
    settled: bool = False
    settledInvoiceIds: Optional[List[str]] = None


class DebitMemoResponse(BaseModel):
    """Response-Modell für Debit Memo"""
    id: str
    number: str
    supplierId: str
    supplierName: str
    invoiceId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    memoDate: str
    netAmount: float
    taxAmount: float
    grossAmount: float
    status: str
    reason: str
    notes: Optional[str] = None
    settled: bool = False
    settledInvoiceIds: Optional[List[str]] = None


def calculate_memo_totals(items: List[MemoItem]) -> tuple[float, float, float]:
    """Berechnet Netto-, Steuer- und Bruttobetrag aus Positionen."""
    net_amount = sum(item.netAmount for item in items)
    tax_amount = sum(item.taxAmount for item in items)
    gross_amount = sum(item.grossAmount for item in items)
    return round(net_amount, 2), round(tax_amount, 2), round(gross_amount, 2)


def get_supplier_name(supplier_id: str, db: Session) -> str:
    """Holt Lieferantennamen aus der Datenbank."""
    try:
        repo = get_repository(db)
        supplier = get_from_store("partner", supplier_id, repo)
        if supplier:
            return supplier.get("name", supplier_id)
    except Exception as e:
        logger.warning(f"Could not fetch supplier name for {supplier_id}: {e}")
    return supplier_id


def get_invoice_number(invoice_id: str, db: Session) -> Optional[str]:
    """Holt Rechnungsnummer aus der Datenbank."""
    try:
        repo = get_repository(db)
        invoice = get_from_store("ap_invoice", invoice_id, repo)
        if invoice:
            return invoice.get("number", invoice_id)
    except Exception as e:
        logger.warning(f"Could not fetch invoice number for {invoice_id}: {e}")
    return None


@router.post("/credit-memos", response_model=CreditMemoResponse)
async def create_credit_memo(
    memo: CreditMemoCreate,
    db: Session = Depends(get_db)
) -> CreditMemoResponse:
    """Erstellt eine neue Gutschrift (Credit Memo)."""
    logger.info(f"Creating credit memo for supplier {memo.supplierId}")
    try:
        repo = get_repository(db)
        
        # Berechne Summen
        net_amount, tax_amount, gross_amount = calculate_memo_totals(memo.items)
        
        # Generiere ID und Nummer
        memo_id = str(uuid.uuid4())
        memo_number = f"CM-{datetime.now().strftime('%Y')}-{memo_id[:8].upper()}"
        
        # Hole Lieferantennamen
        supplier_name = get_supplier_name(memo.supplierId, db)
        
        # Hole Rechnungsnummer falls vorhanden
        invoice_number = None
        if memo.invoiceId:
            invoice_number = get_invoice_number(memo.invoiceId, db)
        
        # Erstelle Credit Memo Objekt
        credit_memo = {
            "id": memo_id,
            "number": memo_number,
            "supplierId": memo.supplierId,
            "supplierName": supplier_name,
            "invoiceId": memo.invoiceId,
            "invoiceNumber": invoice_number,
            "memoDate": memo.memoDate,
            "netAmount": net_amount,
            "taxAmount": tax_amount,
            "grossAmount": gross_amount,
            "status": "OPEN",
            "reason": memo.reason,
            "notes": memo.notes,
            "items": [item.model_dump() for item in memo.items],
            "settled": False,
            "settledInvoiceIds": [],
            "createdAt": datetime.now().isoformat(),
            "createdBy": "system",  # TODO: Get from auth context
        }
        
        # Speichere in Store
        save_to_store("credit_memo", memo_id, credit_memo, repo)
        
        return CreditMemoResponse(**credit_memo)
        
    except Exception as e:
        logger.error(f"Error creating credit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create credit memo: {str(e)}")


@router.post("/debit-memos", response_model=DebitMemoResponse)
async def create_debit_memo(
    memo: DebitMemoCreate,
    db: Session = Depends(get_db)
) -> DebitMemoResponse:
    """Erstellt eine neue Belastung (Debit Memo)."""
    logger.info(f"Creating debit memo for supplier {memo.supplierId}")
    try:
        repo = get_repository(db)
        
        # Berechne Summen
        net_amount, tax_amount, gross_amount = calculate_memo_totals(memo.items)
        
        # Generiere ID und Nummer
        memo_id = str(uuid.uuid4())
        memo_number = f"DM-{datetime.now().strftime('%Y')}-{memo_id[:8].upper()}"
        
        # Hole Lieferantennamen
        supplier_name = get_supplier_name(memo.supplierId, db)
        
        # Hole Rechnungsnummer falls vorhanden
        invoice_number = None
        if memo.invoiceId:
            invoice_number = get_invoice_number(memo.invoiceId, db)
        
        # Erstelle Debit Memo Objekt
        debit_memo = {
            "id": memo_id,
            "number": memo_number,
            "supplierId": memo.supplierId,
            "supplierName": supplier_name,
            "invoiceId": memo.invoiceId,
            "invoiceNumber": invoice_number,
            "memoDate": memo.memoDate,
            "netAmount": net_amount,
            "taxAmount": tax_amount,
            "grossAmount": gross_amount,
            "status": "OPEN",
            "reason": memo.reason,
            "notes": memo.notes,
            "items": [item.model_dump() for item in memo.items],
            "settled": False,
            "settledInvoiceIds": [],
            "createdAt": datetime.now().isoformat(),
            "createdBy": "system",  # TODO: Get from auth context
        }
        
        # Speichere in Store
        save_to_store("debit_memo", memo_id, debit_memo, repo)
        
        return DebitMemoResponse(**debit_memo)
        
    except Exception as e:
        logger.error(f"Error creating debit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create debit memo: {str(e)}")


@router.get("/credit-memos", response_model=List[CreditMemoResponse])
async def list_credit_memos(
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[str] = None,
    settled: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[CreditMemoResponse]:
    """Listet alle Gutschriften auf."""
    logger.info(f"Listing credit memos with skip={skip}, limit={limit}, supplier_id={supplier_id}, settled={settled}")
    try:
        repo = get_repository(db)
        all_memos = list_from_store("credit_memo", repo)
        
        # Filter
        filtered_memos = []
        for memo in all_memos:
            if supplier_id and memo.get("supplierId") != supplier_id:
                continue
            if settled is not None and memo.get("settled") != settled:
                continue
            filtered_memos.append(memo)
        
        # Sortiere nach Datum (neueste zuerst)
        filtered_memos.sort(key=lambda x: x.get("memoDate", ""), reverse=True)
        
        # Pagination
        paginated_memos = filtered_memos[skip:skip + limit]
        
        return [CreditMemoResponse(**memo) for memo in paginated_memos]
        
    except Exception as e:
        logger.error(f"Error listing credit memos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list credit memos: {str(e)}")


@router.get("/debit-memos", response_model=List[DebitMemoResponse])
async def list_debit_memos(
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[str] = None,
    settled: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[DebitMemoResponse]:
    """Listet alle Belastungen auf."""
    logger.info(f"Listing debit memos with skip={skip}, limit={limit}, supplier_id={supplier_id}, settled={settled}")
    try:
        repo = get_repository(db)
        all_memos = list_from_store("debit_memo", repo)
        
        # Filter
        filtered_memos = []
        for memo in all_memos:
            if supplier_id and memo.get("supplierId") != supplier_id:
                continue
            if settled is not None and memo.get("settled") != settled:
                continue
            filtered_memos.append(memo)
        
        # Sortiere nach Datum (neueste zuerst)
        filtered_memos.sort(key=lambda x: x.get("memoDate", ""), reverse=True)
        
        # Pagination
        paginated_memos = filtered_memos[skip:skip + limit]
        
        return [DebitMemoResponse(**memo) for memo in paginated_memos]
        
    except Exception as e:
        logger.error(f"Error listing debit memos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list debit memos: {str(e)}")


@router.get("/credit-memos/{memo_id}", response_model=CreditMemoResponse)
async def get_credit_memo(
    memo_id: str,
    db: Session = Depends(get_db)
) -> CreditMemoResponse:
    """Ruft eine Gutschrift anhand ihrer ID ab."""
    logger.info(f"Fetching credit memo: {memo_id}")
    try:
        repo = get_repository(db)
        memo = get_from_store("credit_memo", memo_id, repo)
        if not memo:
            raise HTTPException(status_code=404, detail="Credit memo not found")
        return CreditMemoResponse(**memo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching credit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch credit memo: {str(e)}")


@router.get("/debit-memos/{memo_id}", response_model=DebitMemoResponse)
async def get_debit_memo(
    memo_id: str,
    db: Session = Depends(get_db)
) -> DebitMemoResponse:
    """Ruft eine Belastung anhand ihrer ID ab."""
    logger.info(f"Fetching debit memo: {memo_id}")
    try:
        repo = get_repository(db)
        memo = get_from_store("debit_memo", memo_id, repo)
        if not memo:
            raise HTTPException(status_code=404, detail="Debit memo not found")
        return DebitMemoResponse(**memo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching debit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch debit memo: {str(e)}")


@router.post("/credit-memos/{memo_id}/settle")
async def settle_credit_memo(
    memo_id: str,
    settlement: SettlementRequest,
    db: Session = Depends(get_db)
) -> dict:
    """Verrechnet eine Gutschrift mit offenen Rechnungen."""
    logger.info(f"Settling credit memo {memo_id} with invoices {settlement.invoiceIds}")
    try:
        repo = get_repository(db)
        
        # Hole Credit Memo
        memo = get_from_store("credit_memo", memo_id, repo)
        if not memo:
            raise HTTPException(status_code=404, detail="Credit memo not found")
        
        if memo.get("settled"):
            raise HTTPException(status_code=400, detail="Credit memo already settled")
        
        # Validiere Rechnungen
        for invoice_id in settlement.invoiceIds:
            invoice = get_from_store("ap_invoice", invoice_id, repo)
            if not invoice:
                raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
            if invoice.get("supplierId") != memo.get("supplierId"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invoice {invoice_id} belongs to different supplier"
                )
        
        # Aktualisiere Credit Memo
        memo["settled"] = True
        memo["settledInvoiceIds"] = settlement.invoiceIds
        memo["status"] = "SETTLED"
        memo["settledAt"] = datetime.now().isoformat()
        
        save_to_store("credit_memo", memo_id, memo, repo)
        
        # TODO: Aktualisiere offene Beträge der Rechnungen
        # Dies würde normalerweise über die Open Items API erfolgen
        
        return {
            "status": "ok",
            "message": f"Credit memo {memo_id} settled with {len(settlement.invoiceIds)} invoices",
            "memoId": memo_id,
            "invoiceIds": settlement.invoiceIds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error settling credit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to settle credit memo: {str(e)}")


@router.post("/debit-memos/{memo_id}/settle")
async def settle_debit_memo(
    memo_id: str,
    settlement: SettlementRequest,
    db: Session = Depends(get_db)
) -> dict:
    """Verrechnet eine Belastung mit offenen Rechnungen."""
    logger.info(f"Settling debit memo {memo_id} with invoices {settlement.invoiceIds}")
    try:
        repo = get_repository(db)
        
        # Hole Debit Memo
        memo = get_from_store("debit_memo", memo_id, repo)
        if not memo:
            raise HTTPException(status_code=404, detail="Debit memo not found")
        
        if memo.get("settled"):
            raise HTTPException(status_code=400, detail="Debit memo already settled")
        
        # Validiere Rechnungen
        for invoice_id in settlement.invoiceIds:
            invoice = get_from_store("ap_invoice", invoice_id, repo)
            if not invoice:
                raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
            if invoice.get("supplierId") != memo.get("supplierId"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invoice {invoice_id} belongs to different supplier"
                )
        
        # Aktualisiere Debit Memo
        memo["settled"] = True
        memo["settledInvoiceIds"] = settlement.invoiceIds
        memo["status"] = "SETTLED"
        memo["settledAt"] = datetime.now().isoformat()
        
        save_to_store("debit_memo", memo_id, memo, repo)
        
        # TODO: Aktualisiere offene Beträge der Rechnungen
        # Dies würde normalerweise über die Open Items API erfolgen
        
        return {
            "status": "ok",
            "message": f"Debit memo {memo_id} settled with {len(settlement.invoiceIds)} invoices",
            "memoId": memo_id,
            "invoiceIds": settlement.invoiceIds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error settling debit memo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to settle debit memo: {str(e)}")

