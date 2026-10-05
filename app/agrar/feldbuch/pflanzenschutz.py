"""
Pflanzenschutz-Dokumentation nach PflSchG / Cross Compliance (Welle AS-W4).

Reine, testbare Logik fuer die Vollstaendigkeits-/Compliance-Pruefung einer
PSM-Massnahme, den Kostensplit nach Wirkungsbereich und den Wartezeit-Hinweis
gegen einen geplanten Erntetermin.

PflSchG/CC-Pflichten je Anwendung: Mittel, Aufwandmenge, Flaeche, Datum,
Anwender (namentlich), Kultur/Anwendungsgebiet, Begruendung/Grund. Die
Wartezeit sichert den Abstand zur Ernte.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Iterable, List, Optional

WIRKUNGSBEREICHE = ("Herbizid", "Fungizid", "Insektizid", "Wachstumsregler", "Sonstiges")


@dataclass
class PsmMassnahme:
    datum: Optional[date]
    mittel: Optional[str]
    menge: Optional[float]
    flaeche: Optional[float]
    anwender: Optional[str]
    wirkungsbereich: Optional[str] = None
    begruendung: Optional[str] = None
    wartezeit_tage: Optional[int] = None
    kosten_eur: Optional[float] = None
    sachkunde_nummer: Optional[str] = None
    sachkunde_gueltig_bis: Optional[date] = None


def psm_compliance(m: PsmMassnahme) -> Dict[str, object]:
    """Prueft die PflSchG-/CC-Pflichtangaben einer PSM-Massnahme."""
    from app.agrar.feldbuch.sachkunde import pruefe_sachkunde

    fehlend: List[str] = []
    if not m.mittel:
        fehlend.append("Mittel")
    if not m.menge or m.menge <= 0:
        fehlend.append("Aufwandmenge")
    if not m.flaeche or m.flaeche <= 0:
        fehlend.append("Flaeche")
    if not m.datum:
        fehlend.append("Datum")
    if not m.anwender:
        fehlend.append("Anwender")
    if not m.begruendung:
        fehlend.append("Begruendung")
    sk = pruefe_sachkunde(
        anwender=m.anwender,
        sachkunde_nummer=m.sachkunde_nummer,
        gueltig_bis=m.sachkunde_gueltig_bis,
        anwendungsdatum=m.datum,
    )
    for item in sk["fehlende"]:
        if item not in fehlend:
            fehlend.append(item)
    return {"compliant": len(fehlend) == 0, "fehlende_pflichtangaben": fehlend}


def wartezeit_hinweis(
    anwendungsdatum: Optional[date],
    wartezeit_tage: Optional[int],
    geplante_ernte: Optional[date],
) -> Optional[Dict[str, object]]:
    """Warnt, wenn die Wartezeit die geplante Ernte nicht einhaelt."""
    if not anwendungsdatum or not wartezeit_tage or not geplante_ernte:
        return None
    fruehestens = date.fromordinal(anwendungsdatum.toordinal() + int(wartezeit_tage))
    eingehalten = geplante_ernte >= fruehestens
    return {
        "fruehester_erntetermin": fruehestens.isoformat(),
        "geplante_ernte": geplante_ernte.isoformat(),
        "wartezeit_eingehalten": eingehalten,
    }


def kostensplit_nach_wirkungsbereich(massnahmen: Iterable[PsmMassnahme]) -> Dict[str, float]:
    """Summiert PSM-Kosten je Wirkungsbereich (Herbizid/Fungizid/Insektizid/…)."""
    split: Dict[str, float] = {b: 0.0 for b in WIRKUNGSBEREICHE}
    for m in massnahmen:
        bereich = m.wirkungsbereich if m.wirkungsbereich in WIRKUNGSBEREICHE else "Sonstiges"
        split[bereich] += float(m.kosten_eur or 0.0)
    return {k: round(v, 2) for k, v in split.items()}
