"""
FXLoader - Wechselkurse von EZB und anderen Quellen
Automatische Abholung und Aktualisierung von Wechselkursen
"""

import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import structlog

from app.core.database import get_db
from app.finance.models import Wechselkurs

logger = structlog.get_logger(__name__)


# ============================================================================
# EZB API Integration
# ============================================================================

class EZBClient:
    """Client für Europäische Zentralbank Wechselkurse"""
    
    EZB_API_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    EZB_HISTORIC_URL = "https://www.ecb.europa.eu/stats/eurofxref-hist-90d.xml"
    
    # EZB referenziert immer gegen EUR
    EZB_CURRENCY_MAP = {
        "USD": "US Dollar",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "CHF": "Swiss Franc",
        "CAD": "Canadian Dollar",
        "AUD": "Australian Dollar",
        "NZD": "New Zealand Dollar",
        "CNY": "Chinese Yuan",
        "HKD": "Hong Kong Dollar",
        "NOK": "Norwegian Krone",
        "SEK": "Swedish Krona",
        "DKK": "Danish Krone",
        "PLN": "Polish Zloty",
        "CZK": "Czech Koruna",
        "HUF": "Hungarian Forint",
        "RON": "Romanian Leu",
        "BGN": "Bulgarian Lev",
        "TRY": "Turkish Lira",
        "ILS": "Israeli Shekel",
        "ZAR": "South African Rand",
        "BRL": "Brazilian Real",
        "MXN": "Mexican Peso",
        "SGD": "Singapore Dollar",
        "KRW": "South Korean Won",
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_daily_rates(self) -> Dict[str, float]:
        """Hole tägliche EZB Wechselkurse"""
        try:
            response = await self.client.get(self.EZB_API_URL)
            response.raise_for_status()
            
            return self._parse_ecb_xml(response.text)
        except Exception as e:
            logger.error("EZB API fetch failed", error=str(e))
            return {}
    
    async def fetch_historic_rates(self, days: int = 90) -> List[Dict]:
        """Hole historische Wechselkurse"""
        try:
            response = await self.client.get(self.EZB_HISTORIC_URL)
            response.raise_for_status()
            
            return self._parse_historic_xml(response.text)
        except Exception as e:
            logger.error("EZB historic fetch failed", error=str(e))
            return []
    
    def _parse_ecb_xml(self, xml_content: str) -> Dict[str, float]:
        """Parse EZB XML Response"""
        rates = {"EUR": 1.0}  # EUR referenziert sich selbst
        
        root = ET.fromstring(xml_content)
        
        # Namespace
        ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
              'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        
        # Datum finden
        cube = root.find('.//ecb:Cube[@time]', ns)
        if cube is None:
            return rates
            
        # Alle Währungen
        for cube_time in cube:
            if cube_time.get('currency'):
                currency = cube_time.get('currency')
                rate = cube_time.get('rate')
                if rate:
                    rates[currency] = float(rate)
        
        return rates
    
    def _parse_historic_xml(self, xml_content: str) -> List[Dict]:
        """Parse historische EZB Daten"""
        records = []
        
        root = ET.fromstring(xml_content)
        ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
              'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        
        # Alle Tages-Cubes
        for day_cube in root.findall('.//ecb:Cube[@time]/..', ns):
            time_attr = day_cube.find('.//ecb:Cube[@time]', ns)
            if time_attr is not None:
                date_str = time_attr.get('time')
                
                for rate_cube in time_cube.findall('.//ecb:Cube[@currency]', ns):
                    currency = rate_cube.get('currency')
                    rate = rate_cube.get('rate')
                    
                    if currency and rate:
                        records.append({
                            "date": date_str,
                            "currency": currency,
                            "rate": float(rate)
                        })
        
        return records
    
    async def close(self):
        await self.client.aclose()


# ============================================================================
# FXLoader Service
# ============================================================================

class FXLoader:
    """
    Wechselkurs-Lader Service
    
    Lädt Wechselkurse von externen Quellen (EZB) und speichert sie in der DB.
    Unterstützt:
    - EZB API (täglich, historisch)
    - Manueller Import
    - CSV Upload
    """
    
    SUPPORTED_SOURCES = ["EZB", "MANUELL", "CSV", "API"]
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.ezb_client = EZBClient()
    
    async def load_ezb_daily(self) -> int:
        """
        Lade tägliche EZB Wechselkurse
        
        Returns:
            Anzahl geladener Datensätze
        """
        logger.info("Loading EZB daily rates", tenant=self.tenant_id)
        
        rates = await self.ezb_client.fetch_daily_rates()
        
        if not rates:
            logger.warning("No rates fetched from EZB")
            return 0
        
        db = next(get_db())
        loaded = 0
        
        try:
            today = date.today()
            
            for currency, rate in rates.items():
                if currency == "EUR":
                    continue  # EUR ist Referenz
                
                # Prüfen ob bereits vorhanden
                existing = db.query(Wechselkurs).filter(
                    Wechselkurs.tenant_id == self.tenant_id,
                    Wechselkurs.waehrung_von == currency,
                    Wechselkurs.waehrung_nach == "EUR",
                    Wechselkurs.kurs_datum == today
                ).first()
                
                if existing:
                    # Update
                    existing.kurs = rate
                    existing.quelle = "EZB"
                    logger.debug("Updated rate", currency=currency, rate=rate)
                else:
                    # Insert
                    wk = Wechselkurs(
                        id=uuid7(),
                        tenant_id=self.tenant_id,
                        waehrung_von=currency,
                        waehrung_nach="EUR",
                        kurs=rate,
                        kurs_datum=today,
                        quelle="EZB",
                        gueltig_von=today,
                        gueltig_bis=None,
                        created_at=datetime.utcnow()
                    )
                    db.add(wk)
                    loaded += 1
            
            db.commit()
            logger.info("EZB rates loaded", count=loaded, tenant=self.tenant_id)
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to load EZB rates", error=str(e))
            raise
        finally:
            db.close()
        
        return loaded
    
    async def load_ezb_historic(self, days: int = 90) -> int:
        """
        Lade historische EZB Wechselkurse
        
        Args:
            days: Anzahl Tage rückwärts
        """
        logger.info("Loading EZB historic rates", tenant=self.tenant_id, days=days)
        
        records = await self.ezb_client.fetch_historic_rates(days)
        
        if not records:
            return 0
        
        db = next(get_db())
        loaded = 0
        
        try:
            for record in records:
                currency = record["currency"]
                rate = record["rate"]
                rate_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
                
                # Check duplicate
                existing = db.query(Wechselkurs).filter(
                    Wechselkurs.tenant_id == self.tenant_id,
                    Wechselkurs.waehrung_von == currency,
                    Wechselkurs.waehrung_nach == "EUR",
                    Wechselkurs.kurs_datum == rate_date
                ).first()
                
                if not existing:
                    wk = Wechselkurs(
                        id=uuid7(),
                        tenant_id=self.tenant_id,
                        waehrung_von=currency,
                        waehrung_nach="EUR",
                        kurs=rate,
                        kurs_datum=rate_date,
                        quelle="EZB",
                        created_at=datetime.utcnow()
                    )
                    db.add(wk)
                    loaded += 1
            
            db.commit()
            logger.info("Historic EZB rates loaded", count=loaded, tenant=self.tenant_id)
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to load historic rates", error=str(e))
            raise
        finally:
            db.close()
        
        return loaded
    
    async def import_manual_rates(self, rates: List[Dict]) -> int:
        """
        Importiere manuelle Wechselkurse
        
        Args:
            rates: Liste von {waehrung_von, waehrung_nach, kurs, kurs_datum}
        """
        db = next(get_db())
        loaded = 0
        
        try:
            for rate in rates:
                wk = Wechselkurs(
                    id=uuid7(),
                    tenant_id=self.tenant_id,
                    waehrung_von=rate["waehrung_von"],
                    waehrung_nach=rate["waehrung_nach"],
                    kurs=rate["kurs"],
                    kurs_datum=rate["kurs_datum"],
                    quelle="MANUELL",
                    created_at=datetime.utcnow()
                )
                db.add(wk)
                loaded += 1
            
            db.commit()
            logger.info("Manual rates imported", count=loaded, tenant=self.tenant_id)
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to import manual rates", error=str(e))
            raise
        finally:
            db.close()
        
        return loaded
    
    async def schedule_daily_update(self):
        """
        Plane täglichen Update-Job
        (Aufruf via Celery/Background Worker)
        """
        from app.core.celery import celery_app
        
        celery_app.add_periodic_task(
            crontab(hour=14, minute=0),  # 14:00 MEZ
            self.load_ezb_daily.s()
        )
    
    async def close(self):
        await self.ezb_client.close()


# ============================================================================
# Helper Functions
# ============================================================================

def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    rates: Dict[str, float]
) -> float:
    """
    Konvertiere Betrag zwischen Währungen
    
    Args:
        amount: Zu konvertierender Betrag
        from_currency: Quellwährung (ISO Code)
        to_currency: Zielwährung (ISO Code)
        rates: Wechselkurse gegen EUR {currency: rate}
    
    Returns:
        Konvertierter Betrag
    """
    if from_currency == to_currency:
        return amount
    
    # Alles über EUR
    if from_currency == "EUR":
        if to_currency not in rates:
            raise ValueError(f"Unknown currency: {to_currency}")
        return amount * rates[to_currency]
    
    if to_currency == "EUR":
        if from_currency not in rates:
            raise ValueError(f"Unknown currency: {from_currency}")
        return amount / rates[from_currency]
    
    # Kreuz-Konvertierung
    if from_currency not in rates or to_currency not in rates:
        raise ValueError(f"Unknown currency: {from_currency} or {to_currency}")
    
    # Über EUR
    amount_eur = amount / rates[from_currency]
    return amount_eur * rates[to_currency]


from app.core.uuid7 import uuid7
from crontab import crontab
