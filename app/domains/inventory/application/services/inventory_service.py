"""
Inventory Service
Core business logic for inventory management
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.models import Article as ArticleModel, Warehouse as WarehouseModel, StockMovement as StockMovementModel
from app.domains.inventory.domain.entities import Article, Warehouse, StockMovement


class InventoryService:
    """Service for inventory management operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_article_stock(self, article_id: str, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current stock levels for an article."""
        query = self.db.query(ArticleModel).filter(ArticleModel.id == article_id)

        if warehouse_id:
            # Get stock for specific warehouse
            article = query.first()
            if not article:
                return {"current_stock": 0, "available_stock": 0, "reserved_stock": 0}

            # For now, return total stock (warehouse-specific stock tracking would need additional table)
            return {
                "current_stock": float(article.current_stock or 0),
                "available_stock": float(article.available_stock or 0),
                "reserved_stock": float(article.reserved_stock or 0)
            }
        else:
            # Get total stock across all warehouses
            article = query.first()
            if not article:
                return {"current_stock": 0, "available_stock": 0, "reserved_stock": 0}

            return {
                "current_stock": float(article.current_stock or 0),
                "available_stock": float(article.available_stock or 0),
                "reserved_stock": float(article.reserved_stock or 0)
            }

    def check_low_stock_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Check for articles that are below minimum stock levels."""
        articles = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == tenant_id,
                ArticleModel.is_active == True,
                ArticleModel.min_stock.isnot(None),
                ArticleModel.current_stock < ArticleModel.min_stock
            )
            .all()
        )

        alerts = []
        for article in articles:
            alerts.append({
                "article_id": article.id,
                "article_number": article.article_number,
                "name": article.name,
                "current_stock": float(article.current_stock or 0),
                "min_stock": float(article.min_stock or 0),
                "deficit": float((article.min_stock or 0) - (article.current_stock or 0))
            })

        return alerts

    def process_stock_movement(
        self,
        article_id: str,
        warehouse_id: str,
        movement_type: str,
        quantity: Decimal,
        unit_cost: Optional[Decimal] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        tenant_id: str = None
    ) -> StockMovement:
        """Process a stock movement and update article stock levels."""

        # Get current article
        article = self.db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
        if not article:
            raise ValueError(f"Article {article_id} not found")

        # Get current warehouse
        warehouse = self.db.query(WarehouseModel).filter(WarehouseModel.id == warehouse_id).first()
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        previous_stock = article.current_stock or Decimal(0)

        # Calculate new stock based on movement type
        if movement_type in ['in', 'adjustment'] and quantity > 0:
            new_stock = previous_stock + quantity
        elif movement_type in ['out', 'adjustment'] and quantity < 0:
            new_stock = previous_stock + quantity  # quantity is negative
        elif movement_type == 'transfer':
            # For transfers, quantity can be positive (incoming) or negative (outgoing)
            new_stock = previous_stock + quantity
        else:
            raise ValueError(f"Invalid movement type: {movement_type}")

        # Ensure stock doesn't go negative for outbound movements
        if movement_type == 'out' and new_stock < 0:
            raise ValueError(f"Insufficient stock. Current: {previous_stock}, Requested: {abs(quantity)}")

        # Calculate total cost if unit cost provided
        total_cost = None
        if unit_cost is not None:
            total_cost = abs(quantity) * unit_cost

        # Create stock movement record
        movement = StockMovementModel(
            id=str(uuid.uuid4()),
            article_id=article_id,
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            reference_number=reference_number,
            notes=notes,
            previous_stock=previous_stock,
            new_stock=new_stock,
            total_cost=total_cost,
            tenant_id=tenant_id or article.tenant_id
        )

        # Update article stock
        article.current_stock = new_stock
        article.available_stock = new_stock - (article.reserved_stock or Decimal(0))
        article.updated_at = datetime.utcnow()

        # Save changes
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        # Publish event for stock movement
        from app.core.event_publisher import get_event_publisher
        from app.domains.shared.events.inventory_events import StockMovementRecordedEvent

        event_publisher = get_event_publisher()
        event = StockMovementRecordedEvent(
            aggregate_id=article_id,
            timestamp=datetime.utcnow(),
            event_id=f"movement-{movement.id}",
            movement_id=movement.id,
            article_id=article_id,
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reference_number=reference_number,
            tenant_id=tenant_id
        )

        # Publish event asynchronously (fire and forget for now)
        import asyncio
        asyncio.create_task(event_publisher.publish(event))

        return StockMovement.model_validate(movement)

    def get_stock_movements(
        self,
        article_id: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        movement_type: Optional[str] = None,
        tenant_id: str = None,
        limit: int = 50
    ) -> List[StockMovement]:
        """Get stock movement history with optional filters."""

        query = self.db.query(StockMovementModel).filter(StockMovementModel.tenant_id == tenant_id)

        if article_id:
            query = query.filter(StockMovementModel.article_id == article_id)
        if warehouse_id:
            query = query.filter(StockMovementModel.warehouse_id == warehouse_id)
        if movement_type:
            query = query.filter(StockMovementModel.movement_type == movement_type)

        movements = query.order_by(StockMovementModel.created_at.desc()).limit(limit).all()

        return [StockMovement.model_validate(movement) for movement in movements]

    def calculate_inventory_value(self, tenant_id: str) -> Dict[str, Any]:
        """Calculate total inventory value and statistics."""

        articles = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == tenant_id,
                ArticleModel.is_active == True
            )
            .all()
        )

        total_value = Decimal(0)
        total_items = 0
        low_stock_items = 0

        for article in articles:
            if article.current_stock and article.current_stock > 0:
                # Use sales price for valuation (could also use purchase price)
                if article.sales_price:
                    total_value += article.current_stock * article.sales_price
                total_items += 1

            # Check for low stock
            if article.min_stock and article.current_stock and article.current_stock < article.min_stock:
                low_stock_items += 1

        return {
            "total_value": float(total_value),
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "currency": "EUR"  # Could be made configurable per tenant
        }