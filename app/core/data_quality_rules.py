"""
Datenqualitätsregeln (Gap 040): MDM-Regeln für Dublette, Pflichtfeld, Referenz.

Zentrale Regeldefinitionen für Stammdaten-Validierung.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class DuplicateRule:
    """Regel: Eindeutigkeit pro Tenant (Dublettencheck)."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    unique_columns: tuple[str, ...]  # z.B. (tenant_id, debitor_number)
    id_column: str = "id"


@dataclass(frozen=True)
class RequiredFieldRule:
    """Regel: Pflichtfeld darf nicht leer sein."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    field: str
    check_empty_string: bool = True


@dataclass(frozen=True)
class ReferenceRule:
    """Regel: Fremdschlüssel muss auf existierenden Datensatz verweisen."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    fk_column: str
    target_schema: str
    target_table: str
    target_pk: str = "id"


# ── Dubletten-Regeln ─────────────────────────────────────────────────────

DUPLICATE_RULES: list[DuplicateRule] = [
    DuplicateRule(
        id="DUP-debtors",
        entity_type="debtors",
        label="Debitorennummer pro Mandant eindeutig",
        schema="domain_erp",
        table="debitors",
        unique_columns=("tenant_id", "debitor_number"),
    ),
    DuplicateRule(
        id="DUP-creditors",
        entity_type="creditors",
        label="Kreditorennummer pro Mandant eindeutig",
        schema="domain_erp",
        table="creditors",
        unique_columns=("tenant_id", "creditor_number"),
    ),
    DuplicateRule(
        id="DUP-articles",
        entity_type="articles",
        label="Artikelnummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="articles",
        unique_columns=("tenant_id", "article_number"),
    ),
    DuplicateRule(
        id="DUP-business-partners",
        entity_type="business_partners",
        label="Partner-Nummer pro Mandant eindeutig",
        schema="domain_erp",
        table="business_partners",
        unique_columns=("tenant_id", "partner_number"),
    ),
    DuplicateRule(
        id="DUP-harvest-acceptance",
        entity_type="harvest_acceptance",
        label="Annahmenummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="harvest_acceptances",
        unique_columns=("tenant_id", "acceptance_number"),
    ),
    DuplicateRule(
        id="DUP-agrar-settlements",
        entity_type="agrar_settlements",
        label="Abrechnungsnummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="agrar_settlements",
        unique_columns=("tenant_id", "settlement_number"),
    ),
]

# ── Pflichtfeld-Regeln ───────────────────────────────────────────────────

REQUIRED_FIELD_RULES: list[RequiredFieldRule] = [
    RequiredFieldRule(
        id="REQ-debtors-name",
        entity_type="debtors",
        label="Debitor: Firmenname erforderlich",
        schema="domain_erp",
        table="debitors",
        field="name",
    ),
    RequiredFieldRule(
        id="REQ-debtors-number",
        entity_type="debtors",
        label="Debitor: Debitorennummer erforderlich",
        schema="domain_erp",
        table="debitors",
        field="debitor_number",
    ),
    RequiredFieldRule(
        id="REQ-creditors-name",
        entity_type="creditors",
        label="Kreditor: Firmenname erforderlich",
        schema="domain_erp",
        table="creditors",
        field="name",
    ),
    RequiredFieldRule(
        id="REQ-creditors-number",
        entity_type="creditors",
        label="Kreditor: Kreditorennummer erforderlich",
        schema="domain_erp",
        table="creditors",
        field="creditor_number",
    ),
    RequiredFieldRule(
        id="REQ-articles-number",
        entity_type="articles",
        label="Artikel: Artikelnummer erforderlich",
        schema="domain_inventory",
        table="articles",
        field="article_number",
    ),
    RequiredFieldRule(
        id="REQ-articles-name",
        entity_type="articles",
        label="Artikel: Bezeichnung erforderlich",
        schema="domain_inventory",
        table="articles",
        field="name",
    ),
]

# ── Referenz-Regeln (orphaned FKs) ───────────────────────────────────────

REFERENCE_RULES: list[ReferenceRule] = [
    ReferenceRule(
        id="REF-offene-posten-debtor",
        entity_type="offene_posten",
        label="Offene Posten: Debitoren-Referenz gültig",
        schema="domain_erp",
        table="offene_posten",
        fk_column="debtor_id",
        target_schema="domain_erp",
        target_table="debitors",
    ),
    ReferenceRule(
        id="REF-offene-posten-creditor",
        entity_type="offene_posten",
        label="Offene Posten: Kreditoren-Referenz gültig",
        schema="domain_erp",
        table="offene_posten",
        fk_column="creditor_id",
        target_schema="domain_erp",
        target_table="creditors",
    ),
]


def get_all_entity_types() -> list[str]:
    """Alle Entity-Typen aus den Regeln sammeln."""
    types: set[str] = set()
    for r in DUPLICATE_RULES:
        types.add(r.entity_type)
    for r in REQUIRED_FIELD_RULES:
        types.add(r.entity_type)
    for r in REFERENCE_RULES:
        types.add(r.entity_type)
    return sorted(types)


# ============================================================================
# Wave-31 Contract Layer: DQRegelTyp, DQRegel, DQRuleSet, validate_datensatz
# ============================================================================

import math
import re
from enum import Enum
from typing import Any

# Maximale Eingabelaenge fuer Format-Regex-Pruefungen (ReDoS-Schutz)
_DQ_FORMAT_MAX_LEN = 200


class DQRegelTyp(str, Enum):
    PFLICHTFELD = "PFLICHTFELD"
    DUPLIKAT_VERDACHT = "DUPLIKAT_VERDACHT"
    REFERENZ_FEHLT = "REFERENZ_FEHLT"
    FORMAT_VERLETZUNG = "FORMAT_VERLETZUNG"
    BEREICH_VERLETZUNG = "BEREICH_VERLETZUNG"


class DQSeverity(str, Enum):
    FEHLER = "FEHLER"
    WARNUNG = "WARNUNG"
    INFO = "INFO"


@dataclass
class DQRegel:
    """Einzelne Datenqualitaetsregel (Wave-31 Contract)."""
    regel_id: str
    typ: DQRegelTyp
    feld: str
    beschreibung: str
    severity: DQSeverity = DQSeverity.FEHLER
    format_regex: str | None = None
    min_wert: float | None = None
    max_wert: float | None = None
    referenz_werte: list[str] = field(default_factory=list)
    unique_felder: list[str] = field(default_factory=list)
    aktiv: bool = True

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "typ": self.typ.value,
            "feld": self.feld,
            "beschreibung": self.beschreibung,
            "severity": self.severity.value,
            "format_regex": self.format_regex,
            "min_wert": self.min_wert,
            "max_wert": self.max_wert,
            "referenz_werte": self.referenz_werte,
            "unique_felder": self.unique_felder,
            "aktiv": self.aktiv,
        }


@dataclass
class DQRuleSet:
    """Regelset fuer einen Stammdatentyp (Wave-31 Contract)."""
    ruleset_id: str
    entity_typ: str
    beschreibung: str
    regeln: list[DQRegel] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "ruleset_id": self.ruleset_id,
            "entity_typ": self.entity_typ,
            "beschreibung": self.beschreibung,
            "schema_version": self.schema_version,
            "regeln": [r.as_dict() for r in self.regeln],
        }


@dataclass
class DQViolation:
    """Einzelne Regelverletzung."""
    regel_id: str
    typ: DQRegelTyp
    feld: str
    severity: DQSeverity
    meldung: str
    wert: Any = None

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "typ": self.typ.value,
            "feld": self.feld,
            "severity": self.severity.value,
            "meldung": self.meldung,
            "wert": str(self.wert) if self.wert is not None else None,
        }


@dataclass
class DQValidationResult:
    """Ergebnis der Datenqualitaetspruefung."""
    entity_typ: str
    ruleset_id: str
    bestanden: bool
    fehler_anzahl: int
    warnungs_anzahl: int
    verletzungen: list[DQViolation] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "entity_typ": self.entity_typ,
            "ruleset_id": self.ruleset_id,
            "bestanden": self.bestanden,
            "fehler_anzahl": self.fehler_anzahl,
            "warnungs_anzahl": self.warnungs_anzahl,
            "verletzungen": [v.as_dict() for v in self.verletzungen],
            "schema_version": self.schema_version,
        }


@dataclass
class DQBatchValidationResult:
    """Ergebnis einer Batch-Validierung ueber mehrere Datensaetze."""
    entity_typ: str
    ruleset_id: str
    total: int
    bestanden: int
    fehler: int
    warnungen: int
    resultate: list[DQValidationResult] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "entity_typ": self.entity_typ,
            "ruleset_id": self.ruleset_id,
            "total": self.total,
            "bestanden": self.bestanden,
            "fehler": self.fehler,
            "warnungen": self.warnungen,
            "resultate": [r.as_dict() for r in self.resultate],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Interne Check-Funktionen
# ---------------------------------------------------------------------------

def _dq_check_pflichtfeld(regel: DQRegel, datensatz: dict) -> DQViolation | None:
    wert = datensatz.get(regel.feld)
    if wert is None or (isinstance(wert, str) and wert.strip() == ""):
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.PFLICHTFELD,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Pflichtfeld '{regel.feld}' fehlt oder ist leer.",
            wert=wert,
        )
    return None


def _dq_check_format(regel: DQRegel, datensatz: dict) -> DQViolation | None:
    if not regel.format_regex:
        return None
    wert = datensatz.get(regel.feld)
    if wert is None:
        return None
    wert_str = str(wert)
    # ReDoS-Schutz: Eingabe auf _DQ_FORMAT_MAX_LEN Zeichen begrenzen
    if len(wert_str) > _DQ_FORMAT_MAX_LEN:
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.FORMAT_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=(
                f"Feld '{regel.feld}' ueberschreitet maximale Laenge "
                f"({_DQ_FORMAT_MAX_LEN} Zeichen) fuer Format-Pruefung."
            ),
            wert=wert_str[:50] + "...",
        )
    if not re.fullmatch(regel.format_regex, wert_str):
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.FORMAT_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' verletzt Format '{regel.format_regex}'. Wert: '{wert_str}'",
            wert=wert,
        )
    return None


def _dq_check_bereich(regel: DQRegel, datensatz: dict) -> DQViolation | None:
    wert = datensatz.get(regel.feld)
    if wert is None:
        return None
    try:
        wert_num = float(wert)
    except (TypeError, ValueError):
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.BEREICH_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' ist kein numerischer Wert: '{wert}'",
            wert=wert,
        )
    # NaN und Inf sind keine gueltigen Feldwerte fuer Bereichspruefungen
    if math.isnan(wert_num) or math.isinf(wert_num):
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.BEREICH_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' enthaelt ungültigen numerischen Wert: '{wert}'",
            wert=wert,
        )
    if regel.min_wert is not None and wert_num < regel.min_wert:
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.BEREICH_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' = {wert_num} < Minimum {regel.min_wert}.",
            wert=wert,
        )
    if regel.max_wert is not None and wert_num > regel.max_wert:
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.BEREICH_VERLETZUNG,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' = {wert_num} > Maximum {regel.max_wert}.",
            wert=wert,
        )
    return None


def _dq_check_referenz(regel: DQRegel, datensatz: dict) -> DQViolation | None:
    if not regel.referenz_werte:
        return None
    wert = datensatz.get(regel.feld)
    if wert is None:
        return None
    if str(wert) not in regel.referenz_werte:
        return DQViolation(
            regel_id=regel.regel_id,
            typ=DQRegelTyp.REFERENZ_FEHLT,
            feld=regel.feld,
            severity=regel.severity,
            meldung=f"Feld '{regel.feld}' = '{wert}' kein gueltiger Referenzwert. Erlaubt: {regel.referenz_werte}",
            wert=wert,
        )
    return None


def _dq_check_duplikat(
    regel: DQRegel,
    datensatz: dict,
    kontext_datensaetze: list[dict] | None,
) -> DQViolation | None:
    if not regel.unique_felder or not kontext_datensaetze:
        return None
    eigene_werte = {f: datensatz.get(f) for f in regel.unique_felder}
    for anderer in kontext_datensaetze:
        if anderer is datensatz:
            continue
        if {f: anderer.get(f) for f in regel.unique_felder} == eigene_werte and any(
            v is not None for v in eigene_werte.values()
        ):
            return DQViolation(
                regel_id=regel.regel_id,
                typ=DQRegelTyp.DUPLIKAT_VERDACHT,
                feld=regel.feld,
                severity=regel.severity,
                meldung=f"Duplikat-Verdacht: Felder {regel.unique_felder} haben identische Werte.",
                wert=eigene_werte,
            )
    return None


def validate_datensatz(
    ruleset: DQRuleSet,
    datensatz: dict,
    kontext_datensaetze: list[dict] | None = None,
) -> DQValidationResult:
    """
    Validiert einen Datensatz gegen ein DQRuleSet.

    Args:
        ruleset: Das Regelset.
        datensatz: Der zu pruefende Datensatz.
        kontext_datensaetze: Weitere Datensaetze fuer Duplikat-Checks.

    Returns:
        DQValidationResult mit allen Verletzungen.
    """
    verletzungen: list[DQViolation] = []

    _checkers = {
        DQRegelTyp.PFLICHTFELD: lambda r, d: _dq_check_pflichtfeld(r, d),
        DQRegelTyp.FORMAT_VERLETZUNG: lambda r, d: _dq_check_format(r, d),
        DQRegelTyp.BEREICH_VERLETZUNG: lambda r, d: _dq_check_bereich(r, d),
        DQRegelTyp.REFERENZ_FEHLT: lambda r, d: _dq_check_referenz(r, d),
        DQRegelTyp.DUPLIKAT_VERDACHT: lambda r, d: _dq_check_duplikat(r, d, kontext_datensaetze),
    }

    for regel in ruleset.regeln:
        if not regel.aktiv:
            continue
        checker = _checkers.get(regel.typ)
        if checker:
            v = checker(regel, datensatz)
            if v is not None:
                verletzungen.append(v)

    fehler = [v for v in verletzungen if v.severity == DQSeverity.FEHLER]
    warnungen = [v for v in verletzungen if v.severity == DQSeverity.WARNUNG]

    return DQValidationResult(
        entity_typ=ruleset.entity_typ,
        ruleset_id=ruleset.ruleset_id,
        bestanden=len(fehler) == 0,
        fehler_anzahl=len(fehler),
        warnungs_anzahl=len(warnungen),
        verletzungen=verletzungen,
    )


def get_default_dq_rulesets() -> dict[str, DQRuleSet]:
    """Liefert Default-DQ-Regelsets fuer die zentralen Stammdaten- und Prozessobjekte."""

    debitor = DQRuleSet(
        ruleset_id="DQ-DEBITOR-001",
        entity_typ="Debitor",
        beschreibung="Datenqualitaetsregeln fuer Debitoren-Stammdaten",
        regeln=[
            DQRegel("DB-001", DQRegelTyp.PFLICHTFELD, "debitor_nr", "Debitorennummer ist Pflicht"),
            DQRegel("DB-002", DQRegelTyp.PFLICHTFELD, "name", "Debitorenname ist Pflicht"),
            DQRegel("DB-003", DQRegelTyp.PFLICHTFELD, "land", "Land ist Pflicht"),
            DQRegel("DB-004", DQRegelTyp.REFERENZ_FEHLT, "land",
                    "Laendercode muss ein unterstuetzter ISO-Code sein",
                    referenz_werte=["DE", "AT", "CH", "NL", "FR", "BE", "IT", "ES", "PL", "CZ", "DK", "LU"]),
            DQRegel("DB-005", DQRegelTyp.DUPLIKAT_VERDACHT, "debitor_nr",
                    "Debitorennummer muss eindeutig sein", unique_felder=["debitor_nr"]),
        ],
    )

    lieferant = DQRuleSet(
        ruleset_id="DQ-LIEFERANT-001",
        entity_typ="Lieferant",
        beschreibung="Datenqualitaetsregeln fuer Lieferanten-Stammdaten",
        regeln=[
            DQRegel("LF-001", DQRegelTyp.PFLICHTFELD, "lieferant_nr", "Lieferantennummer ist Pflicht"),
            DQRegel("LF-002", DQRegelTyp.PFLICHTFELD, "name", "Lieferantenname ist Pflicht"),
            DQRegel("LF-003", DQRegelTyp.FORMAT_VERLETZUNG, "iban",
                    "IBAN muss DE-Format haben (DE + 20 Ziffern)",
                    severity=DQSeverity.WARNUNG, format_regex=r"DE\d{20}"),
            DQRegel("LF-004", DQRegelTyp.FORMAT_VERLETZUNG, "steuernummer",
                    "Steuernummer: 10-11 Ziffern",
                    severity=DQSeverity.WARNUNG, format_regex=r"\d{10,11}"),
            DQRegel("LF-005", DQRegelTyp.DUPLIKAT_VERDACHT, "lieferant_nr",
                    "Lieferantennummer muss eindeutig sein", unique_felder=["lieferant_nr"]),
            DQRegel("LF-006", DQRegelTyp.PFLICHTFELD, "land", "Herkunftsland ist Pflicht"),
            DQRegel("LF-007", DQRegelTyp.REFERENZ_FEHLT, "land",
                    "Laendercode muss ein unterstuetzter ISO-Code sein",
                    referenz_werte=["DE", "AT", "CH", "NL", "FR", "BE", "IT", "ES", "PL", "CZ", "DK", "LU"]),
        ],
    )

    kontrakt = DQRuleSet(
        ruleset_id="DQ-KONTRAKT-001",
        entity_typ="Kontrakt",
        beschreibung="Datenqualitaetsregeln fuer Agrar-Kontrakte",
        regeln=[
            DQRegel("KT-001", DQRegelTyp.PFLICHTFELD, "kontrakt_nr", "Kontraktnummer ist Pflicht"),
            DQRegel("KT-002", DQRegelTyp.PFLICHTFELD, "lieferant_nr", "Lieferantennummer ist Pflicht"),
            DQRegel("KT-003", DQRegelTyp.PFLICHTFELD, "ware", "Warenart ist Pflicht"),
            DQRegel("KT-004", DQRegelTyp.BEREICH_VERLETZUNG, "menge_tonnen",
                    "Menge > 0 und <= 50.000 t", min_wert=0.001, max_wert=50000.0),
            DQRegel("KT-005", DQRegelTyp.BEREICH_VERLETZUNG, "preis_eur_pro_t",
                    "Preis > 0 und <= 1.000 EUR/t", min_wert=0.01, max_wert=1000.0),
            DQRegel("KT-006", DQRegelTyp.REFERENZ_FEHLT, "kontrakt_status",
                    "Kontraktstatus muss gueltiger Wert sein",
                    referenz_werte=["ENTWURF", "AKTIV", "ERFUELLT", "STORNIERT"]),
            DQRegel("KT-007", DQRegelTyp.DUPLIKAT_VERDACHT, "kontrakt_nr",
                    "Kontraktnummer muss eindeutig sein", unique_felder=["kontrakt_nr"]),
            DQRegel("KT-008", DQRegelTyp.REFERENZ_FEHLT, "preismodell",
                    "Preismodell muss gueltiger Wert sein",
                    referenz_werte=["fixed", "follow", "pool"]),
        ],
    )

    wiegeschein = DQRuleSet(
        ruleset_id="DQ-WIEGESCHEIN-001",
        entity_typ="Wiegeschein",
        beschreibung="Datenqualitaetsregeln fuer Wiegescheine",
        regeln=[
            DQRegel("WS-001", DQRegelTyp.PFLICHTFELD, "wiegeschein_nr", "Wiegescheinnummer ist Pflicht"),
            DQRegel("WS-002", DQRegelTyp.PFLICHTFELD, "kontrakt_nr", "Kontraktzuordnung ist Pflicht"),
            DQRegel("WS-003", DQRegelTyp.PFLICHTFELD, "fahrzeug_kennzeichen",
                    "Fahrzeugkennzeichen ist Pflicht"),
            DQRegel("WS-004", DQRegelTyp.BEREICH_VERLETZUNG, "brutto_gewicht_kg",
                    "Bruttogewicht > 0 und <= 60.000 kg", min_wert=1.0, max_wert=60000.0),
            DQRegel("WS-005", DQRegelTyp.BEREICH_VERLETZUNG, "netto_gewicht_kg",
                    "Nettogewicht > 0 und <= 60.000 kg", min_wert=1.0, max_wert=60000.0),
            DQRegel("WS-006", DQRegelTyp.FORMAT_VERLETZUNG, "fahrzeug_kennzeichen",
                    "Kennzeichen: z.B. AB-CD 1234",
                    severity=DQSeverity.WARNUNG,
                    format_regex=r"[A-ZÄÖÜ]{1,3}-[A-Z]{1,2}\s?\d{1,4}[EH]?"),
            DQRegel("WS-007", DQRegelTyp.DUPLIKAT_VERDACHT, "wiegeschein_nr",
                    "Wiegescheinnummer muss eindeutig sein", unique_felder=["wiegeschein_nr"]),
        ],
    )

    artikel = DQRuleSet(
        ruleset_id="DQ-ARTIKEL-001",
        entity_typ="Artikel",
        beschreibung="Datenqualitaetsregeln fuer Artikel-Stammdaten",
        regeln=[
            DQRegel("ART-001", DQRegelTyp.PFLICHTFELD, "artikel_nr", "Artikelnummer ist Pflicht"),
            DQRegel("ART-002", DQRegelTyp.PFLICHTFELD, "bezeichnung", "Artikelbezeichnung ist Pflicht"),
            DQRegel("ART-003", DQRegelTyp.PFLICHTFELD, "einheit", "Mengeneinheit ist Pflicht"),
            DQRegel("ART-004", DQRegelTyp.REFERENZ_FEHLT, "einheit",
                    "Mengeneinheit muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["KG", "T", "LT", "STK", "M2", "M3", "HL"]),
            DQRegel("ART-005", DQRegelTyp.BEREICH_VERLETZUNG, "mehrwertsteuersatz_pct",
                    "MwSt-Satz muss zwischen 0 und 19 liegen", min_wert=0.0, max_wert=19.0),
            DQRegel("ART-006", DQRegelTyp.DUPLIKAT_VERDACHT, "artikel_nr",
                    "Artikelnummer muss eindeutig sein", unique_felder=["artikel_nr"]),
            DQRegel("ART-007", DQRegelTyp.FORMAT_VERLETZUNG, "ean_code",
                    "EAN-Code: 8 oder 13 Ziffern",
                    severity=DQSeverity.WARNUNG, format_regex=r"\d{8}|\d{13}"),
        ],
    )

    ap_rechnung = DQRuleSet(
        ruleset_id="DQ-AP-RECHNUNG-001",
        entity_typ="APRechnung",
        beschreibung="Datenqualitaetsregeln fuer Eingangsrechnungen",
        regeln=[
            DQRegel("AP-001", DQRegelTyp.PFLICHTFELD, "rechnungsnummer", "Rechnungsnummer ist Pflicht"),
            DQRegel("AP-002", DQRegelTyp.PFLICHTFELD, "lieferant_id", "Lieferant ist Pflicht"),
            DQRegel("AP-003", DQRegelTyp.PFLICHTFELD, "faelligkeit", "Faelligkeit ist Pflicht"),
            DQRegel("AP-004", DQRegelTyp.BEREICH_VERLETZUNG, "brutto_betrag_eur",
                    "Bruttobetrag > 0 und <= 10.000.000 EUR", min_wert=0.01, max_wert=10000000.0),
            DQRegel("AP-005", DQRegelTyp.REFERENZ_FEHLT, "waehrung",
                    "Waehrung muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["EUR", "USD", "CHF", "GBP"]),
            DQRegel("AP-006", DQRegelTyp.DUPLIKAT_VERDACHT, "rechnungsnummer",
                    "Rechnungsnummer sollte je Lieferant eindeutig sein",
                    unique_felder=["lieferant_id", "rechnungsnummer"]),
        ],
    )

    abrechnung = DQRuleSet(
        ruleset_id="DQ-ABRECHNUNG-001",
        entity_typ="Abrechnung",
        beschreibung="Datenqualitaetsregeln fuer Agrar-Abrechnungen",
        regeln=[
            DQRegel("SET-001", DQRegelTyp.PFLICHTFELD, "abrechnungsnummer", "Abrechnungsnummer ist Pflicht"),
            DQRegel("SET-002", DQRegelTyp.PFLICHTFELD, "lieferant_id", "Lieferant ist Pflicht"),
            DQRegel("SET-003", DQRegelTyp.BEREICH_VERLETZUNG, "brutto_gewicht_kg",
                    "Bruttogewicht > 0 und <= 100.000.000 kg", min_wert=0.001, max_wert=100000000.0),
            DQRegel("SET-004", DQRegelTyp.BEREICH_VERLETZUNG, "abrechnungsgewicht_kg",
                    "Abrechnungsgewicht > 0 und <= 100.000.000 kg", min_wert=0.001, max_wert=100000000.0),
            DQRegel("SET-005", DQRegelTyp.BEREICH_VERLETZUNG, "preis_eur_pro_t",
                    "Preis > 0 und <= 10.000 EUR/t", min_wert=0.01, max_wert=10000.0),
            DQRegel("SET-006", DQRegelTyp.REFERENZ_FEHLT, "waehrung",
                    "Waehrung muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["EUR"]),
            DQRegel("SET-007", DQRegelTyp.DUPLIKAT_VERDACHT, "abrechnungsnummer",
                    "Abrechnungsnummer sollte eindeutig sein", unique_felder=["abrechnungsnummer"]),
        ],
    )

    ernte_annahme = DQRuleSet(
        ruleset_id="DQ-ERNTE-ANNAHME-001",
        entity_typ="ErnteAnnahme",
        beschreibung="Datenqualitaetsregeln fuer Ernte-Annahme-Erfassung",
        regeln=[
            DQRegel("HA-001", DQRegelTyp.PFLICHTFELD, "annahme_nr", "Annahmenummer ist Pflicht"),
            DQRegel("HA-002", DQRegelTyp.PFLICHTFELD, "kunde_id", "Kunde ist Pflicht"),
            DQRegel("HA-003", DQRegelTyp.PFLICHTFELD, "lieferdatum", "Lieferdatum ist Pflicht"),
            DQRegel("HA-004", DQRegelTyp.REFERENZ_FEHLT, "preismodell",
                    "Preismodell muss gueltiger Wert sein",
                    referenz_werte=["fixed_contract", "spot_daily", "exchange_fix_later"]),
            DQRegel("HA-005", DQRegelTyp.REFERENZ_FEHLT, "annahmemodus",
                    "Annahmemodus muss gueltiger Wert sein",
                    referenz_werte=["STORAGE_ONLY", "PURCHASE_AT_DELIVERY_PTBF", "ADVANCE_ON_STORAGE"]),
            DQRegel("HA-006", DQRegelTyp.REFERENZ_FEHLT, "land",
                    "Laendercode muss ein unterstuetzter ISO-Code sein",
                    referenz_werte=["DE", "AT", "CH", "NL", "FR", "BE", "IT", "ES", "PL", "CZ", "DK", "LU"]),
            DQRegel("HA-007", DQRegelTyp.DUPLIKAT_VERDACHT, "annahme_nr",
                    "Annahmenummer muss eindeutig sein", unique_felder=["annahme_nr"]),
        ],
    )

    qualitaetsprotokoll = DQRuleSet(
        ruleset_id="DQ-QUALITAETSPROTOKOLL-001",
        entity_typ="Qualitaetsprotokoll",
        beschreibung="Datenqualitaetsregeln fuer Qualitaetsprotokolle",
        regeln=[
            DQRegel("QP-001", DQRegelTyp.PFLICHTFELD, "ernteannahme_id", "Ernte-Annahme ist Pflicht"),
            DQRegel("QP-002", DQRegelTyp.PFLICHTFELD, "quelle", "Quelltyp ist Pflicht"),
            DQRegel("QP-003", DQRegelTyp.REFERENZ_FEHLT, "quelle",
                    "Quelltyp muss gueltiger Wert sein",
                    referenz_werte=["manual", "import", "lims", "device"]),
            DQRegel("QP-004", DQRegelTyp.BEREICH_VERLETZUNG, "feuchte_pct",
                    "Feuchte muss zwischen 0 und 100 liegen", min_wert=0.0, max_wert=100.0),
            DQRegel("QP-005", DQRegelTyp.BEREICH_VERLETZUNG, "protein_pct",
                    "Protein muss zwischen 0 und 100 liegen", min_wert=0.0, max_wert=100.0),
            DQRegel("QP-006", DQRegelTyp.BEREICH_VERLETZUNG, "hl_gewicht",
                    "HL-Gewicht muss zwischen 0 und 100 liegen", min_wert=0.0, max_wert=100.0),
        ],
    )

    self_billing = DQRuleSet(
        ruleset_id="DQ-SELF-BILLING-001",
        entity_typ="SelfBilling",
        beschreibung="Datenqualitaetsregeln fuer Self-Billing-Folgebelege",
        regeln=[
            DQRegel("SB-001", DQRegelTyp.PFLICHTFELD, "ernteannahme_id", "Ernte-Annahme ist Pflicht"),
            DQRegel("SB-002", DQRegelTyp.BEREICH_VERLETZUNG, "netto_eur",
                    "Nettobetrag muss > 0 sein", min_wert=0.01, max_wert=10000000.0),
            DQRegel("SB-003", DQRegelTyp.BEREICH_VERLETZUNG, "brutto_eur",
                    "Bruttobetrag muss > 0 sein", min_wert=0.01, max_wert=10000000.0),
            DQRegel("SB-004", DQRegelTyp.BEREICH_VERLETZUNG, "ust_satz_pct",
                    "USt-Satz muss zwischen 0 und 100 liegen", min_wert=0.0, max_wert=100.0),
            DQRegel("SB-005", DQRegelTyp.REFERENZ_FEHLT, "besteuerung",
                    "Besteuerung muss gueltiger Wert sein",
                    referenz_werte=["regular", "ustg24_flat_rate", "small_business"]),
        ],
    )

    feldbuch_massnahme = DQRuleSet(
        ruleset_id="DQ-FELDBUCH-MASSNAHME-001",
        entity_typ="FeldbuchMassnahme",
        beschreibung="Datenqualitaetsregeln fuer importierte Feldbuch-Massnahmen",
        regeln=[
            DQRegel("FB-001", DQRegelTyp.PFLICHTFELD, "datum", "Datum ist Pflicht"),
            DQRegel("FB-002", DQRegelTyp.PFLICHTFELD, "schlag_name", "Schlagname ist Pflicht"),
            DQRegel("FB-003", DQRegelTyp.REFERENZ_FEHLT, "typ",
                    "Massnahmentyp muss gueltiger Wert sein",
                    referenz_werte=["psm", "duengung", "aussaat", "ernte", "bodenbearbeitung", "sonstiges"]),
            DQRegel("FB-004", DQRegelTyp.BEREICH_VERLETZUNG, "flaeche_ha",
                    "Flaeche muss >= 0 sein", min_wert=0.0, max_wert=100000.0),
            DQRegel("FB-005", DQRegelTyp.BEREICH_VERLETZUNG, "menge",
                    "Menge muss >= 0 sein", min_wert=0.0, max_wert=1000000.0),
        ],
    )

    kontoauszug_import = DQRuleSet(
        ruleset_id="DQ-KONTOAUSZUG-IMPORT-001",
        entity_typ="KontoauszugImport",
        beschreibung="Datenqualitaetsregeln fuer importierte Kontoauszugszeilen",
        regeln=[
            DQRegel("BSI-001", DQRegelTyp.PFLICHTFELD, "booking_date", "Buchungsdatum ist Pflicht"),
            DQRegel("BSI-002", DQRegelTyp.FORMAT_VERLETZUNG, "booking_date",
                    "Buchungsdatum muss YYYY-MM-DD sein",
                    format_regex=r"\d{4}-\d{2}-\d{2}"),
            DQRegel("BSI-003", DQRegelTyp.FORMAT_VERLETZUNG, "value_date",
                    "Valutadatum muss YYYY-MM-DD sein",
                    severity=DQSeverity.WARNUNG,
                    format_regex=r"\d{4}-\d{2}-\d{2}"),
            DQRegel("BSI-004", DQRegelTyp.BEREICH_VERLETZUNG, "amount",
                    "Betrag muss numerisch zwischen -100.000.000 und 100.000.000 liegen",
                    min_wert=-100000000.0, max_wert=100000000.0),
            DQRegel("BSI-005", DQRegelTyp.REFERENZ_FEHLT, "currency",
                    "Waehrung muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["EUR", "USD", "CHF", "GBP"]),
            DQRegel("BSI-006", DQRegelTyp.DUPLIKAT_VERDACHT, "reference",
                    "Kontoauszugszeilen sollten je Import-Batch eindeutig sein",
                    unique_felder=["booking_date", "value_date", "amount", "reference"]),
        ],
    )

    journal_import = DQRuleSet(
        ruleset_id="DQ-JOURNAL-IMPORT-001",
        entity_typ="JournalImport",
        beschreibung="Datenqualitaetsregeln fuer importierte Journalzeilen",
        regeln=[
            DQRegel("JI-001", DQRegelTyp.PFLICHTFELD, "entry_date", "Buchungsdatum ist Pflicht"),
            DQRegel("JI-002", DQRegelTyp.FORMAT_VERLETZUNG, "entry_date",
                    "Buchungsdatum muss YYYY-MM-DD, YYYYMMDD oder DD.MM.YYYY sein",
                    format_regex=r"(?:\d{4}-\d{2}-\d{2}|\d{8}|\d{2}\.\d{2}\.\d{4})"),
            DQRegel("JI-003", DQRegelTyp.PFLICHTFELD, "account_number", "Sachkonto ist Pflicht"),
            DQRegel("JI-004", DQRegelTyp.PFLICHTFELD, "description", "Buchungstext ist Pflicht"),
            DQRegel("JI-005", DQRegelTyp.BEREICH_VERLETZUNG, "debit_amount",
                    "Sollbetrag muss >= 0 und <= 100.000.000 sein",
                    min_wert=0.0, max_wert=100000000.0),
            DQRegel("JI-006", DQRegelTyp.BEREICH_VERLETZUNG, "credit_amount",
                    "Habenbetrag muss >= 0 und <= 100.000.000 sein",
                    min_wert=0.0, max_wert=100000000.0),
            DQRegel("JI-007", DQRegelTyp.DUPLIKAT_VERDACHT, "entry_date",
                    "Identische Journalzeilen sollten je Import-Batch eindeutig sein",
                    unique_felder=["entry_date", "account_number", "description", "debit_amount", "credit_amount"]),
        ],
    )

    zahlungsimport = DQRuleSet(
        ruleset_id="DQ-ZAHLUNGSIMPORT-001",
        entity_typ="Zahlungsimport",
        beschreibung="Datenqualitaetsregeln fuer importierte Zahlungseingaenge",
        regeln=[
            DQRegel("PI-001", DQRegelTyp.PFLICHTFELD, "booking_date", "Buchungsdatum ist Pflicht"),
            DQRegel("PI-002", DQRegelTyp.FORMAT_VERLETZUNG, "booking_date",
                    "Buchungsdatum muss YYYY-MM-DD sein",
                    format_regex=r"\d{4}-\d{2}-\d{2}"),
            DQRegel("PI-003", DQRegelTyp.BEREICH_VERLETZUNG, "amount",
                    "Zahlbetrag muss > 0 und <= 100.000.000 sein",
                    min_wert=0.01, max_wert=100000000.0),
            DQRegel("PI-004", DQRegelTyp.REFERENZ_FEHLT, "currency",
                    "Waehrung muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["EUR", "USD", "CHF", "GBP"]),
            DQRegel("PI-005", DQRegelTyp.DUPLIKAT_VERDACHT, "reference",
                    "Zahlungseingaenge sollten je Import-Batch eindeutig sein",
                    unique_felder=["booking_date", "amount", "reference"]),
        ],
    )

    payroll_connector_import = DQRuleSet(
        ruleset_id="DQ-PAYROLL-CONNECTOR-IMPORT-001",
        entity_typ="PayrollConnectorImport",
        beschreibung="Datenqualitaetsregeln fuer importierte Payroll-Connector-Zeilen",
        regeln=[
            DQRegel("PCI-001", DQRegelTyp.PFLICHTFELD, "booking_date", "Buchungsdatum ist Pflicht"),
            DQRegel("PCI-002", DQRegelTyp.FORMAT_VERLETZUNG, "booking_date",
                    "Buchungsdatum muss YYYY-MM-DD, YYYYMMDD oder DD.MM.YYYY sein",
                    format_regex=r"(?:\d{4}-\d{2}-\d{2}|\d{8}|\d{2}\.\d{2}\.\d{4})"),
            DQRegel("PCI-003", DQRegelTyp.PFLICHTFELD, "account", "Konto ist Pflicht"),
            DQRegel("PCI-004", DQRegelTyp.BEREICH_VERLETZUNG, "amount",
                    "Betrag muss > 0 und <= 100.000.000 sein",
                    min_wert=0.01, max_wert=100000000.0),
            DQRegel("PCI-005", DQRegelTyp.REFERENZ_FEHLT, "dc",
                    "Soll/Haben-Kennung muss gueltiger Wert sein",
                    referenz_werte=["S", "H", "D", "C", "1", "2"]),
        ],
    )

    asset_ledger_connector_import = DQRuleSet(
        ruleset_id="DQ-ASSET-LEDGER-CONNECTOR-IMPORT-001",
        entity_typ="AssetLedgerConnectorImport",
        beschreibung="Datenqualitaetsregeln fuer importierte Asset-Ledger-Connector-Zeilen",
        regeln=[
            DQRegel("ACI-001", DQRegelTyp.PFLICHTFELD, "booking_date", "Buchungsdatum ist Pflicht"),
            DQRegel("ACI-002", DQRegelTyp.FORMAT_VERLETZUNG, "booking_date",
                    "Buchungsdatum muss YYYY-MM-DD, YYYYMMDD oder DD.MM.YYYY sein",
                    format_regex=r"(?:\d{4}-\d{2}-\d{2}|\d{8}|\d{2}\.\d{2}\.\d{4})"),
            DQRegel("ACI-003", DQRegelTyp.PFLICHTFELD, "account", "Konto ist Pflicht"),
            DQRegel("ACI-004", DQRegelTyp.BEREICH_VERLETZUNG, "amount",
                    "Betrag muss > 0 und <= 100.000.000 sein",
                    min_wert=0.01, max_wert=100000000.0),
            DQRegel("ACI-005", DQRegelTyp.REFERENZ_FEHLT, "dc",
                    "Soll/Haben-Kennung muss gueltiger Wert sein",
                    referenz_werte=["S", "H", "D", "C", "1", "2"]),
        ],
    )

    daily_price_import = DQRuleSet(
        ruleset_id="DQ-DAILY-PRICE-IMPORT-001",
        entity_typ="DailyPriceImport",
        beschreibung="Datenqualitaetsregeln fuer importierte Tagespreise",
        regeln=[
            DQRegel("DPI-001", DQRegelTyp.PFLICHTFELD, "price_date", "Preisdatum ist Pflicht"),
            DQRegel("DPI-002", DQRegelTyp.FORMAT_VERLETZUNG, "price_date",
                    "Preisdatum muss YYYY-MM-DD sein",
                    format_regex=r"\d{4}-\d{2}-\d{2}"),
            DQRegel("DPI-003", DQRegelTyp.BEREICH_VERLETZUNG, "price_eur_per_ton",
                    "Preis muss > 0 und <= 100.000 EUR/t sein",
                    min_wert=0.01, max_wert=100000.0),
            DQRegel("DPI-004", DQRegelTyp.REFERENZ_FEHLT, "currency",
                    "Waehrung muss gueltiger Wert sein",
                    severity=DQSeverity.WARNUNG,
                    referenz_werte=["EUR", "USD", "CHF", "GBP"]),
            DQRegel("DPI-005", DQRegelTyp.REFERENZ_FEHLT, "source_type",
                    "Quelltyp muss gueltiger Wert sein",
                    referenz_werte=["manual", "exchange", "api"]),
        ],
    )

    return {
        "Debitor": debitor,
        "Lieferant": lieferant,
        "Kontrakt": kontrakt,
        "Wiegeschein": wiegeschein,
        "Artikel": artikel,
        "APRechnung": ap_rechnung,
        "Abrechnung": abrechnung,
        "ErnteAnnahme": ernte_annahme,
        "Qualitaetsprotokoll": qualitaetsprotokoll,
        "SelfBilling": self_billing,
        "FeldbuchMassnahme": feldbuch_massnahme,
        "KontoauszugImport": kontoauszug_import,
        "JournalImport": journal_import,
        "Zahlungsimport": zahlungsimport,
        "PayrollConnectorImport": payroll_connector_import,
        "AssetLedgerConnectorImport": asset_ledger_connector_import,
        "DailyPriceImport": daily_price_import,
    }


def get_dq_ruleset_for_entity(entity_typ: str) -> DQRuleSet | None:
    """Liefert das Default-Regelset fuer einen Entity-Typ oder None."""
    return get_default_dq_rulesets().get(entity_typ)


def validate_datensaetze_batch(
    ruleset: DQRuleSet,
    datensaetze: list[dict],
) -> DQBatchValidationResult:
    """Validiert eine Liste von Datensaetzen gegen ein Regelset."""
    resultate = [
        validate_datensatz(ruleset, datensatz, datensaetze)
        for datensatz in datensaetze
    ]
    fehler = sum(1 for r in resultate if not r.bestanden)
    warnungen = sum(r.warnungs_anzahl for r in resultate)
    return DQBatchValidationResult(
        entity_typ=ruleset.entity_typ,
        ruleset_id=ruleset.ruleset_id,
        total=len(datensaetze),
        bestanden=len(datensaetze) - fehler,
        fehler=fehler,
        warnungen=warnungen,
        resultate=resultate,
    )
