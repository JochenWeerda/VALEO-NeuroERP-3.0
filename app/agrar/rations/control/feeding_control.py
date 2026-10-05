"""DLG 01|2025 feeding-control calculations (chapters 11 and 12)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

MIXING_ACCURACY_WARN_PCT = 5.0

@dataclass
class LoadedComponent:
    feed_id: str
    name: str
    soll_kg: float
    ist_kg: float

@dataclass
class ComponentAccuracy:
    feed_id: str
    name: str
    soll_kg: float
    ist_kg: float
    abweichung_kg: float
    abweichung_pct: Optional[float]
    innerhalb_toleranz: bool

@dataclass
class FeedingControlResult:
    tm_verzehr_kg_kuh: Optional[float]
    vorgelegt_kg: float
    restfutter_kg: float
    aufgenommen_fm_kg: float
    tierzahl: int
    tm_pct: float
    mischgenauigkeit_pct: Optional[float]
    mischgenauigkeit_ok: bool
    komponenten: List[ComponentAccuracy] = field(default_factory=list)
    iofc_eur_kuh: Optional[float] = None
    futterkosten_eur_kuh: Optional[float] = None
    schuettelbox: Optional[Dict[str, Any]] = None
    futtertisch_temp_c: Optional[float] = None
    umgebung_temp_c: Optional[float] = None
    warnungen: List[str] = field(default_factory=list)
    anpassungsvorschlaege: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tm_verzehr_kg_kuh": self.tm_verzehr_kg_kuh,
            "vorgelegt_kg": round(self.vorgelegt_kg, 2),
            "restfutter_kg": round(self.restfutter_kg, 2),
            "aufgenommen_fm_kg": round(self.aufgenommen_fm_kg, 2),
            "tierzahl": self.tierzahl,
            "tm_pct": round(self.tm_pct, 1),
            "mischgenauigkeit_pct": self.mischgenauigkeit_pct,
            "mischgenauigkeit_ok": self.mischgenauigkeit_ok,
            "komponenten": [{
                "feed_id": c.feed_id, "name": c.name,
                "soll_kg": round(c.soll_kg, 2), "ist_kg": round(c.ist_kg, 2),
                "abweichung_kg": round(c.abweichung_kg, 2),
                "abweichung_pct": c.abweichung_pct,
                "innerhalb_toleranz": c.innerhalb_toleranz,
            } for c in self.komponenten],
            "iofc_eur_kuh": self.iofc_eur_kuh,
            "futterkosten_eur_kuh": self.futterkosten_eur_kuh,
            "schuettelbox": self.schuettelbox,
            "futtertisch_temp_c": self.futtertisch_temp_c,
            "umgebung_temp_c": self.umgebung_temp_c,
            "warnungen": self.warnungen,
            "anpassungsvorschlaege": self.anpassungsvorschlaege,
        }

def tm_verzehr_je_kuh(vorgelegt_kg: float, restfutter_kg: float, tm_pct: float, tierzahl: int) -> Optional[float]:
    if tierzahl <= 0:
        return None
    return round(max(vorgelegt_kg - restfutter_kg, 0.0) * tm_pct / 100.0 / tierzahl, 2)

def component_accuracy(comp: LoadedComponent) -> ComponentAccuracy:
    delta = comp.ist_kg - comp.soll_kg
    pct = round(abs(delta) / comp.soll_kg * 100.0, 1) if comp.soll_kg > 1e-9 else None
    ok = pct <= MIXING_ACCURACY_WARN_PCT if pct is not None else comp.ist_kg <= 1e-9
    return ComponentAccuracy(comp.feed_id, comp.name, comp.soll_kg, comp.ist_kg, delta, pct, ok)

def evaluate_shaker_box(*, oben_pct: float, mitte_pct: float, unten_pct: float,
                        fein_pct: float = 0.0, pendf_soll_g_kgdm: Optional[float] = None,
                        ndf_g_kgdm: Optional[float] = None) -> Dict[str, Any]:
    values = [oben_pct, mitte_pct, unten_pct, fein_pct]
    if any(v < 0 for v in values):
        raise ValueError("Schuettelbox-Anteile duerfen nicht negativ sein.")
    if abs(sum(values) - 100.0) > 1.0:
        raise ValueError("Schuettelbox-Anteile muessen zusammen 100 % ergeben (Toleranz 1 %-Punkt).")
    structure = round(oben_pct + mitte_pct, 1)
    actual = round(ndf_g_kgdm * structure / 100.0, 1) if ndf_g_kgdm is not None else None
    delta = round(actual - pendf_soll_g_kgdm, 1) if actual is not None and pendf_soll_g_kgdm is not None else None
    status = "nicht_bewertbar" if delta is None else ("gruen" if delta >= 0 else "gelb" if delta >= -15 else "rot")
    return {"oben_pct": round(oben_pct, 1), "mitte_pct": round(mitte_pct, 1),
            "unten_pct": round(unten_pct, 1), "fein_pct": round(fein_pct, 1),
            "struktur_gt_8mm_pct": structure, "pendf_soll_g_kgdm": pendf_soll_g_kgdm,
            "pendf_ist_g_kgdm": actual, "pendf_delta_g_kgdm": delta, "status": status,
            "selektionsrisiko": oben_pct > 15.0}

def compute_feeding_control(komponenten: List[LoadedComponent], restfutter_kg: float, tierzahl: int,
                            tm_pct: float, *, milch_kg_kuh: Optional[float] = None,
                            milchpreis_eur_kg: Optional[float] = None,
                            futterkosten_eur_kuh: Optional[float] = None,
                            schuettelbox: Optional[Dict[str, Any]] = None,
                            futtertisch_temp_c: Optional[float] = None,
                            umgebung_temp_c: Optional[float] = None) -> FeedingControlResult:
    vorgelegt = sum(max(c.ist_kg, 0.0) for c in komponenten)
    comp_acc = [component_accuracy(c) for c in komponenten]
    soll = sum(max(c.soll_kg, 0.0) for c in komponenten)
    deviation = sum(abs(c.ist_kg - c.soll_kg) for c in komponenten)
    mixing = round(deviation / soll * 100.0, 1) if soll > 1e-9 else None
    mixing_ok = mixing <= MIXING_ACCURACY_WARN_PCT if mixing is not None else True
    warnings: List[str] = []
    suggestions: List[str] = []
    if not mixing_ok:
        warnings.append(f"Mischgenauigkeit {mixing:.1f} % ueber der DLG-Toleranz von 5 %.")
        suggestions.append("Mischwagenbeladung pruefen und Komponenten mit mehr als 5 % Abweichung korrigieren.")
    for c in comp_acc:
        if c.abweichung_pct is not None and not c.innerhalb_toleranz:
            warnings.append(f"{c.name}: Abweichung {c.abweichung_pct:.1f} % (Ist {c.ist_kg:.1f} vs. Soll {c.soll_kg:.1f} kg).")
    if schuettelbox and schuettelbox.get("status") in {"gelb", "rot"}:
        suggestions.append("Strukturquelle und Mischdauer pruefen; peNDF-Ist liegt unter dem Rations-Soll.")
    if schuettelbox and schuettelbox.get("selektionsrisiko"):
        warnings.append("Hoher Obersiebanteil: Entmischungs- oder Selektionsrisiko pruefen.")
    if futtertisch_temp_c is not None and umgebung_temp_c is not None and futtertisch_temp_c - umgebung_temp_c > 5:
        warnings.append("Nacherwaermung > 5 C: Silomanagement, Vorschub und Futtertischhygiene pruefen.")
        suggestions.append("Nacherwaermung durch kuerzere Vorlageintervalle und saubere Anschnittflaeche reduzieren.")
    iofc = round(milch_kg_kuh * milchpreis_eur_kg - futterkosten_eur_kuh, 2) if None not in (milch_kg_kuh, milchpreis_eur_kg, futterkosten_eur_kuh) else None
    return FeedingControlResult(tm_verzehr_je_kuh(vorgelegt, restfutter_kg, tm_pct, tierzahl),
        vorgelegt, restfutter_kg, max(vorgelegt-restfutter_kg, 0), tierzahl, tm_pct, mixing,
        mixing_ok, comp_acc, iofc, round(futterkosten_eur_kuh, 2) if futterkosten_eur_kuh is not None else None,
        schuettelbox, futtertisch_temp_c, umgebung_temp_c, warnings, suggestions)