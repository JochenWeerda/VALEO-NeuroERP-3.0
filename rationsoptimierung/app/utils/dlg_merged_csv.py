"""
Einlesen von ``data/reference/dlg_merged_feeds_lp.csv`` als ``FeedIngredient``-Liste.

Die Spalten ``merge_analytic_id`` und ``merge_note`` werden nicht an Pydantic übergeben.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from ..schemas.feed import FeedIngredient, FeedGroup

# Relativ zum Paket-Root rationsoptimierung/
_DEFAULT_MERGED = (
    Path(__file__).resolve().parents[2] / "data" / "reference" / "dlg_merged_feeds_lp.csv"
)


def load_merged_feed_ingredients(
    csv_path: Path | None = None,
) -> List[FeedIngredient]:
    path = csv_path or _DEFAULT_MERGED
    if not path.is_file():
        raise FileNotFoundError(path)
    out: list[FeedIngredient] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: v for k, v in row.items() if k not in ("merge_analytic_id", "merge_note")}
            row["active"] = str(row.get("active", "true")).lower() in ("1", "true", "yes")
            row["group"] = FeedGroup(row["group"])
            for k in (
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
            ):
                if row.get(k) == "":
                    raise ValueError(f"Leeres Pflichtfeld {k} bei id={row.get('id')}")
                row[k] = float(row[k])
            out.append(FeedIngredient(**row))
    return out
