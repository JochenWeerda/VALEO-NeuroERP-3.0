"""Seedet die Ist-Seite (public.kunden_produktgruppen_bezug) für das
Bedarfsdeckungs-Cockpit mit plausiblen, deterministischen Deckungsgraden.

Modelliert pro Milchvieh-Betrieb je Produktgruppe einen Ist-Bezug (12 M) als
Anteil des objektiven Jahresbedarfs. Der Anteil variiert deterministisch (Hash
aus kunden_nr+Gruppe), sodass realistische Bilder entstehen (Kernsortiment hoch
gedeckt, Randsortiment niedrig/null) — wie im Zielbild (Kraftfutter 76 %,
Mineral 15 %, Kälber 0 % …). quelle='geschaetzt'; echte Aggregation aus Belegen
kann später mit quelle='verkauf' andocken.

Aufruf:  docker exec valeo-neuro-erp-backend python scripts/seed_produktgruppen_bezug.py
"""

from __future__ import annotations

import hashlib
import os
from datetime import date, timedelta

from sqlalchemy import create_engine, text

from app.services.milchvieh_crosssell_service import PRODUKTGRUPPEN

TENANT = "00000000-0000-0000-0000-000000000001"

# Typische Deckungs-Korridore je Gruppe (min%, max%): Kernsortiment hoch,
# Randsortiment niedrig — der konkrete Wert je Betrieb wird im Korridor gehasht.
DECKUNG_KORRIDOR = {
    "kraftfutter": (55, 95),
    "mineral_spezial": (5, 45),
    "kaelber": (0, 35),
    "grundfutterbau": (10, 70),
    "stallbedarf_hygiene": (0, 40),
    "beratung_analyse": (0, 30),
}
# €/1.000 l Mittelwert je Gruppe (aus PRODUKTGRUPPEN-Spanne).
EUR_PER_1000L = {key: (lo + hi) / 2 for key, _label, lo, hi in PRODUKTGRUPPEN}


def _ratio(kunden_nr: str, key: str) -> float:
    lo, hi = DECKUNG_KORRIDOR[key]
    h = int(hashlib.md5(f"{kunden_nr}|{key}".encode()).hexdigest(), 16)
    # ~10 % der Betriebe je Randgruppe bleiben bei 0 (Einstiegschance).
    if lo == 0 and h % 10 < 3:
        return 0.0
    return (lo + (h % (hi - lo + 1))) / 100.0


def main() -> None:
    url = os.environ.get("DATABASE_URL") or "postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp"
    eng = create_engine(url)
    today = date.today()
    inserted = 0
    with eng.begin() as cx:
        betriebe = cx.execute(
            text(
                "SELECT k.kunden_nr, p.milch_kg, p.herd_size_kuehe "
                "FROM public.kunden_milchvieh_profil p JOIN public.kunden k USING (kunden_nr) "
                "WHERE coalesce(k.geloescht, FALSE) = FALSE"
            )
        ).mappings().all()
        for b in betriebe:
            milchmenge_l = float(b["milch_kg"] or 0) * int(b["herd_size_kuehe"] or 0)
            k1000 = milchmenge_l / 1000.0
            for key in EUR_PER_1000L:
                bedarf = k1000 * EUR_PER_1000L[key]
                ratio = _ratio(b["kunden_nr"], key)
                umsatz = round(bedarf * ratio, 2)
                menge = round(umsatz / 350.0, 2) if umsatz else 0  # grobe €→t-Heuristik
                last = (today - timedelta(days=int((int(hashlib.md5(b["kunden_nr"].encode()).hexdigest(), 16) % 300)))) if umsatz else None
                cx.execute(
                    text(
                        """
                        INSERT INTO public.kunden_produktgruppen_bezug
                          (kunden_nr, produktgruppe, menge_12m, umsatz_12m_eur, db_12m_eur, letzter_bezug, quelle, tenant_id)
                        VALUES (:k, :g, :menge, :umsatz, :db, :last, 'geschaetzt', :t)
                        ON CONFLICT (kunden_nr, produktgruppe, tenant_id) DO UPDATE
                          SET umsatz_12m_eur = EXCLUDED.umsatz_12m_eur, menge_12m = EXCLUDED.menge_12m,
                              db_12m_eur = EXCLUDED.db_12m_eur, letzter_bezug = EXCLUDED.letzter_bezug,
                              quelle = 'geschaetzt', updated_at = now()
                        """
                    ),
                    {"k": b["kunden_nr"], "g": key, "menge": menge, "umsatz": umsatz,
                     "db": round(umsatz * 0.18, 2) if umsatz else 0, "last": last, "t": TENANT},
                )
                inserted += 1
    print(f"seed_produktgruppen_bezug: {len(betriebe)} Betriebe × {len(EUR_PER_1000L)} Gruppen = {inserted} Zeilen")


if __name__ == "__main__":
    main()
