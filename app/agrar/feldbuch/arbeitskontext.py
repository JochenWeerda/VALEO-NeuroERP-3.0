"""Arbeitskontext für die Ackerschlagkartei (Lastenheft Kap. 5)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


def build_arbeitskontext(
    *,
    customer_id: str,
    betrieb_name: str,
    wirtschaftsjahr: Optional[int],
    erntejahr: Optional[int] = None,
    rolle: str = "betriebsleiter",
    betriebsstaette: Optional[str] = None,
    sync_status: str = "online",
) -> dict[str, Any]:
    """Baut den verbindlichen Arbeitskontext für Portal/ERP.

    MUSS: Mandant/Kunde, Betrieb, Wirtschaftsjahr, Rolle, Sync-Status.
    """
    if wirtschaftsjahr is None:
        raise ValueError("wirtschaftsjahr ist Pflicht")
    year = int(wirtschaftsjahr)
    if year < 1990 or year > 2100:
        raise ValueError("wirtschaftsjahr ungueltig")
    ernte = int(erntejahr) if erntejahr is not None else year
    return {
        "customerId": customer_id,
        "betriebName": betrieb_name or customer_id,
        "betriebsstaette": betriebsstaette,
        "wirtschaftsjahr": year,
        "erntejahr": ernte,
        "rolle": rolle,
        "syncStatus": sync_status,
        "datenstand": datetime.now(timezone.utc).isoformat(),
    }
