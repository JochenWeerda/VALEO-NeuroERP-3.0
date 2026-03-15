"""
Offene Integrationsfähigkeit für Agenten — Wave 37, Gap 048
Agent-Tool-Registrierung, Capability-Matching, Use-Case-Contracts
für externe Agenten (Perplexity, GPT-Plugins, Claude Tools usw.).

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class AgentKategorie(str, Enum):
    RECHERCHE = "RECHERCHE"
    ANALYSE = "ANALYSE"
    TRANSAKTION = "TRANSAKTION"
    BENACHRICHTIGUNG = "BENACHRICHTIGUNG"
    DOKUMENT = "DOKUMENT"
    INTEGRATION = "INTEGRATION"
    COMPLIANCE = "COMPLIANCE"
    REPORTING = "REPORTING"


class AgentAutorisierungsStufe(str, Enum):
    OEFFENTLICH = "OEFFENTLICH"       # kein Token erforderlich
    AUTHENTIFIZIERT = "AUTHENTIFIZIERT"  # Bearer-Token erforderlich
    BERECHTIGT = "BERECHTIGT"         # Role-Check erforderlich
    PRIVILEGIERT = "PRIVILEGIERT"     # Admin + Audit-Log erforderlich


class ToolParameterTyp(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    ARRAY = "ARRAY"
    OBJECT = "OBJECT"
    ENUM = "ENUM"


class AgentUseCaseStatus(str, Enum):
    AKTIV = "AKTIV"
    BETA = "BETA"
    GEPLANT = "GEPLANT"
    DEAKTIVIERT = "DEAKTIVIERT"


class CapabilityMatchResultTyp(str, Enum):
    VOLLSTAENDIGER_MATCH = "VOLLSTAENDIGER_MATCH"
    TEILWEISER_MATCH = "TEILWEISER_MATCH"
    KEIN_MATCH = "KEIN_MATCH"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ToolParameter:
    """Parameter-Definition für ein Agent-Tool."""
    name: str
    typ: ToolParameterTyp
    beschreibung: str
    pflichtfeld: bool = True
    enum_werte: list[str] = field(default_factory=list)
    beispiel: str = ""

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "typ": self.typ.value,
            "beschreibung": self.beschreibung,
            "pflichtfeld": self.pflichtfeld,
        }
        if self.enum_werte:
            d["enum_werte"] = self.enum_werte
        if self.beispiel:
            d["beispiel"] = self.beispiel
        return d


@dataclass
class AgentTool:
    """Registriertes Agent-Tool mit Capability-Deklaration."""
    tool_id: str
    name: str
    kategorie: AgentKategorie
    autorisierung: AgentAutorisierungsStufe
    beschreibung: str
    endpunkt: str
    methode: str   # GET | POST
    parameter: list[ToolParameter] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    rate_limit_pro_minute: int = 60
    idempotent: bool = True
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "kategorie": self.kategorie.value,
            "autorisierung": self.autorisierung.value,
            "beschreibung": self.beschreibung,
            "endpunkt": self.endpunkt,
            "methode": self.methode,
            "parameter": [p.as_dict() for p in self.parameter],
            "capabilities": self.capabilities,
            "rate_limit_pro_minute": self.rate_limit_pro_minute,
            "idempotent": self.idempotent,
            "schema_version": self.schema_version,
        }


@dataclass
class AgentUseCase:
    """Beschreibt einen konkreten Agenten-Anwendungsfall."""
    use_case_id: str
    name: str
    beschreibung: str
    beteiligte_tools: list[str]   # tool_ids
    benoetigte_capabilities: list[str]
    status: AgentUseCaseStatus
    beispiel_prompt: str = ""
    erwartetes_ergebnis: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "use_case_id": self.use_case_id,
            "name": self.name,
            "beschreibung": self.beschreibung,
            "beteiligte_tools": self.beteiligte_tools,
            "benoetigte_capabilities": self.benoetigte_capabilities,
            "status": self.status.value,
            "beispiel_prompt": self.beispiel_prompt,
            "erwartetes_ergebnis": self.erwartetes_ergebnis,
        }


@dataclass
class CapabilityMatchErgebnis:
    """Ergebnis eines Capability-Matching-Requests."""
    angefragte_capabilities: list[str]
    gefundene_tools: list[AgentTool]
    fehlende_capabilities: list[str]
    match_typ: CapabilityMatchResultTyp
    match_score: float   # 0.0–1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "angefragte_capabilities": self.angefragte_capabilities,
            "gefundene_tools": [t.as_dict() for t in self.gefundene_tools],
            "fehlende_capabilities": self.fehlende_capabilities,
            "match_typ": self.match_typ.value,
            "match_score": round(self.match_score, 4),
            "gefundene_tool_ids": [t.tool_id for t in self.gefundene_tools],
        }


# ---------------------------------------------------------------------------
# Capability-Matching
# ---------------------------------------------------------------------------

def match_capabilities(
    angefragte: list[str],
    tools: list[AgentTool] | None = None,
) -> CapabilityMatchErgebnis:
    """
    Findet Agent-Tools, die die angefragten Capabilities abdecken.

    Matching-Logik:
    - Eine Capability gilt als abgedeckt, wenn mindestens ein Tool sie listet.
    - match_score = abgedeckte / angefragte (0.0–1.0)
    - VOLLSTAENDIGER_MATCH: score == 1.0
    - TEILWEISER_MATCH:     0.0 < score < 1.0
    - KEIN_MATCH:           score == 0.0
    """
    if tools is None:
        tools = get_default_agent_tools()

    angefragte_lower = [c.lower() for c in angefragte]
    abgedeckt: set[str] = set()
    relevante_tools: list[AgentTool] = []

    for tool in tools:
        tool_caps_lower = {c.lower() for c in tool.capabilities}
        treffer = [c for c in angefragte_lower if c in tool_caps_lower]
        if treffer:
            abgedeckt.update(treffer)
            if tool not in relevante_tools:
                relevante_tools.append(tool)

    fehlende = [c for c in angefragte if c.lower() not in abgedeckt]
    score = len(abgedeckt) / len(angefragte) if angefragte else 0.0

    if score == 1.0:
        match_typ = CapabilityMatchResultTyp.VOLLSTAENDIGER_MATCH
    elif score > 0.0:
        match_typ = CapabilityMatchResultTyp.TEILWEISER_MATCH
    else:
        match_typ = CapabilityMatchResultTyp.KEIN_MATCH

    return CapabilityMatchErgebnis(
        angefragte_capabilities=angefragte,
        gefundene_tools=relevante_tools,
        fehlende_capabilities=fehlende,
        match_typ=match_typ,
        match_score=score,
    )


# ---------------------------------------------------------------------------
# Standard-Tools und Use-Cases
# ---------------------------------------------------------------------------

def get_default_agent_tools() -> list[AgentTool]:
    """Gibt die Standard-Agent-Tools des VALEO-ERP zurück (10 Tools)."""
    return [
        AgentTool(
            tool_id="AT-001",
            name="kontrakt_suche",
            kategorie=AgentKategorie.RECHERCHE,
            autorisierung=AgentAutorisierungsStufe.AUTHENTIFIZIERT,
            beschreibung="Sucht Agrar-Kontrakte nach Lieferant, Ware, Datum und Status.",
            endpunkt="/api/v1/agrar/kontrakte",
            methode="GET",
            parameter=[
                ToolParameter("lieferant_id", ToolParameterTyp.STRING, "Lieferanten-ID", pflichtfeld=False),
                ToolParameter("ware", ToolParameterTyp.STRING, "Warenbezeichnung", pflichtfeld=False),
                ToolParameter("status", ToolParameterTyp.ENUM, "Kontraktstatus",
                              pflichtfeld=False, enum_werte=["OFFEN", "TEILERFUELLT", "ERFUELLT"]),
            ],
            capabilities=["kontrakt_lesen", "lieferant_suche", "agrar_recherche"],
            rate_limit_pro_minute=120,
        ),
        AgentTool(
            tool_id="AT-002",
            name="settlement_berechnen",
            kategorie=AgentKategorie.TRANSAKTION,
            autorisierung=AgentAutorisierungsStufe.BERECHTIGT,
            beschreibung="Berechnet Settlement-Vorschau für Wiegeschein-Positionen.",
            endpunkt="/api/v1/agrar/settlement/preview",
            methode="POST",
            parameter=[
                ToolParameter("wiegeschein_id", ToolParameterTyp.STRING, "Wiegeschein-ID"),
                ToolParameter("kontrakt_id", ToolParameterTyp.STRING, "Kontrakt-ID"),
            ],
            capabilities=["settlement_berechnen", "preis_ermitteln", "agrar_transaktion"],
            idempotent=True,
        ),
        AgentTool(
            tool_id="AT-003",
            name="qualitaet_auslesen",
            kategorie=AgentKategorie.RECHERCHE,
            autorisierung=AgentAutorisierungsStufe.AUTHENTIFIZIERT,
            beschreibung="Liest Qualitätswerte (Feuchte, Protein, Fallzahl) für eine Lieferung.",
            endpunkt="/api/v1/agrar/qualitaet",
            methode="GET",
            parameter=[
                ToolParameter("lieferung_id", ToolParameterTyp.STRING, "Lieferungs-ID"),
            ],
            capabilities=["qualitaet_lesen", "agrar_recherche", "laborwerte_abrufen"],
            rate_limit_pro_minute=200,
        ),
        AgentTool(
            tool_id="AT-004",
            name="rechnung_klassifizieren",
            kategorie=AgentKategorie.DOKUMENT,
            autorisierung=AgentAutorisierungsStufe.AUTHENTIFIZIERT,
            beschreibung="Klassifiziert und extrahiert Felder aus einem Eingangsbeleg via OCR.",
            endpunkt="/api/v1/process/dms/classify",
            methode="POST",
            parameter=[
                ToolParameter("dokument_id", ToolParameterTyp.STRING, "DMS-Dokument-ID"),
                ToolParameter("volltext", ToolParameterTyp.STRING, "OCR-Volltext des Belegs"),
            ],
            capabilities=["beleg_klassifizieren", "ocr_extraktion", "dms_integration"],
            idempotent=True,
        ),
        AgentTool(
            tool_id="AT-005",
            name="zahlungslauf_status",
            kategorie=AgentKategorie.RECHERCHE,
            autorisierung=AgentAutorisierungsStufe.BERECHTIGT,
            beschreibung="Gibt Status und Positionen eines Zahlungslaufs zurück.",
            endpunkt="/api/v1/finance/payment-runs",
            methode="GET",
            parameter=[
                ToolParameter("run_id", ToolParameterTyp.STRING, "Zahlungslauf-ID", pflichtfeld=False),
                ToolParameter("status", ToolParameterTyp.ENUM, "Status-Filter",
                              pflichtfeld=False, enum_werte=["ENTWURF", "FREIGEGEBEN", "AUSGEFUEHRT"]),
            ],
            capabilities=["zahlungslauf_lesen", "finance_recherche"],
        ),
        AgentTool(
            tool_id="AT-006",
            name="compliance_pruefen",
            kategorie=AgentKategorie.COMPLIANCE,
            autorisierung=AgentAutorisierungsStufe.BERECHTIGT,
            beschreibung="Prüft Compliance-Status für Lieferant oder Vorgang.",
            endpunkt="/api/v1/compliance",
            methode="POST",
            parameter=[
                ToolParameter("objekt_typ", ToolParameterTyp.ENUM, "Prüfobjekt-Typ",
                              enum_werte=["LIEFERANT", "VORGANG", "BENUTZER"]),
                ToolParameter("objekt_id", ToolParameterTyp.STRING, "ID des Prüfobjekts"),
            ],
            capabilities=["compliance_pruefen", "audit_lesen"],
            rate_limit_pro_minute=30,
            idempotent=True,
        ),
        AgentTool(
            tool_id="AT-007",
            name="silo_belegung_abrufen",
            kategorie=AgentKategorie.RECHERCHE,
            autorisierung=AgentAutorisierungsStufe.AUTHENTIFIZIERT,
            beschreibung="Gibt aktuelle Silobelegung mit Ware, Menge und Qualitätssegment zurück.",
            endpunkt="/api/v1/silo/belegung",
            methode="GET",
            parameter=[
                ToolParameter("silo_id", ToolParameterTyp.STRING, "Silo-ID", pflichtfeld=False),
                ToolParameter("ware", ToolParameterTyp.STRING, "Warenfilter", pflichtfeld=False),
            ],
            capabilities=["silo_lesen", "lager_recherche", "agrar_recherche"],
            rate_limit_pro_minute=200,
        ),
        AgentTool(
            tool_id="AT-008",
            name="preisindex_abrufen",
            kategorie=AgentKategorie.ANALYSE,
            autorisierung=AgentAutorisierungsStufe.AUTHENTIFIZIERT,
            beschreibung="Gibt aktuelle und historische Marktpreisindizes für Agrarwaren zurück.",
            endpunkt="/api/v1/agrar/preisindex",
            methode="GET",
            parameter=[
                ToolParameter("ware", ToolParameterTyp.STRING, "Warenbezeichnung"),
                ToolParameter("von", ToolParameterTyp.STRING, "Startdatum ISO-8601", pflichtfeld=False),
                ToolParameter("bis", ToolParameterTyp.STRING, "Enddatum ISO-8601", pflichtfeld=False),
            ],
            capabilities=["preis_ermitteln", "marktdaten_abrufen", "agrar_analyse"],
            rate_limit_pro_minute=60,
            idempotent=True,
        ),
        AgentTool(
            tool_id="AT-009",
            name="benachrichtigung_senden",
            kategorie=AgentKategorie.BENACHRICHTIGUNG,
            autorisierung=AgentAutorisierungsStufe.BERECHTIGT,
            beschreibung="Sendet eine In-App- oder E-Mail-Benachrichtigung an einen Benutzer.",
            endpunkt="/api/v1/notifications/send",
            methode="POST",
            parameter=[
                ToolParameter("empfaenger_id", ToolParameterTyp.STRING, "Benutzer-ID"),
                ToolParameter("betreff", ToolParameterTyp.STRING, "Betreff der Nachricht"),
                ToolParameter("nachricht", ToolParameterTyp.STRING, "Nachrichtentext"),
                ToolParameter("kanal", ToolParameterTyp.ENUM, "Übertragungskanal",
                              pflichtfeld=False, enum_werte=["IN_APP", "EMAIL", "BEIDE"],
                              beispiel="IN_APP"),
            ],
            capabilities=["benachrichtigung_senden", "workflow_benachrichtigung"],
            idempotent=False,
            rate_limit_pro_minute=20,
        ),
        AgentTool(
            tool_id="AT-010",
            name="report_generieren",
            kategorie=AgentKategorie.REPORTING,
            autorisierung=AgentAutorisierungsStufe.BERECHTIGT,
            beschreibung="Startet die asynchrone Generierung eines Reports (Ernte, Abrechnung, Compliance).",
            endpunkt="/api/v1/process/jobs/enqueue",
            methode="POST",
            parameter=[
                ToolParameter("report_typ", ToolParameterTyp.ENUM, "Reporttyp",
                              enum_werte=["ERNTEKAMPAGNE", "SETTLEMENT", "COMPLIANCE", "BETRIEBSKENNZAHLEN"]),
                ToolParameter("zeitraum_von", ToolParameterTyp.STRING, "Von-Datum ISO-8601"),
                ToolParameter("zeitraum_bis", ToolParameterTyp.STRING, "Bis-Datum ISO-8601"),
            ],
            capabilities=["report_generieren", "hintergrundjob_starten", "reporting"],
            idempotent=True,
            rate_limit_pro_minute=10,
        ),
    ]


def get_default_agent_use_cases() -> list[AgentUseCase]:
    """Gibt die 10 Standard-Use-Cases für externe Agenten zurück."""
    return [
        AgentUseCase(
            use_case_id="UC-001",
            name="Kontrakt-Auskunft",
            beschreibung="Agent beantwortet Anfragen zu offenen Kontrakten eines Lieferanten.",
            beteiligte_tools=["AT-001"],
            benoetigte_capabilities=["kontrakt_lesen", "agrar_recherche"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Welche offenen Kontrakte gibt es für Lieferant L-42?",
            erwartetes_ergebnis="Liste offener Kontrakte mit Menge, Ware und Status",
        ),
        AgentUseCase(
            use_case_id="UC-002",
            name="Settlement-Vorschau",
            beschreibung="Agent berechnet Settlement-Vorschau auf Basis eines Wiegescheins.",
            beteiligte_tools=["AT-002", "AT-003"],
            benoetigte_capabilities=["settlement_berechnen", "qualitaet_lesen"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Berechne Settlement für Wiegeschein WS-2026-0042.",
            erwartetes_ergebnis="Settlement-Vorschau mit Preis, Abzügen und Auszahlungsbetrag",
        ),
        AgentUseCase(
            use_case_id="UC-003",
            name="Eingangsbeleg-Klassifikation",
            beschreibung="Agent klassifiziert und extrahiert Felder aus gescannten Belegen.",
            beteiligte_tools=["AT-004"],
            benoetigte_capabilities=["beleg_klassifizieren", "ocr_extraktion"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Klassifiziere dieses gescannte Dokument und extrahiere Rechnungsdaten.",
            erwartetes_ergebnis="Belegtyp + extrahierte Felder mit Confidence",
        ),
        AgentUseCase(
            use_case_id="UC-004",
            name="Compliance-Schnellprüfung",
            beschreibung="Agent prüft Compliance-Status eines Lieferanten vor Vertragsabschluss.",
            beteiligte_tools=["AT-006"],
            benoetigte_capabilities=["compliance_pruefen"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Ist Lieferant L-17 compliance-freigegeben?",
            erwartetes_ergebnis="Compliance-Status mit offenen Punkten",
        ),
        AgentUseCase(
            use_case_id="UC-005",
            name="Silobelegung Überblick",
            beschreibung="Agent gibt Lagerüberblick für Dispositionsentscheidungen.",
            beteiligte_tools=["AT-007"],
            benoetigte_capabilities=["silo_lesen", "lager_recherche"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Wie ist die aktuelle Weizenkapazität in Silo S-03?",
            erwartetes_ergebnis="Belegung, freie Kapazität und Qualitätssegmente",
        ),
        AgentUseCase(
            use_case_id="UC-006",
            name="Marktpreis-Abfrage",
            beschreibung="Agent ruft aktuelle Marktpreisindizes für Preisverhandlungen ab.",
            beteiligte_tools=["AT-008"],
            benoetigte_capabilities=["preis_ermitteln", "marktdaten_abrufen"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Wie ist der aktuelle MATIF-Weizenpreis?",
            erwartetes_ergebnis="Tagespreis + 30-Tage-Trend",
        ),
        AgentUseCase(
            use_case_id="UC-007",
            name="Zahlungslauf-Monitor",
            beschreibung="Agent überwacht Zahlungsläufe und eskaliert bei Verzögerungen.",
            beteiligte_tools=["AT-005", "AT-009"],
            benoetigte_capabilities=["zahlungslauf_lesen", "benachrichtigung_senden"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Informiere mich wenn Zahlungslauf ZL-2026-03 freigegeben ist.",
            erwartetes_ergebnis="Status-Update + automatische Benachrichtigung",
        ),
        AgentUseCase(
            use_case_id="UC-008",
            name="Erntekampagnen-Report",
            beschreibung="Agent erstellt automatisch den Erntekampagnen-Abschlussbericht.",
            beteiligte_tools=["AT-010"],
            benoetigte_capabilities=["report_generieren", "hintergrundjob_starten"],
            status=AgentUseCaseStatus.BETA,
            beispiel_prompt="Erstelle den Erntekampagnen-Report für Q3 2026.",
            erwartetes_ergebnis="Asynchroner Job gestartet, Report-ID zurückgegeben",
        ),
        AgentUseCase(
            use_case_id="UC-009",
            name="Qualitätsprüfung bei Annahme",
            beschreibung="Agent prüft Qualitätswerte gegen Kontraktspezifikation.",
            beteiligte_tools=["AT-001", "AT-003"],
            benoetigte_capabilities=["qualitaet_lesen", "kontrakt_lesen"],
            status=AgentUseCaseStatus.AKTIV,
            beispiel_prompt="Erfüllt Lieferung LF-2026-0088 die Kontraktanforderungen?",
            erwartetes_ergebnis="Qualitätsdelta + Abzugsberechnung",
        ),
        AgentUseCase(
            use_case_id="UC-010",
            name="Vollautomatische Belegverarbeitung",
            beschreibung="Agent verarbeitet Eingangsbelege komplett: OCR → Klassifikation → Buchungsvorschlag.",
            beteiligte_tools=["AT-004", "AT-009"],
            benoetigte_capabilities=["ocr_extraktion", "beleg_klassifizieren", "benachrichtigung_senden"],
            status=AgentUseCaseStatus.BETA,
            beispiel_prompt="Verarbeite alle neuen Eingangsrechnungen aus dem DMS.",
            erwartetes_ergebnis="Extrahierte Felder + Buchungsvorschlag + Benachrichtigung",
        ),
    ]
