from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class AusnahmeMuster(str, Enum):
    TIMEOUT = "TIMEOUT"
    DATENFEHLER = "DATENFEHLER"
    BERECHTIGUNGSFEHLER = "BERECHTIGUNGSFEHLER"
    RESSOURCENENGPASS = "RESSOURCENENGPASS"
    GESCHAEFTSREGELVERTOSS = "GESCHAEFTSREGELVERTOSS"
    INTEGRATIONSFEHLER = "INTEGRATIONSFEHLER"
    UNBEKANNT = "UNBEKANNT"

class AusnahmeSchwere(str, Enum):
    KRITISCH = "KRITISCH"
    HOCH = "HOCH"
    MITTEL = "MITTEL"
    NIEDRIG = "NIEDRIG"

class MusterErkennungsKonfidenz(str, Enum):
    SICHER = "SICHER"              # >= 90%
    WAHRSCHEINLICH = "WAHRSCHEINLICH"  # 70-89%
    MOEGLICH = "MOEGLICH"          # 50-69%
    UNBEKANNT = "UNBEKANNT"        # < 50%

@dataclass
class AusnahmeSignatur:
    signatur_id: str
    muster: AusnahmeMuster
    schluessel_woerter: list = field(default_factory=list)  # list[str]
    fehler_code_praefixe: list = field(default_factory=list)  # list[str]
    schwere: AusnahmeSchwere = AusnahmeSchwere.MITTEL
    beschreibung: str = ""

    def erkenne_muster(self, fehler_text: str, fehler_code: str = "") -> MusterErkennungsKonfidenz:
        """
        Checks if error matches this signature.
        Count matching schluessel_woerter in fehler_text (case-insensitive).
        Check if fehler_code starts with any fehler_code_praefixe.
        Score:
          - code prefix match: +50 points
          - each keyword match: +20 points
        >= 90 -> SICHER; >= 70 -> WAHRSCHEINLICH; >= 50 -> MOEGLICH; < 50 -> UNBEKANNT
        """
        punkte = 0
        fehler_lower = fehler_text.lower()
        for prae in self.fehler_code_praefixe:
            if fehler_code.startswith(prae):
                punkte += 50
                break
        for wort in self.schluessel_woerter:
            if wort.lower() in fehler_lower:
                punkte += 20
        if punkte >= 90:
            return MusterErkennungsKonfidenz.SICHER
        elif punkte >= 70:
            return MusterErkennungsKonfidenz.WAHRSCHEINLICH
        elif punkte >= 50:
            return MusterErkennungsKonfidenz.MOEGLICH
        return MusterErkennungsKonfidenz.UNBEKANNT

@dataclass
class KlassifizierungsErgebnis:
    muster: AusnahmeMuster
    konfidenz: MusterErkennungsKonfidenz
    signatur_id: Optional[str] = None
    schwere: AusnahmeSchwere = AusnahmeSchwere.MITTEL

def klassifiziere_ausnahme(fehler_text: str, fehler_code: str, signaturen: list) -> KlassifizierungsErgebnis:
    """
    Tests each signatur. Returns best match (highest confidence, SICHER > WAHRSCHEINLICH > MOEGLICH).
    If multiple with same confidence, first wins.
    If no match (all UNBEKANNT) -> AusnahmeMuster.UNBEKANNT, MusterErkennungsKonfidenz.UNBEKANNT.
    """
    rang = {MusterErkennungsKonfidenz.SICHER: 3, MusterErkennungsKonfidenz.WAHRSCHEINLICH: 2,
            MusterErkennungsKonfidenz.MOEGLICH: 1, MusterErkennungsKonfidenz.UNBEKANNT: 0}
    bestes = None
    bester_rang = -1
    for sig in signaturen:
        konfidenz = sig.erkenne_muster(fehler_text, fehler_code)
        if rang[konfidenz] > bester_rang:
            bester_rang = rang[konfidenz]
            bestes = (sig, konfidenz)
    if bestes is None or bester_rang == 0:
        return KlassifizierungsErgebnis(AusnahmeMuster.UNBEKANNT, MusterErkennungsKonfidenz.UNBEKANNT)
    sig, konf = bestes
    return KlassifizierungsErgebnis(sig.muster, konf, sig.signatur_id, sig.schwere)

def get_default_ausnahme_signaturen() -> list:
    return [
        AusnahmeSignatur("AS-001", AusnahmeMuster.TIMEOUT,
                          ["timeout", "connection timed out", "zeitüberschreitung"],
                          ["TIMEOUT_", "CONN_"], AusnahmeSchwere.HOCH, "Verbindungs-Timeout"),
        AusnahmeSignatur("AS-002", AusnahmeMuster.DATENFEHLER,
                          ["validation", "ungültig", "format", "pflichtfeld"],
                          ["VAL_", "DATA_"], AusnahmeSchwere.MITTEL, "Datenfehler"),
        AusnahmeSignatur("AS-003", AusnahmeMuster.BERECHTIGUNGSFEHLER,
                          ["permission", "unauthorized", "forbidden", "berechtigung"],
                          ["AUTH_", "PERM_"], AusnahmeSchwere.HOCH, "Berechtigungsfehler"),
        AusnahmeSignatur("AS-004", AusnahmeMuster.RESSOURCENENGPASS,
                          ["out of memory", "disk full", "resource exhausted", "speicher"],
                          ["RES_", "OOM_"], AusnahmeSchwere.KRITISCH, "Ressourcenengpass"),
        AusnahmeSignatur("AS-005", AusnahmeMuster.INTEGRATIONSFEHLER,
                          ["edi", "api error", "integration", "verbindung"],
                          ["EDI_", "API_", "INT_"], AusnahmeSchwere.HOCH, "Integrationsfehler"),
    ]
