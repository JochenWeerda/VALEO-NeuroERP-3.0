"""
Price Monitoring Worker
Scheduled worker for monitoring market prices and alerting on significant changes
"""

import logging
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

from ..core.config import settings
from app.core.database import get_db
from sqlalchemy import text
from app.infrastructure.models import DailyPrice, ArticlePriceThreshold

logger = logging.getLogger(__name__)

# Schwellen für Alerts (z. B. > 5 % Änderung zum Vortag)
DAILY_PRICE_CHANGE_PERCENT_THRESHOLD = 5.0


class PriceMonitoringWorker:
    """Worker for automated price monitoring and alerting"""

    def __init__(self):
        self.db = None

    async def initialize(self):
        """Initialize database connection"""
        self.db = next(get_db())

    async def run_price_monitoring(self) -> Dict[str, Any]:
        """
        Run price monitoring and generate alerts
        
        Returns:
            Dictionary with monitoring results
        """
        results = {
            'success': True,
            'alerts': [],
            'checks': 0
        }

        try:
            if not self.db:
                await self.initialize()

            # Check 1: Monitor daily prices for significant changes
            alerts = await self._check_daily_price_changes()
            results['alerts'].extend(alerts)
            results['checks'] += 1

            # Check 2: Monitor article price thresholds
            alerts = await self._check_price_thresholds()
            results['alerts'].extend(alerts)
            results['checks'] += 1

            # Check 3: Monitor competitor prices (if configured)
            alerts = await self._check_competitor_prices()
            results['alerts'].extend(alerts)
            results['checks'] += 1

            # Check 4: Monitor supplier price changes
            alerts = await self._check_supplier_price_changes()
            results['alerts'].extend(alerts)
            results['checks'] += 1

            logger.info(f"Price monitoring completed: {results['checks']} checks, {len(results['alerts'])} alerts")

        except Exception as e:
            logger.error(f"Error in price monitoring: {e}")
            results['success'] = False
            results['error'] = str(e)

        return results

    async def _check_daily_price_changes(self) -> List[Dict[str, Any]]:
        """Vergleicht Tagespreise (domain_inventory.daily_prices) mit Vortag und meldet starke Änderungen."""
        alerts: List[Dict[str, Any]] = []
        try:
            if not self.db:
                return []
            today = date.today()
            yesterday = today - timedelta(days=1)
            tenant_id = getattr(settings, "DEFAULT_TENANT_ID", None) or "00000000-0000-0000-0000-000000000001"
            rows_today = (
                self.db.query(DailyPrice)
                .filter(
                    DailyPrice.tenant_id == tenant_id,
                    DailyPrice.price_date == today,
                )
                .limit(500)
                .all()
            )
            rows_yesterday = (
                self.db.query(DailyPrice)
                .filter(
                    DailyPrice.tenant_id == tenant_id,
                    DailyPrice.price_date == yesterday,
                )
                .limit(500)
                .all()
            )
            by_key = lambda r: (r.article_id or "", r.warengruppe or "", r.crop_code or "")
            prev_map = {by_key(r): float(r.price_eur_per_ton) for r in rows_yesterday}
            for r in rows_today:
                key = by_key(r)
                prev = prev_map.get(key)
                if prev is None:
                    continue
                curr = float(r.price_eur_per_ton)
                if prev == 0:
                    continue
                pct = abs((curr - prev) / prev * 100)
                if pct >= DAILY_PRICE_CHANGE_PERCENT_THRESHOLD:
                    alerts.append({
                        "type": "daily_price_change",
                        "article_id": r.article_id,
                        "warengruppe": r.warengruppe,
                        "crop_code": r.crop_code,
                        "previous_eur_per_ton": prev,
                        "current_eur_per_ton": curr,
                        "change_percent": round(pct, 2),
                    })
            logger.info("Checking daily price changes: %s today, %s yesterday, %s alerts", len(rows_today), len(rows_yesterday), len(alerts))
            return alerts
        except Exception as e:
            logger.error(f"Error checking daily prices: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_price_thresholds(self) -> List[Dict[str, Any]]:
        """Prüft Tagespreise gegen article_price_thresholds (min/max) und meldet Preis ≤ 0."""
        alerts: List[Dict[str, Any]] = []
        try:
            if not self.db:
                return []
            today = date.today()
            tenant_id = getattr(settings, "DEFAULT_TENANT_ID", None) or "00000000-0000-0000-0000-000000000001"

            # 1) Tagespreise ≤ 0
            zero_rows = (
                self.db.query(DailyPrice)
                .filter(
                    DailyPrice.tenant_id == tenant_id,
                    DailyPrice.price_date == today,
                    DailyPrice.price_eur_per_ton <= 0,
                )
                .limit(100)
                .all()
            )
            for r in zero_rows:
                alerts.append({
                    "type": "price_threshold",
                    "message": "Tagespreis ≤ 0",
                    "price_id": r.id,
                    "article_id": r.article_id,
                    "crop_code": r.crop_code,
                    "price_eur_per_ton": float(r.price_eur_per_ton),
                })

            # 2) Schwellen aus article_price_thresholds (effective_from <= today, effective_to >= today oder NULL)
            thresholds = (
                self.db.query(ArticlePriceThreshold)
                .filter(
                    ArticlePriceThreshold.tenant_id == tenant_id,
                    ArticlePriceThreshold.effective_from <= today,
                    (ArticlePriceThreshold.effective_to.is_(None)) | (ArticlePriceThreshold.effective_to >= today),
                )
                .all()
            )
            daily_prices = (
                self.db.query(DailyPrice)
                .filter(
                    DailyPrice.tenant_id == tenant_id,
                    DailyPrice.price_date == today,
                )
                .limit(500)
                .all()
            )
            by_key = lambda r: (r.article_id or "", r.warengruppe or "", r.crop_code or "")
            thresh_by_key = {}
            for t in thresholds:
                key = (t.article_id or "", t.warengruppe or "", t.crop_code or "")
                thresh_by_key[key] = t
            for r in daily_prices:
                key = by_key(r)
                t = thresh_by_key.get(key)
                if not t:
                    continue
                price = float(r.price_eur_per_ton)
                if t.min_eur_per_ton is not None and price < float(t.min_eur_per_ton):
                    alerts.append({
                        "type": "price_threshold",
                        "message": "Tagespreis unter Minimum",
                        "price_id": r.id,
                        "article_id": r.article_id,
                        "crop_code": r.crop_code,
                        "price_eur_per_ton": price,
                        "threshold_min": float(t.min_eur_per_ton),
                    })
                if t.max_eur_per_ton is not None and price > float(t.max_eur_per_ton):
                    alerts.append({
                        "type": "price_threshold",
                        "message": "Tagespreis über Maximum",
                        "price_id": r.id,
                        "article_id": r.article_id,
                        "crop_code": r.crop_code,
                        "price_eur_per_ton": price,
                        "threshold_max": float(t.max_eur_per_ton),
                    })
            logger.info("Checking price thresholds: %s alerts", len(alerts))
            return alerts
        except Exception as e:
            logger.error(f"Error checking price thresholds: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_competitor_prices(self) -> List[Dict[str, Any]]:
        """Check competitor prices against our prices"""
        try:
            # Stub: Wettbewerbs-Preisdatenquelle anbinden
            logger.info("Checking competitor prices...")
            return []
        except Exception as e:
            logger.error(f"Error checking competitor prices: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_supplier_price_changes(self) -> List[Dict[str, Any]]:
        """Check for significant supplier price changes"""
        try:
            # Stub: Lieferanten-Preishistorie anbinden
            logger.info("Checking supplier price changes...")
            return []
        except Exception as e:
            logger.error(f"Error checking supplier prices: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def cleanup(self):
        """Clean up database connections"""
        if self.db:
            self.db.close()


async def run_price_monitoring():
    """Main function to run price monitoring"""
    worker = PriceMonitoringWorker()

    try:
        await worker.initialize()
        result = await worker.run_price_monitoring()

        if result['success']:
            logger.info(f"Price monitoring completed: {result}")
        else:
            logger.error(f"Price monitoring failed: {result}")

        return result

    except Exception as e:
        logger.error(f"Critical error in price monitoring worker: {e}")
        return {
            'success': False,
            'error': str(e)
        }

    finally:
        await worker.cleanup()


# Scheduled execution function (to be called by scheduler)
def execute_price_monitoring():
    """Synchronous wrapper for scheduled execution"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_price_monitoring())
        loop.close()

        return result

    except Exception as e:
        logger.error(f"Error executing price monitoring: {e}")
        return {
            'success': False,
            'error': str(e)
        }
