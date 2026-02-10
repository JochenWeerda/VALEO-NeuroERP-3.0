"""
Dunning System API
FIBU-AR-04: Mahnwesen vervollständigen
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
import logging
import uuid

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dunning", tags=["finance", "dunning"])


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
    due_date: date
    open_amount: Decimal
    dunning_fee: Decimal
    interest: Decimal
    total_amount: Decimal
    payment_deadline: date
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
    tenant_id: str = Field(default="system")


@router.get("/rules", response_model=List[DunningRuleResponse])
async def list_dunning_rules(
    active_only: bool = Query(True, description="Show only active rules"),
    tenant_id: str = Query("system", description="Tenant ID"),
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
            query = text(str(query) + " AND active = true")
        
        query = text(str(query) + " ORDER BY level")
        
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
        
    except Exception as e:
        logger.error(f"Error listing dunning rules: {e}")
        # Return default rules if table doesn't exist
        return [
            DunningRuleResponse(
                id="1",
                level=1,
                days_overdue_min=14,
                days_overdue_max=29,
                fee_amount=Decimal("5.00"),
                fee_percentage=Decimal("0.00"),
                interest_rate=Decimal("9.00"),
                payment_deadline_days=14,
                block_customer=False,
                escalate_to_collection=False,
                description_template="Erste Mahnung: Ihre Rechnung ist seit {{days_overdue}} Tagen überfällig.",
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            DunningRuleResponse(
                id="2",
                level=2,
                days_overdue_min=30,
                days_overdue_max=59,
                fee_amount=Decimal("10.00"),
                fee_percentage=Decimal("0.00"),
                interest_rate=Decimal("9.00"),
                payment_deadline_days=14,
                block_customer=True,
                escalate_to_collection=False,
                description_template="Zweite Mahnung: Ihre Rechnung ist seit {{days_overdue}} Tagen überfällig. Bitte zahlen Sie umgehend.",
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            DunningRuleResponse(
                id="3",
                level=3,
                days_overdue_min=60,
                days_overdue_max=None,
                fee_amount=Decimal("15.00"),
                fee_percentage=Decimal("0.00"),
                interest_rate=Decimal("9.00"),
                payment_deadline_days=7,
                block_customer=True,
                escalate_to_collection=True,
                description_template="Letzte Mahnung: Ihre Rechnung ist seit {{days_overdue}} Tagen überfällig. Bei Nichtzahlung werden wir rechtliche Schritte einleiten.",
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]


@router.post("/rules", response_model=DunningRuleResponse, status_code=201)
async def create_dunning_rule(
    rule: DunningRuleCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
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
        rule_id = str(uuid.uuid4())
        
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


@router.post("/process", response_model=List[DunningResponse])
async def process_dunning(
    request: ProcessDunningRequest,
    db: Session = Depends(get_db)
):
    """
    Process dunning for overdue open items based on rules.
    """
    try:
        # Get active dunning rules
        rules = await list_dunning_rules(active_only=True, tenant_id=request.tenant_id, db=db)
        
        if not rules:
            raise HTTPException(status_code=400, detail="No active dunning rules found")
        
        # Get overdue open items
        if request.op_ids:
            op_query = text("""
                SELECT id, debtor_id, booking_date, due_date, open_amount, dunning_level
                FROM domain_erp.offene_posten
                WHERE id = ANY(:op_ids) AND tenant_id = :tenant_id
                AND debtor_id IS NOT NULL
                AND open_amount > 0
            """)
            op_rows = db.execute(op_query, {
                "op_ids": request.op_ids,
                "tenant_id": request.tenant_id
            }).fetchall()
        elif request.debtor_id:
            op_query = text("""
                SELECT id, debtor_id, booking_date, due_date, open_amount, dunning_level
                FROM domain_erp.offene_posten
                WHERE debtor_id = :debtor_id AND tenant_id = :tenant_id
                AND open_amount > 0
            """)
            op_rows = db.execute(op_query, {
                "debtor_id": request.debtor_id,
                "tenant_id": request.tenant_id
            }).fetchall()
        else:
            op_query = text("""
                SELECT id, debtor_id, booking_date, due_date, open_amount, dunning_level
                FROM domain_erp.offene_posten
                WHERE tenant_id = :tenant_id
                AND debtor_id IS NOT NULL
                AND open_amount > 0
                AND due_date < CURRENT_DATE
            """)
            op_rows = db.execute(op_query, {
                "tenant_id": request.tenant_id
            }).fetchall()
        
        created_dunnings = []
        today = date.today()
        
        for op_row in op_rows:
            op_id = str(op_row[0])
            debtor_id = str(op_row[1])
            booking_date = op_row[2]
            due_date = op_row[3]
            open_amount = Decimal(str(op_row[4]))
            current_dunning_level = int(op_row[5]) if op_row[5] else 0
            
            # Calculate days overdue
            days_overdue = (today - due_date).days
            
            if days_overdue < 0:
                continue  # Not overdue yet
            
            # Find applicable rule
            applicable_rule = None
            for rule in sorted(rules, key=lambda r: r.level, reverse=True):
                if rule.days_overdue_min <= days_overdue:
                    if rule.days_overdue_max is None or days_overdue <= rule.days_overdue_max:
                        if rule.level > current_dunning_level:
                            applicable_rule = rule
                            break
            
            if not applicable_rule:
                continue  # No rule applies or already at max level
            
            # Calculate fees and interest
            dunning_fee = applicable_rule.fee_amount
            if applicable_rule.fee_percentage > 0:
                dunning_fee += open_amount * (applicable_rule.fee_percentage / Decimal("100.00"))
            
            # Calculate interest (simple interest: amount * rate * days / 365)
            interest = Decimal("0.00")
            if applicable_rule.interest_rate > 0:
                interest = open_amount * (applicable_rule.interest_rate / Decimal("100.00")) * Decimal(str(days_overdue)) / Decimal("365.00")
            
            total_amount = open_amount + dunning_fee + interest
            payment_deadline = today + timedelta(days=applicable_rule.payment_deadline_days)
            
            # Create dunning notice
            dunning_id = str(uuid.uuid4())
            dunning_insert = text("""
                INSERT INTO domain_erp.dunning_notices
                (id, tenant_id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                 open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                 notes, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :op_id, :debtor_id, :dunning_level, :dunning_date, :due_date,
                 :open_amount, :dunning_fee, :interest, :total_amount, :payment_deadline, :status,
                 :notes, NOW(), NOW())
                RETURNING id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                          open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                          sent_date, payment_date, notes, created_at, updated_at
            """)
            
            # Replace placeholders in description
            description = applicable_rule.description_template.replace("{{days_overdue}}", str(days_overdue))
            
            row = db.execute(dunning_insert, {
                "id": dunning_id,
                "tenant_id": request.tenant_id,
                "op_id": op_id,
                "debtor_id": debtor_id,
                "dunning_level": applicable_rule.level,
                "dunning_date": today,
                "due_date": due_date,
                "open_amount": open_amount,
                "dunning_fee": dunning_fee,
                "interest": interest,
                "total_amount": total_amount,
                "payment_deadline": payment_deadline,
                "status": "created",
                "notes": description
            }).fetchone()
            
            # Update open item dunning level
            update_op_query = text("""
                UPDATE domain_erp.offene_posten
                SET dunning_level = :dunning_level, updated_at = NOW()
                WHERE id = :op_id AND tenant_id = :tenant_id
            """)
            
            db.execute(update_op_query, {
                "dunning_level": applicable_rule.level,
                "op_id": op_id,
                "tenant_id": request.tenant_id
            })
            
            # Block customer if rule requires it
            if applicable_rule.block_customer:
                block_debtor_query = text("""
                    UPDATE domain_erp.debtors
                    SET blocked = true, updated_at = NOW()
                    WHERE id = :debtor_id AND tenant_id = :tenant_id
                """)
                
                db.execute(block_debtor_query, {
                    "debtor_id": debtor_id,
                    "tenant_id": request.tenant_id
                })
            
            created_dunnings.append(DunningResponse(
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
        
        db.commit()
        
        return created_dunnings
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing dunning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process dunning: {str(e)}")


@router.post("", response_model=DunningResponse, status_code=201)
async def create_dunning(
    dunning: DunningCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a manual dunning notice.
    """
    try:
        # Get dunning rule for level
        rule_query = text("""
            SELECT fee_amount, fee_percentage, interest_rate, payment_deadline_days, description_template
            FROM domain_erp.dunning_rules
            WHERE level = :level AND tenant_id = :tenant_id AND active = true
            LIMIT 1
        """)
        
        rule_row = db.execute(rule_query, {
            "level": dunning.dunning_level,
            "tenant_id": tenant_id
        }).fetchone()
        
        # Calculate fees
        if rule_row:
            dunning_fee = Decimal(str(rule_row[0]))
            if Decimal(str(rule_row[1])) > 0:
                dunning_fee += dunning.open_amount * (Decimal(str(rule_row[1])) / Decimal("100.00"))
            
            # Calculate interest
            days_overdue = (dunning.dunning_date - dunning.due_date).days
            if Decimal(str(rule_row[2])) > 0 and days_overdue > 0:
                interest = dunning.open_amount * (Decimal(str(rule_row[2])) / Decimal("100.00")) * Decimal(str(days_overdue)) / Decimal("365.00")
            else:
                interest = Decimal("0.00")
            
            payment_deadline_days = int(rule_row[3])
            description_template = str(rule_row[4])
        else:
            # Default values if no rule found
            dunning_fee = dunning.custom_fee or Decimal("5.00")
            interest = dunning.custom_interest or Decimal("0.00")
            payment_deadline_days = 14
            description_template = "Mahnung Stufe {{dunning_level}}"
        
        # Override with custom values if provided
        if dunning.custom_fee is not None:
            dunning_fee = dunning.custom_fee
        if dunning.custom_interest is not None:
            interest = dunning.custom_interest
        
        total_amount = dunning.open_amount + dunning_fee + interest
        payment_deadline = dunning.dunning_date + timedelta(days=payment_deadline_days)
        
        # Create dunning notice
        dunning_id = str(uuid.uuid4())
        dunning_insert = text("""
            INSERT INTO domain_erp.dunning_notices
            (id, tenant_id, op_id, debtor_id, dunning_level, dunning_date, due_date,
             open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
             notes, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :op_id, :debtor_id, :dunning_level, :dunning_date, :due_date,
             :open_amount, :dunning_fee, :interest, :total_amount, :payment_deadline, :status,
             :notes, NOW(), NOW())
            RETURNING id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                      open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                      sent_date, payment_date, notes, created_at, updated_at
        """)
        
        row = db.execute(dunning_insert, {
            "id": dunning_id,
            "tenant_id": tenant_id,
            "op_id": dunning.op_id,
            "debtor_id": dunning.debtor_id,
            "dunning_level": dunning.dunning_level,
            "dunning_date": dunning.dunning_date,
            "due_date": dunning.due_date,
            "open_amount": dunning.open_amount,
            "dunning_fee": dunning_fee,
            "interest": interest,
            "total_amount": total_amount,
            "payment_deadline": payment_deadline,
            "status": "created",
            "notes": dunning.notes or description_template.replace("{{dunning_level}}", str(dunning.dunning_level))
        }).fetchone()
        
        # Update open item dunning level
        update_op_query = text("""
            UPDATE domain_erp.offene_posten
            SET dunning_level = :dunning_level, updated_at = NOW()
            WHERE id = :op_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_op_query, {
            "dunning_level": dunning.dunning_level,
            "op_id": dunning.op_id,
            "tenant_id": tenant_id
        })
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dunning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dunning: {str(e)}")


@router.get("", response_model=List[DunningResponse])
async def list_dunnings(
    debtor_id: Optional[str] = Query(None, description="Filter by debtor ID"),
    op_id: Optional[str] = Query(None, description="Filter by open item ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tenant_id: str = Query("system", description="Tenant ID"),
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
            query = text(str(query) + " AND " + " AND ".join(conditions))
        
        query = text(str(query) + " ORDER BY dunning_date DESC, dunning_level DESC")
        
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
        
    except Exception as e:
        logger.error(f"Error listing dunnings: {e}")
        return []


@router.put("/{dunning_id}/send", response_model=DunningResponse)
async def send_dunning(
    dunning_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Mark dunning notice as sent.
    """
    try:
        update_query = text("""
            UPDATE domain_erp.dunning_notices
            SET status = 'sent', sent_date = CURRENT_DATE, updated_at = NOW()
            WHERE id = :dunning_id AND tenant_id = :tenant_id
            RETURNING id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                      open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                      sent_date, payment_date, notes, created_at, updated_at
        """)
        
        row = db.execute(update_query, {
            "dunning_id": dunning_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Dunning notice not found")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending dunning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send dunning: {str(e)}")


@router.put("/{dunning_id}/paid", response_model=DunningResponse)
async def mark_dunning_paid(
    dunning_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Mark dunning notice as paid.
    """
    try:
        update_query = text("""
            UPDATE domain_erp.dunning_notices
            SET status = 'paid', payment_date = CURRENT_DATE, updated_at = NOW()
            WHERE id = :dunning_id AND tenant_id = :tenant_id
            RETURNING id, op_id, debtor_id, dunning_level, dunning_date, due_date,
                      open_amount, dunning_fee, interest, total_amount, payment_deadline, status,
                      sent_date, payment_date, notes, created_at, updated_at
        """)
        
        row = db.execute(update_query, {
            "dunning_id": dunning_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Dunning notice not found")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking dunning as paid: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark dunning as paid: {str(e)}")

