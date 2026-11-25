"""Aufbewahrungspflichten nach geltendem Recht - einzige Quelle im System (Stand 25.11.2026).

Rechtsstand:

- **§ 147 AO / § 257 HGB** in der Fassung des Vierten Buerokratieentlastungsgesetzes (BEG IV, in Kraft 01.01.2025):
  Buecher, Aufzeichnungen, Inventare, Jahresabschluesse, Lageberichte, Eroeffnungsbilanz, Arbeitsanweisungen und
  Organisationsunterlagen **10 Jahre**; Buchungsbelege **8 Jahre**; empfangene und abgesandte Handels- und
  Geschaeftsbriefe sowie sonstige steuerlich bedeutsame Unterlagen **6 Jahre**. Die 8 Jahre gelten fuer alle
  Buchungsbelege, deren Frist am 01.01.2025 noch nicht abgelaufen war (Art. 97 § 19a EGAO).
- **§ 14b Abs. 1 UStG**: Rechnungen 8 Jahre (BEG IV).
- **§ 147 Abs. 4 AO / § 257 Abs. 5 HGB**: Die Frist beginnt mit dem **Schluss des Kalenderjahres**, in dem die
  Unterlage entstanden ist (letzte Eintragung, Aufstellung, Empfang/Versand).
- **§ 147 Abs. 3 Satz 3 und 4 AO** (Wachstumschancengesetz 2024): Bei Lieferscheinen, die keine Buchungsbelege sind,
  endet die Frist mit Erhalt bzw. Versand der zugehoerigen Rechnung.
- **§ 147 Abs. 3 Satz 5 AO** (Ablaufhemmung): Die Frist laeuft nicht ab, solange die Unterlagen fuer Steuern
  bedeutsam sind, deren Festsetzungsfrist noch nicht abgelaufen ist. Dazu kommen Loeschsperren (Aussenpruefung,
  Rechtsstreit) - beides prueft ``RetentionPruefung.darf_geloescht_werden``.
- **§ 11 PflSchG i. V. m. Art. 67 VO (EG) 1107/2009**: Aufzeichnungen ueber Pflanzenschutzmittel mindestens 3 Jahre.
- **§ 10 Abs. 5 DueV**: Duengungsaufzeichnungen 7 Jahre nach Ablauf des Duengejahres.

Die Fristen sind Mindestfristen der Aufbewahrung. Nach ihrem Ablauf sind personenbezogene Daten zu loeschen, soweit
kein anderer Zweck traegt (Art. 17 DSGVO). Laengeres Aufbewahren "zur Sicherheit" ist deshalb kein sicherer Hafen.
"""
from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel


class RetentionKlasse(str, Enum):
    STANDARD_10J = "10_jahre"     # Buecher, Aufzeichnungen, Jahresabschluesse, Inventare, Verfahrensdokumentation
    BELEG_8J = "8_jahre"          # Buchungsbelege, Rechnungen
    DUENGUNG_7J = "7_jahre"       # § 10 Abs. 5 DueV
    KUERZER_6J = "6_jahre"        # Handels- und Geschaeftsbriefe, sonstige steuerlich bedeutsame Unterlagen
    PSM_3J = "3_jahre"            # § 11 PflSchG, Mindestfrist
    BIS_RECHNUNG = "bis_rechnung"  # Lieferschein ohne Belegfunktion: bis Erhalt/Versand der Rechnung
    DAUERHAFT = "dauerhaft"


AUFBEWAHRUNGSJAHRE: dict[RetentionKlasse, int] = {
    RetentionKlasse.STANDARD_10J: 10,
    RetentionKlasse.BELEG_8J: 8,
    RetentionKlasse.DUENGUNG_7J: 7,
    RetentionKlasse.KUERZER_6J: 6,
    RetentionKlasse.PSM_3J: 3,
    RetentionKlasse.BIS_RECHNUNG: 0,
    RetentionKlasse.DAUERHAFT: 9999,
}


class RetentionEreignis(str, Enum):
    """Ereignis, in dessen Kalenderjahr die Frist beginnt (Fristende = 31.12. des Jahres + Frist)."""
    BUCHUNGSDATUM = "buchungsdatum"
    JAHRESABSCHLUSS = "jahresabschluss"     # Aufstellung des Jahresabschlusses
    VERTRAGSENDE = "vertragsende"
    ERSTELLUNGSDATUM = "erstellungsdatum"   # Entstehung, Empfang oder Versand
    RECHNUNG = "rechnung"                   # Erhalt/Versand der Rechnung (Lieferscheine ohne Belegfunktion)


def fristende(klasse: RetentionKlasse, ereignisdatum: date) -> date:
    """Letzter Tag der Aufbewahrungspflicht (§ 147 Abs. 4 AO)."""
    if klasse is RetentionKlasse.BIS_RECHNUNG:
        return ereignisdatum  # § 147 Abs. 3 Satz 3/4 AO: endet mit Erhalt bzw. Versand der Rechnung
    if klasse is RetentionKlasse.DAUERHAFT:
        return date.max
    return date(ereignisdatum.year + AUFBEWAHRUNGSJAHRE[klasse], 12, 31)


class RetentionRegel(BaseModel):
    dokumenttyp: str            # z.B. "ap_invoice", "journal_entry"
    klasse: RetentionKlasse
    beginnt_mit: RetentionEreignis
    beschreibung: str
    rechtsgrundlage: str = ""
    schema_version: int = 1

    @property
    def aufbewahrungsjahre(self) -> int:
        return AUFBEWAHRUNGSJAHRE[self.klasse]

    def fristende(self, ereignisdatum: date) -> date:
        return fristende(self.klasse, ereignisdatum)


class RetentionPruefung(BaseModel):
    pruefung_id: str
    dokumenttyp: str
    dokumentdatum: date
    ereignisdatum: date         # Datum des Beginnereignisses
    aufbewahrungsjahre: int
    schema_version: int = 1

    @property
    def aufzubewahren_bis(self) -> date:
        """31.12. des Jahres (Ereignisjahr + Frist) - § 147 Abs. 4 AO."""
        if self.aufbewahrungsjahre == 0:
            return self.ereignisdatum
        return date(self.ereignisdatum.year + self.aufbewahrungsjahre, 12, 31)

    def darf_geloescht_werden(self, heute: date, *, festsetzungsfrist_offen_bis: date | None = None,
                              loeschsperre_aktiv: bool = False) -> bool:
        """Frist abgelaufen, keine Ablaufhemmung (§ 147 Abs. 3 Satz 5 AO) und keine Loeschsperre."""
        if loeschsperre_aktiv:
            return False
        if festsetzungsfrist_offen_bis is not None and heute <= festsetzungsfrist_offen_bis:
            return False
        return heute > self.aufzubewahren_bis

    def verbleibende_tage(self, heute: date) -> int:
        delta = (self.aufzubewahren_bis - heute).days
        return max(0, delta)


# Rechtsgrundlagen je Klasse - einmal formuliert, von allen Regeln genutzt.
AO_BUECHER = "§ 147 Abs. 1 Nr. 1, Abs. 3 AO; § 257 Abs. 1 Nr. 1, Abs. 4 HGB"
AO_BELEG = "§ 147 Abs. 1 Nr. 4, Abs. 3 AO; § 257 Abs. 1 Nr. 4, Abs. 4 HGB (BEG IV)"
USTG_RECHNUNG = "§ 14b Abs. 1 UStG; § 147 Abs. 1 Nr. 4, Abs. 3 AO (BEG IV)"
AO_BRIEF = "§ 147 Abs. 1 Nr. 2, 3, Abs. 3 AO; § 257 Abs. 1 Nr. 2, 3, Abs. 4 HGB"
AO_LIEFERSCHEIN = "§ 147 Abs. 3 Satz 3 und 4 AO"
PFLSCHG = "§ 11 PflSchG i. V. m. Art. 67 VO (EG) 1107/2009"
DUEV = "§ 10 Abs. 5 DueV"


def _regel(typ: str, klasse: RetentionKlasse, beginn: RetentionEreignis, text: str, grund: str) -> RetentionRegel:
    return RetentionRegel(dokumenttyp=typ, klasse=klasse, beginnt_mit=beginn, beschreibung=text, rechtsgrundlage=grund)


def build_default_retention_regeln() -> list[RetentionRegel]:
    """Aufbewahrungsregeln je Dokumenttyp nach geltendem Recht (Stand 25.11.2026)."""
    k, e = RetentionKlasse, RetentionEreignis
    return [
        # Buecher und Aufzeichnungen - 10 Jahre
        _regel("journal_entry", k.STANDARD_10J, e.BUCHUNGSDATUM, "Buchungen (Journal, Hauptbuch): 10 Jahre", AO_BUECHER),
        _regel("jahresabschluss", k.STANDARD_10J, e.JAHRESABSCHLUSS, "Jahresabschluss, Lagebericht, Eroeffnungsbilanz: 10 Jahre", AO_BUECHER),
        _regel("inventar", k.STANDARD_10J, e.ERSTELLUNGSDATUM, "Inventare: 10 Jahre", AO_BUECHER),
        _regel("audit_evidence", k.STANDARD_10J, e.ERSTELLUNGSDATUM,
               "GoBD-Verfahrensdokumentation und Nachweise (Arbeitsanweisungen, Organisationsunterlagen): 10 Jahre",
               AO_BUECHER),
        # Buchungsbelege und Rechnungen - 8 Jahre
        _regel("ap_invoice", k.BELEG_8J, e.ERSTELLUNGSDATUM, "Eingangsrechnungen: 8 Jahre", USTG_RECHNUNG),
        _regel("ar_invoice", k.BELEG_8J, e.ERSTELLUNGSDATUM, "Ausgangsrechnungen: 8 Jahre", USTG_RECHNUNG),
        _regel("payment_run", k.BELEG_8J, e.BUCHUNGSDATUM, "Zahlungsbelege, Kontoauszuege: 8 Jahre", AO_BELEG),
        _regel("agrar_settlement", k.BELEG_8J, e.ERSTELLUNGSDATUM,
               "Abrechnungen und Gutschriften (Ernte, Kontrakt): 8 Jahre", USTG_RECHNUNG),
        _regel("lohnabrechnung", k.BELEG_8J, e.ERSTELLUNGSDATUM, "Lohnabrechnungen als Buchungsbelege: 8 Jahre", AO_BELEG),
        _regel("lieferschein_beleg", k.BELEG_8J, e.ERSTELLUNGSDATUM,
               "Lieferscheine mit Belegfunktion (z. B. Buchung ohne Rechnung): 8 Jahre", AO_BELEG),
        # Handels- und Geschaeftsbriefe - 6 Jahre
        _regel("kontrakt", k.KUERZER_6J, e.VERTRAGSENDE,
               "Vertraege/Kontrakte als Geschaeftsbriefe: 6 Jahre ab Schluss des Jahres des Vertragsendes", AO_BRIEF),
        _regel("handelsbrief", k.KUERZER_6J, e.ERSTELLUNGSDATUM,
               "Angebote mit Auftragsfolge, Auftragsbestaetigungen, Korrespondenz: 6 Jahre", AO_BRIEF),
        _regel("reklamation", k.KUERZER_6J, e.ERSTELLUNGSDATUM, "Reklamationsschriftverkehr: 6 Jahre", AO_BRIEF),
        # Lieferscheine ohne Belegfunktion
        _regel("lieferschein", k.BIS_RECHNUNG, e.RECHNUNG,
               "Lieferscheine ohne Belegfunktion: bis Erhalt bzw. Versand der Rechnung", AO_LIEFERSCHEIN),
        # Fachrecht Landwirtschaft
        _regel("psm_protokoll", k.PSM_3J, e.ERSTELLUNGSDATUM, "Pflanzenschutz-Anwendungsaufzeichnungen: mindestens 3 Jahre", PFLSCHG),
        _regel("duenge_bilanz", k.DUENGUNG_7J, e.ERSTELLUNGSDATUM, "Duengungsaufzeichnungen: 7 Jahre nach Ablauf des Duengejahres", DUEV),
        # Keine gesetzliche Mindestfrist ermittelt - betriebliche Festlegung (QS/GMP+), keine Personendaten
        _regel("silo_reinigungsprotokoll", k.KUERZER_6J, e.ERSTELLUNGSDATUM,
               "Siloreinigung: 6 Jahre (betriebliche Festlegung, keine gesetzliche Mindestfrist)", "betrieblich"),
    ]


def regel_fuer(dokumenttyp: str) -> RetentionRegel | None:
    return next((r for r in build_default_retention_regeln() if r.dokumenttyp == dokumenttyp), None)


# Zuordnung der Dokumenttypen der Finanz-Richtlinientabelle (gobd_aufbewahrungsrichtlinien) zum Katalog.
RICHTLINIE_ZU_DOKUMENTTYP: dict[str, str] = {
    "BUCHUNGSBELEG": "payment_run",
    "EINGANGSRECHNUNG": "ap_invoice",
    "AUSGANGSRECHNUNG": "ar_invoice",
    "JAHRESABSCHLUSS": "jahresabschluss",
    "INVENTAR": "inventar",
    "LOHNABRECHNUNG": "lohnabrechnung",
    "HANDELSBRIEF": "handelsbrief",
    "VERTRAG": "kontrakt",
    "LIEFERSCHEIN": "lieferschein",
}
