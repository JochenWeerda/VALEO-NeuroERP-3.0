"""Mischprotokoll-Helfer fuer den Rationssolver."""

from __future__ import annotations


def mix_group_order(name: str) -> int:
    """Praxisnahe Mischreihenfolge anhand des Futtermittelnamens."""
    n = (name or "").lower()
    if any(k in n for k in ("stroh", "heu")):
        return 1
    if any(k in n for k in ("silage", "gras", "mais")):
        return 2
    if any(k in n for k in ("ruebe", "biertreber", "melasse", "schnitzel", "cop")):
        return 3
    if any(k in n for k in ("mineral", "kraftfutter", "konzentrat", "milchleistung")):
        return 5
    return 4


__all__ = ["mix_group_order"]
