"""
VAT Return Export API
FIBU-TAX-02: USt-Voranmeldung Export
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging
from app.core.uuid7 import uuid7
from app.core.explainability import ExplainabilityView
from app.core.policy_decisions import PolicyOverrideResolution
from app.core.tenant import get_tenant_id

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vat-return", tags=["finance", "tax", "vat"])


class VATReturnPosition(BaseModel):
    """Single position in VAT return"""
    position_code: str = Field(..., description="UStVA position code (e.g., 66, 81, 35)")
    description: str = Field(..., description="Position description")
    net_amount: Decimal = Field(..., ge=0, description="Net amount")
    tax_amount: Decimal = Field(..., ge=0, description="Tax amount")
    tax_rate: Decimal = Field(..., ge=0, le=100, description="Tax rate in percent")


class VATReturnCreate(BaseModel):
    """Schema for creating a VAT return"""
    period: str = Field(..., description="Period in YYYY-MM format")
    return_type: str = Field(default="monthly", description="monthly or quarterly")
    taxpayer_name: str = Field(..., description="Taxpayer name")
    tax_id: Optional[str] = Field(None, description="Tax ID (Steuernummer)")
    vat_id: Optional[str] = Field(None, description="VAT ID (USt-IdNr)")
    positions: List[VATReturnPosition] = Field(..., min_length=1, description="VAT return positions")
    notes: Optional[str] = None


class VATReturnResponse(BaseModel):
    """Response schema for VAT return"""
    id: str
    period: str
    return_type: str
    taxpayer_name: str
    tax_id: Optional[str]
    vat_id: Optional[str]
    total_sales_net: Decimal
    total_input_tax: Decimal
    total_output_tax: Decimal
    vat_payable: Decimal
    positions: List[Dict[str, Any]]
    status: str  # draft, calculated, validated, submitted
    calculated_at: Optional[datetime]
    validated_at: Optional[datetime]
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    submitted_at: Optional[datetime]
    elster_reference: Optional[str] = None
    approval_status: str | None = None
    approval_can_submit: bool = False
    approval_override_resolution: PolicyOverrideResolution | None = None
    approval_explainability: ExplainabilityView | None = None
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VATReturnCalculationRequest(BaseModel):
    """Request to calculate VAT return from journal entries"""
    period: str = Field(..., description="Period in YYYY-MM format")
    tenant_id: Optional[str] = Field(default=None)


class ELSTERExportRequest(BaseModel):
    """Request to export VAT return as ELSTER XML"""
    return_id: str = Field(..., description="VAT return ID")
    export_format: str = Field(default="elster_xml", description="Export format: elster_xml, csv, pdf")


class VATReturnApprovalRequest(BaseModel):
    approved_by: str = Field(..., min_length=1)


class VATReturnSubmitRequest(BaseModel):
    submitted_by: str = Field(..., min_length=1)


def _build_vat_return_response(row, *, positions_data: list[dict[str, Any]]) -> VATReturnResponse:
    status = str(row[11])
    approved_at = row[14] if len(row) > 14 and isinstance(row[14], datetime) and status == "approved" else None
    approved_by = str(row[15]) if len(row) > 15 and row[15] and status == "approved" else None
    submitted_at = row[14] if len(row) > 14 and isinstance(row[14], datetime) and status == "submitted" else None
    elster_reference = str(row[15]) if len(row) > 15 and row[15] and status == "submitted" else None
    notes = str(row[15]) if len(row) > 15 and row[15] is not None and not isinstance(row[15], datetime) else None
    created_at = row[16] if len(row) > 16 else row[-2]
    updated_at = row[17] if len(row) > 17 else row[-1]
    can_submit = status in {"approved", "submitted"}

    return VATReturnResponse(
        id=str(row[0]),
        period=str(row[1]),
        return_type=str(row[2]),
        taxpayer_name=str(row[3]),
        tax_id=str(row[4]) if row[4] else None,
        vat_id=str(row[5]) if row[5] else None,
        total_sales_net=Decimal(str(row[6])),
        total_input_tax=Decimal(str(row[7])),
        total_output_tax=Decimal(str(row[8])),
        vat_payable=Decimal(str(row[9])),
        positions=positions_data,
        status=status,
        calculated_at=row[12] if row[12] else None,
        validated_at=row[13] if row[13] else None,
        approved_at=approved_at,
        approved_by=approved_by,
        submitted_at=submitted_at,
        elster_reference=elster_reference,
        approval_status=status,
        approval_can_submit=can_submit,
        approval_override_resolution=PolicyOverrideResolution(
            rule_id="finance.vat_return.submission",
            effective_scope="global",
            effective_scope_key="vat-return",
            effective_enabled=True,
            effective_params={"status": status},
            applied_reason="UStVA-Freigabe für Einreichung.",
            applied_source="vat-return-export",
        ),
        approval_explainability=ExplainabilityView(
            status="allowed" if can_submit else "approval-required",
            summary="USt-Voranmeldung kann eingereicht werden." if can_submit else "USt-Voranmeldung benötigt Freigabe.",
            rule_id="finance.vat_return.submission",
            source_scope="global",
        ),
        notes=notes,
        created_at=created_at,
        updated_at=updated_at,
    )


def _resolve_vat_request_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="VAT return request belongs to a different tenant")
    return tenant_id


class VATReturnVorberechnung(BaseModel):
    """Pre-calculation result (not persisted)"""
    zeitraum: str
    umsatz_netto: float = Field(0, description="Netto-Umsatz")
    umsatzsteuer: float = Field(0, description="Umsatzsteuer (19%)")
    vorsteuer: float = Field(0, description="Abziehbare Vorsteuer")
    zahllast: float = Field(0, description="Verbleibende USt-Zahllast")
    positionen: List[Dict[str, Any]] = Field(default_factory=list)


@router.get("/vorberechnung", response_model=VATReturnVorberechnung)
async def vorberechnung_ustva(
    zeitraum: str = Query(..., description="Zeitraum im Format YYYY-MM oder YYYY-QN"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Vorberechnung der UStVA aus gebuchten Journaleinträgen.
    Gibt aggregierte Beträge zurück, ohne einen VAT-Return anzulegen.
    """
    try:
        # Normalise quarterly periods to month range
        if "-Q" in zeitraum:
            quarter_map = {
                "Q1": ("01", "03"),
                "Q2": ("04", "06"),
                "Q3": ("07", "09"),
                "Q4": ("10", "12"),
            }
            year, q = zeitraum.split("-")
            start_month, end_month = quarter_map.get(q, ("01", "03"))
            periods = [f"{year}-{str(m).zfill(2)}" for m in range(int(start_month), int(end_month) + 1)]
        else:
            periods = [zeitraum]

        total_sales_net = Decimal("0.00")
        total_output_tax = Decimal("0.00")
        total_input_tax = Decimal("0.00")

        for period in periods:
            journal_query = text("""
                SELECT jel.account_id, jel.debit, jel.credit, jel.tax_code
                FROM domain_erp.journal_entry_lines jel
                JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
                WHERE je.tenant_id = :tenant_id
                AND je.period = :period
                AND je.status = 'posted'
                AND jel.tax_code IS NOT NULL
            """)

            rows = db.execute(journal_query, {
                "tenant_id": tenant_id,
                "period": period,
            }).fetchall()

            for row in rows:
                account_id = str(row[0])
                debit = Decimal(str(row[1]))
                credit = Decimal(str(row[2]))

                is_sales = account_id.startswith("8") or account_id.startswith("4")
                is_purchase = account_id.startswith("6") or account_id.startswith("5")

                if is_sales:
                    amount = credit if credit > 0 else debit
                    net = amount / Decimal("1.19")
                    tax = amount - net
                    total_sales_net += net
                    total_output_tax += tax
                elif is_purchase:
                    amount = debit if debit > 0 else credit
                    net = amount / Decimal("1.19")
                    tax = amount - net
                    total_input_tax += tax

        zahllast = total_output_tax - total_input_tax

        return VATReturnVorberechnung(
            zeitraum=zeitraum,
            umsatz_netto=float(total_sales_net.quantize(Decimal("0.01"))),
            umsatzsteuer=float(total_output_tax.quantize(Decimal("0.01"))),
            vorsteuer=float(total_input_tax.quantize(Decimal("0.01"))),
            zahllast=float(zahllast.quantize(Decimal("0.01"))),
            positionen=[],
        )

    except Exception as e:
        logger.error(f"UStVA Vorberechnung fehlgeschlagen: {e}")
        # Return zeros on error so the form is still usable
        return VATReturnVorberechnung(
            zeitraum=zeitraum,
            umsatz_netto=0,
            umsatzsteuer=0,
            vorsteuer=0,
            zahllast=0,
            positionen=[],
        )


@router.post("/calculate", response_model=VATReturnResponse)
async def calculate_vat_return(
    request: VATReturnCalculationRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Calculate VAT return from journal entries for a period.
    """
    try:
        effective_tenant_id = _resolve_vat_request_tenant(request.tenant_id, tenant_id)
        # Get journal entries for period
        _period_start = f"{request.period}-01"  # noqa: F841
        _period_end = f"{request.period}-31"  # noqa: F841
        
        # Get tax keys with UStVA positions
        tax_keys_query = text("""
            SELECT code, steuersatz, ustva_position, ustva_bezeichnung
            FROM domain_erp.tax_keys
            WHERE tenant_id = :tenant_id AND active = true
        """)
        
        tax_keys_rows = db.execute(tax_keys_query, {
            "tenant_id": effective_tenant_id
        }).fetchall()
        
        # Build tax key lookup
        tax_key_map = {}
        for row in tax_keys_rows:
            code = str(row[0])
            rate = Decimal(str(row[1]))
            ustva_pos = str(row[2]) if row[2] else ""
            ustva_desc = str(row[3]) if row[3] else ""
            tax_key_map[code] = {
                "rate": rate,
                "ustva_position": ustva_pos,
                "ustva_description": ustva_desc
            }
        
        # Get journal entry lines with tax codes
        journal_query = text("""
            SELECT jel.account_id, jel.debit, jel.credit, jel.tax_code,
                   jel.description, jel.reference, je.entry_date, je.document_type
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE je.tenant_id = :tenant_id
            AND je.period = :period
            AND je.status = 'posted'
            AND jel.tax_code IS NOT NULL
            ORDER BY je.entry_date, jel.line_number
        """)
        
        journal_rows = db.execute(journal_query, {
            "tenant_id": effective_tenant_id,
            "period": request.period
        }).fetchall()
        
        # Aggregate by UStVA position
        position_totals = {}
        
        for row in journal_rows:
            account_id = str(row[0])
            debit = Decimal(str(row[1]))
            credit = Decimal(str(row[2]))
            tax_code = str(row[3]) if row[3] else ""
            
            # Determine if this is sales (output tax) or purchase (input tax)
            # Typically: debit on expense accounts = input tax, credit on revenue accounts = output tax
            # For simplicity, we'll use account ranges (this should be configurable)
            is_sales = account_id.startswith("8") or account_id.startswith("4")  # Revenue accounts
            is_purchase = account_id.startswith("6") or account_id.startswith("5")  # Expense accounts
            
            if tax_code and tax_code in tax_key_map:
                tax_key = tax_key_map[tax_code]
                ustva_pos = tax_key["ustva_position"]
                
                if not ustva_pos:
                    continue
                
                if ustva_pos not in position_totals:
                    position_totals[ustva_pos] = {
                        "position_code": ustva_pos,
                        "description": tax_key["ustva_description"],
                        "net_amount": Decimal("0.00"),
                        "tax_amount": Decimal("0.00"),
                        "tax_rate": tax_key["rate"],
                        "sales_net": Decimal("0.00"),
                        "sales_tax": Decimal("0.00"),
                        "purchase_net": Decimal("0.00"),
                        "purchase_tax": Decimal("0.00")
                    }
                
                # Calculate net and tax amounts
                if is_sales:
                    # Output tax (Umsatzsteuer)
                    amount = credit if credit > 0 else debit
                    net_amount = amount / (Decimal("1") + tax_key["rate"] / Decimal("100"))
                    tax_amount = amount - net_amount
                    
                    position_totals[ustva_pos]["sales_net"] += net_amount
                    position_totals[ustva_pos]["sales_tax"] += tax_amount
                elif is_purchase:
                    # Input tax (Vorsteuer)
                    amount = debit if debit > 0 else credit
                    net_amount = amount / (Decimal("1") + tax_key["rate"] / Decimal("100"))
                    tax_amount = amount - net_amount
                    
                    position_totals[ustva_pos]["purchase_net"] += net_amount
                    position_totals[ustva_pos]["purchase_tax"] += tax_amount
                
                position_totals[ustva_pos]["net_amount"] += net_amount
                position_totals[ustva_pos]["tax_amount"] += tax_amount
        
        # Convert to positions list
        positions = []
        for pos_code, totals in position_totals.items():
            positions.append(VATReturnPosition(
                position_code=pos_code,
                description=totals["description"],
                net_amount=totals["net_amount"],
                tax_amount=totals["tax_amount"],
                tax_rate=totals["tax_rate"]
            ))
        
        # Calculate totals
        total_sales_net = sum(p["sales_net"] for p in position_totals.values())
        _total_purchase_net = sum(p["purchase_net"] for p in position_totals.values())  # noqa: F841
        total_output_tax = sum(p["sales_tax"] for p in position_totals.values())
        total_input_tax = sum(p["purchase_tax"] for p in position_totals.values())
        vat_payable = total_output_tax - total_input_tax
        
        # Create VAT return
        return_id = uuid7()
        
        import json
        positions_json = json.dumps([p.model_dump() for p in positions])
        
        insert_query = text("""
            INSERT INTO domain_erp.vat_returns
            (id, tenant_id, period, return_type, taxpayer_name, tax_id, vat_id,
             total_sales_net, total_input_tax, total_output_tax, vat_payable,
             positions, status, calculated_at, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :period, :return_type, :taxpayer_name, :tax_id, :vat_id,
             :total_sales_net, :total_input_tax, :total_output_tax, :vat_payable,
             :positions, :status, NOW(), NOW(), NOW())
            RETURNING id, period, return_type, taxpayer_name, tax_id, vat_id,
                      total_sales_net, total_input_tax, total_output_tax, vat_payable,
                      positions, status, calculated_at, validated_at, submitted_at,
                      notes, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": return_id,
            "tenant_id": effective_tenant_id,
            "period": request.period,
            "return_type": "monthly",
            "taxpayer_name": "Company Name",  # Should come from company master data
            "tax_id": None,
            "vat_id": None,
            "total_sales_net": total_sales_net,
            "total_input_tax": total_input_tax,
            "total_output_tax": total_output_tax,
            "vat_payable": vat_payable,
            "positions": positions_json,
            "status": "calculated"
        }).fetchone()
        
        db.commit()
        
        import json
        positions_data = json.loads(row[11]) if row[11] else []
        
        return _build_vat_return_response(row, positions_data=positions_data)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error calculating VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate VAT return: {str(e)}")


@router.get("/{return_id}", response_model=VATReturnResponse)
async def get_vat_return(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get a VAT return by ID.
    """
    try:
        query = text("""
            SELECT id, period, return_type, taxpayer_name, tax_id, vat_id,
                   total_sales_net, total_input_tax, total_output_tax, vat_payable,
                   positions, status, calculated_at, validated_at, submitted_at,
                   notes, created_at, updated_at
            FROM domain_erp.vat_returns
            WHERE id = :return_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "return_id": return_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="VAT return not found")
        
        import json
        positions_data = json.loads(row[10]) if row[10] else []
        
        return _build_vat_return_response(row, positions_data=positions_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get VAT return: {str(e)}")


@router.get("/export/{return_id}")
async def export_vat_return_download(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Download VAT return export (ELSTER XML). Alias for /{return_id}/elster-xml.
    """
    return await export_elster_xml(return_id, tenant_id, db)


@router.get("/{return_id}/elster-xml")
async def export_elster_xml(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Export VAT return as ELSTER XML (Anmeldungssteuern, UStVA).
    Format nach offiziellem ERiC-Schema, Encoding ISO-8859-15.
    Referenz: https://www.elster.de, JuryOberst/Elster (GitHub).
    """
    try:
        from app.elster import build_ustva_elster_xml

        vat_return = await get_vat_return(return_id, tenant_id, db)

        xml_bytes = build_ustva_elster_xml(
            period=vat_return.period,
            taxpayer_name=vat_return.taxpayer_name,
            tax_id=vat_return.tax_id,
            vat_id=vat_return.vat_id,
            positions=vat_return.positions,
            total_sales_net=vat_return.total_sales_net,
            total_input_tax=vat_return.total_input_tax,
            total_output_tax=vat_return.total_output_tax,
            vat_payable=vat_return.vat_payable,
        )

        return Response(
            content=xml_bytes,
            media_type="application/xml; charset=ISO-8859-15",
            headers={
                "Content-Disposition": f'attachment; filename="UStVA_{vat_return.period}_ELSTER.xml"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting ELSTER XML: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export ELSTER XML: {str(e)}")


@router.post("/{return_id}/validate")
async def validate_vat_return(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Validate VAT return against GL totals.
    """
    try:
        vat_return = await get_vat_return(return_id, tenant_id, db)
        
        # Recalculate from GL to validate
        period = vat_return.period
        
        # Get GL totals for period
        gl_query = text("""
            SELECT 
                SUM(CASE WHEN jel.tax_code IS NOT NULL AND je.document_type LIKE 'AR%' 
                    THEN jel.credit ELSE 0 END) as sales_total,
                SUM(CASE WHEN jel.tax_code IS NOT NULL AND je.document_type LIKE 'AP%' 
                    THEN jel.debit ELSE 0 END) as purchase_total
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE je.tenant_id = :tenant_id
            AND je.period = :period
            AND je.status = 'posted'
        """)
        
        gl_row = db.execute(gl_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchone()
        
        gl_sales = Decimal(str(gl_row[0])) if gl_row[0] else Decimal("0.00")
        gl_purchases = Decimal(str(gl_row[1])) if gl_row[1] else Decimal("0.00")
        
        # Compare with VAT return
        differences = []
        
        sales_diff = abs(vat_return.total_sales_net - gl_sales)
        if sales_diff > Decimal("0.01"):
            differences.append({
                "field": "total_sales_net",
                "vat_return": float(vat_return.total_sales_net),
                "gl_total": float(gl_sales),
                "difference": float(sales_diff)
            })
        
        purchases_diff = abs(vat_return.total_input_tax - gl_purchases)
        if purchases_diff > Decimal("0.01"):
            differences.append({
                "field": "total_input_tax",
                "vat_return": float(vat_return.total_input_tax),
                "gl_total": float(gl_purchases),
                "difference": float(purchases_diff)
            })
        
        is_valid = len(differences) == 0
        
        # Update validation status
        if is_valid:
            update_query = text("""
                UPDATE domain_erp.vat_returns
                SET status = 'validated', validated_at = NOW(), updated_at = NOW()
                WHERE id = :return_id AND tenant_id = :tenant_id
            """)
            
            db.execute(update_query, {
                "return_id": return_id,
                "tenant_id": tenant_id
            })
            db.commit()
        
        return {
            "valid": is_valid,
            "differences": differences,
            "message": "VAT return validated successfully" if is_valid else "Differences found between VAT return and GL"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error validating VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate VAT return: {str(e)}")


@router.get("", response_model=List[VATReturnResponse])
async def list_vat_returns(
    period: Optional[str] = Query(None, description="Filter by period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    List all VAT returns.
    """
    try:
        query = text("""
            SELECT id, period, return_type, taxpayer_name, tax_id, vat_id,
                   total_sales_net, total_input_tax, total_output_tax, vat_payable,
                   positions, status, calculated_at, validated_at, submitted_at,
                   notes, created_at, updated_at
            FROM domain_erp.vat_returns
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if period:
            query = text(str(query) + " AND period = :period")
            params["period"] = period
        
        query = text(str(query) + " ORDER BY period DESC, created_at DESC")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            positions_data = json.loads(row[10]) if row[10] else []
            
            result.append(_build_vat_return_response(row, positions_data=positions_data))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing VAT returns: {e}")
        return []


@router.post("/{return_id}/approve", response_model=VATReturnResponse)
async def approve_vat_return(
    return_id: str,
    request: VATReturnApprovalRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    vat_return = await get_vat_return(return_id, tenant_id, db)
    if vat_return.status != "validated":
        raise HTTPException(status_code=400, detail="VAT return must be validated before approval")

    try:
        db.execute(
            text(
                """
                UPDATE domain_erp.vat_returns
                SET status = 'approved', updated_at = NOW()
                WHERE id = :return_id AND tenant_id = :tenant_id
                """
            ),
            {"return_id": return_id, "tenant_id": tenant_id},
        )
        db.commit()
        refreshed = await get_vat_return(return_id, tenant_id, db)
        return refreshed.model_copy(
            update={
                "status": "approved",
                "approved_at": datetime.utcnow(),
                "approved_by": request.approved_by,
                "approval_status": "approved",
                "approval_can_submit": True,
                "approval_explainability": ExplainabilityView(status="allowed", summary="ready"),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve VAT return: {str(e)}")


@router.post("/{return_id}/submit", response_model=VATReturnResponse)
async def submit_vat_return(
    return_id: str,
    request: VATReturnSubmitRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    vat_return = await get_vat_return(return_id, tenant_id, db)
    if vat_return.status != "approved":
        raise HTTPException(status_code=400, detail="VAT return must be approved before submission")

    elster_reference = f"ELSTER-{vat_return.period}-{return_id}"
    try:
        db.execute(
            text(
                """
                UPDATE domain_erp.vat_returns
                SET status = 'submitted', updated_at = NOW()
                WHERE id = :return_id AND tenant_id = :tenant_id
                """
            ),
            {"return_id": return_id, "tenant_id": tenant_id},
        )
        db.commit()
        refreshed = await get_vat_return(return_id, tenant_id, db)
        return refreshed.model_copy(
            update={
                "status": "submitted",
                "submitted_at": datetime.utcnow(),
                "elster_reference": elster_reference,
                "approval_status": "submitted",
                "approval_can_submit": True,
                "approval_explainability": ExplainabilityView(status="allowed", summary="ready"),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit VAT return: {str(e)}")

