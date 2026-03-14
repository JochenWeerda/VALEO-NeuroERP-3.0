from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date, datetime
import uuid

class EdiNachrichtenTyp(str, Enum):
    ORDERS_D97A = "ORDERS_D97A"        # Bestellung
    INVOIC_D01B = "INVOIC_D01B"        # Eingangsrechnung
    DESADV_D96A = "DESADV_D96A"        # Lieferavis
    PRICAT_D96A = "PRICAT_D96A"        # Preiskatalog

class EdiVerarbeitungsStatus(str, Enum):
    EMPFANGEN = "empfangen"
    IN_VERARBEITUNG = "in_verarbeitung"
    VERARBEITET = "verarbeitet"
    FEHLER = "fehler"
    ABGELEHNT = "abgelehnt"

class EdiPartner(BaseModel):
    partner_id: str
    gln: str                            # Global Location Number (13-stellig)
    name: str
    tenant_id: str
    aktive_nachrichtentypen: list[EdiNachrichtenTyp]
    aktiv: bool = True
    schema_version: int = 1

    def unterstuetzt(self, typ: EdiNachrichtenTyp) -> bool:
        return typ in self.aktive_nachrichtentypen

class EdiNachricht(BaseModel):
    nachricht_id: str
    typ: EdiNachrichtenTyp
    absender_gln: str
    empfaenger_gln: str
    interchange_control_ref: str
    empfangen_am: datetime
    payload_raw: str
    status: EdiVerarbeitungsStatus = EdiVerarbeitungsStatus.EMPFANGEN
    fehler_beschreibung: Optional[str] = None
    verarbeitet_am: Optional[datetime] = None
    dokument_id: Optional[str] = None   # ID des erzeugten Dokuments (AP-Invoice etc.)
    schema_version: int = 1

    def markiere_verarbeitet(self, dokument_id: str) -> "EdiNachricht":
        self.status = EdiVerarbeitungsStatus.VERARBEITET
        self.dokument_id = dokument_id
        self.verarbeitet_am = datetime.utcnow()
        return self

    def markiere_fehler(self, beschreibung: str) -> "EdiNachricht":
        self.status = EdiVerarbeitungsStatus.FEHLER
        self.fehler_beschreibung = beschreibung
        return self

class EdiVerarbeitungsErgebnis(BaseModel):
    nachricht_id: str
    success: bool
    dokument_id: Optional[str] = None
    fehler_beschreibung: Optional[str] = None
    schema_version: int = 1

class SepaZahlungsAuftrag(BaseModel):
    """SEPA-Zahlungsauftrag (pain.001 / pain.008)."""
    auftrag_id: str
    tenant_id: str
    glaeubiger_iban: str
    glaeubiger_bic: str
    schuldner_iban: str
    schuldner_name: str
    betrag_eur: float
    verwendungszweck: str
    mandats_referenz: Optional[str] = None      # Nur bei Lastschrift
    faelligkeitsdatum: date
    ist_lastschrift: bool = False
    schema_version: int = 1

    def ist_valide(self) -> bool:
        """Minimale Validierung: IBAN-Format (DE-Standard 22-stellig)."""
        return (
            len(self.glaeubiger_iban) >= 15
            and len(self.schuldner_iban) >= 15
            and self.betrag_eur > 0
        )

class EdiNachrichtStore(BaseModel):
    nachrichten: dict[str, EdiNachricht] = {}
    partner: dict[str, EdiPartner] = {}
    schema_version: int = 1

    def add_nachricht(self, n: EdiNachricht) -> EdiNachricht:
        self.nachrichten[n.nachricht_id] = n
        return n

    def add_partner(self, p: EdiPartner) -> EdiPartner:
        self.partner[p.partner_id] = p
        return p

    def get_nachricht(self, nachricht_id: str) -> Optional[EdiNachricht]:
        return self.nachrichten.get(nachricht_id)

    def offene_nachrichten(self, tenant_gln: str) -> list[EdiNachricht]:
        return [n for n in self.nachrichten.values()
                if n.empfaenger_gln == tenant_gln
                and n.status == EdiVerarbeitungsStatus.EMPFANGEN]

    def nachrichten_by_typ(self, typ: EdiNachrichtenTyp) -> list[EdiNachricht]:
        return [n for n in self.nachrichten.values() if n.typ == typ]

def parse_edi_nachricht(raw: str, typ: EdiNachrichtenTyp) -> EdiVerarbeitungsErgebnis:
    """Stub-Parser: validiert Mindeststruktur einer EDIFACT-Nachricht."""
    nachricht_id = str(uuid.uuid4())
    if not raw or len(raw.strip()) < 10:
        return EdiVerarbeitungsErgebnis(
            nachricht_id=nachricht_id,
            success=False,
            fehler_beschreibung="Nachricht zu kurz oder leer",
        )
    # Minimale EDIFACT-Struktur: muss UNB (Interchange Header) enthalten
    if typ in (EdiNachrichtenTyp.ORDERS_D97A, EdiNachrichtenTyp.INVOIC_D01B,
               EdiNachrichtenTyp.DESADV_D96A, EdiNachrichtenTyp.PRICAT_D96A):
        if "UNB" not in raw and "<?xml" not in raw:
            return EdiVerarbeitungsErgebnis(
                nachricht_id=nachricht_id,
                success=False,
                fehler_beschreibung=f"Kein UNB-Header fuer {typ.value} gefunden",
            )
    return EdiVerarbeitungsErgebnis(
        nachricht_id=nachricht_id,
        success=True,
        dokument_id=str(uuid.uuid4()),
    )
