"""Event publishing service for CRM Sales."""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

# TODO: Integrate with actual event bus (RabbitMQ/Kafka)
# For now, this is a stub that logs events


class EventPublisher:
    """Publishes domain events for CRM Sales."""
    
    def __init__(self):
        """Initialize event publisher."""
        # TODO: Initialize event bus connection
        pass
    
    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event_type: Event type (e.g., 'crm.opportunity.created')
            payload: Event payload
        """
        # TODO: Publish to actual event bus
        # For now, just log
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(f"[EVENT] {event_type}: {json.dumps(event, default=str)}")
        # In production: await self.event_bus.publish(event_type, event)
    
    async def publish_opportunity_created(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        number: str,
        name: str,
        amount: Optional[float],
        stage: str,
        owner_id: Optional[str],
    ) -> None:
        """Publish opportunity created event."""
        await self.publish(
            "crm.opportunity.created",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "number": number,
                "name": name,
                "amount": amount,
                "stage": stage,
                "owner_id": owner_id,
            },
        )
    
    async def publish_opportunity_updated(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        changes: Dict[str, Any],
        changed_by: Optional[str],
    ) -> None:
        """Publish opportunity updated event."""
        await self.publish(
            "crm.opportunity.updated",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "changes": changes,
                "changed_by": changed_by,
            },
        )
    
    async def publish_opportunity_stage_changed(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        old_stage: str,
        new_stage: str,
        changed_by: Optional[str],
    ) -> None:
        """Publish opportunity stage changed event."""
        await self.publish(
            "crm.opportunity.stage-changed",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "old_stage": old_stage,
                "new_stage": new_stage,
                "changed_by": changed_by,
            },
        )
    
    async def publish_opportunity_won(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        amount: Optional[float],
        actual_close_date: Optional[datetime],
        won_by: Optional[str],
    ) -> None:
        """Publish opportunity won event."""
        await self.publish(
            "crm.opportunity.won",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "amount": amount,
                "actual_close_date": actual_close_date.isoformat() if actual_close_date else None,
                "won_by": won_by,
            },
        )
    
    async def publish_opportunity_lost(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        amount: Optional[float],
        lost_reason: Optional[str],
        lost_by: Optional[str],
    ) -> None:
        """Publish opportunity lost event."""
        await self.publish(
            "crm.opportunity.lost",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "amount": amount,
                "lost_reason": lost_reason,
                "lost_by": lost_by,
            },
        )
    
    async def publish_opportunity_deleted(
        self,
        opportunity_id: UUID,
        tenant_id: str,
        deleted_by: Optional[str],
    ) -> None:
        """Publish opportunity deleted event."""
        await self.publish(
            "crm.opportunity.deleted",
            {
                "opportunity_id": str(opportunity_id),
                "tenant_id": tenant_id,
                "deleted_by": deleted_by,
            },
        )


# Singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get singleton event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
