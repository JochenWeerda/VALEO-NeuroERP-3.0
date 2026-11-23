"""
Dunning System API
FIBU-AR-04: Mahnwesen vervollständigen

Der Mandant kommt aus dem Kontext. Bis 08.10.2026 nahmen sechs Wege ihn aus
``Query("system")`` und Mahnlauf/Verarbeitung aus dem Request-Rumpf (Vorgabe
``"system"``): ohne Parameter mahnte jeder Mandant im selben Topf, mit Parameter
in jedem beliebigen.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging
from app.core.uuid7 import uuid7

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.gobd_artifact import register_artifact, sha256_hex
from app.auth.deps import get_current_user
from app.auth.finance_roles import finance_read, finance_write
from app.core.exceptions import DomainError
from app.services.finance_dunning_service import FinanceDunningService

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/dunning", tags=["finance", "dunning"])

MONEY_QUANT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT)

# Spalten einer Mahnung in der Reihenfolge von ``_notice_response``.
_NOTICE_COLUMNS = ("id, op_id, debtor_id, dunning_level, dunning_date, due_date, open_amount, dunning_fee, interest, "
                   "total_amount, payment_deadline, status, sent_date, payment_date, notes, created_at, updated_at")


def _notice_response(row) -> "DunningResponse":
    return DunningResponse(
        id=str(row[0]), op_id=str(row[1]), debtor_id=str(row[2] or ""), dunning_level=int(row[3]),
        dunning_date=row[4], due_date=row[5], open_amount=Decimal(str(row[6] or 0)),
        dunning_fee=Decimal(str(row[7] or 0)), interest=Decimal(str(row[8] or 0)),
        total_amount=Decimal(str(row[9] or 0)), payment_deadline=row[10], status=str(row[11] or ""),
        sent_date=row[12], payment_date=row[13], notes=str(row[14]) if row[14] else None,
        created_at=row[15], updated_at=row[16] or row[15],
    )



class DunningRule(BaseModel):
    """Dunning rule configuration"""
    level: int = Field(..., ge=1, le=3, description="Dunning level (1-3)")
    days_overdue_min: int = Field(..., ge=0, description="Minimum days overdue for this level")
    days_overdue_max: Optional[int] = Field(None, ge=0, description="Maximum days overdue for this level")
    fee_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Fixed dunning fee")
    fee_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Percentage fee of open amount")
    interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0, description="Interest rate per year (e.g., 9.0 for 9%)")
    payment_deadline_days: int = Field(default=14, ge=1, description="Payment deadline in days")
    block_customer: bool = Field(default=False, description="Block customer at this level")
    escalate_to_collection: bool = Field(default=False, description="Escalate to collection agency")
    description_template: str = Field(..., description="Dunning letter text template")


class DunningRuleCreate(BaseModel):
    """Schema for creating a dunning rule"""
    level: int = Field(..., ge=1, le=3)
    days_overdue_min: int = Field(..., ge=0)
    days_overdue_max: Optional[int] = Field(None, ge=0)
    fee_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    fee_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    payment_deadline_days: int = Field(default=14, ge=1)
    block_customer: bool = Field(default=False)
    escalate_to_collection: bool = Field(default=False)
    description_template: str
    active: bool = Field(default=True)


class DunningRuleResponse(BaseModel):
    """Response schema for dunning rule"""
    id: str
    level: int
    days_overdue_min: int
    days_overdue_max: Optional[int]
    fee_amount: Decimal
    fee_percentage: Decimal
    interest_rate: Decimal
    payment_deadline_days: int
    block_customer: bool
    escalate_to_collection: bool
    description_template: str
    active: bool
    created_at: datetime
    updated_at: datetime


class DunningCreate(BaseModel):
    """Schema for creating a dunning notice"""
    op_id: str = Field(..., description="Open item ID")
    debtor_id: str = Field(..., description="Debtor ID")
    dunning_level: int = Field(..., ge=1, le=3)
    dunning_date: date
    due_date: date
    open_amount: Decimal = Field(..., ge=0)
    custom_fee: Optional[Decimal] = Field(None, ge=0, description="Override calculated fee")
    custom_interest: Optional[Decimal] = Field(None, ge=0, description="Override calculated interest")
    notes: Optional[str] = None


class DunningResponse(BaseModel):
    """Response schema for dunning notice"""
    id: str
    op_id: str
    debtor_id: str
    dunning_level: int
    dunning_date: date
    due_date: Optional[date]  # in der Tabelle nullbar; eine Bestandszeile darf Liste und Versand nicht kippen
    open_amount: Decimal
    dunning_fee: Decimal
    interest: Decimal
    total_amount: Decimal
    payment_deadline: Optional[date]
    status: str
    sent_date: Optional[date]
    payment_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProcessDunningRequest(BaseModel):
    """Request to process dunning for overdue items"""
    debtor_id: Optional[str] = Field(None, description="Process for specific debtor")
    op_ids: Optional[List[str]] = Field(None, description="Process for specific open items")
    auto_apply_rules: bool = Field(default=True, description="Automatically apply dunning rules")
    as_of_date: Optional[date] = Field(None, description="Stichtag für Überfälligkeit (default: heute)")


class DunningRunRequest(BaseModel):
    """Request to start a dunning run (all overdue items as of date)"""
    as_of_date: date = Field(..., description="Stichtag (YYYY-MM-DD)")


class DunningRunResponse(BaseModel):
    """Response after starting a dunning run"""
    run_id: str
    notices_created: int


@router.get("/rules", response_model=List[DunningRuleResponse], summary="Dunning rules auflisten",
            dependencies=[Depends(finance_read)])
async def list_dunning_rules(
    active_only: bool = Query(True, description="Show only active rules"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    List all dunning rules.
    """
    try:
        query = text("""
            SELECT id, level, days_overdue_min, days_overdue_max, fee_amount, fee_percentage,
                   interest_rate, payment_deadline_days, block_customer, escalate_to_collection,
                   description_template, active, created_at, updated_at
            FROM domain_erp.dunning_rules
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if active_only:
            query = text(str(query) + " AND active = true")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        query = text(str(query) + " ORDER BY level")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            result.append(DunningRuleResponse(
                id=str(row[0]),
                level=int(row[1]),
                days_overdue_min=int(row[2]),
                days_overdue_max=int(row[3]) if row[3] else None,
                fee_amount=Decimal(str(row[4])),
                fee_percentage=Decimal(str(row[5])),
                interest_rate=Decimal(str(row[6])),
                payment_deadline_days=int(row[7]),
                block_customer=bool(row[8]),
                escalate_to_collection=bool(row[9]),
                description_template=str(row[10]),
                active=bool(row[11]),
                created_at=row[12],
                updated_at=row[13]
            ))
        
        return result
        
    except SQLAlchemyError as e:
        # Bis 08.10.2026 lieferte dieser Weg bei jedem Datenbankfehler drei
        # erfundene Mahnstufen (Gebuehren 5/10/15 EUR, Ids "1".."3") — und der
        # Mahnlauf, der diese Funktion nutzt, haette damit echte Mahnungen mit
        # Gebuehren erzeugt, die kein Mandant je festgelegt hat.
        db.rollback()
        logger.error("Error listing dunning rules: %s", e)
        raise HTTPException(status_code=503, detail="Mahnregeln nicht lesbar") from e


@router.post("/rules", response_model=DunningRuleResponse, status_code=201, summary="Dunning rule anlegen",
            dependencies=[Depends(finance_write)])
async def create_dunning_rule(
    rule: DunningRuleCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a new dunning rule.
    """
    try:
        # Check if rule for this level already exists
        check_query = text("""
            SELECT id FROM domain_erp.dunning_rules
            WHERE level = :level AND tenant_id = :tenant_id AND active = true
        """)
        
        existing = db.execute(check_query, {
            "level": rule.level,
            "tenant_id": tenant_id
        }).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Active dunning rule for level {rule.level} already exists"
            )
        
        # Insert new rule
        rule_id = uuid7()
        
        insert_query = text("""
            INSERT INTO domain_erp.dunning_rules
            (id, tenant_id, level, days_overdue_min, days_overdue_max, fee_amount, fee_percentage,
             interest_rate, payment_deadline_days, block_customer, escalate_to_collection,
             description_template, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :level, :days_overdue_min, :days_overdue_max, :fee_amount, :fee_percentage,
             :interest_rate, :payment_deadline_days, :block_customer, :escalate_to_collection,
             :description_template, :active, NOW(), NOW())
            RETURNING id, level, days_overdue_min, days_overdue_max, fee_amount, fee_percentage,
                      interest_rate, payment_deadline_days, block_customer, escalate_to_collection,
                      description_template, active, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": rule_id,
            "tenant_id": tenant_id,
            "level": rule.level,
            "days_overdue_min": rule.days_overdue_min,
            "days_overdue_max": rule.days_overdue_max,
            "fee_amount": rule.fee_amount,
            "fee_percentage": rule.fee_percentage,
            "interest_rate": rule.interest_rate,
            "payment_deadline_days": rule.payment_deadline_days,
            "block_customer": rule.block_customer,
            "escalate_to_collection": rule.escalate_to_collection,
            "description_template": rule.description_template,
            "active": rule.active
        }).fetchone()
        
        db.commit()
        
        return DunningRuleResponse(
            id=str(row[0]),
            level=int(row[1]),
            days_overdue_min=int(row[2]),
            days_overdue_max=int(row[3]) if row[3] else None,
            fee_amount=Decimal(str(row[4])),
            fee_percentage=Decimal(str(row[5])),
            interest_rate=Decimal(str(row[6])),
            payment_deadline_days=int(row[7]),
            block_customer=bool(row[8]),
            escalate_to_collection=bool(row[9]),
            description_template=str(row[10]),
            active=bool(row[11]),
            created_at=row[12],
            updated_at=row[13]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dunning rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dunning rule: {str(e)}")


@router.post("/process", response_model=List[DunningResponse], summary="Dunning verarbeiten",
            dependencies=[Depends(finance_write)])
async def process_dunning(
    request: ProcessDunningRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
):
    """Mahnt die mahnfaelligen Posten (Auswahl: ``op_ids`` oder ``debtor_id``) ueber den einen Mahnweg.

    Bis 23.11.2026 rechnete dieser Weg mit eigener Stufen- und Gebuehrenlogik neben dem Mahnlauf
    (``FinanceDunningService.run_dunning``); jetzt ruft er ihn.
    """
    from app.auth.deps import anmeldename
    from app.services.finance_dunning_service import FinanceDunningService

    try:
        ergebnis = FinanceDunningService(db, tenant_id).run_dunning(
            bediener=anmeldename(nutzer) or "unbekannt", op_ids=request.op_ids, debtor_id=request.debtor_id,
            stichtag=request.as_of_date)
    except DomainError:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Mahnwesen nicht verfügbar - keine Mahnung erzeugt") from exc
    ids = [m["id"] for m in ergebnis.get("mahnungen", [])]
    if not ids:
        return []
    rows = db.execute(text(f"SELECT {_NOTICE_COLUMNS} FROM domain_erp.dunning_notices "  # nosec B608 - feste Spalten
                           "WHERE tenant_id = :t AND id = ANY(:ids) ORDER BY dunning_date, dunning_level"),
                      {"t": tenant_id, "ids": ids}).fetchall()
    return [_notice_response(row) for row in rows]



@router.post("/run", response_model=DunningRunResponse, summary="Dunning ausführen",
            dependencies=[Depends(finance_write)])
async def run_dunning(
    request: DunningRunRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
):
    """
    Start a dunning run for all overdue open items as of the given date.
    Returns run_id and number of dunning notices created.
    """
    run_id = str(uuid7())
    process_request = ProcessDunningRequest(as_of_date=request.as_of_date)
    created = await process_dunning(process_request, db, tenant_id, nutzer)
    return DunningRunResponse(
        run_id=run_id,
        notices_created=len(created),
    )




@router.get("", response_model=List[DunningResponse], summary="Dunnings auflisten",
            dependencies=[Depends(finance_read)])
async def list_dunnings(
    debtor_id: Optional[str] = Query(None, description="Filter by debtor ID"),
    op_id: Optional[str] = Query(None, description="Filter by open item ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    List all dunning notices.
    """
    try:
        query = text("""
            SELECT id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                   open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                   sent_date, payment_date, notes, created_at, updated_at
            FROM domain_erp.dunning_notices
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        conditions = []
        
        if debtor_id:
            conditions.append("debtor_id = :debtor_id")
            params["debtor_id"] = debtor_id
        
        if op_id:
            conditions.append("op_id = :op_id")
            params["op_id"] = op_id
        
        if status:
            conditions.append("status = :status")
            params["status"] = status
        
        if conditions:
            query = text(str(query) + " AND " + " AND ".join(conditions))  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        query = text(str(query) + " ORDER BY dunning_date DESC, dunning_level DESC")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            result.append(DunningResponse(
                id=str(row[0]),
                op_id=str(row[1]),
                debtor_id=str(row[2]),
                dunning_level=int(row[3]),
                dunning_date=row[4],
                due_date=row[5],
                open_amount=Decimal(str(row[6])),
                dunning_fee=Decimal(str(row[7])),
                interest=Decimal(str(row[8])),
                total_amount=Decimal(str(row[9])),
                payment_deadline=row[10],
                status=str(row[11]),
                sent_date=row[12] if row[12] else None,
                payment_date=row[13] if row[13] else None,
                notes=str(row[14]) if row[14] else None,
                created_at=row[15],
                updated_at=row[16]
            ))
        
        return result
        
    except SQLAlchemyError as e:
        # Bis 08.10.2026: leere Liste — ein Datenbankfehler sah aus wie "keine Mahnungen".
        db.rollback()
        logger.error("Error listing dunnings: %s", e)
        raise HTTPException(status_code=503, detail="Mahnungen nicht lesbar") from e


@router.put("/{dunning_id}/send", response_model=DunningResponse, summary="Dunning senden",
            dependencies=[Depends(finance_write)])
async def send_dunning(
    dunning_id: str,
    versand_art: str = Query("email", pattern="^(email|post)$", description="email: an den Kunden; post: gedruckt verschickt"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(get_current_user),
):
    """
    Versendet die Mahnung (E-Mail ueber das Postfach ``fibu``) oder haelt den Postversand fest.
    ``sent`` erst danach; ohne Adresse oder Postfach bleibt sie unversendet (422/503).
    """
    try:
        row = FinanceDunningService(db, tenant_id).send_notice(dunning_id, versand_art=versand_art, nutzer=nutzer)
        canonical = f"Mahnung|{dunning_id}|{row[1]}|{row[3]}|{row[6]}|{row[9]}|{versand_art}"
        content_hash = sha256_hex(canonical.encode("utf-8"))
        # Versandstatus und Archiveintrag gemeinsam: ohne Archiv kein "versandt".
        register_artifact(
            db, tenant_id, dunning_id, "other",
            content_hash, f"dunning/sent/{dunning_id}", file_name=f"Mahnung_{dunning_id}_versanddaten.txt",
            created_by=None, doc_type="dunning_notice", content=canonical.encode("utf-8"),
        )
        db.commit()
        
        return DunningResponse(
            id=str(row[0]),
            op_id=str(row[1]),
            debtor_id=str(row[2]),
            dunning_level=int(row[3]),
            dunning_date=row[4],
            due_date=row[5],
            open_amount=Decimal(str(row[6])),
            dunning_fee=Decimal(str(row[7])),
            interest=Decimal(str(row[8])),
            total_amount=Decimal(str(row[9])),
            payment_deadline=row[10],
            status=str(row[11]),
            sent_date=row[12] if row[12] else None,
            payment_date=row[13] if row[13] else None,
            notes=str(row[14]) if row[14] else None,
            created_at=row[15],
            updated_at=row[16]
        )
        
    except (HTTPException, DomainError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending dunning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send dunning: {str(e)}")

