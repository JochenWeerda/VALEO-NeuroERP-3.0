"""CRM domain entities."""

from .customer import Customer
from .lead import Lead, LeadStatus

__all__ = ['Customer', 'Lead', 'LeadStatus']

