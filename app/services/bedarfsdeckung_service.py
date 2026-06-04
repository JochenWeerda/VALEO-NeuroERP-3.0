"""Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — „Die Lücke ist das Vertriebsobjekt".

Stellt je Betrieb den objektiven Jahresbedarf je Produktgruppe (Potenzial) dem
tatsächlichen Ist-Bezug (rollierend 12 M, public.kunden_produktgruppen_bezug)
gegenüber und berechnet Deckungsgrad, Bedarfslücke und Next-Best-Offer.

Zwei Sparten, die sich je Betrieb kombinieren (gemischte Betriebe sehen beide):
- **Milchvieh**: Potenzial aus Herde/Leistung (€/1.000 l Milch), 6 Produktgruppen
  (Wiederverwendung aus milchvieh_crosssell_service).
- **Ackerbau**: Potenzial aus der Marktfrucht-Ackerfläche (€/ha), 3 Produktgruppen
  (Dünger/PSM/Saatgut). Die Grundfutterfläche ist bereits in der Milchvieh-Gruppe
  `grundfutterbau` erfasst und in der Ackerfläche abgezogen (keine Doppelzählung).

    Deckungsgrad % = Ist / Bedarf,  Bedarfslücke € = Bedarf − Ist,
    Chance-Score   = Lücke € × Marge-Faktor × Einstiegs-/Ausbau-Gewicht
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

# Ackerbau-Produktgruppen: €/ha/Jahr Marktfrucht (regional gemittelt über
# Winterweizen/-gerste/Raps; transparente, anpassbare Richtwerte).
ACKERBAU_PRODUKTGRUPPEN = [
    ("duenger_marktfrucht", "Dünger Marktfrucht (N/P/K, Kalk)", 110, 240),
    ("pflanzenschutz", "Pflanzenschutz (Herbizid/Fungizid/Insektizid)", 80, 200),
    ("saatgut_marktfrucht", "Saatgut Marktfrucht (Z-Saat/Hybrid)", 60, 150),
]

# Grobe Margen-Gewichtung je Produktgruppe (Priorisierung der Lücke nach Ertrag).
MARGE_FAKTOR = {
    "kraftfutter": 0.9, "mineral_spezial": 1.6, "kaelber": 1.5,
    "grundfutterbau": 1.1, "stallbedarf_hygiene": 1.4, "beratung_analyse": 1.2,
    "duenger_marktfrucht": 1.0, "pflanzenschutz": 1.3, "saatgut_marktfrucht": 1.1,
}


def _aktion(deckung_pct: float, ist: float) -> str:
    if ist <= 0:
        return "Einstieg"
    if deckung_pct < 40:
        return "Cross-Sell"
    if deckung_pct < 80:
        return "Ausbauen"
    return "Halten"


def _empfehlung(key: str, label: str, herd: int, kf_t_jahr: float, acker_ha: float, luecke: float) -> str:
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
    if key == "duenger_marktfrucht":
        return (f"Dünger Marktfrucht: ~{acker_ha:.0f} ha Ackerfläche. "
                f"Vorschlag: N-Düngung-Frühbezug + Kalk-Erhaltungsdüngung anbieten.")
    if key == "pflanzenschutz":
        return (f"Pflanzenschutz: ~{acker_ha:.0f} ha — Herbizid/Fungizid-Programm. "
                f"Vorschlag: Spritzplan + Saison-Komplettpaket kalkulieren.")
    if key == "saatgut_marktfrucht":
        return (f"Saatgut: ~{acker_ha:.0f} ha — Z-Saatgut/Hybriden. "
                f"Vorschlag: Sortenberatung + Frühbezugskonditionen.")
    return f"{label}: Lücke ~{luecke:.0f} €/Jahr — Angebot/Beratungstermin vorschlagen."


class BedarfsdeckungService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # ── Stammdaten / Profile ──────────────────────────────────────────────
    def _milchvieh(self, kunden_nr: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                """
                SELECT p.herd_size_kuehe, p.milch_kg, p.fett_pct, p.eiw_pct, p.hygiene_bedarf
                FROM public.kunden_milchvieh_profil p
                WHERE p.kunden_nr = :k
                """
            ),
            {"k": kunden_nr},
        ).mappings().first()
        return dict(r) if r else None

    def _ackerbau(self, kunden_nr: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT ackerflaeche_ha, gesamtflaeche_ha, quelle FROM public.kunden_ackerbau_profil WHERE kunden_nr = :k"
            ),
            {"k": kunden_nr},
        ).mappings().first()
        return dict(r) if r else None

    def _stamm(self, kunden_nr: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT kunden_nr, name1 AS name, plz, ort FROM public.kunden "
                "WHERE kunden_nr = :k AND coalesce(geloescht, FALSE) = FALSE"
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

    # ── Gruppen-Aufbau ────────────────────────────────────────────────────
    def _gruppe(self, key: str, label: str, sparte: str, bedarf: int, ist: dict) -> dict:
        ist_row = ist.get(key, {})
        ist_eur = round(float(ist_row.get("umsatz_12m_eur") or 0))
        luecke = max(0, bedarf - ist_eur)
        deckung = round(ist_eur / bedarf * 100) if bedarf > 0 else 0
        score = round(luecke * MARGE_FAKTOR.get(key, 1.0) * (1.3 if ist_eur <= 0 else 1.0))
        return {
            "key": key, "label": label, "sparte": sparte,
            "bedarf_jahr_eur": bedarf, "ist_12m_eur": ist_eur,
            "deckung_pct": min(deckung, 100), "luecke_eur": luecke,
            "score": score, "aktion": _aktion(deckung, ist_eur),
            "letzter_bezug": str(ist_row["letzter_bezug"]) if ist_row.get("letzter_bezug") else None,
            "quelle": ist_row.get("quelle") or "geschaetzt",
        }

    def cockpit(self, kunden_nr: str) -> dict:
        stamm = self._stamm(kunden_nr)
        if not stamm:
            return {}
        mv = self._milchvieh(kunden_nr)
        ab = self._ackerbau(kunden_nr)
        if not mv and not ab:
            return {}
        ist = self._ist_map(kunden_nr)
        gruppen: list[dict] = []

        # — Milchvieh —
        herd = 0
        milchmenge_l = 0
        kf_t_jahr = 0.0
        ecm = None
        if mv:
            herd = int(mv["herd_size_kuehe"] or 0)
            milch = float(mv["milch_kg"]) if mv["milch_kg"] is not None else None
            ecm = ecm_kg(milch, mv["fett_pct"] and float(mv["fett_pct"]), mv["eiw_pct"] and float(mv["eiw_pct"]))
            milchmenge_l = round((milch or 0.0) * herd)
            kf_t_jahr = round((ecm or 0.0) * ((KF_G_PER_KG_ECM_MIN + KF_G_PER_KG_ECM_MAX) / 2) / 1000.0 * herd / 1000.0, 1)
            k1000 = milchmenge_l / 1000.0
            for key, label, lo, hi in PRODUKTGRUPPEN:
                gruppen.append(self._gruppe(key, label, "milchvieh", round(k1000 * (lo + hi) / 2), ist))

        # — Ackerbau —
        acker_ha = 0.0
        if ab:
            acker_ha = float(ab["ackerflaeche_ha"] or 0)
            for key, label, lo, hi in ACKERBAU_PRODUKTGRUPPEN:
                gruppen.append(self._gruppe(key, label, "ackerbau", round(acker_ha * (lo + hi) / 2), ist))

        nbo_grp = max(gruppen, key=lambda g: g["score"], default=None)
        next_best_offer = None
        if nbo_grp and nbo_grp["luecke_eur"] > 0:
            next_best_offer = {
                "produktgruppe": nbo_grp["key"], "label": nbo_grp["label"], "sparte": nbo_grp["sparte"],
                "luecke_eur": nbo_grp["luecke_eur"], "score": nbo_grp["score"],
                "empfehlung": _empfehlung(nbo_grp["key"], nbo_grp["label"], herd, kf_t_jahr, acker_ha, nbo_grp["luecke_eur"]),
            }

        bedarf_ges = sum(g["bedarf_jahr_eur"] for g in gruppen)
        ist_ges = sum(g["ist_12m_eur"] for g in gruppen)
        sparten = [s for s, has in (("milchvieh", bool(mv)), ("ackerbau", bool(ab))) if has]
        return {
            "kunden_nr": kunden_nr, "name": stamm["name"], "plz": stamm["plz"], "ort": stamm["ort"],
            "sparten": sparten,
            "herd_size_kuehe": herd, "milchmenge_l_jahr": milchmenge_l,
            "ecm_kg": round(ecm) if ecm else None, "kraftfutter_t_jahr": kf_t_jahr,
            "ackerflaeche_ha": round(acker_ha, 1),
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
                SELECT DISTINCT k.kunden_nr
                FROM public.kunden k
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                  AND (EXISTS (SELECT 1 FROM public.kunden_milchvieh_profil m WHERE m.kunden_nr = k.kunden_nr)
                    OR EXISTS (SELECT 1 FROM public.kunden_ackerbau_profil a WHERE a.kunden_nr = k.kunden_nr))
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
                "sparten": cp["sparten"],
                "herd_size_kuehe": cp["herd_size_kuehe"], "ackerflaeche_ha": cp["ackerflaeche_ha"],
                "deckung_pct_gesamt": cp["deckung_pct_gesamt"],
                "luecke_eur_gesamt": cp["luecke_eur_gesamt"],
                "top_produktgruppe": nbo["label"], "top_sparte": nbo["sparte"],
                "top_luecke_eur": nbo["luecke_eur"], "top_score": nbo["score"], "empfehlung": nbo["empfehlung"],
            })
        out.sort(key=lambda x: x["top_score"], reverse=True)
        return out[:limit]
