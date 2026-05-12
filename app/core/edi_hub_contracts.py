"""
edi_hub_contracts.py — EDI/API Hub Contracts (Wave 36, Gap 043)

Modelliert EDI-Partner, Nachrichtentypen, Uebertragungskanäle und
Acknowledgment-Tracking als Core-Contracts ohne echten EDI-Stack.

Gap 043: EDI/API Hub fuer Kunden/Lieferanten/Behoerden — >=80% Dokumentenaustausch digital.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EDIStandard(str, Enum):
    """EDI-Nachrichtenstandard."""
    EDIFACT     = "EDIFACT"      # UN/EDIFACT (Landhandel, Behörden)
    ANSI_X12    = "ANSI_X12"     # X12 (US-Markt)
    IDOC        = "IDOC"         # SAP IDoc
    XML_UBL     = "XML_UBL"      # Universal Business Language
    JSON_API    = "JSON_API"     # REST/JSON (moderne APIs)
    CSV_FLAT    = "CSV_FLAT"     # Flach-Datei (Legacy)


class EDINachrichtenTyp(str, Enum):
    """EDIFACT/EDI-Nachrichtentypen relevant fuer Landhandel."""
    ORDERS      = "ORDERS"       # Bestellung
    ORDRSP      = "ORDRSP"       # Bestellantwort
    DESADV      = "DESADV"       # Lieferavis
    INVOIC      = "INVOIC"       # Rechnung
    REMADV      = "REMADV"       # Zahlungsavis
    CONTRL      = "CONTRL"       # Technische Quittung
    APERAK      = "APERAK"       # Anwendungsquittung
    PRICAT      = "PRICAT"       # Preiskatalog
    INVRPT      = "INVRPT"       # Lagerbestandsbericht
    MSCONS      = "MSCONS"       # Messdaten (Silos, IoT)


class EDIUebertragungsKanal(str, Enum):
    """Uebertragungskanal fuer EDI-Nachrichten."""
    AS2         = "AS2"          # Applicability Statement 2
    SFTP        = "SFTP"         # Secure FTP
    REST_WEBHOOK = "REST_WEBHOOK" # Webhook (moderne Partner)
    EMAIL       = "EMAIL"        # E-Mail (Legacy)
    NATS        = "NATS"         # Interner NATS JetStream
    VAN         = "VAN"          # Value Added Network


class EDINachrichtenStatus(str, Enum):
    """Verarbeitungsstatus einer EDI-Nachricht."""
    PENDING     = "PENDING"      # Warte auf Verarbeitung
    GESENDET    = "GESENDET"     # Uebertragen
    QUITTIERT   = "QUITTIERT"   # Partner hat CONTRL/APERAK gesendet
    VERARBEITET = "VERARBEITET"  # Fachlich verarbeitet
    FEHLER      = "FEHLER"       # Verarbeitungsfehler
    ABGELEHNT   = "ABGELEHNT"   # Partner hat abgelehnt


class EDIPartnerTyp(str, Enum):
    """Typ des EDI-Partners."""
    LIEFERANT   = "LIEFERANT"
    KUNDE       = "KUNDE"
    BEHOERDE    = "BEHOERDE"     # Zoll, Statistikamt, etc.
    SPEDITEUR   = "SPEDITEUR"
    BANK        = "BANK"


# ---------------------------------------------------------------------------
# EDI-Partner
# ---------------------------------------------------------------------------

@dataclass
class EDIPartner:
    """
    Definition eines EDI-Partners mit Verbindungsparametern.
    """
    partner_id: str
    name: str
    typ: EDIPartnerTyp
    edi_standard: EDIStandard
    kanal: EDIUebertragungsKanal
    interchangeId: str              # GLN, ILN oder interne ID
    unterstuetzte_nachrichten: list[EDINachrichtenTyp] = field(default_factory=list)
    aktiv: bool = True
    kontakt_email: str = ""
    beschreibung: str = ""

    def as_dict(self) -> dict:
        return {
            "partner_id": self.partner_id,
            "name": self.name,
            "typ": self.typ.value,
            "edi_standard": self.edi_standard.value,
            "kanal": self.kanal.value,
            "interchangeId": self.interchangeId,
            "unterstuetzte_nachrichten": [n.value for n in self.unterstuetzte_nachrichten],
            "aktiv": self.aktiv,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# EDI-Nachricht
# ---------------------------------------------------------------------------

@dataclass
class EDINachricht:
    """
    Repr. einer konkreten EDI-Nachricht (gesendet oder empfangen).
    """
    nachricht_id: str
    partner_id: str
    typ: EDINachrichtenTyp
    standard: EDIStandard
    richtung: str                   # "AUSGEHEND" | "EINGEHEND"
    status: EDINachrichtenStatus
    erstellt_am: datetime
    referenz_dokument_id: str = ""  # z.B. Bestell-ID, Lieferschein-ID
    payload_groesse_bytes: int = 0
    fehler_meldung: str = ""
    quittiert_am: datetime | None = None
    schema_version: int = 1

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in {
            EDINachrichtenStatus.QUITTIERT,
            EDINachrichtenStatus.VERARBEITET,
            EDINachrichtenStatus.FEHLER,
            EDINachrichtenStatus.ABGELEHNT,
        }

    def as_dict(self) -> dict:
        return {
            "nachricht_id": self.nachricht_id,
            "partner_id": self.partner_id,
            "typ": self.typ.value,
            "standard": self.standard.value,
            "richtung": self.richtung,
            "status": self.status.value,
            "erstellt_am": self.erstellt_am.isoformat(),
            "referenz_dokument_id": self.referenz_dokument_id,
            "payload_groesse_bytes": self.payload_groesse_bytes,
            "fehler_meldung": self.fehler_meldung,
            "quittiert_am": self.quittiert_am.isoformat() if self.quittiert_am else None,
            "ist_abgeschlossen": self.ist_abgeschlossen,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Acknowledgment-Tracking
# ---------------------------------------------------------------------------

@dataclass
class EDIAcknowledgmentResult:
    """Ergebnis der Quittungsauswertung fuer eine gesendete Nachricht."""
    nachricht_id: str
    partner_id: str
    erwartet_quittung: bool
    quittung_erhalten: bool
    quittungs_typ: str              # "CONTRL" | "APERAK" | "NONE"
    sla_ok: bool                    # Quittung innerhalb SLA-Zeit?
    wartezeit_sekunden: float | None
    meldung: str
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "nachricht_id": self.nachricht_id,
            "partner_id": self.partner_id,
            "erwartet_quittung": self.erwartet_quittung,
            "quittung_erhalten": self.quittung_erhalten,
            "quittungs_typ": self.quittungs_typ,
            "sla_ok": self.sla_ok,
            "wartezeit_sekunden": self.wartezeit_sekunden,
            "meldung": self.meldung,
            "schema_version": self.schema_version,
        }


# SLA-Zeiten pro Kanal (in Sekunden)
_ACK_SLA_SEKUNDEN: dict[EDIUebertragungsKanal, int] = {
    EDIUebertragungsKanal.AS2:          300,    # 5 Minuten
    EDIUebertragungsKanal.REST_WEBHOOK: 30,     # 30 Sekunden
    EDIUebertragungsKanal.SFTP:         3600,   # 1 Stunde
    EDIUebertragungsKanal.EMAIL:        86400,  # 24 Stunden
    EDIUebertragungsKanal.NATS:         10,     # 10 Sekunden
    EDIUebertragungsKanal.VAN:          7200,   # 2 Stunden
}

# Nachrichten die eine Quittung erfordern
_QUITTUNGSPFLICHTIG: set[EDINachrichtenTyp] = {
    EDINachrichtenTyp.ORDERS,
    EDINachrichtenTyp.INVOIC,
    EDINachrichtenTyp.DESADV,
    EDINachrichtenTyp.REMADV,
}


def evaluate_ack_status(
    nachricht: EDINachricht,
    kanal: EDIUebertragungsKanal,
    jetzt: datetime | None = None,
) -> EDIAcknowledgmentResult:
    """
    Bewertet den Quittungsstatus einer gesendeten Nachricht.

    Args:
        nachricht: Die gesendete Nachricht.
        kanal: Uebertragungskanal (bestimmt SLA).
        jetzt: Aktueller Zeitpunkt fuer SLA-Berechnung.

    Returns:
        EDIAcknowledgmentResult.
    """
    jetzt = jetzt or datetime.now(timezone.utc)
    erwartet = nachricht.typ in _QUITTUNGSPFLICHTIG
    erhalten = nachricht.status in {
        EDINachrichtenStatus.QUITTIERT,
        EDINachrichtenStatus.VERARBEITET,
    }

    if not erwartet:
        return EDIAcknowledgmentResult(
            nachricht_id=nachricht.nachricht_id,
            partner_id=nachricht.partner_id,
            erwartet_quittung=False,
            quittung_erhalten=False,
            quittungs_typ="NONE",
            sla_ok=True,
            wartezeit_sekunden=None,
            meldung=f"Nachrichtentyp {nachricht.typ.value} benoetigt keine Quittung.",
        )

    sla = _ACK_SLA_SEKUNDEN.get(kanal, 3600)
    erstellt = nachricht.erstellt_am
    if erstellt.tzinfo is None:
        erstellt = erstellt.replace(tzinfo=timezone.utc)
    wartezeit = (jetzt - erstellt).total_seconds()

    if erhalten:
        quittiert = nachricht.quittiert_am or jetzt
        if quittiert.tzinfo is None:
            quittiert = quittiert.replace(tzinfo=timezone.utc)
        tatsaechliche_wartezeit = (quittiert - erstellt).total_seconds()
        return EDIAcknowledgmentResult(
            nachricht_id=nachricht.nachricht_id,
            partner_id=nachricht.partner_id,
            erwartet_quittung=True,
            quittung_erhalten=True,
            quittungs_typ="CONTRL",
            sla_ok=tatsaechliche_wartezeit <= sla,
            wartezeit_sekunden=tatsaechliche_wartezeit,
            meldung=f"Quittung erhalten nach {tatsaechliche_wartezeit:.0f}s (SLA: {sla}s).",
        )

    sla_ok = wartezeit <= sla
    return EDIAcknowledgmentResult(
        nachricht_id=nachricht.nachricht_id,
        partner_id=nachricht.partner_id,
        erwartet_quittung=True,
        quittung_erhalten=False,
        quittungs_typ="CONTRL",
        sla_ok=sla_ok,
        wartezeit_sekunden=wartezeit,
        meldung=(
            f"Quittung ausstehend nach {wartezeit:.0f}s "
            f"({'SLA OK' if sla_ok else 'SLA VERLETZT'}, Limit: {sla}s)."
        ),
    )


# ---------------------------------------------------------------------------
# Default-EDI-Partner
# ---------------------------------------------------------------------------

def get_default_edi_partners() -> list[EDIPartner]:
    """Liefert einen Beispiel-Partnerkatalog fuer einen Landhandels-Mandanten."""
    return [
        EDIPartner(
            partner_id="EP-LFS-001",
            name="Raiffeisen-Lagerhaus GmbH",
            typ=EDIPartnerTyp.LIEFERANT,
            edi_standard=EDIStandard.EDIFACT,
            kanal=EDIUebertragungsKanal.AS2,
            interchangeId="4012345000001",
            unterstuetzte_nachrichten=[
                EDINachrichtenTyp.ORDERS,
                EDINachrichtenTyp.ORDRSP,
                EDINachrichtenTyp.DESADV,
                EDINachrichtenTyp.INVOIC,
            ],
            beschreibung="Hauptlieferant Getreide — AS2 ueber zentralen Hub",
        ),
        EDIPartner(
            partner_id="EP-KDE-001",
            name="Metro AG",
            typ=EDIPartnerTyp.KUNDE,
            edi_standard=EDIStandard.EDIFACT,
            kanal=EDIUebertragungsKanal.SFTP,
            interchangeId="4000260000000",
            unterstuetzte_nachrichten=[
                EDINachrichtenTyp.ORDERS,
                EDINachrichtenTyp.INVOIC,
                EDINachrichtenTyp.REMADV,
            ],
            beschreibung="Grosshaendler-Kunde — SFTP taeglich 06:00/18:00",
        ),
        EDIPartner(
            partner_id="EP-BEH-001",
            name="Bundesamt fuer Statistik",
            typ=EDIPartnerTyp.BEHOERDE,
            edi_standard=EDIStandard.XML_UBL,
            kanal=EDIUebertragungsKanal.REST_WEBHOOK,
            interchangeId="DE-DESTATIS-001",
            unterstuetzte_nachrichten=[
                EDINachrichtenTyp.INVRPT,
                EDINachrichtenTyp.MSCONS,
            ],
            beschreibung="Statistische Meldungen Getreidevorraete (§ 15 EG-VO)",
        ),
        EDIPartner(
            partner_id="EP-SPD-001",
            name="DB Cargo AG",
            typ=EDIPartnerTyp.SPEDITEUR,
            edi_standard=EDIStandard.EDIFACT,
            kanal=EDIUebertragungsKanal.VAN,
            interchangeId="4010112000002",
            unterstuetzte_nachrichten=[
                EDINachrichtenTyp.DESADV,
                EDINachrichtenTyp.MSCONS,
            ],
            beschreibung="Bahn-Spediteur fuer Schuttgut-Transporte",
        ),
        EDIPartner(
            partner_id="EP-INT-001",
            name="VALEO Interne Integration",
            typ=EDIPartnerTyp.LIEFERANT,
            edi_standard=EDIStandard.JSON_API,
            kanal=EDIUebertragungsKanal.NATS,
            interchangeId="VALEO-INTERNAL",
            unterstuetzte_nachrichten=list(EDINachrichtenTyp),
            beschreibung="Interner NATS-Adapter fuer alle Nachrichtentypen",
        ),
    ]


# ---------------------------------------------------------------------------
# Nachrichtentyp-Katalog
# ---------------------------------------------------------------------------

@dataclass
class EDINachrichtenKatalogEintrag:
    """Katalog-Eintrag fuer einen EDI-Nachrichtentyp."""
    typ: EDINachrichtenTyp
    beschreibung: str
    standard: EDIStandard
    quittungspflichtig: bool
    typischer_ausloeser: str

    def as_dict(self) -> dict:
        return {
            "typ": self.typ.value,
            "beschreibung": self.beschreibung,
            "standard": self.standard.value,
            "quittungspflichtig": self.quittungspflichtig,
            "typischer_ausloeser": self.typischer_ausloeser,
        }


# ---------------------------------------------------------------------------
# Wave 78 Extensions: DigitalExchangeCoverage, PartnerApiKey, EdiHubAuftrag,
# EdiHubMonitor (Gap 043 — KPI: >=80% Dokumentenaustausch digital)
# ---------------------------------------------------------------------------

# Standards/Kanäle die als "digital" zählen (kein Papier/Fax/Email-Batch)
_DIGITALE_STANDARDS: set[EDIStandard] = {
    EDIStandard.EDIFACT,
    EDIStandard.XML_UBL,
    EDIStandard.JSON_API,
    EDIStandard.ANSI_X12,
    EDIStandard.IDOC,
}


@dataclass
class DigitalExchangeCoverage:
    """
    KPI-Messung: Anteil digitaler Dokumentenaustausch.

    Gap 043 — Ziel: >=80% aller Dokumente digital (EDIFACT oder REST_API).
    CSV_FLAT und EMAIL gelten als nicht-digital.
    """
    gesamt_dokumente: int
    digital_dokumente: int
    periode_beschreibung: str = "letzte 30 Tage"

    @property
    def coverage_pct(self) -> float:
        if self.gesamt_dokumente == 0:
            return 0.0
        return round(self.digital_dokumente / self.gesamt_dokumente * 100, 2)

    @property
    def kpi_erfuellt(self) -> bool:
        """Gap-043-KPI: >=80% digital."""
        return self.coverage_pct >= 80.0

    @property
    def fehlend_fuer_kpi(self) -> int:
        """Wie viele nicht-digitale Dokumente müssen noch migriert werden?"""
        if self.kpi_erfuellt:
            return 0
        ziel = int(self.gesamt_dokumente * 0.80)
        return max(0, ziel - self.digital_dokumente)

    def as_dict(self) -> dict:
        return {
            "gesamt_dokumente": self.gesamt_dokumente,
            "digital_dokumente": self.digital_dokumente,
            "coverage_pct": self.coverage_pct,
            "kpi_erfuellt": self.kpi_erfuellt,
            "fehlend_fuer_kpi": self.fehlend_fuer_kpi,
            "periode_beschreibung": self.periode_beschreibung,
        }


def evaluate_digital_coverage(
    nachrichten: list["EDINachricht"],
    partner_map: dict[str, "EDIPartner"],
) -> DigitalExchangeCoverage:
    """
    Berechnet den Digitalisierungsgrad anhand tatsächlicher Nachrichten.

    Nachrichten von Partnern mit digitalem Standard zählen als digital.
    """
    gesamt = len(nachrichten)
    digital = 0
    for msg in nachrichten:
        partner = partner_map.get(msg.partner_id)
        if partner and partner.edi_standard in _DIGITALE_STANDARDS:
            digital += 1
        elif msg.standard in _DIGITALE_STANDARDS:
            digital += 1
    return DigitalExchangeCoverage(
        gesamt_dokumente=gesamt,
        digital_dokumente=digital,
    )


# ---------------------------------------------------------------------------
# PartnerApiKey — REST-API-Schlüssel für non-EDIFACT Partner
# ---------------------------------------------------------------------------

@dataclass
class PartnerApiKey:
    """
    API-Schlüssel für REST-Partner.

    Der Klartext-Key wird niemals gespeichert — nur der SHA-256-Hash.
    Ablaufdatum None = unbegrenzt gültig.
    """
    key_id: str
    partner_id: str
    key_hash: str           # SHA-256 hex digest des Klartext-Keys
    erstellt_am: datetime
    laeuft_ab_am: datetime | None = None
    aktiv: bool = True
    beschreibung: str = ""

    @property
    def ist_abgelaufen(self) -> bool:
        if self.laeuft_ab_am is None:
            return False
        ablauf = self.laeuft_ab_am
        if ablauf.tzinfo is None:
            ablauf = ablauf.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > ablauf

    @property
    def ist_gueltig(self) -> bool:
        return self.aktiv and not self.ist_abgelaufen

    def verify_hash(self, kandidat_hash: str) -> bool:
        """Prüft einen vorgelegten Hash gegen den gespeicherten Hash."""
        return self.key_hash == kandidat_hash and self.ist_gueltig

    def as_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "partner_id": self.partner_id,
            "key_hash": self.key_hash,
            "erstellt_am": self.erstellt_am.isoformat(),
            "laeuft_ab_am": self.laeuft_ab_am.isoformat() if self.laeuft_ab_am else None,
            "aktiv": self.aktiv,
            "ist_gueltig": self.ist_gueltig,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# EdiHubAuftrag — Ausgehende Dispatch-Queue
# ---------------------------------------------------------------------------

@dataclass
class EdiHubAuftrag:
    """
    Eintrag in der ausgehenden EDI/API-Dispatch-Queue.

    Verwaltet Retry-Logik und Statusübergänge für ausgehende Nachrichten.
    """
    auftrag_id: str
    partner_id: str
    nachrichtentyp: EDINachrichtenTyp
    prioritaet: int                         # 1 = höchste, 5 = niedrigste
    payload_ref: str                        # Referenz auf Quell-Dokument (Bestell-ID etc.)
    erstellt_am: datetime
    versuche: int = 0
    max_versuche: int = 3
    letzter_fehler: str = ""
    status: EDINachrichtenStatus = EDINachrichtenStatus.PENDING

    def __post_init__(self) -> None:
        if not (1 <= self.prioritaet <= 5):
            raise ValueError(f"Prioritaet muss 1–5 sein, nicht {self.prioritaet}")
        if self.max_versuche < 1:
            raise ValueError("max_versuche muss >= 1 sein")

    @property
    def kann_wiederholt_werden(self) -> bool:
        return (
            self.status == EDINachrichtenStatus.FEHLER
            and self.versuche < self.max_versuche
        )

    def versuch_starten(self) -> None:
        """Erhöht Versuchszähler und setzt Status auf GESENDET."""
        self.versuche += 1
        self.status = EDINachrichtenStatus.GESENDET
        self.letzter_fehler = ""

    def versuch_fehlgeschlagen(self, fehler: str) -> None:
        self.status = EDINachrichtenStatus.FEHLER
        self.letzter_fehler = fehler

    def versuch_erfolgreich(self) -> None:
        self.status = EDINachrichtenStatus.QUITTIERT

    def as_dict(self) -> dict:
        return {
            "auftrag_id": self.auftrag_id,
            "partner_id": self.partner_id,
            "nachrichtentyp": self.nachrichtentyp.value,
            "prioritaet": self.prioritaet,
            "payload_ref": self.payload_ref,
            "erstellt_am": self.erstellt_am.isoformat(),
            "versuche": self.versuche,
            "max_versuche": self.max_versuche,
            "letzter_fehler": self.letzter_fehler,
            "status": self.status.value,
            "kann_wiederholt_werden": self.kann_wiederholt_werden,
        }


# ---------------------------------------------------------------------------
# EdiHubMonitor — Betriebszustand des EDI/API Hubs
# ---------------------------------------------------------------------------

@dataclass
class EdiHubMonitor:
    """
    Monitoring-Snapshot des EDI/API Hubs.

    Fasst Betriebskennzahlen und KPI-Status zusammen für
    Health-Dashboard und Alert-Auswertung.
    """
    snapshot_zeitpunkt: datetime
    aktive_partner: int
    nachrichten_gesamt_24h: int
    nachrichten_fehler_24h: int
    sla_verletzungen_24h: int
    ausstehende_auftraege: int
    digital_coverage: DigitalExchangeCoverage

    @property
    def fehlerquote_pct(self) -> float:
        if self.nachrichten_gesamt_24h == 0:
            return 0.0
        return round(
            self.nachrichten_fehler_24h / self.nachrichten_gesamt_24h * 100, 2
        )

    @property
    def hub_gesund(self) -> bool:
        """
        Hub gilt als gesund wenn:
        - KPI >=80% digital erfüllt
        - Fehlerquote <5%
        - Keine SLA-Verletzungen in den letzten 24h
        """
        return (
            self.digital_coverage.kpi_erfuellt
            and self.fehlerquote_pct < 5.0
            and self.sla_verletzungen_24h == 0
        )

    @property
    def alert_level(self) -> str:
        """'OK' | 'WARN' | 'CRITICAL'."""
        if self.hub_gesund:
            return "OK"
        if self.fehlerquote_pct >= 20.0 or self.sla_verletzungen_24h >= 5:
            return "CRITICAL"
        return "WARN"

    def as_dict(self) -> dict:
        return {
            "snapshot_zeitpunkt": self.snapshot_zeitpunkt.isoformat(),
            "aktive_partner": self.aktive_partner,
            "nachrichten_gesamt_24h": self.nachrichten_gesamt_24h,
            "nachrichten_fehler_24h": self.nachrichten_fehler_24h,
            "fehlerquote_pct": self.fehlerquote_pct,
            "sla_verletzungen_24h": self.sla_verletzungen_24h,
            "ausstehende_auftraege": self.ausstehende_auftraege,
            "digital_coverage": self.digital_coverage.as_dict(),
            "hub_gesund": self.hub_gesund,
            "alert_level": self.alert_level,
        }


def get_edi_nachrichtentyp_katalog() -> list[EDINachrichtenKatalogEintrag]:
    """Liefert den Katalog aller unterstuetzten EDI-Nachrichtentypen."""
    return [
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.ORDERS, "Bestellung an Lieferant", EDIStandard.EDIFACT,
            True, "Bestellvorschlag freigegeben",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.ORDRSP, "Bestellantwort vom Lieferant", EDIStandard.EDIFACT,
            False, "Lieferant bestaetigt/aendert Bestellung",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.DESADV, "Lieferavis", EDIStandard.EDIFACT,
            True, "LKW-Abgang beim Lieferanten",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.INVOIC, "Rechnung", EDIStandard.EDIFACT,
            True, "Settlement freigegeben oder Eingangsrechnung erfasst",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.REMADV, "Zahlungsavis", EDIStandard.EDIFACT,
            True, "Zahlungslauf ausgefuehrt",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.CONTRL, "Technische Quittung", EDIStandard.EDIFACT,
            False, "Automatisch bei Empfang jeder EDIFACT-Nachricht",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.PRICAT, "Preiskatalog", EDIStandard.EDIFACT,
            False, "Preisaktualisierung durch Lieferant",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.INVRPT, "Lagerbestandsbericht", EDIStandard.XML_UBL,
            False, "Taeglich / bei Behoerdenanforderung",
        ),
        EDINachrichtenKatalogEintrag(
            EDINachrichtenTyp.MSCONS, "Messdaten-Konsignation", EDIStandard.EDIFACT,
            False, "IoT-Silo-Sensordaten, Fuellstand-Monitoring",
        ),
    ]
