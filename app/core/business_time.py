"""Geschaeftstag in der Betriebszeitzone.

Buchungsdaten sind Periodendaten: aus ``entry_date`` wird ``period`` als
``YYYY-MM`` gebildet. Ein Buchungsdatum aus UTC verschiebt jede Buchung
zwischen 00:00 und 02:00 Ortszeit (MESZ) bzw. 00:00 und 01:00 (MEZ) auf den
Vortag — am Monatsersten damit in die Vorperiode. Fuer einen Betrieb in
Deutschland ist der Geschaeftstag die Ortszeit, nicht UTC.

Die Zeitzone ist ueber ``BUSINESS_TIMEZONE`` konfigurierbar, damit Mandanten
in anderen Zeitzonen nicht auf Europe/Berlin festgenagelt sind.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_BUSINESS_TIMEZONE = "Europe/Berlin"


def business_timezone() -> ZoneInfo:
    name = os.getenv("BUSINESS_TIMEZONE") or DEFAULT_BUSINESS_TIMEZONE
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        # Eine unbekannte Zeitzone darf keine Buchung verhindern; der
        # dokumentierte Standard ist dann die verlaesslichere Annahme.
        return ZoneInfo(DEFAULT_BUSINESS_TIMEZONE)


def business_date_at(instant: datetime) -> date:
    """Geschaeftstag eines Zeitpunkts. Naive Werte gelten als UTC."""
    aware = instant if instant.tzinfo is not None else instant.replace(tzinfo=timezone.utc)
    return aware.astimezone(business_timezone()).date()


def business_now() -> datetime:
    return datetime.now(business_timezone())


def business_today() -> date:
    return business_now().date()
