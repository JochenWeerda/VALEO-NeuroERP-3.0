"""Betriebssnapshot aus CRM-/Kundenfeldern (ASK-BUS-001)."""
from __future__ import annotations

from typing import Any


def build_betrieb_snapshot(customer: dict[str, Any]) -> dict[str, Any]:
    name = customer.get("name") or customer.get("firma") or customer.get("id") or "Betrieb"
    return {
        "customerId": customer.get("id"),
        "betriebName": name,
        "anschrift": {
            "strasse": customer.get("strasse") or customer.get("address"),
            "plz": customer.get("plz") or customer.get("postal_code"),
            "ort": customer.get("ort") or customer.get("city"),
        },
        "bundesland": customer.get("bundesland") or customer.get("state"),
        "kommunikationsdaten": {
            "email": customer.get("email"),
            "telefon": customer.get("telefon") or customer.get("phone"),
        },
        "registrierkennungen": {
            "betriebsnummer": customer.get("betriebsnummer") or customer.get("bnr"),
        },
    }
