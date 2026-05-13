"""Price Monitoring Worker — alerts on significant market price changes."""

import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Dict, List

from ..core.config import settings
from app.infrastructure.models import ArticlePriceThreshold, DailyPrice

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)

DAILY_PRICE_CHANGE_PERCENT_THRESHOLD = 5.0

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _tenant() -> str:
    return getattr(settings, "DEFAULT_TENANT_ID", None) or _DEFAULT_TENANT


def _price_key(r) -> tuple:
    return (r.article_id or "", r.warengruppe or "", r.crop_code or "")


class PriceMonitoringWorker(BaseWorker):
    async def run(self) -> Dict[str, Any]:
        result = self._base_result(alerts=[], checks=0)
        try:
            await self._ensure_db()

            for check in (
                self._check_daily_price_changes,
                self._check_price_thresholds,
                self._check_competitor_prices,
                self._check_supplier_price_changes,
            ):
                result["alerts"].extend(await check())
                result["checks"] += 1

            logger.info(
                "Price monitoring completed: %d checks, %d alerts",
                result["checks"],
                len(result["alerts"]),
            )
        except Exception as exc:
            self._error_result(result, exc)
        return result

    async def _check_daily_price_changes(self) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        try:
            if not self.db:
                return []
            today = date.today()
            yesterday = today - timedelta(days=1)
            tid = _tenant()

            rows_today = (
                self.db.query(DailyPrice)
                .filter(DailyPrice.tenant_id == tid, DailyPrice.price_date == today)
                .limit(500).all()
            )
            rows_yesterday = (
                self.db.query(DailyPrice)
                .filter(DailyPrice.tenant_id == tid, DailyPrice.price_date == yesterday)
                .limit(500).all()
            )
            prev_map = {_price_key(r): float(r.price_eur_per_ton) for r in rows_yesterday}
            for r in rows_today:
                prev = prev_map.get(_price_key(r))
                if prev is None or prev == 0:
                    continue
                curr = float(r.price_eur_per_ton)
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
            logger.info(
                "Daily price check: %d today, %d yesterday, %d alerts",
                len(rows_today), len(rows_yesterday), len(alerts),
            )
            return alerts
        except Exception as exc:
            logger.error("Error checking daily prices: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_price_thresholds(self) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        try:
            if not self.db:
                return []
            today = date.today()
            tid = _tenant()

            zero_rows = (
                self.db.query(DailyPrice)
                .filter(
                    DailyPrice.tenant_id == tid,
                    DailyPrice.price_date == today,
                    DailyPrice.price_eur_per_ton <= 0,
                ).limit(100).all()
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

            thresholds = (
                self.db.query(ArticlePriceThreshold)
                .filter(
                    ArticlePriceThreshold.tenant_id == tid,
                    ArticlePriceThreshold.effective_from <= today,
                    (ArticlePriceThreshold.effective_to.is_(None))
                    | (ArticlePriceThreshold.effective_to >= today),
                ).all()
            )
            daily_prices = (
                self.db.query(DailyPrice)
                .filter(DailyPrice.tenant_id == tid, DailyPrice.price_date == today)
                .limit(500).all()
            )
            thresh_by_key = {
                (t.article_id or "", t.warengruppe or "", t.crop_code or ""): t
                for t in thresholds
            }
            for r in daily_prices:
                t = thresh_by_key.get(_price_key(r))
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
            logger.info("Price threshold check: %d alerts", len(alerts))
            return alerts
        except Exception as exc:
            logger.error("Error checking price thresholds: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_competitor_prices(self) -> List[Dict[str, Any]]:
        try:
            logger.info("Checking competitor prices...")
            return []
        except Exception as exc:
            logger.error("Error checking competitor prices: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_supplier_price_changes(self) -> List[Dict[str, Any]]:
        try:
            logger.info("Checking supplier price changes...")
            return []
        except Exception as exc:
            logger.error("Error checking supplier prices: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_price_monitoring() -> Dict[str, Any]:
    worker = PriceMonitoringWorker()
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:
        logger.error("Critical error in price monitoring worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_price_monitoring() -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_price_monitoring())
        loop.close()
        return result
    except Exception as exc:
        logger.error("Error executing price monitoring: %s", exc)
        return {"success": False, "error": str(exc)}
