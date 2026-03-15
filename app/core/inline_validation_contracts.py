"""
inline_validation_contracts.py — Inline-Validierung (Wave 35, Gap 026)

Felddefinitionen und Validierungsregeln mit domain-spezifischen Erklaerungen.
Ziel: 35% weniger Eingabefehler durch kontextsensitive Echtzeit-Hints.

Gap 026: Inline-Validierung mit domain-spezifischen Erklaerungen.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_MAX_EINGABE_LEN = 500   # ReDoS-Schutz: Laengenbegrenzung vor Regex


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FeldTyp(str, Enum):
    """Datentyp eines validierbaren Feldes."""
    TEXT         = "TEXT"
    ZAHL         = "ZAHL"
    DATUM        = "DATUM"
    EMAIL        = "EMAIL"
    TELEFON      = "TELEFON"
    IBAN         = "IBAN"
    PLZ          = "PLZ"
    KENNZEICHEN  = "KENNZEICHEN"
    MENGE        = "MENGE"
    PREIS        = "PREIS"
    BOOLEAN      = "BOOLEAN"


class ValidierungsRegelTyp(str, Enum):
    """Typ einer Validierungsregel."""
    PFLICHTFELD  = "PFLICHTFELD"   # Darf nicht leer sein
    FORMAT       = "FORMAT"        # Regex-Format-Pruefung
    BEREICH      = "BEREICH"       # Numerischer Bereich
    LAENGE       = "LAENGE"        # Text-Laenge
    REFERENZ     = "REFERENZ"      # Fremdschluessel/Lookup
    CUSTOM       = "CUSTOM"        # Benutzerdefiniert


class ValidierungsStatus(str, Enum):
    GUELTIG      = "GUELTIG"
    FEHLER       = "FEHLER"
    WARNUNG      = "WARNUNG"


# ---------------------------------------------------------------------------
# Validierungsregel
# ---------------------------------------------------------------------------

@dataclass
class InlineValidierungsRegel:
    """
    Eine einzelne Validierungsregel fuer ein Feld.

    Kapselt was geprueft wird, welche Fehlermeldung ausgegeben wird
    und WARUM diese Regel existiert (domain-spezifische Erklaerung).
    """
    regel_id: str
    typ: ValidierungsRegelTyp
    fehlermeldung: str          # Kurz, fuer User sichtbar
    erklaerung: str             # Warum gilt diese Regel? (Tooltip/Detail)
    # Fuer FORMAT-Regeln
    format_regex: str = ""
    # Fuer BEREICH-Regeln
    min_wert: float | None = None
    max_wert: float | None = None
    # Fuer LAENGE-Regeln
    min_laenge: int | None = None
    max_laenge: int | None = None
    # Warnung statt Fehler?
    ist_warnung: bool = False

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "typ": self.typ.value,
            "fehlermeldung": self.fehlermeldung,
            "erklaerung": self.erklaerung,
            "ist_warnung": self.ist_warnung,
        }


# ---------------------------------------------------------------------------
# Felddefinition
# ---------------------------------------------------------------------------

@dataclass
class InlineValidierungsFeld:
    """
    Typisierte Felddefinition mit Validierungsregeln und Erklaerung.
    """
    feld_id: str
    feld_name: str
    domain: str
    typ: FeldTyp
    label: str                  # UI-Label auf Deutsch
    hint: str                   # Kurzer Eingabehinweis
    regeln: list[InlineValidierungsRegel] = field(default_factory=list)
    beispiel_wert: str = ""

    def as_dict(self) -> dict:
        return {
            "feld_id": self.feld_id,
            "feld_name": self.feld_name,
            "domain": self.domain,
            "typ": self.typ.value,
            "label": self.label,
            "hint": self.hint,
            "regeln": [r.as_dict() for r in self.regeln],
            "beispiel_wert": self.beispiel_wert,
        }


# ---------------------------------------------------------------------------
# Validierungsergebnis
# ---------------------------------------------------------------------------

@dataclass
class FeldValidierungsErgebnis:
    """Ergebnis der Inline-Validierung eines einzelnen Feldes."""
    feld_id: str
    wert: str
    status: ValidierungsStatus
    fehlermeldung: str = ""
    erklaerung: str = ""
    angewendete_regel_id: str = ""
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "feld_id": self.feld_id,
            "wert": self.wert,
            "status": self.status.value,
            "fehlermeldung": self.fehlermeldung,
            "erklaerung": self.erklaerung,
            "angewendete_regel_id": self.angewendete_regel_id,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# validate_inline_field
# ---------------------------------------------------------------------------

def validate_inline_field(
    feld: InlineValidierungsFeld,
    wert: Any,
) -> FeldValidierungsErgebnis:
    """
    Validiert einen Eingabewert gegen alle Regeln eines Feldes.

    Prueft in Reihenfolge: PFLICHTFELD -> LAENGE -> FORMAT -> BEREICH.
    Erste Verletzung gewinnt (fail-fast). Warnungen geben WARNUNG zurueck.

    Args:
        feld: Die Felddefinition mit Regeln.
        wert: Der zu pruefende Eingabewert.

    Returns:
        FeldValidierungsErgebnis.
    """
    wert_str = "" if wert is None else str(wert).strip()

    for regel in feld.regeln:
        ergebnis = _pruefe_regel(regel, wert_str, feld.feld_id)
        if ergebnis is not None:
            return ergebnis

    return FeldValidierungsErgebnis(
        feld_id=feld.feld_id,
        wert=wert_str,
        status=ValidierungsStatus.GUELTIG,
    )


def _pruefe_regel(
    regel: InlineValidierungsRegel,
    wert_str: str,
    feld_id: str,
) -> FeldValidierungsErgebnis | None:
    """Prueft eine einzelne Regel. Gibt None zurueck wenn kein Fehler."""
    verletzt = False

    if regel.typ == ValidierungsRegelTyp.PFLICHTFELD:
        verletzt = not wert_str

    elif regel.typ == ValidierungsRegelTyp.LAENGE:
        l = len(wert_str)
        if regel.min_laenge is not None and l < regel.min_laenge:
            verletzt = True
        if regel.max_laenge is not None and l > regel.max_laenge:
            verletzt = True

    elif regel.typ == ValidierungsRegelTyp.FORMAT:
        if not wert_str:
            return None  # Leeres Feld -> Pflichtfeld-Regel zustaendig
        if len(wert_str) > _MAX_EINGABE_LEN:
            verletzt = True
        elif regel.format_regex:
            try:
                verletzt = not re.fullmatch(regel.format_regex, wert_str)
            except re.error:
                verletzt = True

    elif regel.typ == ValidierungsRegelTyp.BEREICH:
        if not wert_str:
            return None
        try:
            num = float(wert_str.replace(",", "."))
            if math.isnan(num) or math.isinf(num):
                verletzt = True
            else:
                if regel.min_wert is not None and num < regel.min_wert:
                    verletzt = True
                if regel.max_wert is not None and num > regel.max_wert:
                    verletzt = True
        except (ValueError, TypeError):
            verletzt = True

    if verletzt:
        status = (
            ValidierungsStatus.WARNUNG
            if regel.ist_warnung
            else ValidierungsStatus.FEHLER
        )
        return FeldValidierungsErgebnis(
            feld_id=feld_id,
            wert=wert_str,
            status=status,
            fehlermeldung=regel.fehlermeldung,
            erklaerung=regel.erklaerung,
            angewendete_regel_id=regel.regel_id,
        )
    return None


# ---------------------------------------------------------------------------
# Default-Felddefinitionen
# ---------------------------------------------------------------------------

def get_default_field_validations() -> list[InlineValidierungsFeld]:
    """
    Liefert Inline-Validierungsdefinitionen fuer Kern-Felder in Agrar und Finance.
    """
    return [
        # --- Agrar: Wiegeschein ---
        InlineValidierungsFeld(
            feld_id="ws-bruttogewicht",
            feld_name="bruttogewicht",
            domain="agrar",
            typ=FeldTyp.MENGE,
            label="Bruttogewicht (kg)",
            hint="Gewicht in kg, z.B. 25000",
            beispiel_wert="25000",
            regeln=[
                InlineValidierungsRegel(
                    "WS-001", ValidierungsRegelTyp.PFLICHTFELD,
                    "Bruttogewicht ist Pflichtfeld.",
                    "Ohne Bruttogewicht kann keine Abrechnung erfolgen.",
                ),
                InlineValidierungsRegel(
                    "WS-002", ValidierungsRegelTyp.BEREICH,
                    "Bruttogewicht muss zwischen 100 und 100.000 kg liegen.",
                    "Typisches LKW-Bruttogewicht: 10.000–40.000 kg. Werte ausserhalb "
                    "koennen auf Eingabefehler oder Waagenfehler hinweisen.",
                    min_wert=100.0,
                    max_wert=100_000.0,
                ),
            ],
        ),
        InlineValidierungsFeld(
            feld_id="ws-feuchte",
            feld_name="feuchte_pct",
            domain="agrar",
            typ=FeldTyp.ZAHL,
            label="Feuchte (%)",
            hint="Feuchtegehalt in Prozent, z.B. 14.5",
            beispiel_wert="14.5",
            regeln=[
                InlineValidierungsRegel(
                    "WS-003", ValidierungsRegelTyp.BEREICH,
                    "Feuchte muss zwischen 5 und 50 % liegen.",
                    "Handelsfeuchte Getreide: 14–15 %. Werte >25 % koennen auf "
                    "Messfehler hinweisen und beeinflussen den Trocknungsabzug.",
                    min_wert=5.0,
                    max_wert=50.0,
                ),
                InlineValidierungsRegel(
                    "WS-004", ValidierungsRegelTyp.BEREICH,
                    "Feuchte ueber 25 % — bitte Messung pruefen.",
                    "Sehr hohe Feuchte erfordert intensive Trocknung — moeglicher "
                    "Messfehler oder feuchtes Erntegut. Ruecksprache mit Lagermeister.",
                    min_wert=25.0,
                    max_wert=50.0,
                    ist_warnung=True,
                ),
            ],
        ),
        InlineValidierungsFeld(
            feld_id="ws-kontrakt-nr",
            feld_name="kontrakt_nummer",
            domain="agrar",
            typ=FeldTyp.TEXT,
            label="Kontraktnummer",
            hint="Format: KT-JJJJ-NNNNN, z.B. KT-2025-00123",
            beispiel_wert="KT-2025-00123",
            regeln=[
                InlineValidierungsRegel(
                    "WS-005", ValidierungsRegelTyp.PFLICHTFELD,
                    "Kontraktnummer ist Pflichtfeld.",
                    "Jeder Wiegeschein muss einem Kontrakt zugeordnet sein "
                    "fuer lueckenlose Rückverfolgung (GoBD).",
                ),
                InlineValidierungsRegel(
                    "WS-006", ValidierungsRegelTyp.FORMAT,
                    "Kontraktnummer muss Format KT-JJJJ-NNNNN haben.",
                    "Das einheitliche Format ermoeglicht automatische Zuordnung "
                    "und verhindert Duplikate im System.",
                    format_regex=r"KT-\d{4}-\d{5}",
                ),
            ],
        ),
        # --- Finance: Rechnung ---
        InlineValidierungsFeld(
            feld_id="re-betrag",
            feld_name="rechnungsbetrag_eur",
            domain="finance",
            typ=FeldTyp.PREIS,
            label="Rechnungsbetrag (EUR)",
            hint="Betrag in Euro, z.B. 15000.00",
            beispiel_wert="15000.00",
            regeln=[
                InlineValidierungsRegel(
                    "RE-001", ValidierungsRegelTyp.PFLICHTFELD,
                    "Rechnungsbetrag ist Pflichtfeld.",
                    "Ohne Betrag kann keine Verbindlichkeit gebucht werden.",
                ),
                InlineValidierungsRegel(
                    "RE-002", ValidierungsRegelTyp.BEREICH,
                    "Rechnungsbetrag muss groesser als 0 EUR sein.",
                    "Negative oder Null-Betrage koennen keine regulaere Rechnung sein — "
                    "Gutschriften werden separat erfasst.",
                    min_wert=0.01,
                ),
                InlineValidierungsRegel(
                    "RE-003", ValidierungsRegelTyp.BEREICH,
                    "Rechnungsbetrag ueber 500.000 EUR — Freigabe erforderlich.",
                    "Rechnungen ueber 500.000 EUR benoetigen Vier-Augen-Freigabe "
                    "(Prokura-Grenze). Bitte Vorgesetzten informieren.",
                    min_wert=500_000.0,
                    ist_warnung=True,
                ),
            ],
        ),
        InlineValidierungsFeld(
            feld_id="re-iban",
            feld_name="iban",
            domain="finance",
            typ=FeldTyp.IBAN,
            label="IBAN",
            hint="Deutsche IBAN: DE + 2 Ziffern + 18 Stellen",
            beispiel_wert="DE89370400440532013000",
            regeln=[
                InlineValidierungsRegel(
                    "RE-004", ValidierungsRegelTyp.FORMAT,
                    "IBAN muss das korrekte Format haben (z.B. DE89370400440532013000).",
                    "Die IBAN wird fuer automatische Zahlungslaeufe benoetigt. "
                    "Fehlerhafte IBANs fuehren zu Zahlungsruecklaeufer-Gebuehren.",
                    format_regex=r"[A-Z]{2}\d{2}[A-Z0-9]{1,30}",
                ),
            ],
        ),
        InlineValidierungsFeld(
            feld_id="re-faelligkeit",
            feld_name="faelligkeitsdatum",
            domain="finance",
            typ=FeldTyp.DATUM,
            label="Faelligkeitsdatum",
            hint="Format: TT.MM.JJJJ",
            beispiel_wert="15.04.2025",
            regeln=[
                InlineValidierungsRegel(
                    "RE-005", ValidierungsRegelTyp.PFLICHTFELD,
                    "Faelligkeitsdatum ist Pflichtfeld.",
                    "Ohne Faelligkeitsdatum kann der Zahlungslauf nicht terminiert werden.",
                ),
                InlineValidierungsRegel(
                    "RE-006", ValidierungsRegelTyp.FORMAT,
                    "Datum muss im Format TT.MM.JJJJ eingegeben werden.",
                    "Das deutsche Datumsformat wird automatisch in ISO-8601 umgewandelt.",
                    format_regex=r"\d{2}\.\d{2}\.\d{4}",
                ),
            ],
        ),
        # --- Compliance ---
        InlineValidierungsFeld(
            feld_id="co-zulassungsnr",
            feld_name="zulassungsnummer",
            domain="compliance",
            typ=FeldTyp.TEXT,
            label="Zulassungsnummer",
            hint="z.B. DE-0012345-00-01",
            beispiel_wert="DE-0012345-00-01",
            regeln=[
                InlineValidierungsRegel(
                    "CO-001", ValidierungsRegelTyp.PFLICHTFELD,
                    "Zulassungsnummer ist Pflichtfeld fuer Compliance-Erfassung.",
                    "Ohne Zulassungsnummer kann das Produkt nicht zur Verwendung "
                    "freigegeben werden (Pflanzenschutzmittelverordnung).",
                ),
                InlineValidierungsRegel(
                    "CO-002", ValidierungsRegelTyp.LAENGE,
                    "Zulassungsnummer muss zwischen 5 und 30 Zeichen lang sein.",
                    "Offizielle Zulassungsnummern haben ein definiertes Laengenprofil.",
                    min_laenge=5,
                    max_laenge=30,
                ),
            ],
        ),
    ]


def get_field_by_id(
    feld_id: str,
    felder: list[InlineValidierungsFeld] | None = None,
) -> InlineValidierungsFeld | None:
    """Sucht ein Feld anhand der feld_id."""
    if felder is None:
        felder = get_default_field_validations()
    for f in felder:
        if f.feld_id == feld_id:
            return f
    return None
