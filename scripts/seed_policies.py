#!/usr/bin/env python3
"""
Seed-Script für Policy-Datenbank
Befüllt die SQLite-Datenbank mit Standard-Policies

Ausführen: python scripts/seed_policies.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.policy import PolicyStore, Rule
from app.policy.models import When, Window, Approval


def seed_policies():
    """Befüllt Datenbank mit Standard-Policies"""
    store = PolicyStore("data/policies.db")

    default_policies = [
        Rule(
            id="pricing.auto.adjust",
            when=When(kpiId="margin", severity=["warn", "crit"]),
            action="pricing.adjust",
            params={"deltaPct": {"warn": 1, "crit": 3}},
            limits={"maxDailyPct": 3.0, "maxWeeklyPct": 7.0},
            window=Window(days=[1, 2, 3, 4, 5], start="08:00", end="18:00"),
            approval=Approval(
                required=True,
                roles=["manager", "admin"],
                bypassIfSeverity="crit"
            ),
            autoExecute=False,
            autoSuggest=True
        ),
        Rule(
            id="inventory.auto.reorder",
            when=When(kpiId="stock", severity=["warn", "crit"]),
            action="inventory.reorder",
            params={"qty": {"warn": 250, "crit": 500}},
            limits={"maxDailyQty": 2000.0},
            window=Window(days=[1, 2, 3, 4, 5, 6], start="07:00", end="20:00"),
            approval=Approval(required=False),
            autoExecute=True,
            autoSuggest=True
        ),
        Rule(
            id="sales.notify.drop",
            when=When(kpiId="rev", severity=["warn", "crit"]),
            action="sales.notify",
            params={
                "topic": "Umsatzabweichung",
                "messageTemplate": "Umsatz {delta}% – bitte prüfen."
            },
            window=Window(days=[0, 1, 2, 3, 4, 5, 6], start="00:00", end="23:59"),
            approval=Approval(required=False),
            autoExecute=True,
            autoSuggest=True
        ),
    ]

    store.bulk_upsert(default_policies)
    print(f"✅ Seeded {len(default_policies)} policies to data/policies.db")


if __name__ == "__main__":
    seed_policies()

