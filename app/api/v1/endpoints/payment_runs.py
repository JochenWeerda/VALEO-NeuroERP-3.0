"""
Payment Runs / SEPA API
FIBU-AP-04: Zahlungsläufe / SEPA
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

router = APIRouter(prefix="/payment-runs", tags=["finance", "ap", "sepa"])


class PaymentItem(BaseModel):
    """Single payment item in a payment run"""
    creditor_id: str = Field(..., description="Creditor ID")
    creditor_name: str = Field(..., description="Creditor name")
    iban: str = Field(..., description="Creditor IBAN")
    bic: Optional[str] = Field(None, description="Creditor BIC (optional for SEPA)")
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    purpose: str = Field(..., description="Payment purpose/reference")
    op_id: Optional[str] = Field(None, description="Open item ID to settle")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    discount_used: bool = Field(default=False, description="Cash discount used")
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Cash discount amount")
    end_to_end_id: Optional[str] = Field(None, description="End-to-end reference")


class PaymentRunCreate(BaseModel):
    """Schema for creating a payment run"""
    run_number: str = Field(..., min_length=1, max_length=50, description="Payment run number")
    execution_date: date = Field(..., description="Execution date")
    initiator_name: str = Field(..., min_length=1, description="Initiator name")
    initiator_iban: str = Field(..., description="Initiator IBAN")
    initiator_bic: str = Field(..., description="Initiator BIC")
    payments: List[PaymentItem] = Field(..., min_items=1, description="Payment items")
    notes: Optional[str] = Field(None, description="Notes")


class PaymentRunResponse(BaseModel):
    """Response schema for payment run"""
    id: str
    run_number: str
    execution_date: date
    initiator_name: str
    initiator_iban: str
    initiator_bic: str
    total_amount: Decimal
    payment_count: int
    status: str  # draft, approved, executed, cancelled, returned
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    executed_at: Optional[datetime]
    sepa_file_id: Optional[str]
    notes: Optional[str]
    payments: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ApprovePaymentRunRequest(BaseModel):
    """Request to approve a payment run"""
    approved_by: str = Field(..., description="User approving the run")


class ExecutePaymentRunRequest(BaseModel):
    """Request to execute a payment run"""
    executed_by: str = Field(..., description="User executing the run")


class ReturnPaymentRequest(BaseModel):
    """Request to process a returned payment"""
    payment_id: str = Field(..., description="Payment ID that was returned")
    return_reason: str = Field(..., description="Return reason code")
    return_date: date = Field(..., description="Return date")
    notes: Optional[str] = None


class SEPAXMLGenerator:
    """Generates SEPA pain.001.001.03 XML files"""
    
    NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
    
    def __init__(self, initiator_name: str, initiator_iban: str, initiator_bic: str):
        self.initiator_name = initiator_name
        self.initiator_iban = self._format_iban(initiator_iban)
        self.initiator_bic = initiator_bic
    
    def _format_iban(self, iban: str) -> str:
        """Remove spaces and convert to uppercase"""
        return iban.replace(" ", "").upper()
    
    def _format_bic(self, bic: str) -> str:
        """Format BIC"""
        return bic.replace(" ", "").upper() if bic else ""
    
    def _format_decimal(self, value: Decimal) -> str:
        """Format decimal for SEPA (2 decimal places)"""
        return f"{value:.2f}"
    
    def generate_credit_transfer(
        self,
        payments: List[PaymentItem],
        message_id: str = None,
        execution_date: date = None
    ) -> str:
        """
        Generate SEPA Credit Transfer XML (pain.001.001.03)
        """
        if message_id is None:
            message_id = f"MSG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        if execution_date is None:
            execution_date = date.today()
        
        # Register namespace
        ET.register_namespace('', self.NAMESPACE)
        
        # Root element
        root = ET.Element("Document", xmlns=self.NAMESPACE)
        
        # CstmrCdtTrfInitn (Customer Credit Transfer Initiation)
        cct_initn = ET.SubElement(root, "CstmrCdtTrfInitn")
        
        # Group Header
        grp_hdr = ET.SubElement(cct_initn, "GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = message_id
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()
        ET.SubElement(grp_hdr, "NbOfTxs").text = str(len(payments))
        
        # Calculate total amount
        total_amount = sum(payment.amount for payment in payments)
        ET.SubElement(grp_hdr, "CtrlSum").text = self._format_decimal(total_amount)
        
        # Initiating Party
        initg_pty = ET.SubElement(grp_hdr, "InitgPty")
        ET.SubElement(initg_pty, "Nm").text = self.initiator_name
        
        # Payment Information
        pmt_inf = ET.SubElement(cct_initn, "PmtInf")
        pmt_inf_id = f"PMT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        ET.SubElement(pmt_inf, "PmtInfId").text = pmt_inf_id
        ET.SubElement(pmt_inf, "PmtMtd").text = "TRF"  # Transfer
        ET.SubElement(pmt_inf, "BtchBookg").text = "false"
        ET.SubElement(pmt_inf, "NbOfTxs").text = str(len(payments))
        ET.SubElement(pmt_inf, "CtrlSum").text = self._format_decimal(total_amount)
        
        # Payment Type Information
        pmt_tp_inf = ET.SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = ET.SubElement(pmt_tp_inf, "SvcLvl")
        ET.SubElement(svc_lvl, "Cd").text = "SEPA"
        
        # Requested Execution Date
        reqd_exctn_dt = ET.SubElement(pmt_inf, "ReqdExctnDt")
        reqd_exctn_dt.text = execution_date.strftime("%Y-%m-%d")
        
        # Debtor (Initiator)
        dbtr = ET.SubElement(pmt_inf, "Dbtr")
        ET.SubElement(dbtr, "Nm").text = self.initiator_name
        
        # Debtor Account
        dbtr_acct = ET.SubElement(pmt_inf, "DbtrAcct")
        dbtr_acct_id = ET.SubElement(dbtr_acct, "Id")
        ET.SubElement(dbtr_acct_id, "IBAN").text = self.initiator_iban
        
        # Debtor Agent (Bank)
        dbtr_agt = ET.SubElement(pmt_inf, "DbtrAgt")
        fin_instn_id = ET.SubElement(dbtr_agt, "FinInstnId")
        ET.SubElement(fin_instn_id, "BIC").text = self.initiator_bic
        
        # Credit Transfer Transaction Information
        for idx, payment in enumerate(payments, start=1):
            cdt_trf_tx_inf = ET.SubElement(pmt_inf, "CdtTrfTxInf")
            
            # Payment Identification
            pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
            end_to_end_id = payment.end_to_end_id or f"E2E-{payment.invoice_number or payment.op_id or idx}"
            ET.SubElement(pmt_id, "EndToEndId").text = end_to_end_id
            
            # Amount
            amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
            instd_amt = ET.SubElement(amt, "InstdAmt", Ccy="EUR")
            instd_amt.text = self._format_decimal(payment.amount)
            
            # Creditor Agent (Bank) - optional for SEPA
            if payment.bic:
                cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
                fin_instn_id = ET.SubElement(cdtr_agt, "FinInstnId")
                ET.SubElement(fin_instn_id, "BIC").text = self._format_bic(payment.bic)
            
            # Creditor
            cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
            ET.SubElement(cdtr, "Nm").text = payment.creditor_name
            
            # Creditor Account
            cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
            cdtr_acct_id = ET.SubElement(cdtr_acct, "Id")
            ET.SubElement(cdtr_acct_id, "IBAN").text = self._format_iban(payment.iban)
            
            # Remittance Information
            rmt_inf = ET.SubElement(cdt_trf_tx_inf, "RmtInf")
            ET.SubElement(rmt_inf, "Ustrd").text = payment.purpose
        
        # Convert to string and prettify
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


@router.post("", response_model=PaymentRunResponse, status_code=201)
async def create_payment_run(
    payment_run: PaymentRunCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new payment run.
    """
    try:
        run_id = str(uuid.uuid4())
        
        total_amount = sum(payment.amount for payment in payment_run.payments)
        
        import json
        payments_json = json.dumps([p.dict() for p in payment_run.payments])
        
        insert_query = text("""
            INSERT INTO domain_erp.payment_runs
            (id, tenant_id, run_number, execution_date, initiator_name, initiator_iban, initiator_bic,
             total_amount, payment_count, status, notes, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :run_number, :execution_date, :initiator_name, :initiator_iban, :initiator_bic,
             :total_amount, :payment_count, :status, :notes, NOW(), NOW())
            RETURNING id, run_number, execution_date, initiator_name, initiator_iban, initiator_bic,
                      total_amount, payment_count, status, approved_at, approved_by, executed_at,
                      sepa_file_id, notes, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": run_id,
            "tenant_id": tenant_id,
            "run_number": payment_run.run_number,
            "execution_date": payment_run.execution_date,
            "initiator_name": payment_run.initiator_name,
            "initiator_iban": payment_run.initiator_iban,
            "initiator_bic": payment_run.initiator_bic,
            "total_amount": total_amount,
            "payment_count": len(payment_run.payments),
            "status": "draft",
            "notes": payment_run.notes
        }).fetchone()
        
        # Insert payment items
        for idx, payment in enumerate(payment_run.payments, start=1):
            payment_id = f"{run_id}-P{idx}"
            payment_insert = text("""
                INSERT INTO domain_erp.payment_run_items
                (id, tenant_id, payment_run_id, creditor_id, creditor_name, iban, bic, amount,
                 purpose, op_id, invoice_number, discount_used, discount_amount, end_to_end_id,
                 status, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :payment_run_id, :creditor_id, :creditor_name, :iban, :bic, :amount,
                 :purpose, :op_id, :invoice_number, :discount_used, :discount_amount, :end_to_end_id,
                 :status, NOW(), NOW())
            """)
            
            db.execute(payment_insert, {
                "id": payment_id,
                "tenant_id": tenant_id,
                "payment_run_id": run_id,
                "creditor_id": payment.creditor_id,
                "creditor_name": payment.creditor_name,
                "iban": payment.iban,
                "bic": payment.bic,
                "amount": payment.amount,
                "purpose": payment.purpose,
                "op_id": payment.op_id,
                "invoice_number": payment.invoice_number,
                "discount_used": payment.discount_used,
                "discount_amount": payment.discount_amount,
                "end_to_end_id": payment.end_to_end_id or f"E2E-{payment.invoice_number or payment.op_id or idx}",
                "status": "pending"
            })
        
        db.commit()
        
        # Get payments for response
        payments_query = text("""
            SELECT creditor_id, creditor_name, iban, bic, amount, purpose, op_id, invoice_number,
                   discount_used, discount_amount, end_to_end_id, status
            FROM domain_erp.payment_run_items
            WHERE payment_run_id = :payment_run_id
            ORDER BY created_at
        """)
        
        payments_rows = db.execute(payments_query, {"payment_run_id": run_id}).fetchall()
        
        payments = [
            {
                "creditor_id": str(row[0]),
                "creditor_name": str(row[1]),
                "iban": str(row[2]),
                "bic": str(row[3]) if row[3] else None,
                "amount": Decimal(str(row[4])),
                "purpose": str(row[5]),
                "op_id": str(row[6]) if row[6] else None,
                "invoice_number": str(row[7]) if row[7] else None,
                "discount_used": bool(row[8]),
                "discount_amount": Decimal(str(row[9])),
                "end_to_end_id": str(row[10]) if row[10] else None,
                "status": str(row[11])
            }
            for row in payments_rows
        ]
        
        return PaymentRunResponse(
            id=str(row[0]),
            run_number=str(row[1]),
            execution_date=row[2],
            initiator_name=str(row[3]),
            initiator_iban=str(row[4]),
            initiator_bic=str(row[5]),
            total_amount=Decimal(str(row[6])),
            payment_count=int(row[7]),
            status=str(row[8]),
            approved_at=row[9] if row[9] else None,
            approved_by=str(row[10]) if row[10] else None,
            executed_at=row[11] if row[11] else None,
            sepa_file_id=str(row[12]) if row[12] else None,
            notes=str(row[13]) if row[13] else None,
            payments=payments,
            created_at=row[14],
            updated_at=row[15]
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment run: {str(e)}")


@router.get("", response_model=List[PaymentRunResponse])
async def list_payment_runs(
    status: Optional[str] = Query(None, description="Filter by status"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all payment runs.
    """
    try:
        query = text("""
            SELECT id, run_number, execution_date, initiator_name, initiator_iban, initiator_bic,
                   total_amount, payment_count, status, approved_at, approved_by, executed_at,
                   sepa_file_id, notes, created_at, updated_at
            FROM domain_erp.payment_runs
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if status:
            query = text(str(query) + " AND status = :status")
            params["status"] = status
        
        query = text(str(query) + " ORDER BY created_at DESC")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            # Get payments for each run
            payments_query = text("""
                SELECT creditor_id, creditor_name, iban, bic, amount, purpose, op_id, invoice_number,
                       discount_used, discount_amount, end_to_end_id, status
                FROM domain_erp.payment_run_items
                WHERE payment_run_id = :payment_run_id
                ORDER BY created_at
            """)
            
            payments_rows = db.execute(payments_query, {"payment_run_id": str(row[0])}).fetchall()
            
            payments = [
                {
                    "creditor_id": str(p_row[0]),
                    "creditor_name": str(p_row[1]),
                    "iban": str(p_row[2]),
                    "bic": str(p_row[3]) if p_row[3] else None,
                    "amount": Decimal(str(p_row[4])),
                    "purpose": str(p_row[5]),
                    "op_id": str(p_row[6]) if p_row[6] else None,
                    "invoice_number": str(p_row[7]) if p_row[7] else None,
                    "discount_used": bool(p_row[8]),
                    "discount_amount": Decimal(str(p_row[9])),
                    "end_to_end_id": str(p_row[10]) if p_row[10] else None,
                    "status": str(p_row[11])
                }
                for p_row in payments_rows
            ]
            
            result.append(PaymentRunResponse(
                id=str(row[0]),
                run_number=str(row[1]),
                execution_date=row[2],
                initiator_name=str(row[3]),
                initiator_iban=str(row[4]),
                initiator_bic=str(row[5]),
                total_amount=Decimal(str(row[6])),
                payment_count=int(row[7]),
                status=str(row[8]),
                approved_at=row[9] if row[9] else None,
                approved_by=str(row[10]) if row[10] else None,
                executed_at=row[11] if row[11] else None,
                sepa_file_id=str(row[12]) if row[12] else None,
                notes=str(row[13]) if row[13] else None,
                payments=payments,
                created_at=row[14],
                updated_at=row[15]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing payment runs: {e}")
        return []


@router.get("/{run_id}", response_model=PaymentRunResponse)
async def get_payment_run(
    run_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get a single payment run by ID.
    """
    try:
        query = text("""
            SELECT id, run_number, execution_date, initiator_name, initiator_iban, initiator_bic,
                   total_amount, payment_count, status, approved_at, approved_by, executed_at,
                   sepa_file_id, notes, created_at, updated_at
            FROM domain_erp.payment_runs
            WHERE id = :run_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "run_id": run_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Payment run not found")
        
        # Get payments
        payments_query = text("""
            SELECT creditor_id, creditor_name, iban, bic, amount, purpose, op_id, invoice_number,
                   discount_used, discount_amount, end_to_end_id, status
            FROM domain_erp.payment_run_items
            WHERE payment_run_id = :payment_run_id
            ORDER BY created_at
        """)
        
        payments_rows = db.execute(payments_query, {"payment_run_id": run_id}).fetchall()
        
        payments = [
            {
                "creditor_id": str(p_row[0]),
                "creditor_name": str(p_row[1]),
                "iban": str(p_row[2]),
                "bic": str(p_row[3]) if p_row[3] else None,
                "amount": Decimal(str(p_row[4])),
                "purpose": str(p_row[5]),
                "op_id": str(p_row[6]) if p_row[6] else None,
                "invoice_number": str(p_row[7]) if p_row[7] else None,
                "discount_used": bool(p_row[8]),
                "discount_amount": Decimal(str(p_row[9])),
                "end_to_end_id": str(p_row[10]) if p_row[10] else None,
                "status": str(p_row[11])
            }
            for p_row in payments_rows
        ]
        
        return PaymentRunResponse(
            id=str(row[0]),
            run_number=str(row[1]),
            execution_date=row[2],
            initiator_name=str(row[3]),
            initiator_iban=str(row[4]),
            initiator_bic=str(row[5]),
            total_amount=Decimal(str(row[6])),
            payment_count=int(row[7]),
            status=str(row[8]),
            approved_at=row[9] if row[9] else None,
            approved_by=str(row[10]) if row[10] else None,
            executed_at=row[11] if row[11] else None,
            sepa_file_id=str(row[12]) if row[12] else None,
            notes=str(row[13]) if row[13] else None,
            payments=payments,
            created_at=row[14],
            updated_at=row[15]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get payment run: {str(e)}")


@router.post("/{run_id}/approve", response_model=PaymentRunResponse)
async def approve_payment_run(
    run_id: str,
    request: ApprovePaymentRunRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Approve a payment run.
    """
    try:
        update_query = text("""
            UPDATE domain_erp.payment_runs
            SET status = 'approved', approved_at = NOW(), approved_by = :approved_by, updated_at = NOW()
            WHERE id = :run_id AND tenant_id = :tenant_id AND status = 'draft'
            RETURNING id
        """)
        
        row = db.execute(update_query, {
            "run_id": run_id,
            "tenant_id": tenant_id,
            "approved_by": request.approved_by
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Payment run not found or cannot be approved")
        
        db.commit()
        
        return await get_payment_run(run_id, tenant_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving payment run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve payment run: {str(e)}")


@router.post("/{run_id}/execute", response_model=PaymentRunResponse)
async def execute_payment_run(
    run_id: str,
    request: ExecutePaymentRunRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Execute a payment run (generate SEPA XML and settle open items).
    """
    try:
        # Get payment run
        payment_run = await get_payment_run(run_id, tenant_id, db)
        
        if payment_run.status != "approved":
            raise HTTPException(status_code=400, detail="Payment run must be approved before execution")
        
        # Generate SEPA XML
        generator = SEPAXMLGenerator(
            initiator_name=payment_run.initiator_name,
            initiator_iban=payment_run.initiator_iban,
            initiator_bic=payment_run.initiator_bic
        )
        
        payment_items = [
            PaymentItem(**payment) for payment in payment_run.payments
        ]
        
        sepa_xml = generator.generate_credit_transfer(
            payments=payment_items,
            message_id=payment_run.run_number,
            execution_date=payment_run.execution_date
        )
        
        # Save SEPA file
        sepa_file_id = f"SEPA-{run_id}"
        
        # Update payment run status
        update_query = text("""
            UPDATE domain_erp.payment_runs
            SET status = 'executed', executed_at = NOW(), sepa_file_id = :sepa_file_id, updated_at = NOW()
            WHERE id = :run_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_query, {
            "run_id": run_id,
            "tenant_id": tenant_id,
            "sepa_file_id": sepa_file_id
        })
        
        # Update payment items status
        update_items_query = text("""
            UPDATE domain_erp.payment_run_items
            SET status = 'executed', updated_at = NOW()
            WHERE payment_run_id = :payment_run_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_items_query, {
            "payment_run_id": run_id,
            "tenant_id": tenant_id
        })
        
        # Settle open items
        for payment in payment_run.payments:
            if payment.get("op_id"):
                try:
                    # Settle open item
                    settle_query = text("""
                        UPDATE domain_erp.offene_posten
                        SET offen = offen - :amount, updated_at = NOW()
                        WHERE id = :op_id AND tenant_id = :tenant_id
                    """)
                    
                    db.execute(settle_query, {
                        "op_id": payment["op_id"],
                        "tenant_id": tenant_id,
                        "amount": payment["amount"]
                    })
                    
                    # If fully settled, mark as closed
                    check_query = text("""
                        UPDATE domain_erp.offene_posten
                        SET offen = 0, updated_at = NOW()
                        WHERE id = :op_id AND tenant_id = :tenant_id AND offen <= 0
                    """)
                    
                    db.execute(check_query, {
                        "op_id": payment["op_id"],
                        "tenant_id": tenant_id
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not settle open item {payment.get('op_id')}: {e}")
        
        db.commit()
        
        return await get_payment_run(run_id, tenant_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error executing payment run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute payment run: {str(e)}")


@router.get("/{run_id}/sepa-xml")
async def get_sepa_xml(
    run_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get SEPA XML file for a payment run.
    """
    try:
        payment_run = await get_payment_run(run_id, tenant_id, db)
        
        if payment_run.status != "executed":
            raise HTTPException(status_code=400, detail="Payment run must be executed to generate SEPA XML")
        
        # Generate SEPA XML
        generator = SEPAXMLGenerator(
            initiator_name=payment_run.initiator_name,
            initiator_iban=payment_run.initiator_iban,
            initiator_bic=payment_run.initiator_bic
        )
        
        payment_items = [
            PaymentItem(**payment) for payment in payment_run.payments
        ]
        
        sepa_xml = generator.generate_credit_transfer(
            payments=payment_items,
            message_id=payment_run.run_number,
            execution_date=payment_run.execution_date
        )
        
        return Response(
            content=sepa_xml,
            media_type="application/xml",
            headers={
                "Content-Disposition": f'attachment; filename="SEPA_{payment_run.run_number}.xml"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SEPA XML: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate SEPA XML: {str(e)}")


@router.post("/{run_id}/return-payment")
async def return_payment(
    run_id: str,
    request: ReturnPaymentRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Process a returned payment (Rückläufer).
    """
    try:
        # Find payment item
        payment_query = text("""
            SELECT id, payment_run_id, op_id, amount, creditor_id
            FROM domain_erp.payment_run_items
            WHERE id = :payment_id AND tenant_id = :tenant_id
        """)
        
        payment_row = db.execute(payment_query, {
            "payment_id": request.payment_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not payment_row:
            raise HTTPException(status_code=404, detail="Payment item not found")
        
        payment_item_id = str(payment_row[0])
        payment_run_id = str(payment_row[1])
        op_id = str(payment_row[2]) if payment_row[2] else None
        amount = Decimal(str(payment_row[4]))
        
        # Update payment item status
        update_payment_query = text("""
            UPDATE domain_erp.payment_run_items
            SET status = 'returned', updated_at = NOW()
            WHERE id = :payment_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_payment_query, {
            "payment_id": request.payment_id,
            "tenant_id": tenant_id
        })
        
        # Reopen open item if it was settled
        if op_id:
            reopen_query = text("""
                UPDATE domain_erp.offene_posten
                SET offen = offen + :amount, updated_at = NOW()
                WHERE id = :op_id AND tenant_id = :tenant_id
            """)
            
            db.execute(reopen_query, {
                "op_id": op_id,
                "tenant_id": tenant_id,
                "amount": amount
            })
        
        # Create return record
        return_id = str(uuid.uuid4())
        return_insert = text("""
            INSERT INTO domain_erp.payment_returns
            (id, tenant_id, payment_run_id, payment_item_id, return_reason, return_date, notes, created_at)
            VALUES
            (:id, :tenant_id, :payment_run_id, :payment_item_id, :return_reason, :return_date, :notes, NOW())
        """)
        
        db.execute(return_insert, {
            "id": return_id,
            "tenant_id": tenant_id,
            "payment_run_id": payment_run_id,
            "payment_item_id": payment_item_id,
            "return_reason": request.return_reason,
            "return_date": request.return_date,
            "notes": request.notes
        })
        
        db.commit()
        
        return {
            "status": "ok",
            "message": "Payment return processed",
            "return_id": return_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing payment return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process payment return: {str(e)}")

