"""
Finance Journal Entry management endpoints
RESTful API for journal entry management with clean architecture.

Supports OData query parameters ($filter, $orderby, $top, $skip) on the
list endpoint for server-side filtering and sorting.
"""

from typing import Optional, List, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.fibu_audit import log_fibu_audit
from ....infrastructure.repositories import JournalEntryRepository
from ....infrastructure.models import JournalEntry as JournalEntryModel
from ....core.dependency_container import container
from ....middleware.odata_adapter import apply_odata
from ..schemas.finance import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntry, JournalEntryLine
)
from ..schemas.base import PaginatedResponse

router = APIRouter()

JOURNAL_ENTRY_ODATA_FIELDS = {
    "id", "entry_number", "entry_date", "posting_date",
    "description", "reference", "source", "status",
    "total_debit", "total_credit", "posted_at",
    "created_at", "updated_at",
}


def _serialize_value(v: Any) -> Any:
    """Make OData projected row values JSON-serializable."""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if hasattr(v, "__float__") and not isinstance(v, (bool, int)):
        return float(v)
    return v


@router.get("/new", response_model=dict)
async def get_new_journal_entry_template(tenant_id: str = Depends(get_tenant_id)):
    """Return default values for the manual booking form."""
    now = datetime.utcnow()
    return {
        "id": None,
        "tenant_id": tenant_id,
        "belegart": "BANK",
        "belegnummer": f"NEW-{now.strftime('%Y%m%d%H%M%S')}",
        "buchungsdatum": now.date().isoformat(),
        "periode": now.strftime("%Y-%m"),
        "buchungstext": "",
        "gesamtSoll": 0,
        "gesamtHaben": 0,
        "differenz": 0,
        "buchungszeilen": [],
        "status": "draft",
    }


@router.post("/", response_model=JournalEntry, status_code=201)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry.

    This endpoint allows creating a new journal entry with multiple lines.
    The entry must balance (total debit = total credit).
    """
    try:
        # Validate that the entry balances
        total_debit = sum(line.debit_amount for line in entry_data.lines)
        total_credit = sum(line.credit_amount for line in entry_data.lines)

        if abs(total_debit - total_credit) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Journal entry does not balance. Debit: {total_debit}, Credit: {total_credit}"
            )

        if not entry_data.reference or not entry_data.reference.strip():
            raise HTTPException(
                status_code=400,
                detail="Belegprinzip: Jede Buchung muss eine Belegreferenz haben (reference-Feld)"
            )

        # FIBU-GL-05: Check if period is open for bookings
        period = getattr(entry_data, "period", None)
        if period:
            from sqlalchemy import text
            period_check = db.execute(
                text("""
                    SELECT status FROM finance_accounting_periods
                    WHERE tenant_id = :tenant_id AND period = :period
                """),
                {"tenant_id": tenant_id, "period": period}
            ).fetchone()

            if period_check and period_check[0] != "OPEN":
                raise HTTPException(
                    status_code=403,
                    detail=f"Period {period} is {period_check[0]}. Bookings are blocked for closed periods."
                )

        entry_repo = container.resolve(JournalEntryRepository)

        # Create the entry data
        entry_dict = entry_data.model_dump()
        entry_dict["tenant_id"] = tenant_id
        entry_dict['total_debit'] = total_debit
        entry_dict['total_credit'] = total_credit

        entry = await entry_repo.create(entry_dict, tenant_id)
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", entry.id,
            {"document_number": getattr(entry, "document_number", None), "period": period},
            request=request,
        )
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create journal entry: {str(e)}")


@router.get("/", response_model=PaginatedResponse[JournalEntry])
async def list_journal_entries(
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    reference: Optional[str] = Query(None, description="Filter by reference (e.g. Importlauf run_id)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List journal entries with pagination and filtering.

    Supports OData query parameters ($filter, $orderby, $top, $skip)
    for server-side data shaping.
    """
    try:
        has_odata = any(k.startswith("$") for k in request.query_params.keys())

        if has_odata:
            count_q = db.query(JournalEntryModel).filter(
                JournalEntryModel.tenant_id == tenant_id
            )
            count_q, _ = apply_odata(
                count_q, JournalEntryModel, request.query_params,
                allowed_fields=JOURNAL_ENTRY_ODATA_FIELDS,
            )
            total = count_q.count()

            q = db.query(JournalEntryModel).filter(
                JournalEntryModel.tenant_id == tenant_id
            )
            q, meta = apply_odata(
                q, JournalEntryModel, request.query_params,
                allowed_fields=JOURNAL_ENTRY_ODATA_FIELDS,
            )
            if "odata_top" not in meta:
                q = q.limit(limit)
            if "odata_skip" not in meta:
                q = q.offset(skip)
            entries = q.all()

            if meta.get("odata_projected"):
                selected = meta["odata_select"]
                items_out = [
                    {k: _serialize_value(v) for k, v in zip(selected, row)}
                    for row in entries
                ]
                return JSONResponse(
                    content={
                        "items": items_out,
                        "total": total,
                        "page": (skip // limit) + 1,
                        "size": limit,
                        "pages": (total + limit - 1) // limit,
                        "has_next": (skip + limit) < total,
                        "has_prev": skip > 0,
                    }
                )
            items_out = [JournalEntry.model_validate(e) for e in entries]
            return PaginatedResponse[JournalEntry](
                items=items_out,
                total=total,
                page=(skip // limit) + 1,
                size=limit,
                pages=(total + limit - 1) // limit,
                has_next=(skip + limit) < total,
                has_prev=skip > 0,
            )

        entry_repo = container.resolve(JournalEntryRepository)

        q_base = db.query(JournalEntryModel).filter(
            JournalEntryModel.tenant_id == tenant_id
        )
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            q_base = q_base.filter(
                JournalEntryModel.entry_date >= start_dt,
                JournalEntryModel.entry_date <= end_dt,
            )
        if reference:
            q_base = q_base.filter(JournalEntryModel.reference == reference)
        if status:
            q_base = q_base.filter(JournalEntryModel.status == status)

        total = q_base.count()
        entries = q_base.order_by(JournalEntryModel.entry_date.desc()).offset(skip).limit(limit).all()

        return PaginatedResponse[JournalEntry](
            items=[JournalEntry.model_validate(entry) for entry in entries],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list journal entries: {str(e)}")


@router.get("/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(
    entry_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get journal entry by ID.

    Retrieve detailed information about a specific journal entry including all lines.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)
        entry = await entry_repo.get_by_id(entry_id, tenant_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve journal entry: {str(e)}")


@router.put("/{entry_id}", response_model=JournalEntry)
async def update_journal_entry(
    entry_id: str,
    entry_data: JournalEntryUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Update journal entry information.

    Modify journal entry details. Note: Only draft entries can be modified.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)

        # Check if entry is still in draft status
        existing_entry = await entry_repo.get_by_id(entry_id, tenant_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        if existing_entry.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft entries can be modified")

        entry = await entry_repo.update(entry_id, entry_data.model_dump(exclude_unset=True), tenant_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        log_fibu_audit(
            db, tenant_id, "update", "journal_entry", entry_id,
            {"updated_fields": list(entry_data.model_dump(exclude_unset=True).keys())},
            request=request,
        )
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update journal entry: {str(e)}")


@router.post("/{entry_id}/post", response_model=JournalEntry)
async def post_journal_entry(
    entry_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Post a journal entry.

    Change the status of a draft journal entry to posted.
    This will update account balances and make the entry permanent.
    """
    try:
        from app.core.blockchain_anchor_runtime import anchor_journal_entry_event

        entry_repo = container.resolve(JournalEntryRepository)
        success = await entry_repo.post_entry(entry_id, tenant_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to post journal entry")
        log_fibu_audit(
            db, tenant_id, "post", "journal_entry", entry_id,
            {"status": "posted"},
            request=request,
        )
        # Return the updated entry
        entry = await entry_repo.get_by_id(entry_id, tenant_id)
        anchor = anchor_journal_entry_event(
            db,
            tenant_id=tenant_id,
            entry_id=entry_id,
            action="post",
            payload={"status": "posted", "reference": getattr(entry, "reference", None)},
        )
        body = JournalEntry.model_validate(entry).model_dump(mode="json")
        body["blockchain_anchor"] = anchor.as_dict()
        return JSONResponse(content=body)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post journal entry: {str(e)}")


@router.post("/{entry_id}/reverse", response_model=None)
async def reverse_journal_entry(
    entry_id: str,
    request: Request,
    reason: str = Query(..., description="Reason for reversal"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a reversal entry.

    Create a new journal entry that reverses the original entry.
    """
    try:
        from app.core.blockchain_anchor_runtime import anchor_journal_entry_event

        entry_repo = container.resolve(JournalEntryRepository)
        reversal_entry = await entry_repo.reverse_entry(entry_id, reason, tenant_id)
        if not reversal_entry:
            raise HTTPException(status_code=400, detail="Failed to create reversal entry")
        log_fibu_audit(
            db, tenant_id, "reverse", "journal_entry", entry_id,
            {"reason": reason, "reversal_entry_id": reversal_entry.id},
            request=request,
        )
        anchor = anchor_journal_entry_event(
            db,
            tenant_id=tenant_id,
            entry_id=entry_id,
            action="reverse",
            payload={"reason": reason, "reversal_entry_id": reversal_entry.id},
        )
        return {
            "message": "Reversal entry created successfully",
            "original_entry_id": entry_id,
            "reversal_entry_id": reversal_entry.id,
            "blockchain_anchor": anchor.as_dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reverse journal entry: {str(e)}")


@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Delete journal entry.

    Only draft entries can be deleted.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)

        # Check if entry is still in draft status
        existing_entry = await entry_repo.get_by_id(entry_id, tenant_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        if existing_entry.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft entries can be deleted")

        success = await entry_repo.delete(entry_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        log_fibu_audit(db, tenant_id, "delete", "journal_entry", entry_id, {"status": "draft"}, request=request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete journal entry: {str(e)}")
