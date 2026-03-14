from __future__ import annotations

from decimal import Decimal


def compute_contract_status(total_quantity: Decimal, remaining_quantity: Decimal, current_status: str) -> str:
    if current_status == "cancelled":
        return "cancelled"
    if remaining_quantity <= Decimal("0"):
        return "fulfilled"
    if remaining_quantity < total_quantity:
        return "partially_allocated"
    return "open"
