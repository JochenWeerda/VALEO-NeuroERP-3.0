"""
VALEO-NeuroERP - SEPA XML Export
Generiert SEPA-Überweisungen und Lastschriften im XML-Format
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom


class SEPAExporter:
    """SEPA XML Generator (pain.001.001.03 für Überweisungen)"""
    
    # Namespaces
    NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
    
    def __init__(self, initiator_name: str, initiator_iban: str, initiator_bic: str):
        """
        Args:
            initiator_name: Name des Auftraggebers
            initiator_iban: IBAN des Auftraggebers
            initiator_bic: BIC des Auftraggebers
        """
        self.initiator_name = initiator_name
        self.initiator_iban = self._format_iban(initiator_iban)
        self.initiator_bic = initiator_bic
    
    def _format_iban(self, iban: str) -> str:
        """Entfernt Leerzeichen aus IBAN"""
        return iban.replace(" ", "").upper()
    
    def _format_bic(self, bic: str) -> str:
        """Formatiert BIC"""
        return bic.replace(" ", "").upper()
    
    def _format_decimal(self, value: Decimal) -> str:
        """Formatiert Dezimalzahl für SEPA (2 Nachkommastellen)"""
        return f"{value:.2f}"
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Formatiert XML mit Einrückungen"""
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    def create_credit_transfer(
        self,
        transactions: List[Dict[str, Any]],
        message_id: str = None,
        execution_date: date = None
    ) -> str:
        """
        Erstellt SEPA-Überweisung (pain.001.001.03)
        
        Args:
            transactions: Liste von Transaktionen mit:
                - recipient_name: Empfängername
                - recipient_iban: Empfänger-IBAN
                - recipient_bic: Empfänger-BIC (optional bei SEPA)
                - amount: Betrag
                - reference: Verwendungszweck
                - end_to_end_id: End-to-End ID (optional)
            message_id: Nachrichten-ID (optional, wird generiert)
            execution_date: Ausführungsdatum (optional, default = heute)
        
        Returns:
            SEPA XML als String
        """
        if message_id is None:
            message_id = f"MSG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        if execution_date is None:
            execution_date = date.today()
        
        # Root-Element
        root = ET.Element("Document", xmlns=self.NAMESPACE)
        
        # CstmrCdtTrfInitn (Customer Credit Transfer Initiation)
        cct_initn = ET.SubElement(root, "CstmrCdtTrfInitn")
        
        # Group Header
        grp_hdr = ET.SubElement(cct_initn, "GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = message_id
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()
        ET.SubElement(grp_hdr, "NbOfTxs").text = str(len(transactions))
        
        # Summe berechnen
        total_amount = sum(Decimal(str(t['amount'])) for t in transactions)
        ET.SubElement(grp_hdr, "CtrlSum").text = self._format_decimal(total_amount)
        
        # Initiating Party
        initg_pty = ET.SubElement(grp_hdr, "InitgPty")
        ET.SubElement(initg_pty, "Nm").text = self.initiator_name
        
        # Payment Information
        pmt_inf = ET.SubElement(cct_initn, "PmtInf")
        pmt_inf_id = f"PMT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        ET.SubElement(pmt_inf, "PmtInfId").text = pmt_inf_id
        ET.SubElement(pmt_inf, "PmtMtd").text = "TRF"  # Transfer
        ET.SubElement(pmt_inf, "BtchBookg").text = "true"
        ET.SubElement(pmt_inf, "NbOfTxs").text = str(len(transactions))
        ET.SubElement(pmt_inf, "CtrlSum").text = self._format_decimal(total_amount)
        
        # Payment Type Information
        pmt_tp_inf = ET.SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = ET.SubElement(pmt_tp_inf, "SvcLvl")
        ET.SubElement(svc_lvl, "Cd").text = "SEPA"
        
        # Requested Execution Date
        ET.SubElement(pmt_inf, "ReqdExctnDt").text = execution_date.isoformat()
        
        # Debtor (Auftraggeber)
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
        
        # Charge Bearer
        ET.SubElement(pmt_inf, "ChrgBr").text = "SLEV"  # Shared
        
        # Credit Transfer Transaction Information (für jede Transaktion)
        for idx, tx in enumerate(transactions, start=1):
            cdt_trf_tx_inf = ET.SubElement(pmt_inf, "CdtTrfTxInf")
            
            # Payment ID
            pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
            end_to_end_id = tx.get('end_to_end_id', f"NOTPROVIDED-{idx}")
            ET.SubElement(pmt_id, "EndToEndId").text = end_to_end_id
            
            # Amount
            amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
            instd_amt = ET.SubElement(amt, "InstdAmt", Ccy="EUR")
            instd_amt.text = self._format_decimal(Decimal(str(tx['amount'])))
            
            # Creditor Agent (Empfänger-Bank) - optional bei SEPA
            if tx.get('recipient_bic'):
                cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
                fin_instn = ET.SubElement(cdtr_agt, "FinInstnId")
                ET.SubElement(fin_instn, "BIC").text = self._format_bic(tx['recipient_bic'])
            
            # Creditor (Empfänger)
            cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
            ET.SubElement(cdtr, "Nm").text = tx['recipient_name'][:70]  # Max 70 Zeichen
            
            # Creditor Account
            cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
            cdtr_acct_id = ET.SubElement(cdtr_acct, "Id")
            ET.SubElement(cdtr_acct_id, "IBAN").text = self._format_iban(tx['recipient_iban'])
            
            # Remittance Information (Verwendungszweck)
            rmt_inf = ET.SubElement(cdt_trf_tx_inf, "RmtInf")
            ET.SubElement(rmt_inf, "Ustrd").text = tx['reference'][:140]  # Max 140 Zeichen
        
        # XML generieren
        return self._prettify_xml(root)
    
    def save_to_file(self, xml_content: str, filename: str = None) -> str:
        """
        Speichert SEPA XML in Datei
        
        Args:
            xml_content: SEPA XML Inhalt
            filename: Dateiname (optional)
        
        Returns:
            Pfad zur gespeicherten Datei
        """
        if filename is None:
            filename = f"SEPA_CreditTransfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filename


# Beispiel-Verwendung
if __name__ == "__main__":
    # SEPA-Exporter initialisieren
    exporter = SEPAExporter(
        initiator_name="VALEO GmbH",
        initiator_iban="DE89370400440532013000",
        initiator_bic="COBADEFFXXX"
    )
    
    # Test-Transaktionen
    transactions = [
        {
            "recipient_name": "Müller Landhandel GmbH",
            "recipient_iban": "DE27100777770209299700",
            "recipient_bic": "NORSDE51XXX",
            "amount": 1250.50,
            "reference": "Rechnung RE-2024-001",
            "end_to_end_id": "RE-2024-001"
        },
        {
            "recipient_name": "Schmidt Agrar KG",
            "recipient_iban": "DE89370400440532013001",
            "amount": 890.00,
            "reference": "Rechnung RE-2024-002",
            "end_to_end_id": "RE-2024-002"
        }
    ]
    
    # SEPA XML generieren
    sepa_xml = exporter.create_credit_transfer(transactions)
    
    print("SEPA-XML generiert:")
    print(sepa_xml)
    
    # Datei speichern
    filename = exporter.save_to_file(sepa_xml)
    print(f"\n✅ Exportiert nach: {filename}")

