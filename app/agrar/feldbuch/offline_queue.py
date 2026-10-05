"""Offline-Operations-Queue (ASK-MOB-001 Kern: Idempotenz/Sync-Plan)."""
from __future__ import annotations

from typing import Any


def merge_offline_ops(ops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupliziert Offline-Ops nach client_ref (letzter Stand gewinnt)."""
    if not ops:
        return []
    by_ref: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for op in ops:
        ref = op.get("client_ref")
        if not ref:
            raise ValueError("client_ref ist Pflicht")
        ref_s = str(ref)
        if ref_s not in by_ref:
            order.append(ref_s)
        by_ref[ref_s] = op
    return [by_ref[r] for r in order]
