"""
Compliance Monitor Background Worker
Periodically checks compliance status and generates alerts
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.agents.workflows.compliance_copilot import check_compliance

logger = logging.getLogger(__name__)


class ComplianceMonitorWorker:
    """Background worker for automated compliance monitoring."""
    
    def __init__(self, interval_seconds: int = 3600):  # Every hour
        self.interval = interval_seconds
        self.running = False
        self.last_check: Optional[datetime] = None
    
    async def start(self) -> None:
        """Start the compliance monitor worker."""
        self.running = True
        logger.info(
            f"Compliance Monitor started (interval: {self.interval}s)"
        )
        
        while self.running:
            try:
                await self._run_compliance_checks()
            except Exception as e:
                logger.error(
                    f"Compliance monitor error: {e}",
                    exc_info=True
                )
            
            await asyncio.sleep(self.interval)
        
        logger.info("Compliance Monitor stopped")
    
    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
    
    async def _run_compliance_checks(self) -> None:
        """Run compliance checks on all entities."""
        db: Session = SessionLocal()
        
        try:
            from app.infrastructure.models import Customer, Article
            
            # Check all customers
            customers = db.query(Customer).filter(
                Customer.is_active == True  # noqa: E712
            ).limit(100).all()
            
            customer_violations = []
            
            for customer in customers:
                result = await check_compliance(
                    entity_type="customer",
                    entity_id=customer.id,
                    entity_data={
                        "name": customer.company_name,
                        "psm_sachkundenachweis": (
                            customer.tax_id is not None
                        ),  # Simplified check
                    }
                )
                
                if result["violations"]:
                    customer_violations.extend(result["violations"])
            
            # Check high-risk articles
            articles = db.query(Article).filter(
                Article.category.in_(["Düngemittel", "Pflanzenschutz"])
            ).limit(100).all()
            
            article_violations = []
            
            for article in articles:
                result = await check_compliance(
                    entity_type="article",
                    entity_id=article.id,
                    entity_data={
                        "name": article.name,
                        "category": article.category,
                        "explosivstoff_konform": True  # TODO: Real check
                    }
                )
                
                if result["violations"]:
                    article_violations.extend(result["violations"])
            
            self.last_check = datetime.utcnow()
            
            total_violations = (
                len(customer_violations) + len(article_violations)
            )
            
            if total_violations > 0:
                logger.warning(
                    f"⚠️ Compliance check found {total_violations} violations"
                )
                # TODO: Send alerts via Event-Bus
            else:
                logger.info("✅ All compliance checks passed")
        
        finally:
            db.close()


# Global worker instance
_compliance_worker: Optional[ComplianceMonitorWorker] = None


def get_compliance_worker() -> ComplianceMonitorWorker:
    """Get the global compliance worker instance."""
    global _compliance_worker
    if _compliance_worker is None:
        _compliance_worker = ComplianceMonitorWorker()
    return _compliance_worker


async def start_compliance_monitor() -> None:
    """Start the compliance monitor worker."""
    worker = get_compliance_worker()
    await worker.start()

