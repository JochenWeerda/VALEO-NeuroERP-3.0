"""SEPA pain.001.001.03 — XML einer Ueberweisungs-Sammeldatei fuer Zahlungslaeufe.

Aus ``app/api/v1/endpoints/payment_runs.py`` ausgelagert (Godfile-Ratsche, CI-GRUEN 14.10.2026); unveraendert.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List
from xml.dom import minidom

from app.core.business_time import business_today

if TYPE_CHECKING:  # nur fuer die Annotation; der Router importiert dieses Modul
    from app.api.v1.endpoints.payment_runs import PaymentItem


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
            execution_date = business_today()

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
