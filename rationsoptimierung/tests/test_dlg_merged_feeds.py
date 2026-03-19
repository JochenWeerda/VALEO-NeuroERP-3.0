"""Gemergte DLG/LKV + LP-CSV laden und stichprobenartig prüfen."""
from pathlib import Path

import pytest

from app.utils.dlg_merged_csv import load_merged_feed_ingredients


def test_load_merged_feeds_weizen_lkv_me():
    feeds = load_merged_feed_ingredients()
    assert len(feeds) >= 15
    w = next(f for f in feeds if f.id == "weizen")
    assert w.me_mj_kgdm == 13.2
    assert w.dm_frac == pytest.approx(0.864)
    assert w.andfom_g_kgdm == 121.0
    assert w.group.value == "concentrate"


def test_merge_script_output_exists():
    p = Path(__file__).resolve().parents[1] / "data" / "reference" / "dlg_merged_feeds_lp.csv"
    assert p.is_file()
