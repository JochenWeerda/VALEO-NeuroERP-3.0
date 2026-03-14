from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date, timedelta
import uuid

class RetentionKlasse(str, Enum):
    KUERZER_6J = "6_jahre"
    STANDARD_10J = "10_jahre"
    DAUERHAFT = "dauerhaft"

class RetentionEreignis(str, Enum):
    """Ereignis ab dem die Aufbewahrungsfrist beginnt."""
    BUCHUNGSDATUM = "buchungsdatum"
    JAHRESABSCHLUSS = "jahresabschluss"
    VERTRAGSENDE = "vertragsende"
    ERSTELLUNGSDATUM = "erstellungsdatum"

class RetentionRegel(BaseModel):
    dokumenttyp: str            # z.B. "ap_invoice", "journal_entry"
    klasse: RetentionKlasse
    beginnt_mit: RetentionEreignis
    beschreibung: str
    schema_version: int = 1

    @property
    def aufbewahrungsjahre(self) -> int:
        mapping = {
            RetentionKlasse.KUERZER_6J: 6,
            RetentionKlasse.STANDARD_10J: 10,
            RetentionKlasse.DAUERHAFT: 9999,
        }
        return mapping[self.klasse]

class RetentionPruefung(BaseModel):
    pruefung_id: str
    dokumenttyp: str
    dokumentdatum: date
    ereignisdatum: date         # Datum des Beginnereignisses (z.B. Jahresabschluss)
    aufbewahrungsjahre: int
    schema_version: int = 1

    @property
    def aufzubewahren_bis(self) -> date:
        return self.ereignisdatum.replace(year=self.ereignisdatum.year + self.aufbewahrungsjahre)

    def darf_geloescht_werden(self, heute: date) -> bool:
        return heute > self.aufzubewahren_bis

    def verbleibende_tage(self, heute: date) -> int:
        delta = (self.aufzubewahren_bis - heute).days
        return max(0, delta)

def build_default_retention_regeln() -> list[RetentionRegel]:
    """GoBD-konforme Standardregeln fuer alle Wave-1-7-Dokumenttypen (SS 147 AO)."""
    return [
        RetentionRegel(
            dokumenttyp="ap_invoice",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.JAHRESABSCHLUSS,
            beschreibung="Eingangsrechnungen: 10 Jahre ab Jahresabschluss (SS147 Abs. 1 Nr. 1 AO)",
        ),
        RetentionRegel(
            dokumenttyp="journal_entry",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.JAHRESABSCHLUSS,
            beschreibung="Buchungsbelege: 10 Jahre (SS147 Abs. 1 Nr. 4 AO)",
        ),
        RetentionRegel(
            dokumenttyp="payment_run",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.BUCHUNGSDATUM,
            beschreibung="Zahlungsbelege: 10 Jahre",
        ),
        RetentionRegel(
            dokumenttyp="audit_evidence",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.ERSTELLUNGSDATUM,
            beschreibung="GoBD-Belegnachweise: 10 Jahre",
        ),
        RetentionRegel(
            dokumenttyp="kontrakt",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.VERTRAGSENDE,
            beschreibung="Vertraege: 10 Jahre ab Vertragsende",
        ),
        RetentionRegel(
            dokumenttyp="agrar_settlement",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.JAHRESABSCHLUSS,
            beschreibung="Abrechnungen: 10 Jahre",
        ),
        RetentionRegel(
            dokumenttyp="psm_protokoll",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.ERSTELLUNGSDATUM,
            beschreibung="PSM-Spritztagebuch: 10 Jahre (SS 11 Abs. 2 PflSchG i.V.m. SS 67 PflSchG)",
        ),
        RetentionRegel(
            dokumenttyp="duenge_bilanz",
            klasse=RetentionKlasse.STANDARD_10J,
            beginnt_mit=RetentionEreignis.ERSTELLUNGSDATUM,
            beschreibung="Duengungsaufzeichnungen: 10 Jahre (SS 10 DueV)",
        ),
        RetentionRegel(
            dokumenttyp="reklamation",
            klasse=RetentionKlasse.KUERZER_6J,
            beginnt_mit=RetentionEreignis.VERTRAGSENDE,
            beschreibung="Reklamationsvorgaenge: 6 Jahre (SS 195 BGB)",
        ),
        RetentionRegel(
            dokumenttyp="silo_reinigungsprotokoll",
            klasse=RetentionKlasse.KUERZER_6J,
            beginnt_mit=RetentionEreignis.ERSTELLUNGSDATUM,
            beschreibung="Siloreinigung: 6 Jahre",
        ),
    ]
