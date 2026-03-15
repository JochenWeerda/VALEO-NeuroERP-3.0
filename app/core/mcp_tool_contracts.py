"""
MCP/OpenAPI Tool Contracts fuer externe Agenten — Wave 31 AP1/AP2

Maschinenlesbare Definitionen aller Agent-Tools des Process-Kernels.
Kompatibel mit Model Context Protocol (MCP) und OpenAPI Tool-Schemas.

Gap 017: MCP/OpenAPI Tool Contracts — 20 produktive Agent-Tools freigeschaltet.

Naming Convention: valeo_{domain}_{operation}
  domain:    agrar | finance | workflow | compliance | process | inventory
  operation: snake_case Verb-Objekt (z.B. settlement_create, sla_evaluate)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


MCP_CONTRACT_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MCPParameterTyp(str, Enum):
    STRING  = "string"
    NUMBER  = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT  = "object"
    ARRAY   = "array"


class MCPToolKategorie(str, Enum):
    LESEN       = "LESEN"        # Reine Leseoperationen (kein Approval noetig)
    SCHREIBEN   = "SCHREIBEN"    # Schreiboperationen (ggf. Approval)
    BERECHNEN   = "BERECHNEN"    # Berechnungen ohne Seiteneffekte
    VALIDIEREN  = "VALIDIEREN"   # Validierungen und Pruefungen
    ESKALIEREN  = "ESKALIEREN"   # Eskalationen und Benachrichtigungen


# ---------------------------------------------------------------------------
# AP1: MCPToolParameter + MCPToolContract
# ---------------------------------------------------------------------------

@dataclass
class MCPToolParameter:
    """Definition eines einzelnen Tool-Parameters (OpenAPI Schema-kompatibel)."""
    name: str
    typ: MCPParameterTyp
    beschreibung: str
    pflicht: bool
    beispiel: Optional[Any] = None
    enum_werte: Optional[list[str]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    def as_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "type": self.typ.value,
            "description": self.beschreibung,
            "required": self.pflicht,
        }
        if self.beispiel is not None:
            d["example"] = self.beispiel
        if self.enum_werte:
            d["enum"] = self.enum_werte
        if self.minimum is not None:
            d["minimum"] = self.minimum
        if self.maximum is not None:
            d["maximum"] = self.maximum
        return d

    def as_json_schema(self) -> dict:
        """OpenAPI/JSON-Schema-kompatible Darstellung."""
        s: dict = {"type": self.typ.value, "description": self.beschreibung}
        if self.enum_werte:
            s["enum"] = self.enum_werte
        if self.minimum is not None:
            s["minimum"] = self.minimum
        if self.maximum is not None:
            s["maximum"] = self.maximum
        return s


@dataclass
class MCPToolContract:
    """
    Verbindlicher Contract fuer ein Agent-Tool.

    tool_name folgt der Konvention: valeo_{domain}_{operation}
    Kompatibel mit MCP ToolDefinition und OpenAPI operationId.
    """
    tool_name: str
    domain: str
    operation: str
    beschreibung: str
    kategorie: MCPToolKategorie
    parameter: list[MCPToolParameter] = field(default_factory=list)
    output_beschreibung: str = ""
    requires_approval: bool = False        # True wenn menschliche Freigabe noetig
    api_endpoint: Optional[str] = None     # REST-Endpunkt der das Tool implementiert
    schema_version: int = MCP_CONTRACT_SCHEMA_VERSION

    def validate_name(self) -> bool:
        """Prueft ob tool_name der valeo_{domain}_{operation}-Konvention entspricht."""
        parts = self.tool_name.split("_", 2)
        return (
            len(parts) >= 3
            and parts[0] == "valeo"
            and parts[1] == self.domain
            and len(parts[2]) > 0
        )

    @property
    def pflicht_parameter(self) -> list[MCPToolParameter]:
        return [p for p in self.parameter if p.pflicht]

    @property
    def optionale_parameter(self) -> list[MCPToolParameter]:
        return [p for p in self.parameter if not p.pflicht]

    def as_mcp_tool(self) -> dict:
        """MCP ToolDefinition-Format."""
        props = {p.name: p.as_json_schema() for p in self.parameter}
        required = [p.name for p in self.pflicht_parameter]
        return {
            "name": self.tool_name,
            "description": self.beschreibung,
            "inputSchema": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        }

    def as_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "domain": self.domain,
            "operation": self.operation,
            "beschreibung": self.beschreibung,
            "kategorie": self.kategorie.value,
            "convention_valid": self.validate_name(),
            "requires_approval": self.requires_approval,
            "api_endpoint": self.api_endpoint,
            "parameter_count": len(self.parameter),
            "pflicht_parameter": [p.name for p in self.pflicht_parameter],
            "optionale_parameter": [p.name for p in self.optionale_parameter],
            "output_beschreibung": self.output_beschreibung,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP2: MCPToolRegistry
# ---------------------------------------------------------------------------

@dataclass
class MCPToolRegistry:
    """Registry aller definierten MCPToolContracts."""
    tools: list[MCPToolContract] = field(default_factory=list)
    schema_version: int = MCP_CONTRACT_SCHEMA_VERSION

    def by_domain(self, domain: str) -> list[MCPToolContract]:
        return [t for t in self.tools if t.domain == domain]

    def by_tool_name(self, tool_name: str) -> Optional[MCPToolContract]:
        for t in self.tools:
            if t.tool_name == tool_name:
                return t
        return None

    def by_kategorie(self, kategorie: MCPToolKategorie) -> list[MCPToolContract]:
        return [t for t in self.tools if t.kategorie == kategorie]

    def validate_all_names(self) -> list[str]:
        """Gibt tool_names zurueck, die nicht der Konvention entsprechen."""
        return [t.tool_name for t in self.tools if not t.validate_name()]

    def as_mcp_tools(self) -> list[dict]:
        """Alle Tools im MCP ToolDefinition-Format."""
        return [t.as_mcp_tool() for t in self.tools]

    def as_dict(self) -> dict:
        return {
            "tool_count": len(self.tools),
            "domains": sorted({t.domain for t in self.tools}),
            "convention_violations": self.validate_all_names(),
            "tools": [t.as_dict() for t in self.tools],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Hilfsfunktionen fuer haeufige Parametertypen
# ---------------------------------------------------------------------------

def _p_str(name: str, desc: str, pflicht: bool = True, beispiel: Any = None) -> MCPToolParameter:
    return MCPToolParameter(name, MCPParameterTyp.STRING, desc, pflicht, beispiel)

def _p_num(name: str, desc: str, pflicht: bool = True,
           minimum: Optional[float] = None, maximum: Optional[float] = None,
           beispiel: Any = None) -> MCPToolParameter:
    return MCPToolParameter(name, MCPParameterTyp.NUMBER, desc, pflicht, beispiel,
                            minimum=minimum, maximum=maximum)

def _p_int(name: str, desc: str, pflicht: bool = False, beispiel: Any = None) -> MCPToolParameter:
    return MCPToolParameter(name, MCPParameterTyp.INTEGER, desc, pflicht, beispiel)

def _p_bool(name: str, desc: str, pflicht: bool = False) -> MCPToolParameter:
    return MCPToolParameter(name, MCPParameterTyp.BOOLEAN, desc, pflicht)

def _p_enum(name: str, desc: str, werte: list[str], pflicht: bool = True,
            beispiel: Any = None) -> MCPToolParameter:
    return MCPToolParameter(name, MCPParameterTyp.STRING, desc, pflicht, beispiel,
                            enum_werte=werte)


# ---------------------------------------------------------------------------
# AP1: get_process_kernel_mcp_tools()
# ---------------------------------------------------------------------------

def get_process_kernel_mcp_tools() -> MCPToolRegistry:
    """
    Liefert alle verbindlichen MCP Tool Contracts des Process-Kernels.

    Mindestens 20 Tools in 6 Domains:
      agrar (6), finance (5), workflow (4), compliance (3), process (3), inventory (2)
    """
    tools: list[MCPToolContract] = [

        # ---------------------------------------------------------------
        # Domain: agrar (6 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_agrar_settlement_list",
            domain="agrar",
            operation="settlement_list",
            beschreibung="Listet Agrar-Settlement-Instanzen mit optionalem Status-Filter",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/agrar/settlements",
            output_beschreibung="Liste von Settlement-Summaries (id, status, betrag, menge)",
            parameter=[
                _p_enum("status", "Filter nach Prozessstatus",
                        ["OFFEN", "IN_PRUEFUNG", "FREIGEGEBEN", "VERBUCHT", "STORNIERT"],
                        pflicht=False),
                _p_str("kampagne", "Erntekampagne-Filter z.B. '2024'", pflicht=False),
                _p_int("limit", "Max. Ergebnisse (default 50, max 500)", False, 50),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_agrar_settlement_get",
            domain="agrar",
            operation="settlement_get",
            beschreibung="Ruft Detail einer Agrar-Settlement-Instanz ab",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/agrar/settlements/{settlement_id}",
            output_beschreibung="Vollstaendige Settlement-Detail inkl. Qualitaet, Nebenkosten, Audit-Hash",
            parameter=[
                _p_str("settlement_id", "Settlement-ID", True, "SET-2024-001"),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_agrar_settlement_approve",
            domain="agrar",
            operation="settlement_approve",
            beschreibung="Erteilt Freigabe fuer ein Settlement (4-Augen-Prinzip)",
            kategorie=MCPToolKategorie.SCHREIBEN,
            requires_approval=True,
            api_endpoint="POST /api/v1/agrar/settlements/{settlement_id}/approve",
            output_beschreibung="Aktualisierter Settlement-Status + Freigabe-Timestamp",
            parameter=[
                _p_str("settlement_id", "Settlement-ID", True),
                _p_str("begruendung", "Freigabe-Begruendung fuer Audit-Trail", True),
                _p_num("betrag_eur", "Erwarteter Bruttobetrag zur Verifikation", True, minimum=0),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_agrar_sla_evaluate",
            domain="agrar",
            operation="sla_evaluate",
            beschreibung="Wertet SLA-Status einer Prozessinstanz aus",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="GET /api/v1/process/sla/eskalationen/{prozess_key}",
            output_beschreibung="SLA-Auswertung: Stufe, Ueberschreitung, Eskalations-Erfordernis",
            parameter=[
                _p_str("prozess_key", "Prozess-Key z.B. 'agrar_settlement'", True),
                _p_num("ist_dauer_stunden", "Tatsaechliche Laufzeit in Stunden", True, minimum=0),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_agrar_kampagne_list",
            domain="agrar",
            operation="kampagne_list",
            beschreibung="Listet verfuegbare Kampagnen-Vorlagen und aktive Kampagnen",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/process/kampagnen/vorlagen",
            output_beschreibung="Liste von KampagnenVorlagen (typ, cn8_code, meilensteine)",
            parameter=[
                _p_enum("typ", "Kampagnen-Typ Filter",
                        ["WINTERWEIZEN", "SOMMERGERSTE", "RAPS", "KOERNERMAIS", "ZUCKERRUEBEN"],
                        pflicht=False),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_agrar_qualitaet_validate",
            domain="agrar",
            operation="qualitaet_validate",
            beschreibung="Prueft Qualitaetsparameter gegen Kampagnen-Schwellenwerte",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/agrar/qualitaet/validate",
            output_beschreibung="Validierungsergebnis: ok/warning/reject pro Parameter",
            parameter=[
                _p_str("fruchtart", "Fruchtart-Code", True, "WW"),
                _p_num("feuchte_pct", "Feuchtegehalt in %", True, minimum=0, maximum=50),
                _p_num("hl_gewicht", "Hektolitergewicht kg/hl", False, minimum=50, maximum=90),
                _p_num("protein_pct", "Proteingehalt in %", False, minimum=0, maximum=25),
            ],
        ),

        # ---------------------------------------------------------------
        # Domain: finance (5 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_finance_ap_invoice_list",
            domain="finance",
            operation="ap_invoice_list",
            beschreibung="Listet Kreditorenrechnungen mit Status-Filter fuer Genehmigungsworkflow",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/finance/ap-invoices",
            output_beschreibung="Liste Kreditorenrechnungen (id, lieferant, betrag, status, faellig)",
            parameter=[
                _p_enum("status", "Genehmigungsstatus-Filter",
                        ["EINGEGANGEN", "IN_PRUEFUNG", "FREIGEGEBEN", "ABGELEHNT", "BEZAHLT"],
                        pflicht=False),
                _p_str("lieferant_id", "Filter nach Lieferant-ID", False),
                _p_bool("faellig_heute", "Nur heute faellige Rechnungen"),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_finance_payment_run_create",
            domain="finance",
            operation="payment_run_create",
            beschreibung="Erstellt einen SEPA-Zahlungslauf fuer freigegebene Rechnungen",
            kategorie=MCPToolKategorie.SCHREIBEN,
            requires_approval=True,
            api_endpoint="POST /api/v1/finance/payment-runs",
            output_beschreibung="Zahlungslauf-ID, Anzahl Positionen, Gesamtbetrag",
            parameter=[
                _p_str("faellig_bis", "ISO-8601 Datum: Rechnungen bis wann einschliessen", True, "2024-10-31"),
                _p_enum("zahlungsart", "SEPA-Zahlungsart",
                        ["UEBERWEISUNG", "LASTSCHRIFT"], True),
                _p_num("max_betrag_eur", "Maximaler Gesamtbetrag des Laufs", False, minimum=0),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_finance_open_items_get",
            domain="finance",
            operation="open_items_get",
            beschreibung="Ruft offene Posten (Debitoren oder Kreditoren) ab",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/finance/open-items",
            output_beschreibung="Liste offener Posten mit Betrag, Faelligkeit, Mahnstufe",
            parameter=[
                _p_enum("typ", "Debitor oder Kreditor", ["debitor", "kreditor"], True),
                _p_str("partner_id", "Geschaeftspartner-ID", False),
                _p_bool("nur_ueberfaellig", "Nur ueberfaellige Posten"),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_finance_dunning_generate",
            domain="finance",
            operation="dunning_generate",
            beschreibung="Erzeugt Mahnvorschlag fuer offene Debitoren-Posten",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="POST /api/v1/finance/dunning/generate",
            output_beschreibung="Mahnvorschlag: betroffene Positionen, Mahnstufen, Gesamtbetrag",
            parameter=[
                _p_str("debitor_id", "Debitor-ID (leer = alle faelligen)", False),
                _p_int("mahnstufe_max", "Maximale Mahnstufe (1-3)", False, 3),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_finance_sla_check",
            domain="finance",
            operation="sla_check",
            beschreibung="Prueft SLO-Compliance fuer einen Finance-Dienst",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/process/slo/check",
            output_beschreibung="SLO-Compliance-Status: ERFUELLT/TOLERANZBEREICH/VERLETZT/UNBEKANNT",
            parameter=[
                _p_str("slo_id", "SLO-Definitions-ID", True, "SLO-API-VERF-01"),
                _p_num("ist_wert", "Gemessener Ist-Wert", True),
            ],
        ),

        # ---------------------------------------------------------------
        # Domain: workflow (4 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_workflow_instance_status",
            domain="workflow",
            operation="instance_status",
            beschreibung="Ruft aktuellen Status einer Workflow-Instanz ab",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/workflow/instances/{instanz_id}",
            output_beschreibung="Instanz-Status, aktueller Schritt, SLA-Stufe, History",
            parameter=[
                _p_str("instanz_id", "Workflow-Instanz-ID", True, "inst-20240901-0042"),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_workflow_step_transition",
            domain="workflow",
            operation="step_transition",
            beschreibung="Fuehrt Zustandsuebergang in einer Workflow-Instanz aus",
            kategorie=MCPToolKategorie.SCHREIBEN,
            requires_approval=False,
            api_endpoint="POST /api/v1/workflow/instances/{instanz_id}/transition",
            output_beschreibung="Neuer Schritt-Status, naechste erlaubte Transitionen",
            parameter=[
                _p_str("instanz_id", "Workflow-Instanz-ID", True),
                _p_str("zu_schritt_id", "Ziel-Schritt-ID", True, "AS-04-PREISFESTSTELLUNG"),
                _p_str("begruendung", "Uebergangs-Begruendung fuer Audit", False),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_workflow_approval_evaluate",
            domain="workflow",
            operation="approval_evaluate",
            beschreibung="Bewertet ob eine Agent-Aktion menschliche Freigabe erfordert",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/process/agent/approval-evaluate",
            output_beschreibung="Risikostufe, requires_human_approval, Freigabe-Rolle",
            parameter=[
                _p_str("aktions_typ", "Typ der geplanten Aktion", True, "SETTLEMENT_FREIGABE"),
                _p_num("betrag_eur", "Transaktionsbetrag fuer Schwellenwert-Bewertung",
                        False, minimum=0),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_workflow_migration_check",
            domain="workflow",
            operation="migration_check",
            beschreibung="Prueft Breaking Changes eines Workflow-Migrationspfads",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/process/workflow-migration/check",
            output_beschreibung="SAFE/WARNUNG/BREAKING + Liste der Verletzungen",
            parameter=[
                _p_str("prozess_key", "Workflow-Prozess-Key", True, "agrar_settlement"),
                _p_str("von_version", "Quell-Version", True, "1.0.0"),
                _p_str("zu_version", "Ziel-Version", True, "1.1.0"),
            ],
        ),

        # ---------------------------------------------------------------
        # Domain: compliance (3 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_compliance_intrastat_validate",
            domain="compliance",
            operation="intrastat_validate",
            beschreibung="Validiert eine Intrastat-Meldung vor der Einreichung",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="GET /api/v1/compliance/intrastat/meldungen/{meldung_id}/validate",
            output_beschreibung="Validierungsergebnis: valid/invalid, Violations-Liste",
            parameter=[
                _p_str("meldung_id", "Intrastat-Meldungs-ID", True),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_compliance_policy_evaluate",
            domain="compliance",
            operation="policy_evaluate",
            beschreibung="Wertet Policy-Regelset gegen einen Prozesskontext aus",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="POST /api/v1/process/policy-rules/evaluate",
            output_beschreibung="Wirksame Aktion (ERLAUBT/ABGELEHNT/WARNUNG/ESKALATION) + Treffer-Liste",
            parameter=[
                _p_str("prozess_key", "Prozess-Key fuer Policy-Lookup", True, "agrar_settlement"),
                _p_num("brutto_eur", "Transaktionsbetrag EUR", False, minimum=0),
                _p_num("netto_tonnen", "Nettogewicht Tonnen", False, minimum=0),
                _p_str("lieferant_typ", "Lieferantentyp (MITGLIED/FREMDBETRIEB)", False),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_compliance_audit_hash_verify",
            domain="compliance",
            operation="audit_hash_verify",
            beschreibung="Verifiziert SHA-256 Audit-Hash eines Abrechnungsdokuments",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/compliance/audit/verify",
            output_beschreibung="hash_ok: bool, Dokument-ID, Verifikationszeitpunkt",
            parameter=[
                _p_str("dokument_id", "Dokument-/Datensatz-ID", True),
                _p_str("erwarteter_hash", "Erwarteter SHA-256 Hash (64 Hex-Zeichen)", True),
            ],
        ),

        # ---------------------------------------------------------------
        # Domain: process (3 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_process_command_dispatch",
            domain="process",
            operation="command_dispatch",
            beschreibung="Dispatcht einen Business-Command an den zustaendigen Handler",
            kategorie=MCPToolKategorie.SCHREIBEN,
            requires_approval=False,
            api_endpoint="POST /api/v1/process/commands/dispatch",
            output_beschreibung="Command-Ergebnis: success, aggregat_id, idempotency_key",
            parameter=[
                _p_str("command_typ", "Command-Typ aus dem Katalog", True, "FREIGABE_ERTEILEN"),
                _p_str("aggregat_id", "Ziel-Aggregat-ID", True),
                _p_str("idempotency_key", "Eindeutiger Idempotenz-Schluessel fuer sichere Retries", True),
                _p_str("ausfuehrender", "User-ID oder Agent-ID", True),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_process_slo_check",
            domain="process",
            operation="slo_check",
            beschreibung="Prueft Einhaltung eines Service-Level-Objectives",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="POST /api/v1/process/slo/check",
            output_beschreibung="SLO-Compliance: ERFUELLT/TOLERANZBEREICH/VERLETZT/UNBEKANNT + Abweichung",
            parameter=[
                _p_str("slo_id", "SLO-ID aus dem Registry", True, "SLO-API-VERF-01"),
                _p_num("ist_wert", "Gemessener Ist-Wert (Einheit je SLO-Typ)", True),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_process_data_quality_validate",
            domain="process",
            operation="data_quality_validate",
            beschreibung="Prueft Stammdaten-Datensatz gegen Qualitaetsregeln",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/process/data-quality/validate",
            output_beschreibung="Validierungsergebnis: valid/invalid, Violations mit Code und Feld",
            parameter=[
                _p_str("entity_typ", "Entitaetstyp (LIEFERANT/KONTRAKT/WIEGESCHEIN/ARTIKEL)", True),
                _p_str("datensatz_json", "JSON-serialisierter Datensatz", True),
            ],
        ),

        # ---------------------------------------------------------------
        # Domain: inventory (2 Tools)
        # ---------------------------------------------------------------
        MCPToolContract(
            tool_name="valeo_inventory_silo_status",
            domain="inventory",
            operation="silo_status",
            beschreibung="Ruft aktuellen Silo-Bestand und Qualitaets-Snapshot ab",
            kategorie=MCPToolKategorie.LESEN,
            api_endpoint="GET /api/v1/silo/{silo_id}/status",
            output_beschreibung="Silo-Bestand: menge_tonnen, fruchtart, feuchte_avg, letzte_Messung",
            parameter=[
                _p_str("silo_id", "Silo-ID", True, "SILO-A1"),
                _p_bool("mit_qualitaet", "Qualitaets-Snapshot einschliessen"),
            ],
        ),

        MCPToolContract(
            tool_name="valeo_inventory_bestand_check",
            domain="inventory",
            operation="bestand_check",
            beschreibung="Prueft verfuegbaren Lagerbestand fuer eine Fruchtart",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="GET /api/v1/lager/bestand",
            output_beschreibung="Verfuegbarer Bestand in Tonnen, reservierte Menge, freie Kapazitaet",
            parameter=[
                _p_str("fruchtart", "Fruchtart-Code", True, "WW"),
                _p_str("standort_id", "Standort-ID (leer = alle Standorte)", False),
            ],
        ),
    ]

    return MCPToolRegistry(tools=tools)
