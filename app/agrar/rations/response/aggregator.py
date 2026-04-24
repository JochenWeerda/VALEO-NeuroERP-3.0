"""Zentrale Rations-Aggregation (Refactor Schritt 2, 2026-04-23).

Statt 20-30 einzelner ``sum(...)``-Aufrufe in ``_build_response`` und Co.
liefert ``aggregate_ration`` in einem einzigen Pass alle tagesbezogenen
Summen und relevanten Sub-Summen (Grobfutter, Co-Produkte, Block-Splits).

Die Struktur ist bewusst auf die **aktuell genutzten** Keys der Feed-Dicts
ausgelegt; ein Umstieg auf eine typisierte ``Feed``-Klasse ist in Schritt 5
vorgesehen und kann diese Aggregation unverändert weiterbenutzen
(``aggregate_ration`` erwartet nur ``Mapping[str, Any]``).

Motivation (User-Feedback 2026-04-23):
- "Für dieselbe fertige Ration werden 20-40 Aggregationen separat gerechnet."
- "einmal eine zentrale Aggregation bauen" und "in einem Pass alles sammeln".

Die Aggregation bleibt **ausdrücklich rein** (keine Seiteneffekte, keine
Response-Konstruktion, keine Solverlogik) und ist damit vollständig
testbar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence


FeedLike = Mapping[str, Any]


def _num(feed: FeedLike, key: str) -> float:
    """Robuste ``float``-Extraktion eines Feed-Feldes (0.0 bei None/Fehler)."""
    try:
        value = feed.get(key)
    except AttributeError:
        return 0.0
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@dataclass(slots=True)
class BlockTotals:
    """Tagesaggregate je Block (``pasture_block`` / ``tmr_block`` /
    ``concentrate_staged_block`` ...)."""

    dmi: float = 0.0
    cost: float = 0.0
    me: float = 0.0
    sidp: float = 0.0
    cp: float = 0.0
    ndf: float = 0.0


@dataclass(slots=True)
class RationAggregates:
    """Einmal-pro-Ration berechnete Aggregate.

    Alle Nährstoff-Summen sind in den Einheiten der Feed-Koeffizienten
    (i. d. R. je kg TM, multipliziert mit der zugeteilten TM-Menge);
    ``total_dmi`` ist in kg TM und ``total_cost`` in EUR/Tag.
    """

    total_dmi: float = 0.0
    total_cost: float = 0.0

    # Nährstoff-Tagesversorgung (kg TM * Koeffizient je kg TM)
    me: float = 0.0
    sidp: float = 0.0
    cp: float = 0.0
    ndf: float = 0.0
    adf: float = 0.0
    st: float = 0.0
    bst: float = 0.0
    zu: float = 0.0
    xl: float = 0.0
    ca: float = 0.0
    p: float = 0.0
    na: float = 0.0
    mg: float = 0.0
    k: float = 0.0
    sidlys: float = 0.0
    sidmet: float = 0.0

    # Struktur-Proxy: peNDF = ndf * peNDF-Faktor(feed)
    pendf: float = 0.0
    # Pansenabbaubare Kohlenhydrate (st + zu - bst) (pabKH)
    pabkh: float = 0.0

    # Grobfutter- und Co-Produkt-Aggregate
    forage_kg: float = 0.0
    forage_ndf: float = 0.0
    forage_me: float = 0.0
    forage_sidp: float = 0.0
    cop_kg: float = 0.0
    cop_ndf: float = 0.0

    # Aggregate je Block (Slice 1f); Keys: "pasture_block", "tmr_block",
    # "concentrate_staged_block" (und ggf. "other").
    by_block: dict[str, BlockTotals] = field(default_factory=dict)

    # --- abgeleitete Dichten (nur bei total_dmi > 0 sinnvoll) --------------

    def density(self, numerator: float) -> float:
        """Dichte je kg TM (0.0 bei leerer Ration)."""
        return numerator / self.total_dmi if self.total_dmi > 0 else 0.0

    @property
    def me_density(self) -> float:
        return self.density(self.me)

    @property
    def pendf_density(self) -> float:
        return self.density(self.pendf)

    @property
    def pabkh_density(self) -> float:
        return self.density(self.pabkh)

    @property
    def st_density(self) -> float:
        return self.density(self.st)

    @property
    def forage_plus_cop_ndf(self) -> float:
        """aNDFomGF + aNDFomCoP gemäß DLG 01|2025 Kap. 8.2."""
        return self.forage_ndf + self.cop_ndf

    @property
    def forage_share_pct(self) -> float:
        return (self.forage_kg / self.total_dmi * 100.0) if self.total_dmi > 0 else 0.0


def _pendf_factor(feed: FeedLike) -> float:
    """peNDF-Faktor je Feed.

    Beibehaltung der bisherigen Implementationslogik aus
    ``rations_optimization._feed_pendf_factor``: Forage=1.0, Co-Produkte
    mit Struktur 0.5, sonstiges Kraftfutter 0.0 (Default).
    """
    if feed.get("forage"):
        return 1.0
    if feed.get("structural_coproduct"):
        return 0.5
    return 0.0


def aggregate_ration(
    feeds: Sequence[FeedLike],
    amounts: Sequence[float],
    block_labels: Optional[Sequence[str]] = None,
    *,
    pendf_factor_fn=_pendf_factor,
) -> RationAggregates:
    """Berechnet alle Standard-Aggregate der Ration in einem einzigen Pass.

    Args:
        feeds: Liste der Feed-Dicts (mit Keys wie "me", "sidp", ...).
        amounts: Zugeteilte kg TM je Feed (gleiche Länge wie ``feeds``).
        block_labels: Optional; wenn gesetzt, wird je Block (Slice 1f)
            aggregiert. Bei None/Länge != feeds findet keine Block-
            Aggregation statt und ``by_block`` bleibt leer.
        pendf_factor_fn: Optional, für Tests - Standard ist der
            bisherige ``_feed_pendf_factor``.
    """
    agg = RationAggregates()
    if not feeds or not amounts:
        return agg
    use_blocks = (
        block_labels is not None and len(block_labels) == len(feeds)
    )
    for i, feed in enumerate(feeds):
        try:
            amt = float(amounts[i])
        except (TypeError, ValueError):
            amt = 0.0
        if amt <= 0.0:
            continue
        price = _num(feed, "price")
        me = _num(feed, "me")
        sidp = _num(feed, "sidp")
        cp = _num(feed, "cp")
        ndf = _num(feed, "ndf")
        adf = _num(feed, "adf")
        st = _num(feed, "st")
        bst = _num(feed, "bst")
        zu = _num(feed, "zu")
        xl = _num(feed, "xl")
        ca = _num(feed, "ca")
        p = _num(feed, "p")
        na = _num(feed, "na")
        mg = _num(feed, "mg")
        k = _num(feed, "k")
        sidlys = _num(feed, "sidlys")
        sidmet = _num(feed, "sidmet")

        agg.total_dmi += amt
        cost_i = amt * price
        agg.total_cost += cost_i
        agg.me += amt * me
        agg.sidp += amt * sidp
        agg.cp += amt * cp
        ndf_sup = amt * ndf
        agg.ndf += ndf_sup
        agg.adf += amt * adf
        agg.st += amt * st
        agg.bst += amt * bst
        agg.zu += amt * zu
        agg.xl += amt * xl
        agg.ca += amt * ca
        agg.p += amt * p
        agg.na += amt * na
        agg.mg += amt * mg
        agg.k += amt * k
        agg.sidlys += amt * sidlys
        agg.sidmet += amt * sidmet
        agg.pendf += amt * ndf * pendf_factor_fn(feed)
        agg.pabkh += amt * (st + zu - bst)

        is_forage = bool(feed.get("forage"))
        is_cop = bool(feed.get("structural_coproduct")) and not is_forage
        if is_forage:
            agg.forage_kg += amt
            agg.forage_ndf += ndf_sup
            agg.forage_me += amt * me
            agg.forage_sidp += amt * sidp
        if is_cop:
            agg.cop_kg += amt
            agg.cop_ndf += ndf_sup

        if use_blocks:
            block = block_labels[i] or "tmr_block"
            slot = agg.by_block.get(block)
            if slot is None:
                slot = BlockTotals()
                agg.by_block[block] = slot
            slot.dmi += amt
            slot.cost += cost_i
            slot.me += amt * me
            slot.sidp += amt * sidp
            slot.cp += amt * cp
            slot.ndf += ndf_sup

    return agg


__all__ = ["RationAggregates", "BlockTotals", "aggregate_ration"]
