"""Aggregiert echte Verhaltenssignale je Betrieb (und je Produktgruppe) aus den
vorhandenen Belegen/Interaktionen, statt sie zu modellieren.

Quellen (rollierend 12 M):
- public.kunden_kontakte      → Preisabfragen/Angebotsaktivität (Kurzinfo/Notiz)
- public.whatsapp_bestellungen → eingegangene Bestellungen (Kaufaktivität)
- public.kunden_produktgruppen_bezug → Bezugsbreite, Letztbezug (Recency), Umsatz

Wo echte Daten fehlen (DEV teils dünn), wird `signal_source='modelliert'`
zurückgegeben, damit der Aufrufer die modellierten Werte behält. Sonst 'belege'.
Die reine Abbildung Werte→Signale ist als Funktion (`signale_aus_werten`) testbar.
"""

from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.kaeufergruppe import Verhaltenssignale


def signale_aus_werten(
    *,
    preisanfragen_12m: int,
    angebote_12m: int,
    bestellungen_12m: int,
    gruppen_bezogen: int,
    deckung_pct: float,
    bedarf_eur: float,
) -> Verhaltenssignale:
    """Reine Abbildung beobachteter Werte → Verhaltenssignale (ohne DB; testbar)."""
    interaktionen = angebote_12m + bestellungen_12m
    abschlussquote = (bestellungen_12m / interaktionen) if interaktionen > 0 else 0.0
    # Mehrlieferanten-Wahrscheinlichkeit: je niedriger unsere Deckung, desto eher
    # bezieht der Betrieb (auch) woanders. Begrenzt auf [0.1, 0.95].
    multi = max(0.1, min(0.95, 1.0 - deckung_pct / 100.0 + 0.15))
    return Verhaltenssignale(
        angebote_12m=angebote_12m,
        preisabfragen_12m=preisanfragen_12m,
        abschlussquote=round(abschlussquote, 3),
        rabatt_schnitt=0.0,                 # aus Belegpositionen, sobald verfügbar
        kauffrequenz_12m=gruppen_bezogen,   # Bezugsbreite als Frequenz-Proxy
        deckung_gesamt_pct=deckung_pct,
        multi_lieferant_wahrsch=round(multi, 3),
        saison_konzentration=0.0,
        bedarf_gesamt_eur=bedarf_eur,
    )


class KaeuferSignalService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    def _kontakte(self, kunden_nr: str) -> tuple[int, int]:
        """(Angebots-/Kontaktaktivität 12 M, davon Preisabfragen)."""
        try:
            r = self.db.execute(
                text(
                    """
                    SELECT count(*) AS akt,
                           count(*) FILTER (WHERE kurzinfo ILIKE '%preis%' OR kurzinfo ILIKE '%angebot%'
                                              OR notiz ILIKE '%preis%' OR notiz ILIKE '%angebot%') AS pa
                    FROM public.kunden_kontakte
                    WHERE kunden_nr = :k AND created_at >= now() - interval '12 months'
                    """
                ),
                {"k": kunden_nr},
            ).mappings().first()
            return int(r["akt"] or 0), int(r["pa"] or 0)
        except Exception:
            self.db.rollback()
            return 0, 0

    def _bestellungen(self, kunden_nr: str) -> int:
        try:
            r = self.db.execute(
                text(
                    "SELECT count(*) FROM public.whatsapp_bestellungen "
                    "WHERE kunden_nr = :k AND eingegangen_am >= now() - interval '12 months'"
                ),
                {"k": kunden_nr},
            ).scalar()
            return int(r or 0)
        except Exception:
            self.db.rollback()
            return 0

    def _bezug(self, kunden_nr: str) -> tuple[int, bool]:
        """(Anzahl bezogener Produktgruppen, ob überhaupt Bezugsdaten vorhanden)."""
        r = self.db.execute(
            text(
                "SELECT count(*) FILTER (WHERE umsatz_12m_eur > 0) AS bezogen, count(*) AS gesamt "
                "FROM public.kunden_produktgruppen_bezug WHERE kunden_nr = :k AND tenant_id = :t"
            ),
            {"k": kunden_nr, "t": self.tenant_id},
        ).mappings().first()
        return int(r["bezogen"] or 0), int(r["gesamt"] or 0) > 0

    def aggregiere(self, kunden_nr: str, deckung_pct: float, bedarf_eur: float) -> Tuple[Verhaltenssignale, str]:
        akt, pa = self._kontakte(kunden_nr)
        best = self._bestellungen(kunden_nr)
        bezogen, hat_bezug = self._bezug(kunden_nr)
        hat_echte_daten = (akt > 0) or (best > 0) or hat_bezug
        sig = signale_aus_werten(
            preisanfragen_12m=pa, angebote_12m=akt, bestellungen_12m=best,
            gruppen_bezogen=bezogen, deckung_pct=deckung_pct, bedarf_eur=bedarf_eur,
        )
        return sig, ("belege" if hat_echte_daten else "modelliert")

    def aggregiere_gruppe(
        self, kunden_nr: str, deckung_pct: float, bedarf_eur: float, bezogen: bool
    ) -> Verhaltenssignale:
        """Signale für EINE Produktgruppe (für die per-Produktgruppe-Käuferlogik).
        Globale Kontakte werden anteilig herangezogen; Kern ist Deckung/Bezug der Gruppe."""
        akt, pa = self._kontakte(kunden_nr)
        return signale_aus_werten(
            preisanfragen_12m=min(pa, 4), angebote_12m=min(akt, 6),
            bestellungen_12m=1 if bezogen else 0,
            gruppen_bezogen=1 if bezogen else 0,
            deckung_pct=deckung_pct, bedarf_eur=bedarf_eur,
        )
