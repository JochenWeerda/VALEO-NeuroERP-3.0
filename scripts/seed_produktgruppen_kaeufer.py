"""Klassifiziert je Betrieb jede Produktgruppe in eine eigene Käufergruppe
(per-Produktgruppe-Käuferlogik) und schreibt sie nach
public.kunden_produktgruppen_bezug.buying_group.

Nutzt das Bedarfsdeckungs-Cockpit (Deckung/Bedarf je Gruppe) + die echte
Signal-Aggregation. Ein Betrieb kann so bei Dünger Preisvergleicher und bei
Kälbermilch Beratungskäufer sein.

Aufruf: docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/seed_produktgruppen_kaeufer.py
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine, text

from app.services.bedarfsdeckung_service import BedarfsdeckungService
from app.services.kaeufer_klassifikator import klassifiziere_mit
from app.services.kaeufer_signal_service import KaeuferSignalService

TENANT = "00000000-0000-0000-0000-000000000001"


def main() -> None:
    url = os.environ.get("DATABASE_URL") or "postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp"
    eng = create_engine(url)
    betriebe = 0
    gruppen = 0
    with eng.begin() as cx:
        knrs = [r[0] for r in cx.execute(
            text(
                """
                SELECT DISTINCT k.kunden_nr FROM public.kunden k
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                  AND (EXISTS (SELECT 1 FROM public.kunden_milchvieh_profil m WHERE m.kunden_nr = k.kunden_nr)
                    OR EXISTS (SELECT 1 FROM public.kunden_ackerbau_profil a WHERE a.kunden_nr = k.kunden_nr))
                """
            )
        ).all()]
        bd = BedarfsdeckungService(cx, TENANT)
        sig_svc = KaeuferSignalService(cx, TENANT)
        for knr in knrs:
            cp = bd.cockpit(knr)
            if not cp:
                continue
            for g in cp.get("produktgruppen", []):
                sig = sig_svc.aggregiere_gruppe(knr, float(g["deckung_pct"]), float(g["bedarf_jahr_eur"]), bool(g["ist_12m_eur"] > 0))
                kl, source = klassifiziere_mit(sig, prefer_ai=False)
                cx.execute(
                    text("UPDATE public.kunden_produktgruppen_bezug SET buying_group = :grp, buying_group_reason = :r, "
                         "buying_group_source = :s, buying_group_confidence = :c, updated_at = now() "
                         "WHERE kunden_nr = :k AND produktgruppe = :pg AND tenant_id = :t"),
                    {"grp": kl.gruppe.value, "r": kl.begruendung, "s": source, "c": kl.confidence,
                     "k": knr, "pg": g["key"], "t": TENANT},
                )
                gruppen += 1
            betriebe += 1
    print(f"seed_produktgruppen_kaeufer: {betriebe} Betriebe, {gruppen} Produktgruppen-Käufergruppen gesetzt")


if __name__ == "__main__":
    main()
