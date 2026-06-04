"""Seedet das Ackerbau-Bedarfsprofil (public.kunden_ackerbau_profil) aus den
GAP-Direktzahlungen als Flächen-Proxy.

ha-Proxy = direct_total_eur / DIRECT_EUR_PER_HA. Davon wird die Grundfutterfläche
abgezogen (Milchvieh: Kühe × FUTTER_HA_PER_KUH), die schon in der Milchvieh-Gruppe
`grundfutterbau` monetarisiert ist → übrig bleibt die Marktfrucht-Ackerfläche.
Nur Betriebe mit >= MIN_ACKER_HA bekommen ein Ackerbau-Profil.

Quelle: public.gap_payments_direct_agg (direct_total_eur je Begünstigtem/Jahr),
verknüpft über normalize_name(kunden.name1) == beneficiary_name_norm.

Aufruf:  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/seed_ackerbau_profil.py
"""

from __future__ import annotations

import json
import os

from sqlalchemy import create_engine, text

from app.services.gap_pipeline import normalize_name

TENANT = "00000000-0000-0000-0000-000000000001"
DIRECT_EUR_PER_HA = 300.0   # GAP-Direktzahlung → förderfähige ha (DE-Richtwert)
FUTTER_HA_PER_KUH = 0.55    # Grünland + Silomais je Kuh inkl. Jungvieh
MIN_ACKER_HA = 3.0          # darunter kein eigenes Ackerbau-Profil

# Regionale Standard-Fruchtfolge Nordwest-Niedersachsen (Marktfrucht-Anteile).
KULTUR_MIX = {"Winterweizen": 0.35, "Wintergerste": 0.25, "Winterraps": 0.20, "Sonstige": 0.20}


def main() -> None:
    url = os.environ.get("DATABASE_URL") or "postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp"
    eng = create_engine(url)
    inserted = 0
    skipped = 0
    with eng.begin() as cx:
        # Direktzahlung je (name_norm, plz): jüngstes Jahr.
        agg: dict[tuple, float] = {}
        for r in cx.execute(text("SELECT ref_year, beneficiary_name_norm, postal_code, direct_total_eur FROM public.gap_payments_direct_agg WHERE direct_total_eur > 0")).mappings():
            key = (r["beneficiary_name_norm"], r["postal_code"])
            agg[key] = max(agg.get(key, 0.0), float(r["direct_total_eur"]))

        kunden = cx.execute(
            text(
                "SELECT k.kunden_nr, k.name1, k.plz, m.herd_size_kuehe "
                "FROM public.kunden k "
                "LEFT JOIN public.kunden_milchvieh_profil m ON m.kunden_nr = k.kunden_nr "
                "WHERE k.kunden_nr LIKE 'GAP%' AND coalesce(k.geloescht, FALSE) = FALSE"
            )
        ).mappings().all()

        for k in kunden:
            nn = normalize_name(k["name1"])
            direct = agg.get((nn, k["plz"]))
            if direct is None:
                # PLZ-unabhängiger Fallback über den Namen
                cand = [v for (name, _plz), v in agg.items() if name == nn]
                direct = max(cand) if cand else None
            if not direct:
                skipped += 1
                continue
            gesamt = direct / DIRECT_EUR_PER_HA
            futter = (int(k["herd_size_kuehe"] or 0) * FUTTER_HA_PER_KUH)
            acker = max(0.0, gesamt - futter)
            if acker < MIN_ACKER_HA:
                skipped += 1
                continue
            cx.execute(
                text(
                    """
                    INSERT INTO public.kunden_ackerbau_profil
                      (kunden_nr, gesamtflaeche_ha, futterflaeche_ha, ackerflaeche_ha, direct_payment_eur, kultur_mix, quelle, tenant_id)
                    VALUES (:k, :ges, :fut, :ack, :dir, CAST(:mix AS JSONB), 'gap_proxy', :t)
                    ON CONFLICT (kunden_nr) DO UPDATE
                      SET gesamtflaeche_ha = EXCLUDED.gesamtflaeche_ha, futterflaeche_ha = EXCLUDED.futterflaeche_ha,
                          ackerflaeche_ha = EXCLUDED.ackerflaeche_ha, direct_payment_eur = EXCLUDED.direct_payment_eur,
                          kultur_mix = EXCLUDED.kultur_mix, quelle = 'gap_proxy', updated_at = now()
                    """
                ),
                {"k": k["kunden_nr"], "ges": round(gesamt, 1), "fut": round(futter, 1), "ack": round(acker, 1),
                 "dir": round(direct, 2), "mix": json.dumps(KULTUR_MIX), "t": TENANT},
            )
            inserted += 1
    print(f"seed_ackerbau_profil: {inserted} Ackerbau-Profile angelegt, {skipped} ohne (kein Match / < {MIN_ACKER_HA} ha)")


if __name__ == "__main__":
    main()
