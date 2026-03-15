"""
Query-Vertrags-Registry — Wave 29 AP4/AP5

Typisierte Read-Model-Abfragen fuer den Process-Kernel.
Kein Frontend-Client erhaelt undefinierte Felder (Gap 031).

Query-Contracts geben verbindlich vor:
  - welche Felder ein Query-Ergebnis enthaelt
  - ob Felder nullable sind
  - welcher Datentyp erwartet wird

Dadurch koennen Clients zur Compile-/Laufzeit pruefen, ob ein Query-Ergebnis
dem Contract entspricht, ohne unbekannte undefined-Werte zu erhalten.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


QUERY_CONTRACT_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class QueryFeldTyp(str, Enum):
    STRING   = "string"
    INT      = "int"
    FLOAT    = "float"
    DECIMAL  = "decimal"    # Als String serialisiert (monetaere Werte)
    BOOL     = "bool"
    DATETIME = "datetime"   # ISO-8601 String
    DATE     = "date"       # ISO-8601 Datumsstring
    LIST     = "list"       # JSON-Array (homogen)
    DICT     = "dict"       # Eingebettetes Objekt
    ENUM     = "enum"       # String aus definierten Werten


class QueryViolationCode(str, Enum):
    PFLICHTFELD_FEHLT        = "PFLICHTFELD_FEHLT"
    UNERWARTETES_FELD        = "UNERWARTETES_FELD"
    NULLABLE_VERLETZUNG      = "NULLABLE_VERLETZUNG"   # Pflichtfeld ist None
    TYP_VERLETZUNG           = "TYP_VERLETZUNG"
    ENUM_WERT_UNBEKANNT      = "ENUM_WERT_UNBEKANNT"


# ---------------------------------------------------------------------------
# AP4: QueryResultFeld + QueryContract + QueryRegistry
# ---------------------------------------------------------------------------

@dataclass
class QueryResultFeld:
    """Definition eines Feldes im Query-Ergebnis."""
    name: str
    typ: QueryFeldTyp
    nullable: bool
    beschreibung: str
    enum_werte: Optional[list[str]] = None    # Nur wenn typ == ENUM
    beispiel: Optional[str] = None

    def as_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "typ": self.typ.value,
            "nullable": self.nullable,
            "beschreibung": self.beschreibung,
        }
        if self.enum_werte:
            d["enum_werte"] = self.enum_werte
        if self.beispiel:
            d["beispiel"] = self.beispiel
        return d


@dataclass
class QueryContract:
    """
    Verbindlicher Contract fuer eine Read-Model-Abfrage.

    query_id folgt der Konvention: {domain}.{ressource}.{operation}
    z.B. "agrar.settlement.list", "finance.ap_invoice.detail"
    """
    query_id: str
    prozess_key: str
    beschreibung: str
    felder: list[QueryResultFeld] = field(default_factory=list)
    schema_version: int = QUERY_CONTRACT_SCHEMA_VERSION

    @property
    def pflicht_felder(self) -> list[QueryResultFeld]:
        return [f for f in self.felder if not f.nullable]

    @property
    def nullable_felder(self) -> list[QueryResultFeld]:
        return [f for f in self.felder if f.nullable]

    @property
    def feld_namen(self) -> set[str]:
        return {f.name for f in self.felder}

    def as_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "prozess_key": self.prozess_key,
            "beschreibung": self.beschreibung,
            "feld_count": len(self.felder),
            "pflicht_felder": [f.name for f in self.pflicht_felder],
            "nullable_felder": [f.name for f in self.nullable_felder],
            "felder": [f.as_dict() for f in self.felder],
            "schema_version": self.schema_version,
        }


@dataclass
class QueryRegistry:
    """Registry aller definierten QueryContracts."""
    contracts: list[QueryContract] = field(default_factory=list)
    schema_version: int = QUERY_CONTRACT_SCHEMA_VERSION

    def by_prozess_key(self, prozess_key: str) -> list[QueryContract]:
        return [c for c in self.contracts if c.prozess_key == prozess_key]

    def by_query_id(self, query_id: str) -> Optional[QueryContract]:
        for c in self.contracts:
            if c.query_id == query_id:
                return c
        return None

    def as_dict(self) -> dict:
        return {
            "contract_count": len(self.contracts),
            "prozess_keys": sorted({c.prozess_key for c in self.contracts}),
            "contracts": [c.as_dict() for c in self.contracts],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP5: validate_query_result()
# ---------------------------------------------------------------------------

@dataclass
class QueryViolation:
    code: QueryViolationCode
    feld: str
    message: str

    def as_dict(self) -> dict:
        return {
            "code": self.code.value,
            "feld": self.feld,
            "message": self.message,
        }


@dataclass
class QueryValidationResult:
    query_id: str
    valid: bool
    violations: list[QueryViolation] = field(default_factory=list)
    schema_version: int = QUERY_CONTRACT_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "valid": self.valid,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_query_result(
    contract: QueryContract,
    result: dict[str, Any],
    strict: bool = False,
) -> QueryValidationResult:
    """
    Prueft ob ein Query-Ergebnis dem QueryContract entspricht.

    Checks:
    - Alle Pflichtfelder (nullable=False) sind vorhanden und nicht None
    - Nullable-Felder duerfen None sein
    - strict=True: Unbekannte Felder im Ergebnis sind Violations
    - Enum-Werte werden geprueft wenn definiert
    """
    violations: list[QueryViolation] = []

    contract_felder = {f.name: f for f in contract.felder}
    result_keys = set(result.keys())

    for feld in contract.felder:
        wert = result.get(feld.name)

        if feld.name not in result:
            violations.append(QueryViolation(
                code=QueryViolationCode.PFLICHTFELD_FEHLT,
                feld=feld.name,
                message=f"Pflichtfeld '{feld.name}' fehlt im Ergebnis",
            ))
            continue

        if wert is None and not feld.nullable:
            violations.append(QueryViolation(
                code=QueryViolationCode.NULLABLE_VERLETZUNG,
                feld=feld.name,
                message=f"Pflichtfeld '{feld.name}' ist None (nullable=False)",
            ))
            continue

        if wert is None:
            continue  # nullable + None ist OK

        # Enum-Pruefung
        if feld.typ == QueryFeldTyp.ENUM and feld.enum_werte:
            if str(wert) not in feld.enum_werte:
                violations.append(QueryViolation(
                    code=QueryViolationCode.ENUM_WERT_UNBEKANNT,
                    feld=feld.name,
                    message=f"Wert '{wert}' nicht in erlaubten Enum-Werten: {feld.enum_werte}",
                ))

        # Basistyp-Pruefung
        typ_ok = _check_typ(wert, feld.typ)
        if not typ_ok:
            violations.append(QueryViolation(
                code=QueryViolationCode.TYP_VERLETZUNG,
                feld=feld.name,
                message=f"Feld '{feld.name}': Typ {type(wert).__name__} passt nicht zu {feld.typ.value}",
            ))

    if strict:
        unbekannte = result_keys - contract.feld_namen
        for feld_name in sorted(unbekannte):
            violations.append(QueryViolation(
                code=QueryViolationCode.UNERWARTETES_FELD,
                feld=feld_name,
                message=f"Unbekanntes Feld '{feld_name}' nicht im Contract definiert",
            ))

    return QueryValidationResult(
        query_id=contract.query_id,
        valid=len(violations) == 0,
        violations=violations,
    )


def _check_typ(wert: Any, typ: QueryFeldTyp) -> bool:
    """Prueft ob ein Wert dem erwarteten QueryFeldTyp entspricht."""
    if typ == QueryFeldTyp.STRING:
        return isinstance(wert, str)
    if typ == QueryFeldTyp.INT:
        return isinstance(wert, int) and not isinstance(wert, bool)
    if typ in (QueryFeldTyp.FLOAT, QueryFeldTyp.DECIMAL):
        return isinstance(wert, (int, float, str)) and not isinstance(wert, bool)
    if typ == QueryFeldTyp.BOOL:
        return isinstance(wert, bool)
    if typ in (QueryFeldTyp.DATETIME, QueryFeldTyp.DATE):
        return isinstance(wert, str)  # ISO-8601 als String
    if typ == QueryFeldTyp.LIST:
        return isinstance(wert, list)
    if typ == QueryFeldTyp.DICT:
        return isinstance(wert, dict)
    if typ == QueryFeldTyp.ENUM:
        return isinstance(wert, str)
    return True


# ---------------------------------------------------------------------------
# AP4: get_process_kernel_queries()
# ---------------------------------------------------------------------------

def get_process_kernel_queries() -> QueryRegistry:
    """
    Liefert alle verbindlichen Query-Contracts des Process-Kernels.

    Abdeckung: agrar_settlement, wareneingang, qualitaetspruefung,
               ap_invoice, workflow_instance, sla_status
    """
    contracts: list[QueryContract] = [

        # ---------------------------------------------------------------
        # agrar_settlement
        # ---------------------------------------------------------------
        QueryContract(
            query_id="agrar.settlement.list",
            prozess_key="agrar_settlement",
            beschreibung="Liste aller Abrechnungsinstanzen (Kurzform fuer ListReport)",
            felder=[
                QueryResultFeld("settlement_id", QueryFeldTyp.STRING, False, "Eindeutige Settlement-ID", beispiel="SET-2024-001"),
                QueryResultFeld("lieferant_id", QueryFeldTyp.STRING, False, "Lieferant-Referenz"),
                QueryResultFeld("lieferant_name", QueryFeldTyp.STRING, True, "Lieferantenname (aus BP-Stamm)"),
                QueryResultFeld("status", QueryFeldTyp.ENUM, False, "Prozessstatus",
                                enum_werte=["OFFEN", "IN_PRUEFUNG", "FREIGEGEBEN", "VERBUCHT", "STORNIERT"]),
                QueryResultFeld("brutto_eur", QueryFeldTyp.DECIMAL, False, "Bruttobetrag EUR"),
                QueryResultFeld("menge_tonnen", QueryFeldTyp.DECIMAL, False, "Angelieferte Menge in Tonnen"),
                QueryResultFeld("kampagne", QueryFeldTyp.STRING, True, "Erntekampagne (z.B. 2024)"),
                QueryResultFeld("erstellt_am", QueryFeldTyp.DATETIME, False, "Erstellungszeitpunkt ISO-8601"),
            ],
        ),

        QueryContract(
            query_id="agrar.settlement.detail",
            prozess_key="agrar_settlement",
            beschreibung="Vollstaendige Detailansicht eines Settlements (fuer ObjectPage)",
            felder=[
                QueryResultFeld("settlement_id", QueryFeldTyp.STRING, False, "Settlement-ID"),
                QueryResultFeld("lieferant_id", QueryFeldTyp.STRING, False, "Lieferant-Referenz"),
                QueryResultFeld("lieferant_name", QueryFeldTyp.STRING, True, "Lieferantenname"),
                QueryResultFeld("status", QueryFeldTyp.ENUM, False, "Prozessstatus",
                                enum_werte=["OFFEN", "IN_PRUEFUNG", "FREIGEGEBEN", "VERBUCHT", "STORNIERT"]),
                QueryResultFeld("brutto_eur", QueryFeldTyp.DECIMAL, False, "Bruttobetrag EUR"),
                QueryResultFeld("netto_eur", QueryFeldTyp.DECIMAL, False, "Nettobetrag EUR nach Abzuegen"),
                QueryResultFeld("menge_tonnen", QueryFeldTyp.DECIMAL, False, "Menge in Tonnen"),
                QueryResultFeld("fruchtart", QueryFeldTyp.STRING, False, "Fruchtart-Code (WW/SG/RA/KM/ZR)"),
                QueryResultFeld("qualitaet", QueryFeldTyp.DICT, True, "Qualitaetswerte (feuchte_pct, hl_gewicht, protein_pct)"),
                QueryResultFeld("nebenkosten", QueryFeldTyp.LIST, True, "Nebenkostenpositionen"),
                QueryResultFeld("audit_hash", QueryFeldTyp.STRING, True, "SHA-256 Audit-Hash"),
                QueryResultFeld("kampagne", QueryFeldTyp.STRING, True, "Erntekampagne"),
                QueryResultFeld("erstellt_am", QueryFeldTyp.DATETIME, False, "Erstellungszeitpunkt"),
                QueryResultFeld("freigegeben_am", QueryFeldTyp.DATETIME, True, "Freigabezeitpunkt"),
            ],
        ),

        # ---------------------------------------------------------------
        # wareneingang
        # ---------------------------------------------------------------
        QueryContract(
            query_id="agrar.wareneingang.list",
            prozess_key="wareneingang",
            beschreibung="Liste Wareneingaenge (Wiegescheine) fuer Annahme-Uebersicht",
            felder=[
                QueryResultFeld("wiegeschein_nr", QueryFeldTyp.STRING, False, "Wiegeschein-Nummer"),
                QueryResultFeld("lieferant_id", QueryFeldTyp.STRING, False, "Lieferant-Referenz"),
                QueryResultFeld("datum", QueryFeldTyp.DATE, False, "Annahmedatum ISO-8601"),
                QueryResultFeld("brutto_kg", QueryFeldTyp.DECIMAL, False, "Bruttgewicht in kg"),
                QueryResultFeld("netto_tonnen", QueryFeldTyp.DECIMAL, False, "Nettogewicht in Tonnen"),
                QueryResultFeld("fruchtart", QueryFeldTyp.STRING, False, "Fruchtart-Code"),
                QueryResultFeld("status", QueryFeldTyp.ENUM, False, "Annahme-Status",
                                enum_werte=["AUSSTEHEND", "ANGENOMMEN", "ABGELEHNT", "VERBUCHT"]),
            ],
        ),

        # ---------------------------------------------------------------
        # ap_invoice (Finance)
        # ---------------------------------------------------------------
        QueryContract(
            query_id="finance.ap_invoice.list",
            prozess_key="ap_invoice",
            beschreibung="Kreditorenrechnungen fuer Genehmigungsworkflow-Uebersicht",
            felder=[
                QueryResultFeld("rechnung_id", QueryFeldTyp.STRING, False, "Rechnungs-ID"),
                QueryResultFeld("lieferant_id", QueryFeldTyp.STRING, False, "Lieferant-Referenz"),
                QueryResultFeld("rechnungsnummer", QueryFeldTyp.STRING, False, "Externe Rechnungsnummer"),
                QueryResultFeld("rechnungsdatum", QueryFeldTyp.DATE, False, "Rechnungsdatum"),
                QueryResultFeld("faelligkeitsdatum", QueryFeldTyp.DATE, True, "Faelligkeitsdatum"),
                QueryResultFeld("brutto_eur", QueryFeldTyp.DECIMAL, False, "Bruttobetrag EUR"),
                QueryResultFeld("mwst_eur", QueryFeldTyp.DECIMAL, False, "MwSt-Betrag EUR"),
                QueryResultFeld("status", QueryFeldTyp.ENUM, False, "Genehmigungsstatus",
                                enum_werte=["EINGEGANGEN", "IN_PRUEFUNG", "FREIGEGEBEN", "ABGELEHNT", "BEZAHLT"]),
                QueryResultFeld("genehmigt_von", QueryFeldTyp.STRING, True, "Genehmiger (User-ID)"),
            ],
        ),

        # ---------------------------------------------------------------
        # workflow_instance
        # ---------------------------------------------------------------
        QueryContract(
            query_id="workflow.instance.status",
            prozess_key="workflow",
            beschreibung="Workflow-Instanz-Status fuer Process-Explorer",
            felder=[
                QueryResultFeld("instanz_id", QueryFeldTyp.STRING, False, "Prozessinstanz-ID"),
                QueryResultFeld("prozess_key", QueryFeldTyp.STRING, False, "Technischer Prozess-Key"),
                QueryResultFeld("aktueller_schritt", QueryFeldTyp.STRING, False, "Aktueller Schritt-ID"),
                QueryResultFeld("status", QueryFeldTyp.ENUM, False, "Instanz-Status",
                                enum_werte=["AKTIV", "ABGESCHLOSSEN", "ABGEBROCHEN", "BLOCKIERT"]),
                QueryResultFeld("gestartet_am", QueryFeldTyp.DATETIME, False, "Startzeit ISO-8601"),
                QueryResultFeld("zuletzt_aktualisiert", QueryFeldTyp.DATETIME, False, "Letzte Aenderung"),
                QueryResultFeld("sla_stufe", QueryFeldTyp.ENUM, True, "Aktuelle SLA-Eskalationsstufe",
                                enum_werte=["OK", "WARNUNG", "KRITISCH", "BLOCKIERT"]),
                QueryResultFeld("tenant_id", QueryFeldTyp.STRING, False, "Mandant-ID"),
            ],
        ),

        # ---------------------------------------------------------------
        # sla_status
        # ---------------------------------------------------------------
        QueryContract(
            query_id="process.sla.evaluation",
            prozess_key="sla",
            beschreibung="SLA-Auswertungsergebnis fuer eine Prozessinstanz",
            felder=[
                QueryResultFeld("policy_id", QueryFeldTyp.STRING, False, "SLA-Policy-ID"),
                QueryResultFeld("prozess_key", QueryFeldTyp.STRING, False, "Prozess-Key"),
                QueryResultFeld("instanz_id", QueryFeldTyp.STRING, False, "Prozessinstanz-ID"),
                QueryResultFeld("ist_dauer_stunden", QueryFeldTyp.DECIMAL, False, "Tatsaechliche Laufzeit in Stunden"),
                QueryResultFeld("stufe", QueryFeldTyp.ENUM, False, "Eskalationsstufe",
                                enum_werte=["OK", "WARNUNG", "KRITISCH", "BLOCKIERT"]),
                QueryResultFeld("ueberschreitung_stunden", QueryFeldTyp.DECIMAL, False, "Ueberschreitung in Stunden (0 wenn OK)"),
                QueryResultFeld("eskalation_erforderlich", QueryFeldTyp.BOOL, False, "Eskalation an Teamleiter noetig"),
                QueryResultFeld("prozess_blockiert", QueryFeldTyp.BOOL, False, "Prozess ist gesperrt"),
                QueryResultFeld("benachrichtigungs_rolle", QueryFeldTyp.STRING, False, "Empfaenger der Eskalation"),
            ],
        ),

        # ---------------------------------------------------------------
        # intrastat
        # ---------------------------------------------------------------
        QueryContract(
            query_id="compliance.intrastat.meldung",
            prozess_key="intrastat_meldung",
            beschreibung="Intrastat-Meldung fuer Compliance-Uebersicht",
            felder=[
                QueryResultFeld("meldung_id", QueryFeldTyp.STRING, False, "Meldungs-ID"),
                QueryResultFeld("meldezeitraum", QueryFeldTyp.STRING, False, "Meldezeitraum YYYY-MM"),
                QueryResultFeld("meldender_ust_id", QueryFeldTyp.STRING, False, "USt-ID des Melders"),
                QueryResultFeld("positionen_count", QueryFeldTyp.INT, False, "Anzahl Warenbewegungen"),
                QueryResultFeld("gesamtwert_eur", QueryFeldTyp.DECIMAL, False, "Gesamtwarenwert EUR"),
                QueryResultFeld("validiert", QueryFeldTyp.BOOL, False, "Meldung wurde validiert"),
                QueryResultFeld("violations_count", QueryFeldTyp.INT, True, "Anzahl Validierungsfehler"),
            ],
        ),
    ]

    return QueryRegistry(contracts=contracts)
