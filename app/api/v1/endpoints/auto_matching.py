"""
Automatic Matching API
FIBU-BNK-03: Automatisches Matching
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
import re

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-matching", tags=["finance", "bank", "matching"])


class MatchingRule(BaseModel):
    """Matching rule configuration"""
    rule_name: str = Field(..., description="Rule name")
    priority: int = Field(default=0, description="Rule priority (higher = checked first)")
    match_type: str = Field(..., description="Match type: amount, reference, iban, date_range, combined")
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    confidence_threshold: float = Field(default=0.8, ge=0, le=1, description="Minimum confidence to auto-match")
    auto_apply: bool = Field(default=True, description="Automatically apply matches above threshold")
    active: bool = Field(default=True, description="Active status")


class MatchingRuleCreate(BaseModel):
    """Schema for creating a matching rule"""
    rule_name: str = Field(..., min_length=1, max_length=100)
    priority: int = Field(default=0)
    match_type: str = Field(..., description="amount, reference, iban, date_range, combined")
    conditions: Dict[str, Any] = Field(...)
    confidence_threshold: float = Field(default=0.8, ge=0, le=1)
    auto_apply: bool = Field(default=True)
    active: bool = Field(default=True)


class MatchSuggestion(BaseModel):
    """Match suggestion for a bank statement line"""
    statement_line_id: str
    op_id: str
    confidence: float = Field(..., ge=0, le=1)
    match_type: str  # EXACT_AMOUNT, REFERENCE, IBAN, DATE_RANGE, COMBINED
    match_reason: str
    amount_difference: Optional[Decimal] = None
    date_difference_days: Optional[int] = None


class MatchResult(BaseModel):
    """Result of matching operation"""
    statement_line_id: str
    op_id: Optional[str] = None
    matched: bool
    confidence: float
    match_type: Optional[str] = None
    match_reason: Optional[str] = None
    auto_matched: bool = False
    matched_by: Optional[str] = None
    matched_at: Optional[datetime] = None
    suggestions: List[MatchSuggestion] = []


class AutoMatchRequest(BaseModel):
    """Request to perform automatic matching"""
    statement_id: Optional[str] = Field(None, description="Match specific statement")
    bank_account: Optional[str] = Field(None, description="Match for specific bank account")
    auto_apply: bool = Field(default=False, description="Automatically apply high-confidence matches")
    min_confidence: float = Field(default=0.8, ge=0, le=1, description="Minimum confidence for auto-apply")
    tenant_id: str = Field(default="system")


class MatchingStatistics(BaseModel):
    """Matching statistics"""
    total_lines: int
    matched_lines: int
    unmatched_lines: int
    auto_matched_lines: int
    manual_matched_lines: int
    match_rate: float
    average_confidence: float
    by_match_type: Dict[str, int]


@router.get("/rules", response_model=List[MatchingRule])
async def list_matching_rules(
    active_only: bool = Query(True, description="Show only active rules"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all matching rules.
    """
    try:
        query = text("""
            SELECT id, rule_name, priority, match_type, conditions, confidence_threshold,
                   auto_apply, active, created_at, updated_at
            FROM domain_erp.matching_rules
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if active_only:
            query = text(str(query) + " AND active = true")
        
        query = text(str(query) + " ORDER BY priority DESC, rule_name")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            conditions_data = json.loads(row[4]) if row[4] else {}
            
            result.append(MatchingRule(
                rule_name=str(row[1]),
                priority=int(row[2]),
                match_type=str(row[3]),
                conditions=conditions_data,
                confidence_threshold=float(row[5]),
                auto_apply=bool(row[6]),
                active=bool(row[7])
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing matching rules: {e}")
        # Return default rules if table doesn't exist
        return [
            MatchingRule(
                rule_name="Exact Amount Match",
                priority=100,
                match_type="amount",
                conditions={"tolerance": 0.01, "date_range_days": 30},
                confidence_threshold=0.95,
                auto_apply=True,
                active=True
            ),
            MatchingRule(
                rule_name="Reference Match",
                priority=90,
                match_type="reference",
                conditions={"fuzzy": True, "date_range_days": 60},
                confidence_threshold=0.85,
                auto_apply=True,
                active=True
            ),
            MatchingRule(
                rule_name="IBAN Match",
                priority=80,
                match_type="iban",
                conditions={"date_range_days": 90},
                confidence_threshold=0.90,
                auto_apply=True,
                active=True
            ),
            MatchingRule(
                rule_name="Combined Match",
                priority=70,
                match_type="combined",
                conditions={"amount_tolerance": 0.05, "date_range_days": 30, "require_reference": False},
                confidence_threshold=0.80,
                auto_apply=False,
                active=True
            )
        ]


@router.post("/rules", response_model=MatchingRule, status_code=201)
async def create_matching_rule(
    rule: MatchingRuleCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new matching rule.
    """
    try:
        rule_id = str(uuid.uuid4())
        
        import json
        conditions_json = json.dumps(rule.conditions)
        
        insert_query = text("""
            INSERT INTO domain_erp.matching_rules
            (id, tenant_id, rule_name, priority, match_type, conditions, confidence_threshold,
             auto_apply, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :rule_name, :priority, :match_type, :conditions, :confidence_threshold,
             :auto_apply, :active, NOW(), NOW())
            RETURNING id, rule_name, priority, match_type, conditions, confidence_threshold,
                      auto_apply, active, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": rule_id,
            "tenant_id": tenant_id,
            "rule_name": rule.rule_name,
            "priority": rule.priority,
            "match_type": rule.match_type,
            "conditions": conditions_json,
            "confidence_threshold": rule.confidence_threshold,
            "auto_apply": rule.auto_apply,
            "active": rule.active
        }).fetchone()
        
        db.commit()
        
        import json
        conditions_data = json.loads(row[4]) if row[4] else {}
        
        return MatchingRule(
            rule_name=str(row[1]),
            priority=int(row[2]),
            match_type=str(row[3]),
            conditions=conditions_data,
            confidence_threshold=float(row[5]),
            auto_apply=bool(row[6]),
            active=bool(row[7])
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating matching rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create matching rule: {str(e)}")


def _extract_reference_numbers(text: str) -> List[str]:
    """Extract potential reference numbers from text"""
    if not text:
        return []
    
    # Common patterns: RE-2024-001, INV-12345, 2024/001, etc.
    patterns = [
        r'RE[-/]\d{4}[-/]\d+',  # RE-2024-001
        r'INV[-/]\d+',  # INV-12345
        r'\d{4}[/-]\d+',  # 2024/001
        r'\d{6,}',  # Long numeric strings
    ]
    
    references = []
    for pattern in patterns:
        matches = re.findall(pattern, text.upper())
        references.extend(matches)
    
    return list(set(references))


def _calculate_amount_match_confidence(
    statement_amount: Decimal,
    op_amount: Decimal,
    tolerance: Decimal = Decimal("0.01")
) -> float:
    """Calculate confidence for amount-based matching"""
    difference = abs(statement_amount - op_amount)
    
    if difference <= tolerance:
        return 1.0
    elif difference <= op_amount * Decimal("0.01"):  # 1% tolerance
        return 0.95
    elif difference <= op_amount * Decimal("0.05"):  # 5% tolerance
        return 0.85
    else:
        return max(0.0, 1.0 - float(difference / op_amount))


def _calculate_reference_match_confidence(
    statement_reference: str,
    op_reference: str
) -> float:
    """Calculate confidence for reference-based matching"""
    if not statement_reference or not op_reference:
        return 0.0
    
    statement_ref_upper = statement_reference.upper().strip()
    op_ref_upper = op_reference.upper().strip()
    
    # Exact match
    if statement_ref_upper == op_ref_upper:
        return 1.0
    
    # Contains match
    if statement_ref_upper in op_ref_upper or op_ref_upper in statement_ref_upper:
        return 0.9
    
    # Extract reference numbers
    statement_refs = _extract_reference_numbers(statement_reference)
    op_refs = _extract_reference_numbers(op_reference)
    
    if statement_refs and op_refs:
        for s_ref in statement_refs:
            for o_ref in op_refs:
                if s_ref == o_ref:
                    return 0.95
                elif s_ref in o_ref or o_ref in s_ref:
                    return 0.85
    
    return 0.0


def _calculate_date_match_confidence(
    statement_date: date,
    op_due_date: date,
    max_days: int = 30
) -> float:
    """Calculate confidence for date-based matching"""
    days_diff = abs((statement_date - op_due_date).days)
    
    if days_diff == 0:
        return 1.0
    elif days_diff <= 7:
        return 0.95
    elif days_diff <= 14:
        return 0.85
    elif days_diff <= max_days:
        return max(0.5, 1.0 - (days_diff / max_days) * 0.5)
    else:
        return 0.0


@router.post("/match", response_model=List[MatchResult])
async def auto_match(
    request: AutoMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform automatic matching of bank statement lines with open items.
    """
    try:
        # Get matching rules
        rules = await list_matching_rules(active_only=True, tenant_id=request.tenant_id, db=db)
        
        # Get unmatched bank statement lines
        if request.statement_id:
            lines_query = text("""
                SELECT id, booking_date, amount, currency, reference, remittance_info,
                       creditor_iban, debtor_iban, status
                FROM domain_erp.bank_statement_lines
                WHERE statement_id = :statement_id AND tenant_id = :tenant_id
                AND (status = 'UNMATCHED' OR status IS NULL)
            """)
            lines_rows = db.execute(lines_query, {
                "statement_id": request.statement_id,
                "tenant_id": request.tenant_id
            }).fetchall()
        else:
            lines_query = text("""
                SELECT id, booking_date, amount, currency, reference, remittance_info,
                       creditor_iban, debtor_iban, status
                FROM domain_erp.bank_statement_lines
                WHERE tenant_id = :tenant_id
                AND (status = 'UNMATCHED' OR status IS NULL)
            """)
            params = {"tenant_id": request.tenant_id}
            
            if request.bank_account:
                lines_query = text(str(lines_query) + " AND bank_account = :bank_account")
                params["bank_account"] = request.bank_account
            
            lines_rows = db.execute(lines_query, params).fetchall()
        
        # Get open items
        op_query = text("""
            SELECT id, rechnungsnr, kunde_id, kunde_name, betrag, offen, faelligkeit, zahlbar
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id AND offen > 0
        """)
        
        op_rows = db.execute(op_query, {"tenant_id": request.tenant_id}).fetchall()
        
        # Build open items lookup
        open_items = {}
        for op_row in op_rows:
            op_id = str(op_row[0])
            open_items[op_id] = {
                "id": op_id,
                "document_number": str(op_row[1]) if op_row[1] else "",
                "customer_id": str(op_row[2]) if op_row[2] else "",
                "customer_name": str(op_row[3]) if op_row[3] else "",
                "amount": Decimal(str(op_row[4])),
                "open_amount": Decimal(str(op_row[5])),
                "due_date": op_row[6],
                "payable": bool(op_row[7]) if op_row[7] is not None else True
            }
        
        results = []
        
        # Process each statement line
        for line_row in lines_rows:
            line_id = str(line_row[0])
            line_booking_date = line_row[1]
            line_amount = Decimal(str(line_row[2]))
            line_currency = str(line_row[3])
            line_reference = str(line_row[4]) if line_row[4] else ""
            line_remittance = str(line_row[5]) if line_row[5] else ""
            line_creditor_iban = str(line_row[6]) if line_row[6] else ""
            line_debtor_iban = str(line_row[7]) if line_row[7] else ""
            
            # Combine reference and remittance info
            full_reference = f"{line_reference} {line_remittance}".strip()
            
            suggestions = []
            best_match = None
            best_confidence = 0.0
            
            # Try each matching rule
            for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
                if rule.match_type == "amount":
                    tolerance = Decimal(str(rule.conditions.get("tolerance", 0.01)))
                    date_range = rule.conditions.get("date_range_days", 30)
                    
                    for op_id, op in open_items.items():
                        if op["open_amount"] <= 0:
                            continue
                        
                        amount_conf = _calculate_amount_match_confidence(
                            line_amount, op["open_amount"], tolerance
                        )
                        
                        if amount_conf > 0:
                            date_conf = _calculate_date_match_confidence(
                                line_booking_date, op["due_date"], date_range
                            )
                            
                            combined_conf = (amount_conf * 0.7) + (date_conf * 0.3)
                            
                            if combined_conf > best_confidence:
                                best_confidence = combined_conf
                                best_match = op_id
                            
                            suggestions.append(MatchSuggestion(
                                statement_line_id=line_id,
                                op_id=op_id,
                                confidence=combined_conf,
                                match_type="EXACT_AMOUNT" if amount_conf >= 0.95 else "AMOUNT",
                                match_reason=f"Amount match: {amount_conf:.2%}, Date match: {date_conf:.2%}",
                                amount_difference=abs(line_amount - op["open_amount"]),
                                date_difference_days=abs((line_booking_date - op["due_date"]).days)
                            ))
                
                elif rule.match_type == "reference":
                    date_range = rule.conditions.get("date_range_days", 60)
                    
                    for op_id, op in open_items.items():
                        if op["open_amount"] <= 0:
                            continue
                        
                        ref_conf = _calculate_reference_match_confidence(
                            full_reference, op["document_number"]
                        )
                        
                        if ref_conf > 0:
                            amount_conf = _calculate_amount_match_confidence(
                                line_amount, op["open_amount"], Decimal("0.10")
                            )
                            date_conf = _calculate_date_match_confidence(
                                line_booking_date, op["due_date"], date_range
                            )
                            
                            combined_conf = (ref_conf * 0.5) + (amount_conf * 0.3) + (date_conf * 0.2)
                            
                            if combined_conf > best_confidence:
                                best_confidence = combined_conf
                                best_match = op_id
                            
                            suggestions.append(MatchSuggestion(
                                statement_line_id=line_id,
                                op_id=op_id,
                                confidence=combined_conf,
                                match_type="REFERENCE",
                                match_reason=f"Reference match: {ref_conf:.2%}",
                                amount_difference=abs(line_amount - op["open_amount"]),
                                date_difference_days=abs((line_booking_date - op["due_date"]).days)
                            ))
                
                elif rule.match_type == "iban":
                    date_range = rule.conditions.get("date_range_days", 90)
                    
                    # Get customer IBAN from debtor master data
                    for op_id, op in open_items.items():
                        if op["open_amount"] <= 0:
                            continue
                        
                        # Check if IBAN matches (would need to query debtor master data)
                        # For now, skip IBAN matching
                        pass
                
                elif rule.match_type == "combined":
                    # Combine multiple factors
                    for op_id, op in open_items.items():
                        if op["open_amount"] <= 0:
                            continue
                        
                        amount_conf = _calculate_amount_match_confidence(
                            line_amount, op["open_amount"], Decimal(str(rule.conditions.get("amount_tolerance", 0.05)))
                        )
                        date_conf = _calculate_date_match_confidence(
                            line_booking_date, op["due_date"], rule.conditions.get("date_range_days", 30)
                        )
                        ref_conf = _calculate_reference_match_confidence(
                            full_reference, op["document_number"]
                        ) if not rule.conditions.get("require_reference", False) or full_reference else 0.5
                        
                        combined_conf = (amount_conf * 0.4) + (date_conf * 0.3) + (ref_conf * 0.3)
                        
                        if combined_conf > best_confidence:
                            best_confidence = combined_conf
                            best_match = op_id
                        
                        suggestions.append(MatchSuggestion(
                            statement_line_id=line_id,
                            op_id=op_id,
                            confidence=combined_conf,
                            match_type="COMBINED",
                            match_reason=f"Combined: Amount {amount_conf:.2%}, Date {date_conf:.2%}, Ref {ref_conf:.2%}",
                            amount_difference=abs(line_amount - op["open_amount"]),
                            date_difference_days=abs((line_booking_date - op["due_date"]).days)
                        ))
            
            # Sort suggestions by confidence
            suggestions.sort(key=lambda x: x.confidence, reverse=True)
            
            # Determine if we should auto-match
            auto_matched = False
            matched_op_id = None
            
            if request.auto_apply and best_match and best_confidence >= request.min_confidence:
                # Find applicable rule
                applicable_rule = None
                for rule in rules:
                    if best_confidence >= rule.confidence_threshold and rule.auto_apply:
                        applicable_rule = rule
                        break
                
                if applicable_rule:
                    matched_op_id = best_match
                    auto_matched = True
                    
                    # Update statement line
                    update_line_query = text("""
                        UPDATE domain_erp.bank_statement_lines
                        SET status = 'MATCHED', matched_op_id = :op_id, matched_at = NOW(), updated_at = NOW()
                        WHERE id = :line_id AND tenant_id = :tenant_id
                    """)
                    
                    db.execute(update_line_query, {
                        "line_id": line_id,
                        "op_id": matched_op_id,
                        "tenant_id": request.tenant_id
                    })
                    
                    # Create match record
                    match_id = str(uuid.uuid4())
                    match_insert = text("""
                        INSERT INTO domain_erp.bank_matches
                        (id, tenant_id, statement_line_id, op_id, confidence, match_type, auto_matched, matched_at)
                        VALUES (:id, :tenant_id, :line_id, :op_id, :confidence, :match_type, :auto_matched, NOW())
                    """)
                    
                    db.execute(match_insert, {
                        "id": match_id,
                        "tenant_id": request.tenant_id,
                        "line_id": line_id,
                        "op_id": matched_op_id,
                        "confidence": best_confidence,
                        "match_type": suggestions[0].match_type if suggestions else "AUTO",
                        "auto_matched": True
                    })
            
            results.append(MatchResult(
                statement_line_id=line_id,
                op_id=matched_op_id,
                matched=auto_matched,
                confidence=best_confidence,
                match_type=suggestions[0].match_type if suggestions else None,
                match_reason=suggestions[0].match_reason if suggestions else None,
                auto_matched=auto_matched,
                matched_by="SYSTEM" if auto_matched else None,
                matched_at=datetime.now() if auto_matched else None,
                suggestions=suggestions[:5]  # Top 5 suggestions
            ))
        
        db.commit()
        
        return results
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error performing auto-matching: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform auto-matching: {str(e)}")


@router.post("/match/{line_id}/apply")
async def apply_match(
    line_id: str,
    op_id: str = Query(..., description="Open item ID to match"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Manually apply a match suggestion.
    """
    try:
        # Update statement line
        update_line_query = text("""
            UPDATE domain_erp.bank_statement_lines
            SET status = 'MATCHED', matched_op_id = :op_id, matched_at = NOW(), updated_at = NOW()
            WHERE id = :line_id AND tenant_id = :tenant_id
        """)
        
        result = db.execute(update_line_query, {
            "line_id": line_id,
            "op_id": op_id,
            "tenant_id": tenant_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Statement line not found")
        
        # Create match record
        match_id = str(uuid.uuid4())
        match_insert = text("""
            INSERT INTO domain_erp.bank_matches
            (id, tenant_id, statement_line_id, op_id, confidence, match_type, auto_matched, matched_at)
            VALUES (:id, :tenant_id, :line_id, :op_id, :confidence, :match_type, :auto_matched, NOW())
        """)
        
        db.execute(match_insert, {
            "id": match_id,
            "tenant_id": tenant_id,
            "line_id": line_id,
            "op_id": op_id,
            "confidence": 1.0,  # Manual match = 100% confidence
            "match_type": "MANUAL",
            "auto_matched": False
        })
        
        db.commit()
        
        return {
            "status": "ok",
            "message": "Match applied",
            "match_id": match_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error applying match: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply match: {str(e)}")


@router.get("/statistics", response_model=MatchingStatistics)
async def get_matching_statistics(
    statement_id: Optional[str] = Query(None, description="Filter by statement ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get matching statistics.
    """
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_lines,
                SUM(CASE WHEN status = 'MATCHED' THEN 1 ELSE 0 END) as matched_lines,
                SUM(CASE WHEN status = 'UNMATCHED' OR status IS NULL THEN 1 ELSE 0 END) as unmatched_lines
            FROM domain_erp.bank_statement_lines
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if statement_id:
            query = text(str(query) + " AND statement_id = :statement_id")
            params["statement_id"] = statement_id
        
        row = db.execute(query, params).fetchone()
        
        total_lines = int(row[0]) if row[0] else 0
        matched_lines = int(row[1]) if row[1] else 0
        unmatched_lines = int(row[2]) if row[2] else 0
        
        # Get auto-matched vs manual
        auto_query = text("""
            SELECT COUNT(*) FROM domain_erp.bank_matches
            WHERE tenant_id = :tenant_id AND auto_matched = true
        """)
        
        auto_params = {"tenant_id": tenant_id}
        if statement_id:
            auto_query = text(str(auto_query) + " AND statement_line_id IN (SELECT id FROM domain_erp.bank_statement_lines WHERE statement_id = :statement_id)")
            auto_params["statement_id"] = statement_id
        
        auto_matched = int(db.execute(auto_query, auto_params).scalar() or 0)
        manual_matched = matched_lines - auto_matched
        
        # Get average confidence
        conf_query = text("""
            SELECT AVG(confidence) FROM domain_erp.bank_matches
            WHERE tenant_id = :tenant_id
        """)
        
        conf_params = {"tenant_id": tenant_id}
        if statement_id:
            conf_query = text(str(conf_query) + " AND statement_line_id IN (SELECT id FROM domain_erp.bank_statement_lines WHERE statement_id = :statement_id)")
            conf_params["statement_id"] = statement_id
        
        avg_confidence = float(db.execute(conf_query, conf_params).scalar() or 0.0)
        
        # Get by match type
        type_query = text("""
            SELECT match_type, COUNT(*) FROM domain_erp.bank_matches
            WHERE tenant_id = :tenant_id
            GROUP BY match_type
        """)
        
        type_params = {"tenant_id": tenant_id}
        if statement_id:
            type_query = text(str(type_query) + " AND statement_line_id IN (SELECT id FROM domain_erp.bank_statement_lines WHERE statement_id = :statement_id)")
            type_params["statement_id"] = statement_id
        
        type_rows = db.execute(type_query, type_params).fetchall()
        by_match_type = {str(row[0]): int(row[1]) for row in type_rows}
        
        match_rate = (matched_lines / total_lines) if total_lines > 0 else 0.0
        
        return MatchingStatistics(
            total_lines=total_lines,
            matched_lines=matched_lines,
            unmatched_lines=unmatched_lines,
            auto_matched_lines=auto_matched,
            manual_matched_lines=manual_matched,
            match_rate=match_rate,
            average_confidence=avg_confidence,
            by_match_type=by_match_type
        )
        
    except Exception as e:
        logger.error(f"Error getting matching statistics: {e}")
        return MatchingStatistics(
            total_lines=0,
            matched_lines=0,
            unmatched_lines=0,
            auto_matched_lines=0,
            manual_matched_lines=0,
            match_rate=0.0,
            average_confidence=0.0,
            by_match_type={}
        )

