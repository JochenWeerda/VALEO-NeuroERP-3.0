"""Tests fuer den Preflight Phase 0 (RATION-CANON-03, Skill §3/§11.1).

Deckt insbesondere Golden Case 3 (Σ Minima > TM), 4 (Σ Maxima < TM) und
12 (fehlende Analyse als Finding, nicht 0) ab.

Reine Unit-Tests:

    pytest tests/test_rations_preflight.py \
        --noconftest -p no:cacheprovider --no-cov -o addopts=""
"""

from typing import Any, Dict, List

from app.agrar.rations.preflight import (
    REQUIRED_FEED_KEYS,
    Severity,
    run_preflight,
)


def _feed(**kw: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "id": "f1",
        "name": "Maissilage",
        "me": 10.5,
        "sidp": 65.0,
        "dm_frac": 0.33,
        "min_kg": 0.0,
        "max_kg": 8.0,
        "price": 0.045,
    }
    base.update(kw)
    return base


def _codes(report) -> List[str]:
    return [f["code"] for f in report.to_dict()["findings"]]


class TestHappyPath:
    def test_clean_ration_has_no_blocker(self):
        feeds = [
            _feed(id="f1", name="Maissilage", min_kg=0.0, max_kg=14.0),
            _feed(id="f2", name="Grassilage", me=10.6, sidp=68.0, min_kg=0.0, max_kg=12.0),
        ]
        rep = run_preflight(
            feeds, dmi_min_kg=18.0, dmi_max_kg=24.0,
            profile={"milk_kg_day": 38, "body_weight_kg": 650},
        )
        assert rep.ok is True
        assert rep.has_blocker is False
        assert rep.to_dict()["blocker_count"] == 0


class TestGoldenCase12MissingAnalysis:
    def test_missing_me_is_finding_not_zero(self):
        feeds = [_feed(me=None, max_kg=20.0)]
        rep = run_preflight(feeds, dmi_min_kg=18.0, dmi_max_kg=24.0)
        assert "FEED_ANALYSIS_MISSING" in _codes(rep)
        assert rep.has_blocker is True

    def test_absent_key_is_missing(self):
        feed = _feed(max_kg=20.0)
        del feed["sidp"]
        rep = run_preflight([feed], dmi_min_kg=18.0, dmi_max_kg=24.0)
        missing = [
            f for f in rep.to_dict()["findings"] if f["code"] == "FEED_ANALYSIS_MISSING"
        ]
        assert any(f["metric"] == "sidp" for f in missing)

    def test_me_zero_is_valid_for_mineral(self):
        # me=0 (Mineralfutter) ist ein Wert, kein Fehlwert.
        feed = _feed(id="min", name="Mineralfutter", me=0.0, sidp=0.0, dm_frac=0.95, max_kg=0.3)
        rep = run_preflight([feed], dmi_min_kg=18.0, dmi_max_kg=24.0)
        assert "FEED_ANALYSIS_MISSING" not in _codes(rep)

    def test_all_required_keys_checked(self):
        for key in REQUIRED_FEED_KEYS:
            feed = _feed(max_kg=20.0)
            feed[key] = None
            rep = run_preflight([feed], dmi_min_kg=18.0, dmi_max_kg=24.0)
            assert "FEED_ANALYSIS_MISSING" in _codes(rep), f"{key} nicht geprueft"


class TestGoldenCase3SumMinExceedsDmi:
    def test_sum_min_exceeds_dmi_max_is_blocker(self):
        feeds = [
            _feed(id="a", name="A", min_kg=10.0, max_kg=15.0),
            _feed(id="b", name="B", min_kg=12.0, max_kg=15.0),
        ]
        rep = run_preflight(feeds, dmi_min_kg=18.0, dmi_max_kg=20.0)
        assert "SUM_MIN_EXCEEDS_DMI_MAX" in _codes(rep)
        assert rep.has_blocker is True
        finding = next(
            f for f in rep.to_dict()["findings"]
            if f["code"] == "SUM_MIN_EXCEEDS_DMI_MAX"
        )
        assert finding["actual"] == 22.0
        assert finding["limit"] == 20.0
        assert finding["unit"] == "kg TM/d"


class TestGoldenCase4SumMaxBelowDmi:
    def test_sum_max_below_required_dmi_is_blocker(self):
        feeds = [
            _feed(id="a", name="A", min_kg=0.0, max_kg=5.0),
            _feed(id="b", name="B", min_kg=0.0, max_kg=6.0),
        ]
        rep = run_preflight(feeds, dmi_min_kg=18.0, dmi_max_kg=24.0)
        assert "SUM_MAX_BELOW_DMI_MIN" in _codes(rep)
        finding = next(
            f for f in rep.to_dict()["findings"]
            if f["code"] == "SUM_MAX_BELOW_DMI_MIN"
        )
        assert finding["actual"] == 11.0
        assert finding["limit"] == 18.0


class TestPerFeedConsistency:
    def test_min_gt_max_is_blocker(self):
        feeds = [_feed(min_kg=9.0, max_kg=4.0)]
        rep = run_preflight(feeds, dmi_min_kg=3.0, dmi_max_kg=24.0)
        assert "FEED_MIN_GT_MAX" in _codes(rep)

    def test_negative_bound_is_blocker(self):
        feeds = [_feed(min_kg=-1.0, max_kg=5.0)]
        rep = run_preflight(feeds, dmi_min_kg=3.0, dmi_max_kg=24.0)
        assert "FEED_BOUND_NEGATIVE" in _codes(rep)

    def test_dm_frac_out_of_range_is_flagged(self):
        # 33 statt 0.33 (Prozent-Verwechslung) -> implausibel
        feeds = [_feed(dm_frac=33.0, max_kg=20.0)]
        rep = run_preflight(feeds, dmi_min_kg=3.0, dmi_max_kg=24.0)
        assert "DM_FRAC_IMPLAUSIBLE" in _codes(rep)

    def test_missing_price_is_warning_not_blocker(self):
        feeds = [_feed(price=None, max_kg=20.0)]
        rep = run_preflight(feeds, dmi_min_kg=3.0, dmi_max_kg=24.0)
        codes = _codes(rep)
        assert "FEED_PRICE_MISSING" in codes
        # allein fehlender Preis blockiert nicht.
        price_finding = next(
            f for f in rep.to_dict()["findings"] if f["code"] == "FEED_PRICE_MISSING"
        )
        assert price_finding["severity"] == "warning"


class TestDmiBandAndProfile:
    def test_dmi_band_inconsistent_is_blocker(self):
        feeds = [_feed(max_kg=20.0)]
        rep = run_preflight(feeds, dmi_min_kg=25.0, dmi_max_kg=20.0)
        assert "DMI_BAND_INCONSISTENT" in _codes(rep)

    def test_missing_target_and_weight_are_warnings(self):
        feeds = [_feed(max_kg=20.0)]
        rep = run_preflight(
            feeds, dmi_min_kg=18.0, dmi_max_kg=24.0, profile={"milk_kg_day": 0}
        )
        codes = _codes(rep)
        assert "TARGET_MILK_MISSING" in codes
        assert "BODY_WEIGHT_MISSING" in codes
        # Warnungen blockieren nicht.
        assert rep.has_blocker is False

    def test_inactive_feed_is_skipped(self):
        feeds = [
            _feed(id="a", name="A", max_kg=20.0),
            _feed(id="bad", name="Bad", me=None, active=False, max_kg=20.0),
        ]
        rep = run_preflight(feeds, dmi_min_kg=18.0, dmi_max_kg=24.0)
        assert "FEED_ANALYSIS_MISSING" not in _codes(rep)


class TestReportShape:
    def test_finding_has_all_contract_fields(self):
        feeds = [_feed(me=None, max_kg=20.0)]
        rep = run_preflight(feeds, dmi_min_kg=18.0, dmi_max_kg=24.0)
        f = rep.to_dict()["findings"][0]
        for key in (
            "code", "severity", "metric", "actual", "limit", "unit",
            "cause", "remediation",
        ):
            assert key in f, f"Finding fehlt Feld {key}"

    def test_severity_is_plain_string(self):
        assert Severity.BLOCKER.value == "blocker"
