"""Cross-Sell-Auswertung Milchvieh: Hygiene-Bedarf + Kraftfutter-Potenzial.

Leitet aus ``public.kunden_milchvieh_profil`` (Herde/Leistung/Zellzahl) konkrete
Verkaufspotenziale je Milchvieh-Kunde ab:

- **Eutergesundheit/Hygiene** (Dippmittel/Reiniger): Basisverbrauch je Kuh/Jahr,
  gewichtet nach ``hygiene_bedarf`` (Zellzahl-Indikator) × Herdengröße.
- **Kraftfutter**: ~219–237 g je kg ECM × ECM-Leistung × Herdengröße → t/Jahr.

ECM (energiekorrigierte Milch, DLG):
    ECM_kg = Milch_kg × (0,38 × Fett% + 0,21 × Eiweiß% + 1,05) / 3,28

Planungsannahmen (Koeffizienten) sind bewusst transparent und anpassbar.
Reine Lese-/Rechenschicht (keine Mutation).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Kraftfutter-Bedarf je kg ECM (Spanne lt. Vorgabe).
KF_G_PER_KG_ECM_MIN = 219
KF_G_PER_KG_ECM_MAX = 237

# Landhandel-Cross-Sell-Umsatzpotenzial je 1.000 l Milch (€), Praxis-Richtwerte
# (BZA/Rinder-Report): adressierbar 150-260 (Zielwert 200), konservativ
# gewinnbarer Zusatzumsatz 80-120. Milch kg ~ Liter.
CROSSSELL_EUR_PER_1000L_MIN = 150
CROSSSELL_EUR_PER_1000L_ZIEL = 200
CROSSSELL_EUR_PER_1000L_MAX = 260
GEWINNBAR_EUR_PER_1000L_MIN = 80
GEWINNBAR_EUR_PER_1000L_MAX = 120

# Dippmittel/Euterhygiene-Basisverbrauch je Kuh/Jahr (L) und Bedarfsgewichtung.
DIPP_L_PER_COW_BASE = 8.0
HYGIENE_FACTOR = {"niedrig": 1.0, "mittel": 1.3, "hoch": 1.7}
HYGIENE_RANK = {"hoch": 3, "mittel": 2, "niedrig": 1}

# Cross-Sell-Aufschlüsselung nach Produktgruppen: (key, Label, €/1.000 l min, max).
# Summe der Spannen ≈ 150–268 €/1.000 l (= adressierbares Gesamtpotenzial).
PRODUKTGRUPPEN = [
    ("kraftfutter", "Kraftfutter/Eiweiß/Ausgleichsfutter", 90, 130),
    ("mineral_spezial", "Mineral-/Spezialfutter, Puffer, Hefen, Toxinbinder", 10, 25),
    ("kaelber", "Kälberfutter/Milchaustauscher/Starter", 8, 20),
    ("grundfutterbau", "Grundfutterbau (Saatgut/Dünger/PSM/Siliermittel/Folie)", 30, 60),
    ("stallbedarf_hygiene", "Einstreu/Hygiene/Klauenpflege/Stallbedarf", 10, 25),
    ("beratung_analyse", "Beratung/Analyse/Rationsservice", 2, 8),
]


def produktgruppen_potenzial(milchmenge_l: float) -> list[dict]:
    """€-Potenzial je Produktgruppe aus der Jahresmilchmenge (kg ~ l)."""
    k = (milchmenge_l or 0.0) / 1000.0
    return [
        {"key": key, "label": label, "eur_per_1000l": [lo, hi],
         "eur_jahr_min": round(k * lo), "eur_jahr_max": round(k * hi)}
        for key, label, lo, hi in PRODUKTGRUPPEN
    ]


def ecm_kg(milch_kg: Optional[float], fett_pct: Optional[float], eiw_pct: Optional[float]) -> Optional[float]:
    """ECM je Kuh/Jahr nach DLG-Formel; None wenn Eingaben fehlen."""
    if not milch_kg or fett_pct is None or eiw_pct is None:
        return None
    return milch_kg * (0.38 * fett_pct + 0.21 * eiw_pct + 1.05) / 3.28


def _f(v) -> Optional[float]:
    return float(v) if v is not None else None


class MilchviehCrossSellService:
    """Berechnet die Cross-Sell-Potenziale für Milchvieh-Kunden."""

    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        # public.kunden_milchvieh_profil ist nicht mandanten-skaliert (kein tenant_id);
        # tenant_id wird für Signatur-Konsistenz akzeptiert, aber nicht gefiltert.
        self.db = db
        self.tenant_id = tenant_id

    def _rows(self) -> list[dict]:
        return [
            dict(r)
            for r in self.db.execute(
                text(
                    """
                    SELECT k.kunden_nr, k.name1 AS name, k.plz, k.ort,
                           p.herd_size_kuehe, p.herd_size_group, p.milch_kg,
                           p.fett_pct, p.eiw_pct, p.zellzahl_tsd_ml,
                           p.zellzahl_quelle, p.hygiene_bedarf
                    FROM public.kunden_milchvieh_profil p
                    JOIN public.kunden k USING (kunden_nr)
                    WHERE coalesce(k.geloescht, FALSE) = FALSE
                    """
                )
            ).mappings().all()
        ]

    def _build(self, r: dict) -> dict:
        herd = int(r["herd_size_kuehe"] or 0)
        milch = _f(r["milch_kg"])
        ecm = ecm_kg(milch, _f(r["fett_pct"]), _f(r["eiw_pct"]))
        bedarf = r["hygiene_bedarf"] or "niedrig"

        kf_cow_min = (ecm or 0.0) * KF_G_PER_KG_ECM_MIN / 1000.0  # kg/Kuh/Jahr
        kf_cow_max = (ecm or 0.0) * KF_G_PER_KG_ECM_MAX / 1000.0
        kf_t_min = round(kf_cow_min * herd / 1000.0, 1)            # t/Jahr/Betrieb
        kf_t_max = round(kf_cow_max * herd / 1000.0, 1)

        dipp_l = round(DIPP_L_PER_COW_BASE * HYGIENE_FACTOR.get(bedarf, 1.0) * herd)

        # Landhandel-Kennzahl: Cross-Sell-Umsatzpotenzial aus der Jahresmilchmenge.
        milchmenge_l = round((milch or 0.0) * herd)  # l/Jahr (kg ~ l)
        k = milchmenge_l / 1000.0
        return {
            "kunden_nr": r["kunden_nr"],
            "name": r["name"],
            "plz": r["plz"],
            "ort": r["ort"],
            "herd_size_kuehe": herd,
            "herd_size_group": r["herd_size_group"],
            "milch_kg": round(milch) if milch else None,
            "ecm_kg": round(ecm) if ecm else None,
            "milchmenge_l_jahr": milchmenge_l,
            "fett_pct": _f(r["fett_pct"]),
            "eiw_pct": _f(r["eiw_pct"]),
            "zellzahl_tsd_ml": r["zellzahl_tsd_ml"],
            "zellzahl_quelle": r["zellzahl_quelle"],
            "hygiene_bedarf": bedarf,
            "hygiene_dipp_l_jahr": dipp_l,
            "kraftfutter_t_jahr_min": kf_t_min,
            "kraftfutter_t_jahr_max": kf_t_max,
            "crosssell_ziel_eur": round(k * CROSSSELL_EUR_PER_1000L_ZIEL),
            "crosssell_adressierbar_eur_min": round(k * CROSSSELL_EUR_PER_1000L_MIN),
            "crosssell_adressierbar_eur_max": round(k * CROSSSELL_EUR_PER_1000L_MAX),
            "crosssell_gewinnbar_eur_min": round(k * GEWINNBAR_EUR_PER_1000L_MIN),
            "crosssell_gewinnbar_eur_max": round(k * GEWINNBAR_EUR_PER_1000L_MAX),
            "produktgruppen": produktgruppen_potenzial(milchmenge_l),
        }

    def list_items(
        self,
        hygiene_bedarf: Optional[str] = None,
        min_kuehe: Optional[int] = None,
        sort: str = "kraftfutter",
    ) -> list[dict]:
        items = [self._build(r) for r in self._rows()]
        if hygiene_bedarf:
            items = [i for i in items if i["hygiene_bedarf"] == hygiene_bedarf]
        if min_kuehe:
            items = [i for i in items if i["herd_size_kuehe"] >= min_kuehe]
        if sort == "hygiene":
            items.sort(key=lambda i: (HYGIENE_RANK.get(i["hygiene_bedarf"], 0), i["hygiene_dipp_l_jahr"]), reverse=True)
        elif sort == "umsatz":
            items.sort(key=lambda i: i["crosssell_ziel_eur"], reverse=True)
        else:  # kraftfutter (Default)
            items.sort(key=lambda i: i["kraftfutter_t_jahr_max"], reverse=True)
        return items

    def summary(self) -> dict:
        items = [self._build(r) for r in self._rows()]
        by_bedarf = {"niedrig": 0, "mittel": 0, "hoch": 0}
        for i in items:
            by_bedarf[i["hygiene_bedarf"]] = by_bedarf.get(i["hygiene_bedarf"], 0) + 1
        total_milch = sum(i["milchmenge_l_jahr"] for i in items)
        return {
            "kunden": len(items),
            "nach_hygiene_bedarf": by_bedarf,
            "milchmenge_l_jahr_gesamt": total_milch,
            "kraftfutter_t_jahr_gesamt_min": round(sum(i["kraftfutter_t_jahr_min"] for i in items), 1),
            "kraftfutter_t_jahr_gesamt_max": round(sum(i["kraftfutter_t_jahr_max"] for i in items), 1),
            "dippmittel_l_jahr_gesamt": sum(i["hygiene_dipp_l_jahr"] for i in items),
            "kf_g_je_kg_ecm": [KF_G_PER_KG_ECM_MIN, KF_G_PER_KG_ECM_MAX],
            # Cross-Sell-Umsatzpotenzial (€/Jahr) gesamt + nach Produktgruppe.
            "crosssell_eur_jahr_adressierbar_min": round(sum(i["crosssell_adressierbar_eur_min"] for i in items)),
            "crosssell_eur_jahr_ziel": round(sum(i["crosssell_ziel_eur"] for i in items)),
            "crosssell_eur_jahr_adressierbar_max": round(sum(i["crosssell_adressierbar_eur_max"] for i in items)),
            "crosssell_eur_jahr_gewinnbar_min": round(sum(i["crosssell_gewinnbar_eur_min"] for i in items)),
            "crosssell_eur_jahr_gewinnbar_max": round(sum(i["crosssell_gewinnbar_eur_max"] for i in items)),
            "produktgruppen": produktgruppen_potenzial(total_milch),
            "crosssell_eur_je_1000l": {
                "adressierbar": [CROSSSELL_EUR_PER_1000L_MIN, CROSSSELL_EUR_PER_1000L_MAX],
                "ziel": CROSSSELL_EUR_PER_1000L_ZIEL,
                "gewinnbar": [GEWINNBAR_EUR_PER_1000L_MIN, GEWINNBAR_EUR_PER_1000L_MAX],
            },
        }
