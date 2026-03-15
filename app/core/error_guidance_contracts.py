"""
error_guidance_contracts.py — Error-UX / Leitsystem fuer Ausnahmefaelle (Wave 35, Gap 028)

Strukturiertes Leitsystem: Fehlerklassen -> Leitaktionen -> User-Guidance.
Ziel: 50% weniger Abbruchquote bei Fehlern durch klare Handlungsanweisungen.

Gap 028: Leitsystem fuer Ausnahmefaelle (Error UX).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FehlerKategorie(str, Enum):
    """Klassifikation des Fehlers aus User-Perspektive."""
    BENUTZER_FEHLER       = "BENUTZER_FEHLER"       # Falsche Eingabe, behebbar
    BERECHTIGUNGS_FEHLER  = "BERECHTIGUNGS_FEHLER"  # Keine Berechtigung
    PROZESS_FEHLER        = "PROZESS_FEHLER"         # Prozess-Zustandsproblem
    DATENFEHLER           = "DATENFEHLER"            # Inkonsistente/fehlende Daten
    SYSTEM_FEHLER         = "SYSTEM_FEHLER"          # Infrastrukturproblem
    LIMIT_FEHLER          = "LIMIT_FEHLER"           # Rate-Limit, Batch-Limit
    TIMEOUT_FEHLER        = "TIMEOUT_FEHLER"         # Zeitlimit ueberschritten


class LeitAktion(str, Enum):
    """Empfohlene Leitaktion fuer den User bei einem Fehler."""
    EINGABE_KORRIGIEREN   = "EINGABE_KORRIGIEREN"   # Eingabe ueberpruefen und korrigieren
    BERECHTIGUNG_ANFRAGEN = "BERECHTIGUNG_ANFRAGEN" # Vorgesetzten/Admin kontaktieren
    WARTEN_UND_WIEDERHOLEN = "WARTEN_UND_WIEDERHOLEN" # Kurz warten, dann erneut versuchen
    SUPPORT_KONTAKTIEREN  = "SUPPORT_KONTAKTIEREN"  # IT-Support anrufen/ticket
    PROZESS_NEU_STARTEN   = "PROZESS_NEU_STARTEN"   # Prozess abbrechen und neu beginnen
    DATEN_PRUEFEN         = "DATEN_PRUEFEN"          # Stammdaten/Kontext pruefen
    WEITERARBEITEN        = "WEITERARBEITEN"         # Warnung — kein Stop erforderlich
    ADMINISTRATOR_INFORMIEREN = "ADMINISTRATOR_INFORMIEREN"  # Admin benachrichtigen


class FehlerSchwere(str, Enum):
    """Schwere des Fehlers aus UX-Perspektive."""
    BLOCKIEREND  = "BLOCKIEREND"   # User kann nicht weiterarbeiten
    WARNUNG      = "WARNUNG"       # Kann weiterarbeiten, sollte pruefen
    INFO         = "INFO"          # Nur zur Information


class FehlerKontext(str, Enum):
    """In welchem Prozessschritt ist der Fehler aufgetreten."""
    WARENEINGANG  = "WARENEINGANG"
    KONTRAKT      = "KONTRAKT"
    SETTLEMENT    = "SETTLEMENT"
    ZAHLUNGSLAUF  = "ZAHLUNGSLAUF"
    COMPLIANCE    = "COMPLIANCE"
    STAMMDATEN    = "STAMMDATEN"
    WORKFLOW      = "WORKFLOW"
    ALLGEMEIN     = "ALLGEMEIN"


# ---------------------------------------------------------------------------
# Error-Guidance-Regel
# ---------------------------------------------------------------------------

@dataclass
class ErrorGuidanceRegel:
    """
    Zuordnung: HTTP-Statuscode + FehlerKategorie -> LeitAktion + User-Text.
    """
    regel_id: str
    http_status: int
    fehler_kategorie: FehlerKategorie
    leit_aktion: LeitAktion
    schwere: FehlerSchwere
    titel: str                  # Kurztitel fuer den User
    erklaerung: str             # Was ist passiert?
    handlungsanweisung: str     # Was soll der User konkret tun?
    kontext: FehlerKontext = FehlerKontext.ALLGEMEIN
    aktiv: bool = True

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "http_status": self.http_status,
            "fehler_kategorie": self.fehler_kategorie.value,
            "leit_aktion": self.leit_aktion.value,
            "schwere": self.schwere.value,
            "titel": self.titel,
            "erklaerung": self.erklaerung,
            "handlungsanweisung": self.handlungsanweisung,
            "kontext": self.kontext.value,
        }


# ---------------------------------------------------------------------------
# Error-Guidance-Result
# ---------------------------------------------------------------------------

@dataclass
class ErrorGuidanceResult:
    """
    Strukturierter Leitfaden fuer den User nach einem Fehler.
    Kein Stack-Trace, keine interne Detail — nur handlungsrelevante Info.
    """
    angewendete_regel_id: str | None
    http_status: int
    fehler_kategorie: FehlerKategorie
    leit_aktion: LeitAktion
    schwere: FehlerSchwere
    titel: str
    erklaerung: str
    handlungsanweisung: str
    kontext: FehlerKontext
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "angewendete_regel_id": self.angewendete_regel_id,
            "http_status": self.http_status,
            "fehler_kategorie": self.fehler_kategorie.value,
            "leit_aktion": self.leit_aktion.value,
            "schwere": self.schwere.value,
            "titel": self.titel,
            "erklaerung": self.erklaerung,
            "handlungsanweisung": self.handlungsanweisung,
            "kontext": self.kontext.value,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# evaluate_error_guidance
# ---------------------------------------------------------------------------

def evaluate_error_guidance(
    http_status: int,
    fehler_kategorie: FehlerKategorie,
    kontext: FehlerKontext,
    regeln: list[ErrorGuidanceRegel],
) -> ErrorGuidanceResult:
    """
    Bestimmt die optimale Leitaktion fuer einen aufgetretenen Fehler.

    Matching-Logik:
    1. Aktive Regeln mit passendem http_status und fehler_kategorie
    2. Kontext-spezifische Regeln bevorzugt (ALLGEMEIN als Fallback)
    3. Kein Match -> generische SUPPORT_KONTAKTIEREN-Anweisung

    Args:
        http_status: HTTP-Statuscode des Fehlers.
        fehler_kategorie: Klassifikation des Fehlers.
        kontext: Prozessschritt in dem der Fehler auftrat.
        regeln: Liste der konfigurierten Guidance-Regeln.

    Returns:
        ErrorGuidanceResult.
    """
    kandidaten = [
        r for r in regeln
        if r.aktiv
        and r.http_status == http_status
        and r.fehler_kategorie == fehler_kategorie
    ]

    if not kandidaten:
        # Fallback: Status-basierter Default
        return _default_guidance(http_status, fehler_kategorie, kontext)

    # Kontext-spezifisch bevorzugen
    kontext_treffer = [r for r in kandidaten if r.kontext == kontext]
    if kontext_treffer:
        regel = kontext_treffer[0]
    else:
        # Generische Regel (ALLGEMEIN) oder erste Regel
        allgemein = [r for r in kandidaten if r.kontext == FehlerKontext.ALLGEMEIN]
        regel = allgemein[0] if allgemein else kandidaten[0]

    return ErrorGuidanceResult(
        angewendete_regel_id=regel.regel_id,
        http_status=http_status,
        fehler_kategorie=fehler_kategorie,
        leit_aktion=regel.leit_aktion,
        schwere=regel.schwere,
        titel=regel.titel,
        erklaerung=regel.erklaerung,
        handlungsanweisung=regel.handlungsanweisung,
        kontext=kontext,
    )


def _default_guidance(
    http_status: int,
    fehler_kategorie: FehlerKategorie,
    kontext: FehlerKontext,
) -> ErrorGuidanceResult:
    """Generische Fallback-Guidance wenn keine Regel passt."""
    if http_status == 422:
        return ErrorGuidanceResult(
            angewendete_regel_id=None,
            http_status=http_status,
            fehler_kategorie=fehler_kategorie,
            leit_aktion=LeitAktion.EINGABE_KORRIGIEREN,
            schwere=FehlerSchwere.BLOCKIEREND,
            titel="Eingabe ungueltig",
            erklaerung="Die eingegebenen Daten konnten nicht verarbeitet werden.",
            handlungsanweisung="Bitte Eingaben pruefen und korrigieren.",
            kontext=kontext,
        )
    if http_status == 403:
        return ErrorGuidanceResult(
            angewendete_regel_id=None,
            http_status=http_status,
            fehler_kategorie=fehler_kategorie,
            leit_aktion=LeitAktion.BERECHTIGUNG_ANFRAGEN,
            schwere=FehlerSchwere.BLOCKIEREND,
            titel="Keine Berechtigung",
            erklaerung="Sie haben keine Berechtigung fuer diese Aktion.",
            handlungsanweisung="Bitte Vorgesetzten oder Administrator kontaktieren.",
            kontext=kontext,
        )
    if http_status == 429:
        return ErrorGuidanceResult(
            angewendete_regel_id=None,
            http_status=http_status,
            fehler_kategorie=fehler_kategorie,
            leit_aktion=LeitAktion.WARTEN_UND_WIEDERHOLEN,
            schwere=FehlerSchwere.WARNUNG,
            titel="Zu viele Anfragen",
            erklaerung="Das System wird zu stark belastet.",
            handlungsanweisung="Bitte kurz warten und dann erneut versuchen.",
            kontext=kontext,
        )
    return ErrorGuidanceResult(
        angewendete_regel_id=None,
        http_status=http_status,
        fehler_kategorie=fehler_kategorie,
        leit_aktion=LeitAktion.SUPPORT_KONTAKTIEREN,
        schwere=FehlerSchwere.BLOCKIEREND,
        titel="Unerwarteter Fehler",
        erklaerung="Ein unbekannter Fehler ist aufgetreten.",
        handlungsanweisung="Bitte IT-Support kontaktieren und Fehlerzeitpunkt mitteilen.",
        kontext=kontext,
    )


# ---------------------------------------------------------------------------
# Default-Guidance-Regeln
# ---------------------------------------------------------------------------

def get_default_error_guidance_rules() -> list[ErrorGuidanceRegel]:
    """
    Liefert Default-Guidance-Regeln fuer die haeufigsten Fehlermuster.

    Abdeckung: 422 Validierung, 403 Berechtigung, 409 Konflikt,
    429 Rate-Limit, 503 Service-degraded, 500 Systemfehler.
    """
    return [
        # --- 422 Eingabefehler ---
        ErrorGuidanceRegel(
            "EG-422-001", 422, FehlerKategorie.BENUTZER_FEHLER,
            LeitAktion.EINGABE_KORRIGIEREN, FehlerSchwere.BLOCKIEREND,
            "Pflichtfeld fehlt oder ungueltig",
            "Ein oder mehrere Pflichtfelder sind leer oder enthalten ungueltge Werte.",
            "Bitte alle rot markierten Felder ausfuellen und Formate pruefen "
            "(z.B. Datum: TT.MM.JJJJ, Betrag: nur Zahlen).",
            FehlerKontext.ALLGEMEIN,
        ),
        ErrorGuidanceRegel(
            "EG-422-002", 422, FehlerKategorie.BENUTZER_FEHLER,
            LeitAktion.EINGABE_KORRIGIEREN, FehlerSchwere.BLOCKIEREND,
            "Wiegeschein-Daten ungueltig",
            "Gewicht oder Feuchte liegen ausserhalb der erlaubten Grenzwerte.",
            "Bitte Waagenausdruck pruefen. Bruttogewicht: 100–100.000 kg, "
            "Feuchte: 5–50 %. Bei Verdacht auf Waagendefekt: Lagermeister informieren.",
            FehlerKontext.WARENEINGANG,
        ),
        ErrorGuidanceRegel(
            "EG-422-003", 422, FehlerKategorie.DATENFEHLER,
            LeitAktion.DATEN_PRUEFEN, FehlerSchwere.BLOCKIEREND,
            "Kontraktnummer nicht gefunden",
            "Die eingegebene Kontraktnummer existiert nicht im System.",
            "Bitte Kontraktnummer aus dem Auftragsschein pruefen. "
            "Format: KT-JJJJ-NNNNN. Neuen Kontrakt bei Sachbearbeiter anfordern.",
            FehlerKontext.WARENEINGANG,
        ),
        # --- 403 Berechtigung ---
        ErrorGuidanceRegel(
            "EG-403-001", 403, FehlerKategorie.BERECHTIGUNGS_FEHLER,
            LeitAktion.BERECHTIGUNG_ANFRAGEN, FehlerSchwere.BLOCKIEREND,
            "Freigabe-Berechtigung fehlt",
            "Sie sind nicht berechtigt, diese Freigabe zu erteilen.",
            "Freigaben ab diesem Betrag benoetigen die Rolle 'Leiter' oder hoeher. "
            "Bitte Vorgesetzten zur Freigabe bitten.",
            FehlerKontext.SETTLEMENT,
        ),
        ErrorGuidanceRegel(
            "EG-403-002", 403, FehlerKategorie.BERECHTIGUNGS_FEHLER,
            LeitAktion.BERECHTIGUNG_ANFRAGEN, FehlerSchwere.BLOCKIEREND,
            "Zahlungslauf nicht autorisiert",
            "Zahlungslaeufe duerfen nur von Buchhaltung oder Leitung gestartet werden.",
            "Bitte die Buchhaltung informieren. Fuer dringende Zahlungen: "
            "Prokuristen kontaktieren.",
            FehlerKontext.ZAHLUNGSLAUF,
        ),
        ErrorGuidanceRegel(
            "EG-403-003", 403, FehlerKategorie.BERECHTIGUNGS_FEHLER,
            LeitAktion.BERECHTIGUNG_ANFRAGEN, FehlerSchwere.BLOCKIEREND,
            "Keine Berechtigung",
            "Sie haben fuer diese Aktion keine Berechtigung.",
            "Bitte Administrator oder Vorgesetzten kontaktieren um Berechtigungen "
            "zu erhalten.",
            FehlerKontext.ALLGEMEIN,
        ),
        # --- 409 Konflikt ---
        ErrorGuidanceRegel(
            "EG-409-001", 409, FehlerKategorie.PROZESS_FEHLER,
            LeitAktion.PROZESS_NEU_STARTEN, FehlerSchwere.BLOCKIEREND,
            "Datensatz wurde geaendert",
            "Der Datensatz wurde zwischenzeitlich von einem anderen Benutzer geaendert.",
            "Bitte Seite neu laden und Ihre Aenderungen erneut eingeben. "
            "Bei haeufigem Auftreten: Koordination mit dem Team vereinbaren.",
            FehlerKontext.ALLGEMEIN,
        ),
        ErrorGuidanceRegel(
            "EG-409-002", 409, FehlerKategorie.PROZESS_FEHLER,
            LeitAktion.DATEN_PRUEFEN, FehlerSchwere.BLOCKIEREND,
            "Doppelter Wiegeschein",
            "Ein Wiegeschein mit dieser Wagennummer und Uhrzeit existiert bereits.",
            "Bitte pruefen ob dieser LKW bereits gewogen wurde (Wiegeschein-Liste). "
            "Duplikate koennen durch doppeltes Einbuchen entstehen.",
            FehlerKontext.WARENEINGANG,
        ),
        # --- 429 Rate-Limit ---
        ErrorGuidanceRegel(
            "EG-429-001", 429, FehlerKategorie.LIMIT_FEHLER,
            LeitAktion.WARTEN_UND_WIEDERHOLEN, FehlerSchwere.WARNUNG,
            "Zu viele Anfragen — kurz warten",
            "Das System erhielt zu viele Anfragen von Ihrem Konto.",
            "Bitte 30 Sekunden warten und dann erneut versuchen. "
            "Bei dauerhaftem Auftreten: IT-Support informieren.",
            FehlerKontext.ALLGEMEIN,
        ),
        # --- 503 Service degraded ---
        ErrorGuidanceRegel(
            "EG-503-001", 503, FehlerKategorie.SYSTEM_FEHLER,
            LeitAktion.WARTEN_UND_WIEDERHOLEN, FehlerSchwere.BLOCKIEREND,
            "Dienst temporaer nicht verfuegbar",
            "Ein Backend-Dienst ist momentan nicht erreichbar (Cache/DB).",
            "Bitte 1–2 Minuten warten und erneut versuchen. "
            "Bei laengerem Ausfall (>5 min): IT-Bereitschaft informieren.",
            FehlerKontext.ALLGEMEIN,
        ),
        ErrorGuidanceRegel(
            "EG-503-002", 503, FehlerKategorie.TIMEOUT_FEHLER,
            LeitAktion.WARTEN_UND_WIEDERHOLEN, FehlerSchwere.WARNUNG,
            "Abfrage-Timeout — Daten werden geladen",
            "Die Abfrage hat laenger gedauert als erwartet.",
            "Das System liefert zwischengespeicherte Daten. "
            "Aktuelle Werte in einigen Minuten verfuegbar.",
            FehlerKontext.ALLGEMEIN,
        ),
        # --- 500 Systemfehler ---
        ErrorGuidanceRegel(
            "EG-500-001", 500, FehlerKategorie.SYSTEM_FEHLER,
            LeitAktion.SUPPORT_KONTAKTIEREN, FehlerSchwere.BLOCKIEREND,
            "Systemfehler aufgetreten",
            "Ein unerwarteter Fehler ist im System aufgetreten.",
            "Bitte Fehlerzeitpunkt notieren und IT-Support kontaktieren "
            "(Tel. oder Ticket). Aktion NICHT mehrfach wiederholen.",
            FehlerKontext.ALLGEMEIN,
        ),
        # --- Compliance ---
        ErrorGuidanceRegel(
            "EG-422-004", 422, FehlerKategorie.DATENFEHLER,
            LeitAktion.DATEN_PRUEFEN, FehlerSchwere.BLOCKIEREND,
            "Zulassung abgelaufen oder ungueltig",
            "Das verwendete Produkt hat keine gueltge Zulassung fuer diesen Zweck.",
            "Bitte Zulassungsregister pruefen. Nur Produkte mit aktiver Zulassung "
            "duerfen verwendet werden (Pflanzenschutzgesetz §12).",
            FehlerKontext.COMPLIANCE,
        ),
    ]
