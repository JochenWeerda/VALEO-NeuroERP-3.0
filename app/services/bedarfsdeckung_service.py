"""Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — „Die Lücke ist das Vertriebsobjekt".

Stellt je Betrieb den objektiven Jahresbedarf je Produktgruppe (Potenzial, aus dem
Milchvieh-Profil abgeleitet) dem tatsächlichen Ist-Bezug (rollierend 12 M,
public.kunden_produktgruppen_bezug) gegenüber und berechnet:

    Deckungsgrad % = Ist / Bedarf × 100
    Bedarfslücke € = Bedarf − Ist
    Chance-Score   = Lücke € × Marge-Faktor × Einstiegs-/Ausbau-Gewicht

Aus der größten Lücke wird ein konkretes Next-Best-Offer abgeleitet (Produktgruppe,
Vorschlagsmenge, Begründung) — eine direkt ausführbare Verkäuferaktion.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.milchvieh_crosssell_service import (
    KF_G_PER_KG_ECM_MIN,
    KF_G_PER_KG_ECM_MAX,
    PRODUKTGRUPPEN,
    ecm_kg,
)

# Grobe Margen-Gewichtung je Produktgruppe (Priorisierung der Lücke nach Ertrag).
MARGE_FAKTOR = {
    "kraftfutter": 0.9,           # hohe Menge, niedrige Marge
    "mineral_spezial": 1.6,       # hohe Marge
    "kaelber": 1.5,
    "grundfutterbau": 1.1,
    "stallbedarf_hygiene": 1.4,
    "beratung_analyse": 1.2,
}

# Aktions-Label nach Deckungsgrad.
def _aktion(deckung_pct: float, ist: float) -> str:
    if ist <= 0:
        return "Einstieg"
    if deckung_pct < 40:
        return "Cross-Sell"
    if deckung_pct < 80:
        return "Ausbauen"
    return "Halten"


def _empfehlung(key: str, label: str, herd: int, kf_t_jahr: float, luecke: float) -> str:
    """Konkreter, ausführbarer Vorschlag für die größte Lücke."""
    if key == "kraftfutter" and kf_t_jahr > 0:
        start = max(1.0, round(kf_t_jahr * 0.25, 1))
        return (f"Kraftfutter: Bedarf ~{kf_t_jahr:.0f} t/Jahr, große ungedeckte Menge. "
                f"Vorschlag: Startmenge {start:g} t mit Probelieferung + Rationscheck.")
    if key == "mineral_spezial":
        return (f"Mineral-/Spezialfutter: bei {herd} Kühen ~{max(1, round(herd*0.06)):d} t/Jahr. "
                f"Vorschlag: Mineralfutter-Angebot 1 t Startmenge vor Weideaustrieb.")
    if key == "kaelber":
        return ("Kälberprodukte: Milchaustauscher/Starter — Einstieg über Kälberstall. "
                "Vorschlag: 1 Palette MAT + Starter als Probe.")
    if key == "grundfutterbau":
        return ("Grundfutterbau: Saatgut/Dünger/PSM/Siliermittel/Folie zur Saison bündeln. "
                "Vorschlag: Frühbezugs-Paket Mais/Grünland anbieten.")
    if key == "stallbedarf_hygiene":
        return ("Stallbedarf/Hygiene: Einstreu/Dippmittel/Klauenpflege als Abo. "
                "Vorschlag: Hygiene-Grundausstattung + Nachbezug quartalsweise.")
    return f"{label}: Lücke ~{luecke:.0f} €/Jahr — Angebot/Beratungstermin vorschlagen."


class BedarfsdeckungService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # ── Betriebs-Stammdaten + Potenzial ───────────────────────────────────
    def _profil(self, kunden_nr: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                """
                SELECT k.kunden_nr, k.name1 AS name, k.plz, k.ort,
                       p.herd_size_kuehe, p.herd_size_group, p.milch_kg,
                       p.fett_pct, p.eiw_pct, p.hygiene_bedarf
                FROM public.kunden_milchvieh_profil p
                JOIN public.kunden k USING (kunden_nr)
                WHERE k.kunden_nr = :k AND coalesce(k.geloescht, FALSE) = FALSE
                """
            ),
            {"k": kunden_nr},
        ).mappings().first()
        return dict(r) if r else None

    def _ist_map(self, kunden_nr: str) -> dict[str, dict]:
        rows = self.db.execute(
            text(
                "SELECT produktgruppe, umsatz_12m_eur, menge_12m, db_12m_eur, letzter_bezug, quelle "
                "FROM public.kunden_produktgruppen_bezug WHERE kunden_nr = :k AND tenant_id = :t"
            ),
            {"k": kunden_nr, "t": self.tenant_id},
        ).mappings().all()
        return {r["produktgruppe"]: dict(r) for r in rows}

    def cockpit(self, kunden_nr: str) -> dict:
        prof = self._profil(kunden_nr)
        if not prof:
            return {}
        herd = int(prof["herd_size_kuehe"] or 0)
        milch = float(prof["milch_kg"]) if prof["milch_kg"] is not None else None
        ecm = ecm_kg(milch, prof["fett_pct"] and float(prof["fett_pct"]), prof["eiw_pct"] and float(prof["eiw_pct"]))
        milchmenge_l = round((milch or 0.0) * herd)
        kf_t_jahr = round((ecm or 0.0) * ((KF_G_PER_KG_ECM_MIN + KF_G_PER_KG_ECM_MAX) / 2) / 1000.0 * herd / 1000.0, 1)
        k1000 = milchmenge_l / 1000.0
        ist = self._ist_map(kunden_nr)

        gruppen = []
        for key, label, lo, hi in PRODUKTGRUPPEN:
            bedarf = round(k1000 * (lo + hi) / 2)  # Mittel des €/1.000 l-Korridors
            ist_row = ist.get(key, {})
            ist_eur = round(float(ist_row.get("umsatz_12m_eur") or 0))
            luecke = max(0, bedarf - ist_eur)
            deckung = round(ist_eur / bedarf * 100) if bedarf > 0 else 0
            score = round(luecke * MARGE_FAKTOR.get(key, 1.0) * (1.3 if ist_eur <= 0 else 1.0))
            gruppen.append({
                "key": key, "label": label,
                "bedarf_jahr_eur": bedarf, "ist_12m_eur": ist_eur,
                "deckung_pct": min(deckung, 100), "luecke_eur": luecke,
                "score": score, "aktion": _aktion(deckung, ist_eur),
                "letzter_bezug": str(ist_row["letzter_bezug"]) if ist_row.get("letzter_bezug") else None,
                "quelle": ist_row.get("quelle") or "geschaetzt",
            })

        # Next-Best-Offer = höchster Score (Lücke × Marge × Einstieg).
        nbo_grp = max(gruppen, key=lambda g: g["score"], default=None)
        next_best_offer = None
        if nbo_grp and nbo_grp["luecke_eur"] > 0:
            next_best_offer = {
                "produktgruppe": nbo_grp["key"], "label": nbo_grp["label"],
                "luecke_eur": nbo_grp["luecke_eur"], "score": nbo_grp["score"],
                "empfehlung": _empfehlung(nbo_grp["key"], nbo_grp["label"], herd, kf_t_jahr, nbo_grp["luecke_eur"]),
            }

        bedarf_ges = sum(g["bedarf_jahr_eur"] for g in gruppen)
        ist_ges = sum(g["ist_12m_eur"] for g in gruppen)
        return {
            "kunden_nr": kunden_nr, "name": prof["name"], "plz": prof["plz"], "ort": prof["ort"],
            "herd_size_kuehe": herd, "milchmenge_l_jahr": milchmenge_l,
            "ecm_kg": round(ecm) if ecm else None, "kraftfutter_t_jahr": kf_t_jahr,
            "bedarf_jahr_eur_gesamt": bedarf_ges, "ist_12m_eur_gesamt": ist_ges,
            "luecke_eur_gesamt": max(0, bedarf_ges - ist_ges),
            "deckung_pct_gesamt": round(ist_ges / bedarf_ges * 100) if bedarf_ges > 0 else 0,
            "produktgruppen": gruppen,
            "next_best_offer": next_best_offer,
        }

    # ── Durchdringungs-Pipeline (aggregiert über alle Betriebe) ───────────
    def pipeline(self, limit: int = 100) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT k.kunden_nr, k.name1 AS name, k.plz, k.ort, p.herd_size_kuehe,
                       p.milch_kg, p.fett_pct, p.eiw_pct
                FROM public.kunden_milchvieh_profil p
                JOIN public.kunden k USING (kunden_nr)
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                """
            )
        ).mappings().all()
        out = []
        for r in rows:
            cp = self.cockpit(r["kunden_nr"])
            if not cp or not cp.get("next_best_offer"):
                continue
            nbo = cp["next_best_offer"]
            out.append({
                "kunden_nr": cp["kunden_nr"], "name": cp["name"], "plz": cp["plz"], "ort": cp["ort"],
                "herd_size_kuehe": cp["herd_size_kuehe"],
                "deckung_pct_gesamt": cp["deckung_pct_gesamt"],
                "luecke_eur_gesamt": cp["luecke_eur_gesamt"],
                "top_produktgruppe": nbo["label"], "top_luecke_eur": nbo["luecke_eur"],
                "top_score": nbo["score"], "empfehlung": nbo["empfehlung"],
            })
        out.sort(key=lambda x: x["top_score"], reverse=True)
        return out[:limit]
