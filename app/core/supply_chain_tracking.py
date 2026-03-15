"""
Supply Chain Tracking — Wave 36, Gap 044
Lieferketten-Tracking: TrackingEvents, ETA-Berechnung, Abweichungsalarme.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class TrackingEventTyp(str, Enum):
    ABFAHRT = "ABFAHRT"
    ANKUNFT = "ANKUNFT"
    UMSCHLAG = "UMSCHLAG"
    ZOLLFREIGABE = "ZOLLFREIGABE"
    QUALITAETSPRUEFUNG = "QUALITAETSPRUEFUNG"
    LAGEREINGANG = "LAGEREINGANG"
    LAGERAUSGANG = "LAGERAUSGANG"
    LIEFERBESTAETIGUNG = "LIEFERBESTAETIGUNG"
    VERZOEGERUNG_GEMELDET = "VERZOEGERUNG_GEMELDET"
    AUSNAHME = "AUSNAHME"


class TrackingStatusGesamtlage(str, Enum):
    PLANMAESSIG = "PLANMAESSIG"
    LEICHTE_ABWEICHUNG = "LEICHTE_ABWEICHUNG"
    KRITISCHE_ABWEICHUNG = "KRITISCHE_ABWEICHUNG"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    UNBEKANNT = "UNBEKANNT"


class AbweichungsTyp(str, Enum):
    ZEITLICHE_VERZOEGERUNG = "ZEITLICHE_VERZOEGERUNG"
    MENGENABWEICHUNG = "MENGENABWEICHUNG"
    QUALITAETSABWEICHUNG = "QUALITAETSABWEICHUNG"
    ROUTEAENDERUNG = "ROUTEAENDERUNG"
    DOKUMENTENFEHLER = "DOKUMENTENFEHLER"
    ZOLLAENDERUNG = "ZOLLAENDERUNG"


class AbweichungsSchwere(str, Enum):
    INFO = "INFO"
    WARNUNG = "WARNUNG"
    KRITISCH = "KRITISCH"


class TransportModus(str, Enum):
    LKW = "LKW"
    BAHN = "BAHN"
    SCHIFF = "SCHIFF"
    FLUGZEUG = "FLUGZEUG"
    MULTIMODAL = "MULTIMODAL"


class LieferkettenPhase(str, Enum):
    BESCHAFFUNG = "BESCHAFFUNG"
    TRANSPORT_EINGEHEND = "TRANSPORT_EINGEHEND"
    LAGERUNG = "LAGERUNG"
    VERARBEITUNG = "VERARBEITUNG"
    TRANSPORT_AUSGEHEND = "TRANSPORT_AUSGEHEND"
    AUSLIEFERUNG = "AUSLIEFERUNG"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TrackingEvent:
    """Einzelnes Ereignis in der Lieferkette."""
    event_id: str
    lieferung_id: str
    typ: TrackingEventTyp
    ort: str
    zeitstempel: datetime
    phase: LieferkettenPhase
    meldender: str = ""
    notiz: str = ""
    ist_meilenstein: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "lieferung_id": self.lieferung_id,
            "typ": self.typ.value,
            "ort": self.ort,
            "zeitstempel": self.zeitstempel.isoformat(),
            "phase": self.phase.value,
            "meldender": self.meldender,
            "notiz": self.notiz,
            "ist_meilenstein": self.ist_meilenstein,
        }


@dataclass
class ETABerechnungsRequest:
    """Anfrage für ETA-Berechnung einer Lieferung."""
    lieferung_id: str
    transport_modus: TransportModus
    ursprungsort: str
    zielort: str
    geplante_abfahrt: datetime
    distanz_km: float
    zwischenstopps: int = 0
    zoll_erforderlich: bool = False
    priorisiert: bool = False


@dataclass
class ETABerechnungsErgebnis:
    """Ergebnis der ETA-Berechnung."""
    lieferung_id: str
    geschaetzte_ankunft: datetime
    konfidenz_prozent: int
    berechnet_am: datetime
    puffer_stunden: float
    route_beschreibung: str
    hinweise: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "lieferung_id": self.lieferung_id,
            "geschaetzte_ankunft": self.geschaetzte_ankunft.isoformat(),
            "konfidenz_prozent": self.konfidenz_prozent,
            "berechnet_am": self.berechnet_am.isoformat(),
            "puffer_stunden": self.puffer_stunden,
            "route_beschreibung": self.route_beschreibung,
            "hinweise": self.hinweise,
        }


@dataclass
class AbweichungsAlarm:
    """Abweichungsalarm für eine Lieferung."""
    alarm_id: str
    lieferung_id: str
    typ: AbweichungsTyp
    schwere: AbweichungsSchwere
    beschreibung: str
    erkannt_am: datetime
    eskalations_empfaenger: list[str] = field(default_factory=list)
    automatisch_eskaliert: bool = False
    behoben: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "alarm_id": self.alarm_id,
            "lieferung_id": self.lieferung_id,
            "typ": self.typ.value,
            "schwere": self.schwere.value,
            "beschreibung": self.beschreibung,
            "erkannt_am": self.erkannt_am.isoformat(),
            "eskalations_empfaenger": self.eskalations_empfaenger,
            "automatisch_eskaliert": self.automatisch_eskaliert,
            "behoben": self.behoben,
        }


@dataclass
class LieferkettenStatusErgebnis:
    """Gesamtstatus einer Lieferkette."""
    lieferung_id: str
    gesamtlage: TrackingStatusGesamtlage
    aktuelle_phase: LieferkettenPhase
    letzte_events: list[TrackingEvent]
    aktive_alarme: list[AbweichungsAlarm]
    eta: ETABerechnungsErgebnis | None
    fortschritt_prozent: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "lieferung_id": self.lieferung_id,
            "gesamtlage": self.gesamtlage.value,
            "aktuelle_phase": self.aktuelle_phase.value,
            "letzte_events": [e.as_dict() for e in self.letzte_events],
            "aktive_alarme": [a.as_dict() for a in self.aktive_alarme],
            "eta": self.eta.as_dict() if self.eta else None,
            "fortschritt_prozent": self.fortschritt_prozent,
        }


# ---------------------------------------------------------------------------
# ETA-Berechnung
# ---------------------------------------------------------------------------

# Durchschnittsgeschwindigkeiten in km/h pro Transportmodus
_DURCHSCHNITTS_KMH: dict[TransportModus, float] = {
    TransportModus.LKW: 75.0,
    TransportModus.BAHN: 90.0,
    TransportModus.SCHIFF: 25.0,
    TransportModus.FLUGZEUG: 750.0,
    TransportModus.MULTIMODAL: 60.0,
}

# Zoll-Aufschlag in Stunden
_ZOLL_STUNDEN: float = 24.0

# Stopp-Aufschlag in Stunden pro Zwischenstopp
_STOPP_STUNDEN: float = 4.0

# Pufferfaktoren
_PUFFER_STANDARD: float = 0.15   # 15 % Puffer
_PUFFER_PRIORISIERT: float = 0.05  # 5 % bei Prio-Sendung


def berechne_eta(req: ETABerechnungsRequest, jetzt: datetime | None = None) -> ETABerechnungsErgebnis:
    """
    Berechnet die voraussichtliche Ankunftszeit (ETA) einer Lieferung.

    Formel:
    - Fahrzeit = distanz_km / kmh
    - Puffer   = fahrzeit * puffer_faktor
    - Zoll     = 24 h wenn zoll_erforderlich
    - Stopps   = zwischenstopps * 4 h
    - ETA      = geplante_abfahrt + fahrzeit + puffer + zoll + stopps
    """
    if jetzt is None:
        jetzt = datetime.utcnow()

    if req.distanz_km <= 0:
        raise ValueError("distanz_km muss positiv sein")
    if math.isnan(req.distanz_km) or math.isinf(req.distanz_km):
        raise ValueError("distanz_km darf nicht NaN oder Inf sein")

    kmh = _DURCHSCHNITTS_KMH.get(req.transport_modus, 60.0)
    fahrzeit_h = req.distanz_km / kmh

    puffer_faktor = _PUFFER_PRIORISIERT if req.priorisiert else _PUFFER_STANDARD
    puffer_h = fahrzeit_h * puffer_faktor

    zoll_h = _ZOLL_STUNDEN if req.zoll_erforderlich else 0.0
    stopp_h = req.zwischenstopps * _STOPP_STUNDEN

    gesamt_h = fahrzeit_h + puffer_h + zoll_h + stopp_h
    eta_dt = req.geplante_abfahrt + timedelta(hours=gesamt_h)

    # Konfidenz: sinkt bei langer Route, Zoll, vielen Stopps
    konfidenz = 90
    if req.distanz_km > 1000:
        konfidenz -= 10
    if req.zoll_erforderlich:
        konfidenz -= 10
    if req.zwischenstopps > 2:
        konfidenz -= 5
    if req.transport_modus == TransportModus.SCHIFF:
        konfidenz -= 5
    konfidenz = max(50, min(95, konfidenz))

    hinweise: list[str] = []
    if req.zoll_erforderlich:
        hinweise.append("Zollabfertigung: +24 h eingeplant")
    if req.zwischenstopps > 0:
        hinweise.append(f"{req.zwischenstopps} Zwischenstopp(s): +{int(stopp_h)} h eingeplant")
    if req.priorisiert:
        hinweise.append("Prio-Sendung: reduzierter Puffer (5 %)")

    route = (
        f"{req.ursprungsort} → {req.zielort} "
        f"via {req.transport_modus.value} ({req.distanz_km:.0f} km)"
    )

    return ETABerechnungsErgebnis(
        lieferung_id=req.lieferung_id,
        geschaetzte_ankunft=eta_dt,
        konfidenz_prozent=konfidenz,
        berechnet_am=jetzt,
        puffer_stunden=round(puffer_h, 2),
        route_beschreibung=route,
        hinweise=hinweise,
    )


# ---------------------------------------------------------------------------
# Abweichungsalarme bewerten
# ---------------------------------------------------------------------------

# Schwellen für zeitliche Verzögerungen
_VERZOEGERUNG_WARNUNG_H: float = 4.0    # 4 Stunden → WARNUNG
_VERZOEGERUNG_KRITISCH_H: float = 24.0  # 24 Stunden → KRITISCH


def bewerte_zeitliche_abweichung(
    lieferung_id: str,
    alarm_id: str,
    verzoegerung_stunden: float,
    erkannt_am: datetime | None = None,
) -> AbweichungsAlarm:
    """
    Erzeugt einen Abweichungsalarm für eine Zeitverzögerung.

    - < 4 h   → INFO
    - 4–24 h  → WARNUNG
    - >= 24 h → KRITISCH (automatische Eskalation)
    """
    if erkannt_am is None:
        erkannt_am = datetime.utcnow()

    if verzoegerung_stunden < _VERZOEGERUNG_WARNUNG_H:
        schwere = AbweichungsSchwere.INFO
        eskalation = False
        empfaenger: list[str] = []
    elif verzoegerung_stunden < _VERZOEGERUNG_KRITISCH_H:
        schwere = AbweichungsSchwere.WARNUNG
        eskalation = False
        empfaenger = ["disposition@valeo.de"]
    else:
        schwere = AbweichungsSchwere.KRITISCH
        eskalation = True
        empfaenger = ["disposition@valeo.de", "leitung@valeo.de"]

    beschreibung = (
        f"Lieferung {lieferung_id} verzoegert sich um "
        f"{verzoegerung_stunden:.1f} Stunden."
    )

    return AbweichungsAlarm(
        alarm_id=alarm_id,
        lieferung_id=lieferung_id,
        typ=AbweichungsTyp.ZEITLICHE_VERZOEGERUNG,
        schwere=schwere,
        beschreibung=beschreibung,
        erkannt_am=erkannt_am,
        eskalations_empfaenger=empfaenger,
        automatisch_eskaliert=eskalation,
    )


def bewerte_mengenabweichung(
    lieferung_id: str,
    alarm_id: str,
    soll_menge: float,
    ist_menge: float,
    erkannt_am: datetime | None = None,
) -> AbweichungsAlarm:
    """
    Erzeugt einen Abweichungsalarm für eine Mengenabweichung.

    Abweichungsgrad = |ist - soll| / soll * 100 %
    - < 2 %  → INFO
    - 2–5 %  → WARNUNG
    - >= 5 % → KRITISCH
    """
    if erkannt_am is None:
        erkannt_am = datetime.utcnow()

    if soll_menge <= 0:
        raise ValueError("soll_menge muss positiv sein")

    abweichung_pct = abs(ist_menge - soll_menge) / soll_menge * 100.0

    if abweichung_pct < 2.0:
        schwere = AbweichungsSchwere.INFO
        eskalation = False
        empfaenger: list[str] = []
    elif abweichung_pct < 5.0:
        schwere = AbweichungsSchwere.WARNUNG
        eskalation = False
        empfaenger = ["wareneingang@valeo.de"]
    else:
        schwere = AbweichungsSchwere.KRITISCH
        eskalation = True
        empfaenger = ["wareneingang@valeo.de", "einkauf@valeo.de"]

    beschreibung = (
        f"Mengenabweichung: Soll {soll_menge:.2f}, Ist {ist_menge:.2f} "
        f"({abweichung_pct:.1f} % Abweichung)"
    )

    return AbweichungsAlarm(
        alarm_id=alarm_id,
        lieferung_id=lieferung_id,
        typ=AbweichungsTyp.MENGENABWEICHUNG,
        schwere=schwere,
        beschreibung=beschreibung,
        erkannt_am=erkannt_am,
        eskalations_empfaenger=empfaenger,
        automatisch_eskaliert=eskalation,
    )


# ---------------------------------------------------------------------------
# Gesamtstatus-Auswertung
# ---------------------------------------------------------------------------

# Fortschritts-Mapping nach Phase
_PHASE_FORTSCHRITT: dict[LieferkettenPhase, int] = {
    LieferkettenPhase.BESCHAFFUNG: 10,
    LieferkettenPhase.TRANSPORT_EINGEHEND: 30,
    LieferkettenPhase.LAGERUNG: 50,
    LieferkettenPhase.VERARBEITUNG: 65,
    LieferkettenPhase.TRANSPORT_AUSGEHEND: 80,
    LieferkettenPhase.AUSLIEFERUNG: 100,
}


def bewerte_lieferkettenstatus(
    lieferung_id: str,
    aktuelle_phase: LieferkettenPhase,
    events: list[TrackingEvent],
    alarme: list[AbweichungsAlarm],
    eta: ETABerechnungsErgebnis | None = None,
) -> LieferkettenStatusErgebnis:
    """
    Bewertet den Gesamtstatus einer Lieferkette.

    Gesamtlage-Logik:
    - ABGESCHLOSSEN  wenn phase == AUSLIEFERUNG und kein kritischer Alarm
    - KRITISCHE_ABWEICHUNG wenn >= 1 KRITISCH-Alarm aktiv
    - LEICHTE_ABWEICHUNG  wenn >= 1 WARNUNG-Alarm aktiv
    - PLANMAESSIG         sonst
    """
    aktive_alarme = [a for a in alarme if not a.behoben]
    hat_kritisch = any(a.schwere == AbweichungsSchwere.KRITISCH for a in aktive_alarme)
    hat_warnung = any(a.schwere == AbweichungsSchwere.WARNUNG for a in aktive_alarme)

    if aktuelle_phase == LieferkettenPhase.AUSLIEFERUNG and not hat_kritisch:
        gesamtlage = TrackingStatusGesamtlage.ABGESCHLOSSEN
    elif hat_kritisch:
        gesamtlage = TrackingStatusGesamtlage.KRITISCHE_ABWEICHUNG
    elif hat_warnung:
        gesamtlage = TrackingStatusGesamtlage.LEICHTE_ABWEICHUNG
    else:
        gesamtlage = TrackingStatusGesamtlage.PLANMAESSIG

    # Letzte 5 Events (zeitlich absteigend)
    sortierte_events = sorted(events, key=lambda e: e.zeitstempel, reverse=True)
    letzte_events = sortierte_events[:5]

    fortschritt = _PHASE_FORTSCHRITT.get(aktuelle_phase, 0)

    return LieferkettenStatusErgebnis(
        lieferung_id=lieferung_id,
        gesamtlage=gesamtlage,
        aktuelle_phase=aktuelle_phase,
        letzte_events=letzte_events,
        aktive_alarme=aktive_alarme,
        eta=eta,
        fortschritt_prozent=fortschritt,
    )


# ---------------------------------------------------------------------------
# Beispieldaten
# ---------------------------------------------------------------------------

def get_example_tracking_events(lieferung_id: str = "LF-2026-0001") -> list[TrackingEvent]:
    """Gibt Beispiel-TrackingEvents für Demo und Tests zurück."""
    basis = datetime(2026, 3, 10, 6, 0)
    return [
        TrackingEvent(
            event_id="EVT-001",
            lieferung_id=lieferung_id,
            typ=TrackingEventTyp.ABFAHRT,
            ort="Hannover-Lagerhaus",
            zeitstempel=basis,
            phase=LieferkettenPhase.TRANSPORT_EINGEHEND,
            meldender="Fahrer K. Müller",
            ist_meilenstein=True,
        ),
        TrackingEvent(
            event_id="EVT-002",
            lieferung_id=lieferung_id,
            typ=TrackingEventTyp.UMSCHLAG,
            ort="Bielefeld-Depot",
            zeitstempel=basis + timedelta(hours=3),
            phase=LieferkettenPhase.TRANSPORT_EINGEHEND,
            meldender="Depotleiter",
        ),
        TrackingEvent(
            event_id="EVT-003",
            lieferung_id=lieferung_id,
            typ=TrackingEventTyp.ANKUNFT,
            ort="Münster-Silo",
            zeitstempel=basis + timedelta(hours=6),
            phase=LieferkettenPhase.LAGERUNG,
            meldender="Wareneingang",
            ist_meilenstein=True,
        ),
    ]
