"""
Daily Price Service für Ernte-Annahme.

Verwaltet Tagespreise für dynamische Preisermittlung.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Protocol, Literal


SourceType = Literal["manual", "exchange", "api"]


@dataclass
class DailyPrice:
    """Tagespreis-Datenstruktur."""
    id: str
    tenant_id: str
    price_eur_per_ton: Decimal
    price_date: date
    valid_from: datetime
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    currency: str = "EUR"
    valid_to: Optional[datetime] = None
    source_type: Optional[SourceType] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


@dataclass
class DailyPriceCreate:
    """Input für Preis-Erstellung."""
    tenant_id: str
    price_eur_per_ton: Decimal
    price_date: date
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    currency: str = "EUR"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source_type: SourceType = "manual"
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    created_by: Optional[str] = None


@dataclass
class DailyPriceFilter:
    """Filter für Preis-Abfrage."""
    tenant_id: str
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    price_date: Optional[date] = None
    valid_at: Optional[datetime] = None  # Für Gültigkeitsprüfung


class DailyPriceRepository(Protocol):
    """Protocol für Daily Price Repository."""
    
    def create(self, price: DailyPrice) -> DailyPrice:
        """Erstellt einen neuen Tagespreis."""
        ...
    
    def get_by_id(self, price_id: str) -> Optional[DailyPrice]:
        """Ruft einen Preis anhand der ID ab."""
        ...
    
    def find_price(self, filter: DailyPriceFilter) -> Optional[DailyPrice]:
        """Findet einen Preis basierend auf Filterkriterien."""
        ...
    
    def get_price_history(
        self,
        tenant_id: str,
        article_id: Optional[str] = None,
        warengruppe: Optional[str] = None,
        crop_code: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100,
    ) -> list[DailyPrice]:
        """Ruft Preis-Historie ab."""
        ...
    
    def bulk_create(self, prices: list[DailyPrice]) -> list[DailyPrice]:
        """Erstellt mehrere Preise auf einmal."""
        ...


def get_price_for_date(
    repo: DailyPriceRepository,
    filter: DailyPriceFilter,
) -> Optional[DailyPrice]:
    """
    Ruft den Preis für ein bestimmtes Datum ab.
    
    Priorität:
    1. article_id (falls vorhanden)
    2. warengruppe (falls vorhanden)
    3. crop_code (falls vorhanden)
    
    Falls price_date nicht angegeben, wird das aktuelle Datum verwendet.
    """
    if filter.price_date is None:
        filter.price_date = date.today()
    
    return repo.find_price(filter)


def create_daily_price(
    repo: DailyPriceRepository,
    create_input: DailyPriceCreate,
) -> DailyPrice:
    """
    Erstellt einen neuen Tagespreis.
    
    Mindestens eines der Felder article_id, warengruppe oder crop_code muss gesetzt sein.
    """
    if not create_input.article_id and not create_input.warengruppe and not create_input.crop_code:
        raise ValueError("At least one of article_id, warengruppe, or crop_code must be set")
    
    # Default valid_from = price_date 00:00:00
    valid_from = create_input.valid_from
    if valid_from is None:
        valid_from = datetime.combine(create_input.price_date, datetime.min.time())
    
    price = DailyPrice(
        id=f"dp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        tenant_id=create_input.tenant_id,
        article_id=create_input.article_id,
        warengruppe=create_input.warengruppe,
        crop_code=create_input.crop_code,
        price_eur_per_ton=create_input.price_eur_per_ton,
        currency=create_input.currency,
        price_date=create_input.price_date,
        valid_from=valid_from,
        valid_to=create_input.valid_to,
        source_type=create_input.source_type,
        source_id=create_input.source_id,
        source_name=create_input.source_name,
        created_at=datetime.now(),
        created_by=create_input.created_by,
    )
    
    return repo.create(price)


def bulk_import_prices(
    repo: DailyPriceRepository,
    tenant_id: str,
    prices: list[DailyPriceCreate],
    created_by: Optional[str] = None,
) -> list[DailyPrice]:
    """
    Importiert mehrere Tagespreise auf einmal.
    
    Nützlich für Bulk-Import aus Excel/CSV oder API-Synchronisation.
    """
    daily_prices = []
    
    for create_input in prices:
        # Setze created_by falls nicht gesetzt
        if create_input.created_by is None:
            create_input.created_by = created_by
        
        price = create_daily_price(repo, create_input)
        daily_prices.append(price)
    
    return repo.bulk_create(daily_prices)


def get_price_history(
    repo: DailyPriceRepository,
    tenant_id: str,
    article_id: Optional[str] = None,
    warengruppe: Optional[str] = None,
    crop_code: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 100,
) -> list[DailyPrice]:
    """
    Ruft die Preis-Historie ab.
    
    Nützlich für Preis-Charts und Trend-Analysen.
    """
    return repo.get_price_history(
        tenant_id=tenant_id,
        article_id=article_id,
        warengruppe=warengruppe,
        crop_code=crop_code,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


