"""Canonical feed-catalog rules and compatibility adapter for the solver."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any, Iterable, Mapping


class FeedKind(StrEnum):
    FORAGE = "forage"
    CONCENTRATE = "concentrate"
    MINERAL = "mineral"
    ADDITIVE = "additive"
    BYPRODUCT = "byproduct"
    LIQUID = "liquid"
    OTHER = "other"


class FeedApprovalStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    BLOCKED = "blocked"
    RETIRED = "retired"


def infer_feed_kind(category: str) -> FeedKind:
    value = category.casefold()
    if any(token in value for token in ("grundfutter", "silage", "heu")):
        return FeedKind.FORAGE
    if "mineral" in value:
        return FeedKind.MINERAL
    if "nebenprodukt" in value:
        return FeedKind.BYPRODUCT
    return FeedKind.CONCENTRATE


def _date(value: date | str | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(value)


def validate_feed(feed_kind: FeedKind, approval_status: FeedApprovalStatus,
                  valid_from: date | str | None, valid_until: date | str | None,
                  dry_matter_pct: Decimal | None) -> dict[str, Any]:
    start, end = _date(valid_from), _date(valid_until)
    if start and end and end < start:
        raise ValueError("Gueltigkeitsende darf nicht vor dem Beginn liegen.")
    if dry_matter_pct is not None and not Decimal("0") < dry_matter_pct <= Decimal("100"):
        raise ValueError("Trockenmasse muss groesser 0 und hoechstens 100 Prozent sein.")
    return {
        "feed_kind": feed_kind.value,
        "approval_status": approval_status.value,
        "valid_from": start,
        "valid_until": end,
        "dry_matter_pct": dry_matter_pct,
    }


_SOLVER_VALUE_MAP = {
    "metabolizable_energy": "me",
    "sidp": "sidp",
    "crude_protein": "cp",
    "ndf": "ndf",
    "adf": "adf",
    "starch": "st",
    "bypass_starch": "bst",
    "sugar": "zu",
    "nfc": "nfc",
    "crude_fat": "xl",
    "calcium": "ca",
    "phosphorus": "p",
    "sodium": "na",
    "magnesium": "mg",
    "potassium": "k",
    "rmd": "rmd",
    "omdfan1": "omdfan1",
    "sidlys": "sidlys",
    "sidmet": "sidmet",
    "ndfd": "ndfd",
    "gross_energy": "ge",
    "dcab": "dcab",
    "edg": "edg",
}


def build_solver_feed(head: Mapping[str, Any],
                      reference_values: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Map persisted feed data to the stable dict consumed by ``Feed.from_dict``.

    Flexible values win over legacy columns. Legacy percentages are converted to
    the solver's g/kg-DM convention and remain a bounded compatibility fallback.
    """
    dm_pct = Decimal(str(head.get("trockensubstanz") or "100"))
    cp = Decimal(str(head.get("protein") or "0")) * Decimal("10")
    me = Decimal(str(head.get("energie") or "0"))
    values: dict[str, Decimal] = {}
    for item in reference_values:
        code = str(item.get("nutrient_code") or "")
        if code:
            values[code] = Decimal(str(item.get("value") or "0"))
    if "dry_matter" in values:
        dm_pct = values["dry_matter"]
    if "crude_protein" in values:
        cp = values["crude_protein"]
    if "metabolizable_energy" in values:
        me = values["metabolizable_energy"]
    dm_frac = dm_pct / Decimal("100") if dm_pct else Decimal("1")
    price_t = Decimal(str(head.get("price_eur_t") or head.get("preis_pro_t") or "0"))
    price_kg_dm = price_t / Decimal("1000") / dm_frac if dm_frac > 0 else Decimal("0")
    feed_kind = str(head.get("feed_kind") or "")
    art = str(head.get("art") or "").casefold()
    forage = feed_kind == FeedKind.FORAGE.value or any(token in art for token in ("grundfutter", "silage", "heu"))
    result: dict[str, Any] = {
        "id": str(head.get("id") or ""), "name": str(head.get("name") or ""),
        "group": str(head.get("art") or ""), "futterart": feed_kind or str(head.get("art") or ""),
        "forage": forage, "structural_coproduct": feed_kind == FeedKind.BYPRODUCT.value,
        "dm_frac": float(dm_frac), "price": float(price_kg_dm),
        "min_kg": float(head.get("min_kg") or 0), "max_kg": float(head.get("max_kg") or 0),
        "me": float(me), "cp": float(cp),
    }
    for code, target in _SOLVER_VALUE_MAP.items():
        if code in values and code not in {"metabolizable_energy", "crude_protein"}:
            result[target] = float(values[code])
    return result
