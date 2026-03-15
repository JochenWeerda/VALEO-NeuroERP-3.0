"""
Human-in-the-loop AI-Freigaben — Wave 30 AP1/AP2

Jede Agent-Aktion wird nach Risikostufe klassifiziert.
HOCH und KRITISCH erfordern zwingend menschliche Freigabe.
Alle Entscheidungen werden als unveraenderliche ApprovalRecords gespeichert (Audit-Trail).

Gap 015: Human-in-the-loop Freigaben fuer AI Aktionen — 100% AI-Aktionen mit Approval-Trail.

Risikostufen:
  NIEDRIG   — Lesende/informative Aktionen, kein Freigabe-Erfordernis
  MITTEL    — Schreibende Aktionen mit kleinem Betrag, Freigabe empfohlen
  HOCH      — Schreibende Aktionen mit grossem Betrag, Freigabe erforderlich
  KRITISCH  — Irreversible oder gefahrenträchtige Aktionen, Freigabe erzwungen
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


APPROVAL_GATE_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ApprovalRisikostufe(str, Enum):
    NIEDRIG   = "NIEDRIG"
    MITTEL    = "MITTEL"
    HOCH      = "HOCH"
    KRITISCH  = "KRITISCH"


class ApprovalDecision(str, Enum):
    GENEHMIGT  = "GENEHMIGT"
    ABGELEHNT  = "ABGELEHNT"
    TIMEOUT    = "TIMEOUT"       # Freigabefrist abgelaufen
    ESKALIERT  = "ESKALIERT"     # An uebergeordnete Instanz eskaliert


class ApprovalAusloserTyp(str, Enum):
    """Was hat die Risikobewertung ausgeloest."""
    BETRAG_SCHWELLE       = "BETRAG_SCHWELLE"
    IRREVERSIBLE_AKTION   = "IRREVERSIBLE_AKTION"
    EXTERNE_PARTEI        = "EXTERNE_PARTEI"
    MASSENDATEN           = "MASSENDATEN"
    REGULATORISCH         = "REGULATORISCH"
    SICHERHEITSKRITISCH   = "SICHERHEITSKRITISCH"
    STANDARD              = "STANDARD"


# ---------------------------------------------------------------------------
# AP1: ApprovalRegel + HumanApprovalRequirement
# ---------------------------------------------------------------------------

@dataclass
class ApprovalRegel:
    """
    Einzelne Bewertungsregel fuer den Approval-Gate.

    Wenn alle Bedingungen zutreffen, wird die Risikostufe angewendet.
    Regeln werden nach Prioritaet absteigend ausgewertet (hoeher = wichtiger).
    """
    regel_id: str
    bezeichnung: str
    risiko_stufe: ApprovalRisikostufe
    ausloser_typ: ApprovalAusloserTyp
    begruendung: str
    prioritaet: int = 100          # Hoeher = staerkere Gewichtung
    aktions_typen: list[str] = field(default_factory=list)    # Leere Liste = gilt fuer alle
    betrag_schwelle_eur: Optional[float] = None                # None = kein Betrags-Check
    massendaten_schwelle: Optional[int] = None                 # Anzahl betroffener Datensaetze

    def matches(self, aktions_typ: str, kontext: dict[str, Any]) -> bool:
        """Prueft ob die Regel auf die Aktion zutrifft."""
        # Aktionstyp-Filter
        if self.aktions_typen and aktions_typ not in self.aktions_typen:
            return False
        # Betrags-Schwelle
        if self.betrag_schwelle_eur is not None:
            betrag = kontext.get("betrag_eur", 0)
            try:
                if float(betrag) < self.betrag_schwelle_eur:
                    return False
            except (TypeError, ValueError):
                return False
        # Massendaten-Schwelle
        if self.massendaten_schwelle is not None:
            datensaetze = kontext.get("datensaetze_count", 0)
            try:
                if int(datensaetze) < self.massendaten_schwelle:
                    return False
            except (TypeError, ValueError):
                return False
        return True

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "bezeichnung": self.bezeichnung,
            "risiko_stufe": self.risiko_stufe.value,
            "ausloser_typ": self.ausloser_typ.value,
            "begruendung": self.begruendung,
            "prioritaet": self.prioritaet,
            "aktions_typen": self.aktions_typen,
            "betrag_schwelle_eur": self.betrag_schwelle_eur,
            "massendaten_schwelle": self.massendaten_schwelle,
        }


@dataclass
class HumanApprovalRequirement:
    """Ergebnis der Risikobewertung einer Agent-Aktion."""
    aktions_typ: str
    risiko_stufe: ApprovalRisikostufe
    requires_human_approval: bool
    ausgeloeste_regel_id: Optional[str]        # None wenn kein Treffer (NIEDRIG-Default)
    ausloser_typ: ApprovalAusloserTyp
    begruendung: str
    freigabe_rolle: str                        # Wer darf freigeben
    schema_version: int = APPROVAL_GATE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "aktions_typ": self.aktions_typ,
            "risiko_stufe": self.risiko_stufe.value,
            "requires_human_approval": self.requires_human_approval,
            "ausgeloeste_regel_id": self.ausgeloeste_regel_id,
            "ausloser_typ": self.ausloser_typ.value,
            "begruendung": self.begruendung,
            "freigabe_rolle": self.freigabe_rolle,
            "schema_version": self.schema_version,
        }


# Risikostufen die menschliche Freigabe erfordern
_FREIGABE_PFLICHT_STUFEN = {ApprovalRisikostufe.HOCH, ApprovalRisikostufe.KRITISCH}

# Freigabe-Rollen je Risikostufe
_FREIGABE_ROLLEN: dict[ApprovalRisikostufe, str] = {
    ApprovalRisikostufe.NIEDRIG:  "agent_autonom",
    ApprovalRisikostufe.MITTEL:   "sachbearbeiter",
    ApprovalRisikostufe.HOCH:     "teamleiter",
    ApprovalRisikostufe.KRITISCH: "geschaeftsfuehrung",
}

# Rang fuer Risikostufen (hoeher = kritischer)
_RISIKO_RANG: dict[ApprovalRisikostufe, int] = {
    ApprovalRisikostufe.NIEDRIG:  1,
    ApprovalRisikostufe.MITTEL:   2,
    ApprovalRisikostufe.HOCH:     3,
    ApprovalRisikostufe.KRITISCH: 4,
}


def evaluate_approval_requirement(
    aktions_typ: str,
    kontext: dict[str, Any],
    regeln: list[ApprovalRegel],
) -> HumanApprovalRequirement:
    """
    Klassifiziert eine Agent-Aktion nach Risikostufe.

    - Alle passenden Regeln werden gesammelt.
    - Die hoechste Risikostufe gewinnt.
    - Wenn keine Regel passt → NIEDRIG (keine menschliche Freigabe).
    - HOCH und KRITISCH setzen requires_human_approval=True.
    """
    treffer: list[tuple[int, ApprovalRegel]] = []  # (prioritaet, regel)

    for regel in regeln:
        if regel.matches(aktions_typ, kontext):
            treffer.append((regel.prioritaet, regel))

    if not treffer:
        return HumanApprovalRequirement(
            aktions_typ=aktions_typ,
            risiko_stufe=ApprovalRisikostufe.NIEDRIG,
            requires_human_approval=False,
            ausgeloeste_regel_id=None,
            ausloser_typ=ApprovalAusloserTyp.STANDARD,
            begruendung="Keine Bewertungsregel ausgeloest — NIEDRIG-Default",
            freigabe_rolle=_FREIGABE_ROLLEN[ApprovalRisikostufe.NIEDRIG],
        )

    # Hoechste Risikostufe bestimmen
    hoechste_stufe = max(
        (r for _, r in treffer),
        key=lambda r: _RISIKO_RANG[r.risiko_stufe],
    )

    return HumanApprovalRequirement(
        aktions_typ=aktions_typ,
        risiko_stufe=hoechste_stufe.risiko_stufe,
        requires_human_approval=hoechste_stufe.risiko_stufe in _FREIGABE_PFLICHT_STUFEN,
        ausgeloeste_regel_id=hoechste_stufe.regel_id,
        ausloser_typ=hoechste_stufe.ausloser_typ,
        begruendung=hoechste_stufe.begruendung,
        freigabe_rolle=_FREIGABE_ROLLEN[hoechste_stufe.risiko_stufe],
    )


# ---------------------------------------------------------------------------
# AP2: ApprovalRecord + record_approval_decision()
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ApprovalRecord:
    """
    Unveraenderlicher Audit-Record einer Freigabeentscheidung.

    frozen=True: Nach Erstellung nicht mehr veraenderbar (Audit-Integritaet).
    """
    record_id: str              # SHA-256 Fingerprint des Records
    aktions_typ: str
    instanz_id: str
    agent_id: str
    risiko_stufe: str           # ApprovalRisikostufe.value
    decision: str               # ApprovalDecision.value
    entschieden_von: str        # User-ID oder "system/timeout"
    entschieden_am: str         # ISO-8601 Zeitstempel
    begruendung: str
    kontext_hash: str           # SHA-256 des Kontexts zum Entscheidungszeitpunkt
    schema_version: int = APPROVAL_GATE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "aktions_typ": self.aktions_typ,
            "instanz_id": self.instanz_id,
            "agent_id": self.agent_id,
            "risiko_stufe": self.risiko_stufe,
            "decision": self.decision,
            "entschieden_von": self.entschieden_von,
            "entschieden_am": self.entschieden_am,
            "begruendung": self.begruendung,
            "kontext_hash": self.kontext_hash,
            "schema_version": self.schema_version,
        }


def _compute_kontext_hash(kontext: dict[str, Any]) -> str:
    canonical = json.dumps(kontext, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _compute_record_id(
    aktions_typ: str,
    instanz_id: str,
    agent_id: str,
    entschieden_am: str,
    decision: str,
) -> str:
    raw = f"{aktions_typ}|{instanz_id}|{agent_id}|{entschieden_am}|{decision}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def record_approval_decision(
    aktions_typ: str,
    instanz_id: str,
    agent_id: str,
    risiko_stufe: ApprovalRisikostufe,
    decision: ApprovalDecision,
    entschieden_von: str,
    begruendung: str,
    kontext: dict[str, Any],
    timestamp: Optional[datetime] = None,
) -> ApprovalRecord:
    """
    Erstellt einen unveraenderlichen Audit-Record fuer eine Freigabeentscheidung.

    Der record_id-Fingerprint ist deterministisch aus den Eingabewerten berechnet.
    kontext_hash sichert den Zustand des Kontexts zum Entscheidungszeitpunkt.
    """
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc)
    entschieden_am = timestamp.isoformat()
    record_id = _compute_record_id(aktions_typ, instanz_id, agent_id, entschieden_am, decision.value)
    kontext_hash = _compute_kontext_hash(kontext)

    return ApprovalRecord(
        record_id=record_id,
        aktions_typ=aktions_typ,
        instanz_id=instanz_id,
        agent_id=agent_id,
        risiko_stufe=risiko_stufe.value,
        decision=decision.value,
        entschieden_von=entschieden_von,
        entschieden_am=entschieden_am,
        begruendung=begruendung,
        kontext_hash=kontext_hash,
    )


# ---------------------------------------------------------------------------
# AP2: get_default_approval_rules()
# ---------------------------------------------------------------------------

def get_default_approval_rules() -> list[ApprovalRegel]:
    """
    Default-Bewertungsregeln fuer Agrar-Agent-Aktionen.

    Abdeckung: Settlement-Freigabe, Massenaenderungen, externe Transfers,
               GoBD-relevante Buchungen, Stammdatenaenderungen.
    """
    return [
        # ---------------------------------------------------------------
        # KRITISCH — Irreversible oder regul. Hochrisikoaktionen
        # ---------------------------------------------------------------
        ApprovalRegel(
            regel_id="AG-K-001",
            bezeichnung="GoBD-Belegstorno (irreversibel)",
            risiko_stufe=ApprovalRisikostufe.KRITISCH,
            ausloser_typ=ApprovalAusloserTyp.IRREVERSIBLE_AKTION,
            begruendung="Belegstorno nach GoBD nicht mehr ruecknehmbar; Vier-Augen-Pflicht",
            prioritaet=200,
            aktions_typen=["BELEG_STORNIEREN", "BUCHUNG_STORNIEREN"],
        ),
        ApprovalRegel(
            regel_id="AG-K-002",
            bezeichnung="SEPA-Massenzahlung ueber 500k EUR",
            risiko_stufe=ApprovalRisikostufe.KRITISCH,
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="SEPA-Zahlung >500k EUR erfordert Geschaftsfuehrungsfreigabe",
            prioritaet=200,
            aktions_typen=["ZAHLUNG_AUSLOESEN", "ZAHLUNGSLAUF_STARTEN"],
            betrag_schwelle_eur=500_000.0,
        ),
        ApprovalRegel(
            regel_id="AG-K-003",
            bezeichnung="Massenstammdatenaenderung (>1000 Datensaetze)",
            risiko_stufe=ApprovalRisikostufe.KRITISCH,
            ausloser_typ=ApprovalAusloserTyp.MASSENDATEN,
            begruendung="Massenhafte Stammdatenaenderung erfordert Vier-Augen-Kontrolle",
            prioritaet=190,
            aktions_typen=["STAMMDATEN_MASSENAENDERUNG", "BULK_UPDATE"],
            massendaten_schwelle=1000,
        ),

        # ---------------------------------------------------------------
        # HOCH — Schreibend, grosser Betrag oder regulatorisch
        # ---------------------------------------------------------------
        ApprovalRegel(
            regel_id="AG-H-001",
            bezeichnung="Settlement-Freigabe ab 50k EUR",
            risiko_stufe=ApprovalRisikostufe.HOCH,
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="Settlement-Auszahlung >50k EUR erfordert Teamleiter-Freigabe",
            prioritaet=150,
            aktions_typen=["SETTLEMENT_FREIGABE", "SETTLEMENT_VERBUCHEN"],
            betrag_schwelle_eur=50_000.0,
        ),
        ApprovalRegel(
            regel_id="AG-H-002",
            bezeichnung="Externe Ueberweisung an neuen Zahlungsempfaenger",
            risiko_stufe=ApprovalRisikostufe.HOCH,
            ausloser_typ=ApprovalAusloserTyp.EXTERNE_PARTEI,
            begruendung="Neue externe Zahlungsempfaenger ohne Whitelist erfordern Freigabe",
            prioritaet=150,
            aktions_typen=["ZAHLUNG_AUSLOESEN", "UEBERWEISUNG_ERSTELLEN"],
        ),
        ApprovalRegel(
            regel_id="AG-H-003",
            bezeichnung="Intrastat-Meldungseinreichung",
            risiko_stufe=ApprovalRisikostufe.HOCH,
            ausloser_typ=ApprovalAusloserTyp.REGULATORISCH,
            begruendung="Regulatorische Meldung an Behoerde erfordert explizite Freigabe",
            prioritaet=140,
            aktions_typen=["INTRASTAT_EINREICHEN", "ELSTER_UEBERTRAGEN"],
        ),

        # ---------------------------------------------------------------
        # MITTEL — Schreibend, kleiner Betrag oder interne Aktion
        # ---------------------------------------------------------------
        ApprovalRegel(
            regel_id="AG-M-001",
            bezeichnung="Settlement bis 50k EUR (Standard)",
            risiko_stufe=ApprovalRisikostufe.MITTEL,
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="Settlement-Buchung < 50k EUR: Sachbearbeiter-Freigabe empfohlen",
            prioritaet=80,
            aktions_typen=["SETTLEMENT_FREIGABE", "SETTLEMENT_VERBUCHEN"],
            betrag_schwelle_eur=1.0,   # Jede Settlement-Aktion ist mindestens MITTEL
        ),
        ApprovalRegel(
            regel_id="AG-M-002",
            bezeichnung="Kontrakt-Preis-Aenderung",
            risiko_stufe=ApprovalRisikostufe.MITTEL,
            ausloser_typ=ApprovalAusloserTyp.STANDARD,
            begruendung="Preisaenderungen am Kontrakt wirken auf laufende Berechnungen",
            prioritaet=80,
            aktions_typen=["KONTRAKT_PREIS_AENDERN"],
        ),

        # ---------------------------------------------------------------
        # NIEDRIG — Lesend oder nicht-finanziell
        # ---------------------------------------------------------------
        ApprovalRegel(
            regel_id="AG-N-001",
            bezeichnung="Lesende Abfragen (Reports, Dashboards)",
            risiko_stufe=ApprovalRisikostufe.NIEDRIG,
            ausloser_typ=ApprovalAusloserTyp.STANDARD,
            begruendung="Reine Leseoperationen benoetigen keine menschliche Freigabe",
            prioritaet=10,
            aktions_typen=[
                "REPORT_GENERIEREN", "DASHBOARD_LADEN", "EXPORT_ERSTELLEN",
                "PREISE_ABRUFEN", "BESTAND_PRUEFEN",
            ],
        ),
    ]
