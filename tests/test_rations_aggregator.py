"""Tests fuer die neue zentrale Rations-Aggregation (Refactor Schritt 2).

Prueft insbesondere:
- Konsistenz mit den bisherigen ``_sum``-/``sum``-Aufrufen aus
  ``_build_response``.
- Korrekte Block-Aggregation (Slice 1f).
- pendf/pabkh/Forage-/CoP-Splits.
"""

from __future__ import annotations

import pytest

from app.agrar.rations.response import aggregate_ration, RationAggregates


def _mk(
    feed_id: str,
    *,
    forage: bool = False,
    cop: bool = False,
    me: float = 0.0,
    sidp: float = 0.0,
    cp: float = 0.0,
    ndf: float = 0.0,
    adf: float = 0.0,
    st: float = 0.0,
    bst: float = 0.0,
    zu: float = 0.0,
    xl: float = 0.0,
    ca: float = 0.0,
    p: float = 0.0,
    na: float = 0.0,
    mg: float = 0.0,
    k: float = 0.0,
    price: float = 0.0,
):
    return {
        "id": feed_id,
        "forage": forage,
        "structural_coproduct": cop,
        "me": me, "sidp": sidp, "cp": cp,
        "ndf": ndf, "adf": adf,
        "st": st, "bst": bst, "zu": zu, "xl": xl,
        "ca": ca, "p": p, "na": na, "mg": mg, "k": k,
        "price": price,
    }


def test_empty_ration_returns_zero_aggregate():
    agg = aggregate_ration([], [])
    assert agg.total_dmi == 0.0
    assert agg.total_cost == 0.0
    assert agg.me == 0.0
    assert agg.forage_kg == 0.0
    assert agg.by_block == {}


def test_zero_amounts_are_skipped():
    feeds = [_mk("a", me=10.0, price=0.20), _mk("b", me=20.0, price=0.30)]
    agg = aggregate_ration(feeds, [0.0, 0.0])
    assert agg.total_dmi == 0.0
    assert agg.me == 0.0


def test_basic_single_feed_aggregation():
    feed = _mk(
        "silage",
        forage=True,
        me=10.5, sidp=78.0, cp=155.0,
        ndf=420.0, adf=250.0,
        st=20.0, bst=10.0, zu=15.0,
        xl=30.0, ca=6.0, p=3.5, na=1.2, mg=2.1, k=18.0,
        price=0.05,
    )
    agg = aggregate_ration([feed], [10.0])
    assert agg.total_dmi == 10.0
    assert agg.total_cost == pytest.approx(0.5)
    assert agg.me == pytest.approx(105.0)
    assert agg.sidp == pytest.approx(780.0)
    assert agg.cp == pytest.approx(1550.0)
    assert agg.ndf == pytest.approx(4200.0)
    # pabKH = st + zu - bst
    assert agg.pabkh == pytest.approx(10.0 * (20.0 + 15.0 - 10.0))
    # forage-spezifisch
    assert agg.forage_kg == 10.0
    assert agg.forage_ndf == pytest.approx(4200.0)
    assert agg.forage_me == pytest.approx(105.0)
    # Grobfutter: peNDF-Faktor 1.0
    assert agg.pendf == pytest.approx(4200.0)


def test_coproduct_vs_forage_split():
    forage = _mk("grass", forage=True, ndf=400.0)
    coproduct = _mk("beetpulp", cop=True, ndf=350.0)
    concentrate = _mk("barley", ndf=150.0)
    agg = aggregate_ration(
        [forage, coproduct, concentrate],
        [8.0, 2.0, 3.0],
    )
    assert agg.forage_kg == 8.0
    assert agg.cop_kg == 2.0
    assert agg.forage_ndf == pytest.approx(3200.0)
    assert agg.cop_ndf == pytest.approx(700.0)
    assert agg.forage_plus_cop_ndf == pytest.approx(3900.0)
    # peNDF: forage=1.0, cop=0.5, concentrate=0.0
    assert agg.pendf == pytest.approx(8.0 * 400.0 + 2.0 * 350.0 * 0.5 + 0.0)


def test_densities_match_manual_calculation():
    feeds = [
        _mk("a", me=10.0, st=100.0, ndf=300.0, forage=True),
        _mk("b", me=12.0, st=300.0, ndf=100.0),
    ]
    agg = aggregate_ration(feeds, [5.0, 5.0])
    assert agg.total_dmi == 10.0
    # me_density = (5*10+5*12)/10
    assert agg.me_density == pytest.approx(11.0)
    assert agg.st_density == pytest.approx(200.0)
    assert agg.forage_share_pct == pytest.approx(50.0)


def test_block_aggregation_by_labels():
    pasture = _mk("weide", forage=True, me=10.8, cp=220.0, ndf=450.0, price=0.03)
    silage = _mk("gs", forage=True, me=10.4, cp=160.0, ndf=430.0, price=0.05)
    concentrate = _mk("mlf", me=11.2, cp=180.0, ndf=200.0, price=0.40)
    agg = aggregate_ration(
        [pasture, silage, concentrate],
        [12.0, 5.0, 4.0],
        block_labels=["pasture_block", "tmr_block", "concentrate_staged_block"],
    )
    assert set(agg.by_block.keys()) == {
        "pasture_block", "tmr_block", "concentrate_staged_block",
    }
    pb = agg.by_block["pasture_block"]
    tb = agg.by_block["tmr_block"]
    cb = agg.by_block["concentrate_staged_block"]
    assert pb.dmi == 12.0
    assert tb.dmi == 5.0
    assert cb.dmi == 4.0
    assert pb.me == pytest.approx(129.6)
    assert cb.cost == pytest.approx(1.6)
    # Summe der Block-DMI = gesamtes DMI
    assert (pb.dmi + tb.dmi + cb.dmi) == agg.total_dmi


def test_block_labels_none_leaves_by_block_empty():
    feeds = [_mk("a", me=10.0), _mk("b", me=12.0)]
    agg = aggregate_ration(feeds, [4.0, 2.0])
    assert agg.by_block == {}


def test_missing_numeric_fields_default_to_zero():
    feed = {"id": "x", "forage": False}  # keinerlei Nutrient-Keys
    agg = aggregate_ration([feed], [5.0])
    assert agg.total_dmi == 5.0
    assert agg.me == 0.0
    assert agg.sidp == 0.0
