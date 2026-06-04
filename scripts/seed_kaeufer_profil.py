"""Seedet das Käufergruppen-Profil (public.kunden_kaeufer_profil).

Modelliert je Betrieb deterministische Verhaltenssignale (Angebote, Preisabfragen,
Abschlussquote, Rabatt, Kauffrequenz, Mehrlieferanten-Wahrscheinlichkeit,
Saisonkonzentration) — abgeleitet aus dem Gesamt-Deckungsgrad (aus
kunden_produktgruppen_bezug vs. modelliertem Bedarf) und einem Hash —, ruft den
regelbasierten Klassifikator und speichert Gruppe + Begründung + Confidence.
signal_source='modelliert'; echte Angebots-/Belegaggregation dockt später an.

Aufruf: docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/seed_kaeufer_profil.py
"""

from __future__ import annotations

import hashlib
import os

from sqlalchemy import create_engine, text

from app.services.kaeufergruppe import Verhaltenssignale, klassifiziere

TENANT = "00000000-0000-0000-0000-000000000001"


def _h(seed: str, mod: int) -> int:
    return int(hashlib.md5(seed.encode()).hexdigest(), 16) % mod


def main() -> None:
    url = os.environ.get("DATABASE_URL") or "postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp"
    eng = create_engine(url)
    n = 0
    with eng.begin() as cx:
        # Betriebe mit Profil + ihr modellierter Gesamt-Deckungsgrad / Bedarf.
        rows = cx.execute(
            text(
                """
                SELECT k.kunden_nr,
                       coalesce(sum(b.umsatz_12m_eur), 0) AS ist_ges,
                       coalesce(sum(b.umsatz_12m_eur) FILTER (WHERE TRUE), 0) AS dummy
                FROM public.kunden k
                LEFT JOIN public.kunden_produktgruppen_bezug b ON b.kunden_nr = k.kunden_nr
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                  AND (EXISTS (SELECT 1 FROM public.kunden_milchvieh_profil m WHERE m.kunden_nr = k.kunden_nr)
                    OR EXISTS (SELECT 1 FROM public.kunden_ackerbau_profil a WHERE a.kunden_nr = k.kunden_nr))
                GROUP BY k.kunden_nr
                """
            )
        ).mappings().all()

        for r in rows:
            knr = r["kunden_nr"]
            ist_ges = float(r["ist_ges"] or 0)
            # Bedarf grob aus Ist + modellierter Restlücke rekonstruieren ist teuer;
            # stattdessen Deckungsgrad als Signal aus einem stabilen Hash + Ist-Höhe.
            deckung = 8 + _h(knr + "deck", 80)          # 8..87 %
            bedarf_ges = ist_ges / (deckung / 100.0) if deckung else 0
            preisabfragen = _h(knr + "pa", 18)           # 0..17
            angebote = max(preisabfragen - _h(knr + "ang", 6), 0)
            win = round(_h(knr + "win", 90) / 100.0, 3)  # 0..0.89
            rabatt = round(_h(knr + "rab", 9) / 100.0, 3)  # 0..0.08
            freq = _h(knr + "freq", 20)                  # 0..19
            multi = round(0.3 + _h(knr + "multi", 60) / 100.0, 3)  # 0.30..0.89
            saison = round(_h(knr + "sai", 100) / 100.0, 3)

            sig = Verhaltenssignale(
                angebote_12m=angebote, preisabfragen_12m=preisabfragen,
                abschlussquote=win, rabatt_schnitt=rabatt, kauffrequenz_12m=freq,
                deckung_gesamt_pct=deckung, multi_lieferant_wahrsch=multi,
                saison_konzentration=saison, bedarf_gesamt_eur=bedarf_ges,
            )
            kl = klassifiziere(sig)
            loyalty = round(min(1.0, (deckung / 100.0) * (1 - rabatt) * (win + 0.2)), 3)
            churn = round(max(0.0, 1 - loyalty - (0.1 if freq >= 8 else 0)), 3)

            cx.execute(
                text(
                    """
                    INSERT INTO public.kunden_kaeufer_profil
                      (kunden_nr, buying_group, buying_group_confidence, buying_group_reason, buying_group_source,
                       price_request_count_12m, offer_count_12m, offer_win_rate_12m, average_discount_rate,
                       purchase_frequency_12m, multi_supplier_prob, season_concentration,
                       loyalty_score, churn_risk_score, signal_source, tenant_id)
                    VALUES (:k, :g, :conf, :reason, 'rule_based', :pa, :ang, :win, :rab, :freq, :multi, :sai,
                            :loy, :churn, 'modelliert', :t)
                    ON CONFLICT (kunden_nr) DO UPDATE SET
                      buying_group = EXCLUDED.buying_group, buying_group_confidence = EXCLUDED.buying_group_confidence,
                      buying_group_reason = EXCLUDED.buying_group_reason, buying_group_source = 'rule_based',
                      buying_group_updated_at = now(),
                      price_request_count_12m = EXCLUDED.price_request_count_12m, offer_count_12m = EXCLUDED.offer_count_12m,
                      offer_win_rate_12m = EXCLUDED.offer_win_rate_12m, average_discount_rate = EXCLUDED.average_discount_rate,
                      purchase_frequency_12m = EXCLUDED.purchase_frequency_12m, multi_supplier_prob = EXCLUDED.multi_supplier_prob,
                      season_concentration = EXCLUDED.season_concentration, loyalty_score = EXCLUDED.loyalty_score,
                      churn_risk_score = EXCLUDED.churn_risk_score, updated_at = now()
                    """
                ),
                {"k": knr, "g": kl.gruppe.value, "conf": kl.confidence, "reason": kl.begruendung,
                 "pa": preisabfragen, "ang": angebote, "win": win, "rab": rabatt, "freq": freq,
                 "multi": multi, "sai": saison, "loy": loyalty, "churn": churn, "t": TENANT},
            )
            n += 1
    print(f"seed_kaeufer_profil: {n} Käufergruppen-Profile klassifiziert (rule_based)")


if __name__ == "__main__":
    main()
