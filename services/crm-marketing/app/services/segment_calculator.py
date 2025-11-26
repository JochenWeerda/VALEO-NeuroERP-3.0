"""Segment calculation engine."""

from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any
import httpx
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Segment, SegmentRule, SegmentMember, SegmentType, RuleOperator, LogicalOperator
from app.config.settings import settings


class SegmentCalculator:
    """Calculates segment members based on rules."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crm_core_url = "http://localhost:5700"  # TODO: Get from config
    
    async def _fetch_contacts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Fetch all contacts from crm-core service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.crm_core_url}/api/v1/contacts",
                    params={"tenant_id": tenant_id},
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json() or []
        except Exception as e:
            print(f"Error fetching contacts: {e}")
            return []
        return []
    
    async def _evaluate_rule(self, rule: SegmentRule, contact: Dict[str, Any]) -> bool:
        """Evaluate a single rule against a contact."""
        field_value = self._get_field_value(contact, rule.field)
        rule_value = rule.value
        
        if rule.operator == RuleOperator.EQUALS:
            return str(field_value) == str(rule_value.get('value', ''))
        elif rule.operator == RuleOperator.NOT_EQUALS:
            return str(field_value) != str(rule_value.get('value', ''))
        elif rule.operator == RuleOperator.CONTAINS:
            return str(rule_value.get('value', '')).lower() in str(field_value).lower()
        elif rule.operator == RuleOperator.NOT_CONTAINS:
            return str(rule_value.get('value', '')).lower() not in str(field_value).lower()
        elif rule.operator == RuleOperator.STARTS_WITH:
            return str(field_value).startswith(str(rule_value.get('value', '')))
        elif rule.operator == RuleOperator.ENDS_WITH:
            return str(field_value).endswith(str(rule_value.get('value', '')))
        elif rule.operator == RuleOperator.GREATER_THAN:
            try:
                return float(field_value) > float(rule_value.get('value', 0))
            except (ValueError, TypeError):
                return False
        elif rule.operator == RuleOperator.LESS_THAN:
            try:
                return float(field_value) < float(rule_value.get('value', 0))
            except (ValueError, TypeError):
                return False
        elif rule.operator == RuleOperator.GREATER_EQUAL:
            try:
                return float(field_value) >= float(rule_value.get('value', 0))
            except (ValueError, TypeError):
                return False
        elif rule.operator == RuleOperator.LESS_EQUAL:
            try:
                return float(field_value) <= float(rule_value.get('value', 0))
            except (ValueError, TypeError):
                return False
        elif rule.operator == RuleOperator.IN:
            values = rule_value.get('values', [])
            return str(field_value) in [str(v) for v in values]
        elif rule.operator == RuleOperator.NOT_IN:
            values = rule_value.get('values', [])
            return str(field_value) not in [str(v) for v in values]
        elif rule.operator == RuleOperator.IS_NULL:
            return field_value is None or field_value == ''
        elif rule.operator == RuleOperator.IS_NOT_NULL:
            return field_value is not None and field_value != ''
        elif rule.operator == RuleOperator.BETWEEN:
            min_val = rule_value.get('min')
            max_val = rule_value.get('max')
            try:
                val = float(field_value)
                return (min_val is None or val >= float(min_val)) and (max_val is None or val <= float(max_val))
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _get_field_value(self, contact: Dict[str, Any], field_path: str) -> Any:
        """Get field value from contact using dot notation (e.g., 'contact.email_domain')."""
        parts = field_path.split('.')
        value = contact
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    async def _evaluate_rules(self, rules: List[SegmentRule], contact: Dict[str, Any]) -> bool:
        """Evaluate all rules with logical operators."""
        if not rules:
            return True
        
        result = await self._evaluate_rule(rules[0], contact)
        
        for i in range(1, len(rules)):
            rule = rules[i]
            rule_result = await self._evaluate_rule(rule, contact)
            
            if rule.logical_operator == LogicalOperator.AND:
                result = result and rule_result
            elif rule.logical_operator == LogicalOperator.OR:
                result = result or rule_result
            else:
                # Default to AND if not specified
                result = result and rule_result
        
        return result
    
    async def calculate_segment(self, segment_id: UUID, force_full: bool = False):
        """
        Calculate members for a dynamic segment.
        
        Steps:
        1. Fetch all contacts from crm-core service
        2. Evaluate rules against contact data
        3. Add/remove members accordingly
        """
        segment = await self.db.get(Segment, segment_id)
        if not segment or segment.type != SegmentType.DYNAMIC:
            return
        
        # Fetch rules
        rules_stmt = select(SegmentRule).where(
            SegmentRule.segment_id == segment_id
        ).order_by(SegmentRule.order)
        rules_result = await self.db.execute(rules_stmt)
        rules = list(rules_result.scalars().all())
        
        if not rules:
            # No rules, clear all members
            await self.db.execute(
                delete(SegmentMember).where(
                    and_(
                        SegmentMember.segment_id == segment_id,
                        SegmentMember.removed_at.is_(None)
                    )
                )
            )
            segment.member_count = 0
            segment.last_calculated_at = datetime.utcnow()
            await self.db.commit()
            return
        
        # Fetch contacts
        contacts = await self._fetch_contacts(segment.tenant_id)
        
        # Get existing members
        existing_members_stmt = select(SegmentMember).where(
            and_(
                SegmentMember.segment_id == segment_id,
                SegmentMember.removed_at.is_(None)
            )
        )
        existing_members_result = await self.db.execute(existing_members_stmt)
        existing_members = {str(member.contact_id): member for member in existing_members_result.scalars().all()}
        
        # Evaluate rules for each contact
        matching_contact_ids = []
        for contact in contacts:
            contact_id = contact.get('id')
            if not contact_id:
                continue
            
            if await self._evaluate_rules(rules, contact):
                matching_contact_ids.append(UUID(contact_id))
        
        # Add new members
        for contact_id in matching_contact_ids:
            contact_id_str = str(contact_id)
            if contact_id_str not in existing_members:
                member = SegmentMember(
                    segment_id=segment_id,
                    contact_id=contact_id,
                    added_by="system"
                )
                self.db.add(member)
        
        # Remove members that no longer match
        for contact_id_str, member in existing_members.items():
            if UUID(contact_id_str) not in matching_contact_ids:
                member.removed_at = datetime.utcnow()
                member.removed_by = "system"
        
        # Update segment
        segment.member_count = len(matching_contact_ids)
        segment.last_calculated_at = datetime.utcnow()
        
        await self.db.commit()
