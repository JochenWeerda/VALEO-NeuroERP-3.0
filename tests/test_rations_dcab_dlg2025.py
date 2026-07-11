"""
F3-Regression: DCAB-Rations-Aggregat gegen DLG 01|2025 (Kap. 9.2.2).

Die Ration-DCAB ist der TM-gewichtete Mittelwert der futtermittelspezifischen
DCAB [meq/kg TM]. Prueft die Aggregation im Rations-Aggregator.
"""
from __future__ import annotations

import os
import sys

import pytest

_RATIONS_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _RATIONS_ROOT not in sys.path:
    sys.path.insert(0, _RATIONS_ROOT)

from app.agrar.rations.response.aggregator import aggregate_ration  # noqa: E402


def _feed(**kw):
    base = {"price": 0.0, "me": 0.0, "sidp": 0.0, "cp": 0.0, "ndf": 0.0, "adf": 0.0,
            "st": 0.0, "bst": 0.0, "zu": 0.0, "xl": 0.0, "ca": 0.0, "p": 0.0,
            "na": 0.0, "mg": 0.0, "k": 0.0, "s": 0.0, "cl": 0.0, "dcab": 0.0}
    base.update(kw)
    return base


class TestDcabAggregate:
    def test_tm_weighted_mean(self):
        # Zwei Futtermittel: DCAB +300 (10 kg TM) und -100 (5 kg TM)
        # Erwartung: (300*10 + (-100)*5) / 15 = (3000 - 500)/15 = 166,67 meq/kg TM
        feeds = [_feed(dcab=300.0), _feed(dcab=-100.0)]
        agg = aggregate_ration(feeds, [10.0, 5.0])
        dcab_ration = agg.dcab / agg.total_dmi
        assert dcab_ration == pytest.approx((300 * 10 - 100 * 5) / 15.0, abs=1e-6)

    def test_anionic_ration_negative(self):
        # Reine anionische Ration -> negatives DCAB (close-up-Ziel)
        feeds = [_feed(dcab=-80.0), _feed(dcab=-120.0)]
        agg = aggregate_ration(feeds, [8.0, 4.0])
        assert (agg.dcab / agg.total_dmi) < 0

    def test_potassium_density(self):
        # K-Dichte = TM-gewichtete K-Summe / Gesamt-TM
        feeds = [_feed(k=30.0), _feed(k=6.0)]
        agg = aggregate_ration(feeds, [10.0, 10.0])
        assert (agg.k / agg.total_dmi) == pytest.approx(18.0, abs=1e-6)

    def test_sulphur_chloride_summed(self):
        feeds = [_feed(s=1.5, cl=3.0), _feed(s=2.5, cl=1.0)]
        agg = aggregate_ration(feeds, [2.0, 2.0])
        assert agg.s == pytest.approx(1.5 * 2 + 2.5 * 2, abs=1e-6)
        assert agg.cl == pytest.approx(3.0 * 2 + 1.0 * 2, abs=1e-6)
