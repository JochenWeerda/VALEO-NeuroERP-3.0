"""
Replenishment Service
Handles automated replenishment logic and purchase order suggestions
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.models import Article as ArticleModel
from app.domains.inventory.domain.entities import Article


class ReplenishmentService:
    """Service for automated replenishment and purchase order suggestions."""

    def __init__(self, db: Session):
        self.db = db

    def get_replenishment_suggestions(self, tenant_id: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Generate replenishment suggestions based on stock levels and usage patterns."""

        # Get articles that need replenishment
        articles = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == tenant_id,
                ArticleModel.is_active == True,
                ArticleModel.min_stock.isnot(None)
            )
            .all()
        )

        suggestions = []

        for article in articles:
            current_stock = article.current_stock or Decimal(0)
            min_stock = article.min_stock or Decimal(0)
            max_stock = article.max_stock or min_stock * Decimal(2)  # Default max = 2x min

            # Check if replenishment is needed
            if current_stock < min_stock:
                deficit = min_stock - current_stock
                suggested_quantity = max_stock - current_stock  # Replenish to max level

                # Calculate estimated cost
                estimated_cost = None
                if article.purchase_price:
                    estimated_cost = suggested_quantity * article.purchase_price

                suggestions.append({
                    "article_id": article.id,
                    "article_number": article.article_number,
                    "name": article.name,
                    "current_stock": float(current_stock),
                    "min_stock": float(min_stock),
                    "max_stock": float(max_stock),
                    "deficit": float(deficit),
                    "suggested_quantity": float(suggested_quantity),
                    "unit": article.unit,
                    "estimated_cost": float(estimated_cost) if estimated_cost else None,
                    "currency": article.currency,
                    "supplier_number": article.supplier_number,
                    "priority": self._calculate_priority(current_stock, min_stock, max_stock)
                })

        # Sort by priority (high first)
        suggestions.sort(key=lambda x: x["priority"], reverse=True)

        return suggestions

    def _calculate_priority(self, current: Decimal, min_stock: Decimal, max_stock: Decimal) -> int:
        """Calculate replenishment priority (1-5, 5 being highest)."""

        if current <= 0:
            return 5  # Critical - out of stock
        elif current < min_stock * Decimal(0.5):
            return 4  # Very urgent
        elif current < min_stock:
            return 3  # Urgent
        elif current < min_stock * Decimal(1.5):
            return 2  # Soon
        else:
            return 1  # Normal

    def get_slow_moving_inventory(self, tenant_id: str, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """Identify slow-moving inventory that may need special handling."""

        # This would typically analyze stock movement history
        # For now, return articles with no recent movements (simplified)

        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

        # Get articles with low turnover (simplified logic)
        articles = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == tenant_id,
                ArticleModel.is_active == True,
                ArticleModel.current_stock.isnot(None),
                ArticleModel.current_stock > 0
            )
            .all()
        )

        slow_moving = []
        for article in articles:
            # Calculate stock turnover ratio (simplified)
            # In a real implementation, this would analyze actual movement history
            stock_value = float((article.current_stock or 0) * (article.purchase_price or article.sales_price or 0))

            # Flag as slow moving if stock value is significant but no recent activity
            if stock_value > 1000:  # Configurable threshold
                slow_moving.append({
                    "article_id": article.id,
                    "article_number": article.article_number,
                    "name": article.name,
                    "current_stock": float(article.current_stock or 0),
                    "stock_value": stock_value,
                    "days_since_last_movement": days_threshold,  # Placeholder
                    "category": article.category,
                    "recommendation": "Consider markdown or special promotion"
                })

        return slow_moving

    def generate_purchase_order_suggestions(
        self,
        tenant_id: str,
        supplier_filter: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate purchase order suggestions grouped by supplier."""

        suggestions = self.get_replenishment_suggestions(tenant_id)

        # Group by supplier
        by_supplier = {}
        for suggestion in suggestions:
            supplier = suggestion.get("supplier_number", "Unknown Supplier")

            if supplier_filter and supplier != supplier_filter:
                continue

            if supplier not in by_supplier:
                by_supplier[supplier] = []

            by_supplier[supplier].append(suggestion)

        # Sort items within each supplier by priority
        for supplier_items in by_supplier.values():
            supplier_items.sort(key=lambda x: x["priority"], reverse=True)

        return by_supplier

    def get_inventory_turnover_report(self, tenant_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Generate inventory turnover analysis."""

        # This is a simplified version - real implementation would analyze movement history
        articles = (
            self.db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == tenant_id,
                ArticleModel.is_active == True
            )
            .all()
        )

        total_inventory_value = Decimal(0)
        total_cost_of_goods_sold = Decimal(0)  # Would be calculated from actual sales

        for article in articles:
            if article.current_stock and article.purchase_price:
                total_inventory_value += article.current_stock * article.purchase_price

        # Calculate turnover ratio (simplified)
        if total_inventory_value > 0:
            turnover_ratio = total_cost_of_goods_sold / total_inventory_value
            turnover_days = period_days / float(turnover_ratio) if turnover_ratio > 0 else float('inf')
        else:
            turnover_ratio = 0
            turnover_days = float('inf')

        return {
            "period_days": period_days,
            "total_inventory_value": float(total_inventory_value),
            "total_cogs": float(total_cost_of_goods_sold),
            "turnover_ratio": float(turnover_ratio),
            "turnover_days": turnover_days,
            "analysis_date": datetime.utcnow().isoformat()
        }