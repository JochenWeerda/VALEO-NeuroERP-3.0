"""
Führt zusammen:
  - data/reference/lkv_sachsen_getreide_ernte_2025_tabelle1.csv
  - data/reference/dlg_2025_kraftfutter_wiederkauer_tabelle2.csv
  - data/reference/dlg_2025_lp_import_filled_sourced.csv

Ausgabe:
  - data/reference/dlg_merged_feeds_lp.csv  (Spalten wie sample_feeds.csv + Zusatzspalten)
  - data/reference/dlg_merge_report.csv     (alle Zeilen mit Status)

Grobfutter/Silagen ohne Zeile in den kurzen Referenz-CSVs: ``data/reference/dlg_forage_merge_overlay.json``
(Templates + ``lp_feed_template`` + optional ``standalone_feed_ids``).

Aufruf (aus rationsoptimierung):
  python scripts/merge_dlg_reference_to_lp_csv.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_REF = _ROOT / "data" / "reference"


def _load_csv_dicts(name: str) -> list[dict]:
    p = _REF / name
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _load_analytics() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for fn in (
        "lkv_sachsen_getreide_ernte_2025_tabelle1.csv",
        "dlg_2025_kraftfutter_wiederkauer_tabelle2.csv",
    ):
        for row in _load_csv_dicts(fn):
            out[row["id"]] = row
    return out


def _resolve_analytic_id(feed_id: str, aliases: dict) -> tuple[str | None, str | None]:
    """Returns (analytic_id, note)."""
    expl = aliases.get("explicit", {})
    if feed_id in expl:
        return expl[feed_id], None
    if feed_id in aliases.get("raps_variants_use_base_dlg_row", []):
        return "raps_extraktionsschrot_dlg2025", "Analytik = Basis-Rapsextraktionsschrot DLG (Variante)"
    cereals = aliases.get("ernte2025_cereals", [])
    if feed_id in cereals:
        return f"{feed_id}_ernte2025", "Analytik = LKV Ernte 2025"
    return None, None


def _dlg_group_to_feed_group(g: str) -> str:
    if not g:
        return "concentrate"
    gl = g.lower()
    if (
        "grundfutter" in gl
        or "grobfutter" in gl
        or "silage" in gl
        or "heu" in gl
        or "luzerne" in gl
        or "kleegras" in gl
    ):
        return "forage"
    if "feuchtkonzentrat" in gl or "trockenkonzentrat" in gl:
        return "concentrate"
    return "concentrate"


def _load_forage_overlay() -> dict:
    p = _REF / "dlg_forage_merge_overlay.json"
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _lp_or_template(row: dict, key: str, tmpl_val: float) -> float:
    v = _f(row.get(key))
    return tmpl_val if v is None else v


def _merged_row_from_forage_template(lp_row: dict, tmpl: dict) -> dict:
    """Baut eine Output-Zeile aus Overlay-Template + LP-Feldern (sidp, Mineralien, Preis, min/max, Notizen)."""
    fid = lp_row["feed_id"]
    sidp = _lp_or_template(lp_row, "sidp_g_kgdm", float(tmpl["sidp_g_kgdm"]))
    ca = _lp_or_template(lp_row, "ca_g_kgdm", float(tmpl["ca_g_kgdm"]))
    p_min = _lp_or_template(lp_row, "p_g_kgdm", float(tmpl["p_g_kgdm"]))
    na = _lp_or_template(lp_row, "na_g_kgdm", float(tmpl["na_g_kgdm"]))
    price = _f(lp_row.get("price_eur_kgdm"))
    if price is None:
        price = float(tmpl["price_eur_kgdm"])
    min_k = _f(lp_row.get("min_kgdm"))
    if min_k is None:
        min_k = float(tmpl["min_kgdm"])
    max_k = _f(lp_row.get("max_kgdm"))
    if max_k is None:
        max_k = float(tmpl["max_kgdm"])

    grp = str(tmpl.get("group") or "forage")
    base_note = str(tmpl.get("merge_note") or "")
    lp_notes = lp_row.get("notes") or ""
    merge_note = base_note + ("; " if base_note and lp_notes else "") + lp_notes

    return {
        "id": fid,
        "name": lp_row.get("feed_name") or fid,
        "group": grp,
        "dm_frac": float(tmpl["dm_frac"]),
        "price_eur_kgdm": price,
        "me_mj_kgdm": float(tmpl["me_mj_kgdm"]),
        "sidp_g_kgdm": sidp,
        "andfom_g_kgdm": float(tmpl["andfom_g_kgdm"]),
        "starch_g_kgdm": float(tmpl["starch_g_kgdm"]),
        "sugar_g_kgdm": float(tmpl["sugar_g_kgdm"]),
        "fat_g_kgdm": float(tmpl["fat_g_kgdm"]),
        "ca_g_kgdm": ca,
        "p_g_kgdm": p_min,
        "na_g_kgdm": na,
        "min_kgdm": min_k,
        "max_kgdm": max_k,
        "active": "true",
        "merge_analytic_id": str(tmpl["merge_analytic_id"]),
        "merge_note": merge_note,
    }


def _f(x, default: float | None = None) -> float | None:
    if x is None or str(x).strip() == "":
        return default
    try:
        return float(x)
    except ValueError:
        return default


def main() -> None:
    aliases_path = _REF / "feed_analytic_aliases.json"
    with aliases_path.open(encoding="utf-8") as f:
        aliases = json.load(f)

    analytics = _load_analytics()
    filled = _load_csv_dicts("dlg_2025_lp_import_filled_sourced.csv")
    forage_ov = _load_forage_overlay()
    lp_tpl: dict[str, str] = forage_ov.get("lp_feed_template") or {}
    forage_templates: dict[str, dict] = forage_ov.get("templates") or {}

    merged_rows: list[dict] = []

    for row in filled:
        fid = row["feed_id"]
        aid, note = _resolve_analytic_id(fid, aliases)
        an = analytics.get(aid) if aid else None

        tpl_name = lp_tpl.get(fid)
        if an is None and tpl_name and tpl_name in forage_templates:
            merged_rows.append(_merged_row_from_forage_template(row, forage_templates[tpl_name]))
            continue

        if an is None:
            continue

        dm_frac = _f(an["tm_g_kg_fm"])
        if dm_frac is not None:
            dm_frac = round(dm_frac / 1000.0, 4)

        me = _f(an.get("me_mj_kg_tm"))
        sidp = _f(row.get("sidp_g_kgdm"), 0.0)
        ca = _f(row.get("ca_g_kgdm"), 0.0)
        p = _f(row.get("p_g_kgdm"), 0.0)
        na = _f(row.get("na_g_kgdm"), 0.0)
        price = _f(row.get("price_eur_kgdm"), 0.25)

        grp = _dlg_group_to_feed_group(row.get("group") or "")

        out = {
            "id": fid,
            "name": row.get("feed_name") or fid,
            "group": grp,
            "dm_frac": dm_frac if dm_frac is not None else "",
            "price_eur_kgdm": price if price is not None else 0.25,
            "me_mj_kgdm": me if me is not None else "",
            "sidp_g_kgdm": sidp if sidp is not None else "",
            "andfom_g_kgdm": _f(an.get("andfom_g_kg_tm"), ""),
            "starch_g_kgdm": _f(an.get("starch_g_kg_tm"), ""),
            "sugar_g_kgdm": _f(an.get("sugar_g_kg_tm"), ""),
            "fat_g_kgdm": _f(an.get("rf_g_kg_tm"), ""),
            "ca_g_kgdm": ca,
            "p_g_kgdm": p,
            "na_g_kgdm": na,
            "min_kgdm": _f(row.get("min_kgdm"), 0.0),
            "max_kgdm": _f(row.get("max_kgdm"), 8.0),
            "active": "true",
            "merge_analytic_id": aid,
            "merge_note": (note or "") + ("; " if note and row.get("notes") else "") + (row.get("notes") or ""),
        }
        merged_rows.append(out)

    done_ids = {m["id"] for m in merged_rows}
    standalone_labels = {"grassilage": "Grassilage"}
    for sid in forage_ov.get("standalone_feed_ids") or []:
        if sid in done_ids:
            continue
        tmpl = forage_templates.get(sid)
        if tmpl is None:
            continue
        synthetic = {"feed_id": sid, "feed_name": standalone_labels.get(sid, sid), "notes": ""}
        merged_rows.append(_merged_row_from_forage_template(synthetic, tmpl))

    merged_path = _REF / "dlg_merged_feeds_lp.csv"
    report_path = _REF / "dlg_merge_report.csv"

    fieldnames = [
        "id",
        "name",
        "group",
        "dm_frac",
        "price_eur_kgdm",
        "me_mj_kgdm",
        "sidp_g_kgdm",
        "andfom_g_kgdm",
        "starch_g_kgdm",
        "sugar_g_kgdm",
        "fat_g_kgdm",
        "ca_g_kgdm",
        "p_g_kgdm",
        "na_g_kgdm",
        "min_kgdm",
        "max_kgdm",
        "active",
        "merge_analytic_id",
        "merge_note",
    ]

    with merged_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(merged_rows)

    done_merged = {m["id"]: m for m in merged_rows}
    final_report: list[dict] = []
    for row in filled:
        fid = row["feed_id"]
        if fid in done_merged:
            m = done_merged[fid]
            final_report.append(
                {
                    "feed_id": fid,
                    "status": "merged",
                    "analytic_id": m["merge_analytic_id"],
                    "note": str(m.get("merge_note") or "")[:500],
                }
            )
        else:
            final_report.append(
                {
                    "feed_id": fid,
                    "status": "no_analytic_match",
                    "analytic_id": "",
                    "note": "Kein Eintrag in LKV-Ernte-2025- oder DLG-Kraftfutter-Referenz-CSV",
                }
            )

    with report_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["feed_id", "status", "analytic_id", "note"])
        w.writeheader()
        w.writerows(final_report)

    print(f"Gemerged: {len(merged_rows)} Zeilen -> {merged_path}")
    print(f"Report:   {len(final_report)} Zeilen -> {report_path}")
    print(f"Ohne Analytik-Match: {sum(1 for r in final_report if r['status'] != 'merged')}")


if __name__ == "__main__":
    main()
    sys.exit(0)
