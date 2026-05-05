"""Tests fuer die Feed-Dataclass-Sicht (Refactor Schritt 5)."""

from __future__ import annotations

import pytest

from app.agrar.rations.solver import Feed


def test_from_dict_basic_conversion():
    data = {
        "id": "silage",
        "name": "Grassilage 2. Schnitt",
        "group": "Grundfutter/Grassilage",
        "futterart": "Grundfutter",
        "forage": True,
        "dm_frac": 0.35,
        "price": 0.06,
        "min_kg": 0.0,
        "max_kg": 14.0,
        "me": 10.5,
        "sidp": 78.0,
        "cp": 165.0,
        "ndf": 420.0,
    }
    feed = Feed.from_dict(data)
    assert feed.id == "silage"
    assert feed.forage is True
    assert feed.structural_coproduct is False
    assert feed.dm_frac == pytest.approx(0.35)
    assert feed.me == pytest.approx(10.5)
    assert feed.rmd is None


def test_missing_numeric_keys_default_to_zero():
    feed = Feed.from_dict({"id": "x"})
    assert feed.me == 0.0
    assert feed.sidp == 0.0
    assert feed.dm_frac == 0.0
    assert feed.rmd is None
    assert feed.fan_slope_source == "fallback"


def test_none_values_are_handled():
    feed = Feed.from_dict({
        "id": "y", "name": None, "me": None, "rmd": None, "group": None,
    })
    assert feed.name == "None"  # str(None); nicht ideal, aber kein Crash
    assert feed.me == 0.0
    assert feed.rmd is None


def test_private_flags_are_preserved():
    feed = Feed.from_dict({
        "id": "min",
        "_fan_slope_source": "mapped",
        "_special": "pasture_mg",
    })
    assert feed.fan_slope_source == "mapped"
    assert feed.special == "pasture_mg"


def test_structural_coproduct_flag():
    feed = Feed.from_dict({
        "id": "beetpulp", "structural_coproduct": True, "forage": False,
    })
    assert feed.structural_coproduct is True
    assert feed.forage is False


def test_slots_prevents_ad_hoc_attrs():
    """``@dataclass(slots=True)`` verhindert das dynamische Hinzufuegen von Attributen.

    Das ist ein bewusster Schutz: so kann kein Aufrufer schleichend
    weitere Felder setzen, die dann in ``aggregate_ration`` o. ae.
    ignoriert wuerden.
    """
    feed = Feed.from_dict({"id": "z"})
    with pytest.raises(AttributeError):
        feed.irgendwas_erfunden = 42  # type: ignore[attr-defined]
