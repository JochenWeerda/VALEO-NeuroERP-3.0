"""Referenz-CSVs DLG 2025 / LKV Ernte 2025 – Integrität der übernommenen Zahlen."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

_REF = Path(__file__).resolve().parents[1] / "data" / "reference"


def _read_rows(name: str) -> list[dict]:
    path = _REF / name
    assert path.is_file(), f"missing {path}"
    # utf-8-sig: BOM aus Excel-Export ignorieren
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_lkv_getreide_ernte_2025_weizen_values():
    rows = _read_rows("lkv_sachsen_getreide_ernte_2025_tabelle1.csv")
    w = next(r for r in rows if r["id"] == "weizen_ernte2025")
    assert float(w["tm_g_kg_fm"]) == 864
    assert float(w["me_mj_kg_tm"]) == 13.2
    assert float(w["starch_g_kg_tm"]) == 652
    assert float(w["andfom_g_kg_tm"]) == 121
    assert float(w["rf_g_kg_tm"]) == 19


def test_dlg_kraftfutter_soja_hp_values():
    rows = _read_rows("dlg_2025_kraftfutter_wiederkauer_tabelle2.csv")
    s = next(r for r in rows if r["id"] == "soja_extraktionsschrot_hp_dlg2025")
    assert float(s["tm_g_kg_fm"]) == 890
    assert float(s["me_mj_kg_tm"]) == 14.1
    assert float(s["rp_g_kg_tm"]) == 525
    assert float(s["starch_g_kg_tm"]) == 45


def test_dm_frac_from_tm_matches_expectation():
    rows = _read_rows("lkv_sachsen_getreide_ernte_2025_tabelle1.csv")
    for r in rows:
        tm = float(r["tm_g_kg_fm"])
        assert 800 <= tm <= 920
        dm = tm / 1000.0
        assert 0.80 <= dm <= 0.93


def test_lp_import_filled_sourced_has_sidp_and_sources():
    rows = _read_rows("dlg_2025_lp_import_filled_sourced.csv")
    assert rows
    ab = next(r for r in rows if r["feed_id"] == "ackerbohnen")
    assert float(ab["sidp_g_kgdm"]) == 118.0
    assert "dlg.org" in (ab.get("source_sidp") or "").lower()
    assert "source_group" in rows[0]


def test_lp_import_template_csv_structure():
    rows = _read_rows("dlg_2025_lp_import_template.csv")
    assert rows, "dlg_2025_lp_import_template.csv fehlt oder ist leer"
    assert set(rows[0].keys()) >= {
        "feed_id",
        "feed_name",
        "source_set",
        "sidp_g_kgdm",
        "group",
        "min_kgdm",
        "max_kgdm",
    }
    ids = {r["feed_id"] for r in rows}
    assert "gerste" in ids and "weizen" in ids
    assert len(rows) >= 25
