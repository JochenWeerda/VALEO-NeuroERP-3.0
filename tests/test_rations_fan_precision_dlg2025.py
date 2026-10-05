from app.agrar.rations.fan_precision import (
    effective_degradation_pct, me_at_fani, omd_at_fani, passage_rate_pct_h, precision_for_feed,
)

def test_dlg_omd_and_me_example_fan35():
    assert omd_at_fani(80, 3.5) == 74.375
    me, omd = me_at_fani(me_fan1=12.0, ge_mj_kgdm=18.54, ash_g_kgdm=100, cp_g_kgdm=157.5, omd_fan1_pct=80, fani=3.5)
    assert omd == 74.375
    assert 11.54 <= me <= 11.58

def test_table6_passage_endpoints():
    assert passage_rate_pct_h(1, "roughage") == 2.6
    assert passage_rate_pct_h(4, "roughage") == 5.3
    assert passage_rate_pct_h(1, "concentrate") == 3.5
    assert passage_rate_pct_h(4, "concentrate") == 7.2
    assert passage_rate_pct_h(1, "mixed_juice") == 2.9
    assert passage_rate_pct_h(4, "mixed_juice") == 5.8

def test_dlg_edg_grass_example():
    fan1 = effective_degradation_pct(a_pct=14, b_pct=78, c_pct_h=15.2, lag_h=1.3, passage_rate_pct=2.6)
    fan35 = effective_degradation_pct(a_pct=14, b_pct=78, c_pct_h=15.2, lag_h=1.3, passage_rate_pct=4.8)
    assert 77.0 <= fan1 <= 79.0
    assert 68.0 <= fan35 <= 70.0

def test_precision_increases_udp_and_reduces_me():
    value = precision_for_feed(fani=3.5, passage_class="roughage", me_fan1=12, sidp_fan1=104,
        ge_mj_kgdm=17.4, ash_g_kgdm=160, cp_g_kgdm=200, omd_fan1_pct=78,
        a_pct=14, b_pct=78, c_pct_h=15, lag_h=1.3, sidudp_pct=87)
    assert value.me_fani_mj_kgdm < value.me_fan1_mj_kgdm
    assert value.edg_fani_pct < value.edg_fan1_pct
    assert value.udp_fani_pct > 20
    assert value.sidp_fani_g_kgdm > 0
def test_dlg_feed_pipeline_uses_exact_precision():
    from app.api.v1.endpoints.rations_optimization import _annotate_feeds_with_fan_catalog, _apply_fan_effect, _get_feeds
    feeds = _get_feeds()
    assert feeds
    feed = next(item for item in feeds if item.get("omdfan1") is not None and item.get("protein_a") is not None)
    assert feed.get("ash") is not None
    assert feed.get("protein_b") is not None
    assert feed.get("protein_c") is not None
    _annotate_feeds_with_fan_catalog([feed])
    adjusted = _apply_fan_effect([feed], 3.5)[0]
    precision = adjusted["_fan_precision"]
    assert precision["method"] == "DLG-01|2025-ch4.3-ch6.2"
    assert precision["passage_rate_pct_h"] > 2.6
    assert precision["omd_fani_pct"] < precision["omd_fan1_pct"]
    assert adjusted["me"] < adjusted["_me_fan1"]


def test_incomplete_custom_feed_is_explicit_fallback():
    from app.api.v1.endpoints.rations_optimization import _annotate_feeds_with_fan_catalog, _apply_fan_effect
    feed = {"id": "custom", "name": "Eigenmischung", "group": "Kraftfutter", "futterart": "", "forage": False, "me": 11.0, "sidp": 120.0}
    _annotate_feeds_with_fan_catalog([feed])
    adjusted = _apply_fan_effect([feed], 3.0)[0]
    assert adjusted["me"] < 11.0
    assert adjusted["_fan_precision"]["method"] == "conservative-catalog-fallback-missing-analysis"