"""Zulässige Lieferschein-Status. Entspricht ``ck_delivery_notes_status``."""

from __future__ import annotations

ZULAESSIG = frozenset({
    "draft",
    "printed",
    "posted",
    "shipped",
    "delivered",
    "invoiced",
    "BERECHNET",
    "storniert",
    "cancelled",
    "geliefert",
})


def pruefe_status(status: str) -> None:
    if status not in ZULAESSIG:
        erlaubt = ", ".join(sorted(ZULAESSIG))
        raise ValueError(f"Lieferschein-Status {status!r} ist nicht zulässig. Erlaubt: {erlaubt}")
