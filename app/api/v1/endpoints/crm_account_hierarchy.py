"""CRM Account-Hierarchien — Parent/Child-Beziehungen zwischen Business-Partnern.

Verwendet sqlalchemy.text() (thin-router-Muster).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()


def _get_tenant_id(x_tenant_id: str = Header(..., alias="X-Tenant-ID")) -> str:
    return x_tenant_id


# ---------------------------------------------------------------------------
# Helper: load one account row (tenant-scoped)
# ---------------------------------------------------------------------------

def _load_account(db: Session, account_id: str, tenant_id: str) -> Optional[dict[str, Any]]:
    try:
        row = db.execute(
            text(
                """
                SELECT id, name_1, name_2, partner_number, parent_id, status
                FROM business_partners
                WHERE id = :aid AND tenant_id = :tid
                """
            ),
            {"aid": account_id, "tid": tenant_id},
        ).fetchone()
    except Exception:
        db.rollback()
        return None
    if not row:
        return None
    return {
        "id": str(row[0]),
        "name": row[1],
        "name_2": row[2],
        "partner_number": row[3],
        "parent_id": str(row[4]) if row[4] else None,
        "status": row[5],
    }


def _load_children(db: Session, account_id: str, tenant_id: str) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                """
                SELECT id, name_1, name_2, partner_number, parent_id, status
                FROM business_partners
                WHERE parent_id = :aid AND tenant_id = :tid
                """
            ),
            {"aid": account_id, "tid": tenant_id},
        ).fetchall()
    except Exception:
        db.rollback()
        return []
    return [
        {
            "id": str(r[0]),
            "name": r[1],
            "name_2": r[2],
            "partner_number": r[3],
            "parent_id": str(r[4]) if r[4] else None,
            "status": r[5],
            "children": [],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /{id}/hierarchy
# ---------------------------------------------------------------------------

@router.get("/{account_id}/hierarchy", response_model=CompatFlexOut, tags=["crm", "accounts"], summary="Account hierarchy abrufen")
async def get_account_hierarchy(
    account_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant_id),
):
    """Parent + alle Kinder rekursiv, max 3 Ebenen."""
    root = _load_account(db, account_id, tenant_id)
    if not root:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")

    # Resolve parent
    parent = None
    if root.get("parent_id"):
        parent = _load_account(db, root["parent_id"], tenant_id)
        if parent and parent.get("parent_id"):
            grandparent = _load_account(db, parent["parent_id"], tenant_id)
            parent["parent"] = grandparent

    # Resolve children (level 1)
    children_l1 = _load_children(db, account_id, tenant_id)
    for child in children_l1:
        # Level 2
        children_l2 = _load_children(db, child["id"], tenant_id)
        for child2 in children_l2:
            # Level 3
            child2["children"] = _load_children(db, child2["id"], tenant_id)
        child["children"] = children_l2

    return {
        "account": root,
        "parent": parent,
        "children": children_l1,
        "depth": 3,
    }


# ---------------------------------------------------------------------------
# POST /{id}/set-parent
# ---------------------------------------------------------------------------

@router.post("/{account_id}/set-parent", response_model=CompatFlexOut, tags=["crm", "accounts"], summary="Account parent setzen")
async def set_account_parent(
    account_id: str,
    parent_id: Optional[str] = Query(None, description="Parent-Account-ID (null = root)"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant_id),
):
    """Parent-ID setzen mit Zirkularitätsprüfung (max 10 Ebenen)."""
    account = _load_account(db, account_id, tenant_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")

    # Circular check: walk up from parent_id to ensure account_id is not an ancestor
    if parent_id:
        parent_check = _load_account(db, parent_id, tenant_id)
        if not parent_check:
            raise HTTPException(status_code=404, detail="Parent-Account nicht gefunden")

        # Walk up ancestor chain
        current_id = parent_id
        visited: set[str] = set()
        for _ in range(10):
            if current_id in visited:
                break
            if current_id == account_id:
                raise HTTPException(
                    status_code=422,
                    detail="Zirkularitätsfehler: Account ist bereits ein Vorfahre des angegebenen Parents.",
                )
            visited.add(current_id)
            current = _load_account(db, current_id, tenant_id)
            if not current or not current.get("parent_id"):
                break
            current_id = current["parent_id"]

    try:
        db.execute(
            text(
                """
                UPDATE business_partners
                SET parent_id = :pid, updated_at = NOW()
                WHERE id = :aid AND tenant_id = :tid
                """
            ),
            {"pid": parent_id, "aid": account_id, "tid": tenant_id},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Parent setzen fehlgeschlagen: {exc}") from exc

    return {
        "account_id": account_id,
        "parent_id": parent_id,
        "message": "Parent erfolgreich gesetzt",
    }


# ---------------------------------------------------------------------------
# GET /{id}/consolidated — konsolidierter Umsatz
# ---------------------------------------------------------------------------

@router.get("/{account_id}/consolidated", response_model=CompatFlexOut, tags=["crm", "accounts"], summary="Consolidated revenue abrufen")
async def get_consolidated_revenue(
    account_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant_id),
):
    """Konsolidierter Umsatz über alle Tochtergesellschaften (max 3 Ebenen)."""
    account = _load_account(db, account_id, tenant_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")

    # Collect all account IDs in hierarchy (BFS, max 3 levels)
    all_ids: list[str] = [account_id]
    queue = [account_id]
    for _ in range(3):
        next_queue: list[str] = []
        for aid in queue:
            children = _load_children(db, aid, tenant_id)
            for c in children:
                cid = c["id"]
                if cid not in all_ids:
                    all_ids.append(cid)
                    next_queue.append(cid)
        queue = next_queue
        if not queue:
            break

    # Query revenue for all collected IDs
    revenue_data: list[dict[str, Any]] = []
    total_revenue = 0.0
    total_orders = 0

    for aid in all_ids:
        try:
            row = db.execute(
                text(
                    """
                    SELECT
                        COUNT(*)::int AS order_count,
                        COALESCE(SUM(total_amount), 0) AS revenue
                    FROM sales_orders
                    WHERE customer_id = :cid
                      AND tenant_id = :tid
                      AND status NOT IN ('CANCELLED', 'DRAFT')
                    """
                ),
                {"cid": aid, "tid": tenant_id},
            ).fetchone()
            if row:
                rev = float(row[1])
                total_revenue += rev
                total_orders += row[0]
                acct = _load_account(db, aid, tenant_id)
                revenue_data.append({
                    "account_id": aid,
                    "account_name": acct["name"] if acct else aid,
                    "order_count": row[0],
                    "revenue": rev,
                })
        except Exception:
            db.rollback()

    return {
        "account_id": account_id,
        "account_name": account["name"],
        "consolidated_revenue": total_revenue,
        "consolidated_orders": total_orders,
        "subsidiaries_count": len(all_ids) - 1,
        "breakdown": revenue_data,
    }
