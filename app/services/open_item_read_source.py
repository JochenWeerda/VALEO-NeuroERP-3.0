"""Canonical open-item read source shared by the API and Studio detail summaries."""
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException


def _get_open_items_relation(db: Session) -> tuple[str, set[str]]:
    schema = str(db.execute(text("""SELECT n.nspname FROM pg_class c
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.oid=to_regclass('offene_posten')""")).scalar() or "public")
    rows = db.execute(text("""SELECT column_name FROM information_schema.columns
        WHERE table_name='offene_posten' AND table_schema=:table_schema"""),
        {"table_schema":schema}).fetchall()
    return f"{schema}.offene_posten", {str(row[0]) for row in rows}


def _expr(cols: set[str], primary: str, fallback: str | None = None, default_sql: str = "NULL") -> str:
    if primary in cols:
        return primary
    if fallback and fallback in cols:
        return fallback
    return default_sql


def read_settlements(db: Session, op_id: str, tenant_id: str) -> list[dict]:
    if not tenant_id:
        raise HTTPException(403, "Verifizierter Mandant fehlt")
    relation, _ = _get_open_items_relation(db)
    parent = db.execute(text(f"SELECT id FROM {relation} WHERE tenant_id=:tenant AND id=:id"),
                        {"tenant":tenant_id,"id":op_id}).mappings().first()
    if not parent:
        raise HTTPException(404,"Open item not found")
    rows = db.execute(text("""SELECT j.id,j.entry_number,j.entry_date,j.description,
        j.total_debit,j.created_at,j.currency AS waehrung FROM domain_erp.journal_entries j
        WHERE j.source='op_settlement' AND j.tenant_id=:tenant
        AND EXISTS (SELECT 1 FROM domain_shared.audit_logs a
            WHERE a.tenant_id=j.tenant_id AND a.entity_id=j.id
            AND a.entity_type='journal_entry' AND a.action='create'
            AND a.changes->>'source'='op_settlement' AND a.changes->>'op_id'=:op_id)
        ORDER BY j.entry_date DESC,j.created_at DESC,j.id ASC"""),
        {"tenant":tenant_id,"op_id":op_id}).mappings().all()
    return [{"id":str(row["id"]),"payment_amount":float(row["total_debit"] or 0),
             "payment_date":row["entry_date"].isoformat() if row["entry_date"] else None,
             "payment_reference":row["entry_number"],"payment_type":"payment","notes":row["description"],
             "created_at":row["created_at"].isoformat() if row["created_at"] else None,
             "waehrung":row["waehrung"]} for row in rows]
