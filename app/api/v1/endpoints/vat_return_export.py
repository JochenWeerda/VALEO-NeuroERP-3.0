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
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

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
    positions: List[VATReturnPosition] = Field(..., min_items=1, description="VAT return positions")
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
    submitted_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VATReturnCalculationRequest(BaseModel):
    """Request to calculate VAT return from journal entries"""
    period: str = Field(..., description="Period in YYYY-MM format")
    tenant_id: str = Field(default="system")


class ELSTERExportRequest(BaseModel):
    """Request to export VAT return as ELSTER XML"""
    return_id: str = Field(..., description="VAT return ID")
    export_format: str = Field(default="elster_xml", description="Export format: elster_xml, csv, pdf")


@router.post("/calculate", response_model=VATReturnResponse)
async def calculate_vat_return(
    request: VATReturnCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate VAT return from journal entries for a period.
    """
    try:
        # Get journal entries for period
        period_start = f"{request.period}-01"
        period_end = f"{request.period}-31"
        
        # Get tax keys with UStVA positions
        tax_keys_query = text("""
            SELECT code, steuersatz, ustva_position, ustva_bezeichnung
            FROM domain_erp.tax_keys
            WHERE tenant_id = :tenant_id AND active = true
        """)
        
        tax_keys_rows = db.execute(tax_keys_query, {
            "tenant_id": request.tenant_id
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
            SELECT jel.account_id, jel.debit_amount, jel.credit_amount, jel.tax_code,
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
            "tenant_id": request.tenant_id,
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
        total_purchase_net = sum(p["purchase_net"] for p in position_totals.values())
        total_output_tax = sum(p["sales_tax"] for p in position_totals.values())
        total_input_tax = sum(p["purchase_tax"] for p in position_totals.values())
        vat_payable = total_output_tax - total_input_tax
        
        # Create VAT return
        return_id = str(uuid.uuid4())
        
        import json
        positions_json = json.dumps([p.dict() for p in positions])
        
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
            "tenant_id": request.tenant_id,
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
            status=str(row[12]),
            calculated_at=row[13] if row[13] else None,
            validated_at=row[14] if row[14] else None,
            submitted_at=row[15] if row[15] else None,
            notes=str(row[16]) if row[16] else None,
            created_at=row[17],
            updated_at=row[18]
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error calculating VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate VAT return: {str(e)}")


@router.get("/{return_id}", response_model=VATReturnResponse)
async def get_vat_return(
    return_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
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
            status=str(row[11]),
            calculated_at=row[12] if row[12] else None,
            validated_at=row[13] if row[13] else None,
            submitted_at=row[14] if row[14] else None,
            notes=str(row[15]) if row[15] else None,
            created_at=row[16],
            updated_at=row[17]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting VAT return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get VAT return: {str(e)}")


@router.get("/{return_id}/elster-xml")
async def export_elster_xml(
    return_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Export VAT return as ELSTER XML format.
    """
    try:
        vat_return = await get_vat_return(return_id, tenant_id, db)
        
        # Generate ELSTER XML (simplified format - actual ELSTER format is more complex)
        # This is a basic structure that can be extended
        ET.register_namespace('', 'http://www.elster.de/2002/XML-Schema')
        
        root = ET.Element("Elster", xmlns="http://www.elster.de/2002/XML-Schema")
        
        # Header
        header = ET.SubElement(root, "Header")
        ET.SubElement(header, "Version").text = "1.0"
        ET.SubElement(header, "CreatedAt").text = datetime.now().isoformat()
        
        # VAT Return Data
        vat_data = ET.SubElement(root, "VATReturn")
        ET.SubElement(vat_data, "Period").text = vat_return.period
        ET.SubElement(vat_data, "ReturnType").text = vat_return.return_type
        ET.SubElement(vat_data, "TaxpayerName").text = vat_return.taxpayer_name
        
        if vat_return.tax_id:
            ET.SubElement(vat_data, "TaxID").text = vat_return.tax_id
        if vat_return.vat_id:
            ET.SubElement(vat_data, "VATID").text = vat_return.vat_id
        
        # Summary
        summary = ET.SubElement(vat_data, "Summary")
        ET.SubElement(summary, "TotalSalesNet").text = str(vat_return.total_sales_net)
        ET.SubElement(summary, "TotalInputTax").text = str(vat_return.total_input_tax)
        ET.SubElement(summary, "TotalOutputTax").text = str(vat_return.total_output_tax)
        ET.SubElement(summary, "VATPayable").text = str(vat_return.vat_payable)
        
        # Positions
        positions_elem = ET.SubElement(vat_data, "Positions")
        for pos in vat_return.positions:
            pos_elem = ET.SubElement(positions_elem, "Position")
            ET.SubElement(pos_elem, "Code").text = str(pos.get("position_code", ""))
            ET.SubElement(pos_elem, "Description").text = str(pos.get("description", ""))
            ET.SubElement(pos_elem, "NetAmount").text = str(pos.get("net_amount", "0.00"))
            ET.SubElement(pos_elem, "TaxAmount").text = str(pos.get("tax_amount", "0.00"))
            ET.SubElement(pos_elem, "TaxRate").text = str(pos.get("tax_rate", "0.00"))
        
        # Convert to string
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_content = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
        
        return Response(
            content=xml_content,
            media_type="application/xml",
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
    tenant_id: str = Query("system", description="Tenant ID"),
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
                    THEN jel.credit_amount ELSE 0 END) as sales_total,
                SUM(CASE WHEN jel.tax_code IS NOT NULL AND je.document_type LIKE 'AP%' 
                    THEN jel.debit_amount ELSE 0 END) as purchase_total
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
    tenant_id: str = Query("system", description="Tenant ID"),
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
            
            result.append(VATReturnResponse(
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
                status=str(row[11]),
                calculated_at=row[12] if row[12] else None,
                validated_at=row[13] if row[13] else None,
                submitted_at=row[14] if row[14] else None,
                notes=str(row[15]) if row[15] else None,
                created_at=row[16],
                updated_at=row[17]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing VAT returns: {e}")
        return []

