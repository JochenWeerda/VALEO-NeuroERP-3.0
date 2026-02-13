"""
Inventory Event Handlers
Event-driven workflows for automated inventory management
"""

import logging
from typing import List
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.event_publisher import get_event_publisher
from ....infrastructure.models import Article as ArticleModel
from ..domain.entities import Article
from ...shared.events.inventory_events import (
    StockLevelChangedEvent,
    LowStockAlertEvent,
    StockOutEvent,
    ReplenishmentNeededEvent,
    StockMovementRecordedEvent
)

logger = logging.getLogger(__name__)


class InventoryEventHandlers:
    """Handles inventory-related domain events."""

    def __init__(self, db: Session):
        self.db = db
        self.event_publisher = get_event_publisher()

    async def handle_stock_movement_recorded(self, event: StockMovementRecordedEvent) -> None:
        """Handle stock movement recorded events."""
        try:
            # Check for low stock alerts
            await self._check_low_stock_alert(event.article_id, event.tenant_id)

            # Check for stock out conditions
            await self._check_stock_out_alert(event.article_id, event.tenant_id)

            # Publish stock level changed event
            stock_change_event = StockLevelChangedEvent(
                aggregate_id=event.article_id,
                timestamp=event.timestamp,
                event_id=f"stock-changed-{event.movement_id}",
                article_id=event.article_id,
                warehouse_id=event.warehouse_id,
                previous_stock=event.previous_stock,
                new_stock=event.new_stock,
                change_quantity=event.quantity,
                movement_type=event.movement_type,
                reference_number=event.reference_number
            )

            await self.event_publisher.publish(stock_change_event)

        except Exception as e:
            logger.error(f"Error handling stock movement event: {e}")

    async def _check_low_stock_alert(self, article_id: str, tenant_id: str) -> None:
        """Check if article is below minimum stock and trigger alert."""
        article = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.id == article_id,
                ArticleModel.tenant_id == tenant_id
            )
            .first()
        )

        if not article or not article.min_stock:
            return

        current_stock = article.current_stock or 0
        if current_stock < article.min_stock:
            # Trigger low stock alert
            alert_event = LowStockAlertEvent(
                aggregate_id=article_id,
                timestamp=article.updated_at,
                event_id=f"low-stock-{article_id}",
                article_id=article_id,
                article_number=article.article_number,
                article_name=article.name,
                current_stock=current_stock,
                min_stock=article.min_stock,
                warehouse_id="",  # Would need warehouse-specific tracking
                tenant_id=tenant_id
            )

            await self.event_publisher.publish(alert_event)

            # Also trigger replenishment suggestion
            suggested_quantity = (article.max_stock or article.min_stock * 2) - current_stock
            priority = self._calculate_replenishment_priority(current_stock, article.min_stock)

            replenishment_event = ReplenishmentNeededEvent(
                aggregate_id=article_id,
                timestamp=article.updated_at,
                event_id=f"replenish-{article_id}",
                article_id=article_id,
                article_number=article.article_number,
                article_name=article.name,
                current_stock=current_stock,
                min_stock=article.min_stock,
                suggested_quantity=suggested_quantity,
                priority=priority,
                supplier_number=article.supplier_number,
                tenant_id=tenant_id
            )

            await self.event_publisher.publish(replenishment_event)

    async def _check_stock_out_alert(self, article_id: str, tenant_id: str) -> None:
        """Check if article is out of stock and trigger alert."""
        article = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.id == article_id,
                ArticleModel.tenant_id == tenant_id
            )
            .first()
        )

        if not article:
            return

        current_stock = article.current_stock or 0
        if current_stock <= 0:
            # Trigger stock out alert
            out_event = StockOutEvent(
                aggregate_id=article_id,
                timestamp=article.updated_at,
                event_id=f"stock-out-{article_id}",
                article_id=article_id,
                article_number=article.article_number,
                article_name=article.name,
                warehouse_id="",  # Would need warehouse-specific tracking
                tenant_id=tenant_id
            )

            await self.event_publisher.publish(out_event)

    def _calculate_replenishment_priority(self, current_stock: float, min_stock: float) -> int:
        """Calculate replenishment priority (1-5, 5 being highest)."""
        if current_stock <= 0:
            return 5  # Critical - out of stock
        elif current_stock < min_stock * 0.5:
            return 4  # Very urgent
        elif current_stock < min_stock:
            return 3  # Urgent
        elif current_stock < min_stock * 1.5:
            return 2  # Soon
        else:
            return 1  # Normal


# Event handler registration
async def register_inventory_event_handlers():
    """Register all inventory event handlers."""
    # This would be called during application startup
    # For now, handlers are called directly from services
    pass


# Notification handlers for external integrations
class InventoryNotificationHandlers:
    """Handles notifications for inventory events."""

    async def handle_low_stock_alert(self, event: LowStockAlertEvent) -> None:
        """Send notifications for low stock alerts."""
        # Implementation would integrate with notification service
        logger.info(f"Low stock alert: {event.article_name} ({event.article_number}) - Current: {event.current_stock}, Min: {event.min_stock}")

    async def handle_stock_out(self, event: StockOutEvent) -> None:
        """Send notifications for stock out events."""
        # Implementation would integrate with notification service
        logger.warning(f"Stock out alert: {event.article_name} ({event.article_number}) is out of stock")

    async def handle_replenishment_needed(self, event: ReplenishmentNeededEvent) -> None:
        """Handle replenishment suggestions."""
        # Could trigger automated purchase orders or notifications
        logger.info(f"Replenishment needed: {event.article_name} - Suggest ordering {event.suggested_quantity} units (Priority: {event.priority})")