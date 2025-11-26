"""Route-Module fuer das Finance Fibu-Gateway."""

from . import approval_rules, chart_of_accounts, journal_entries, op_management

__all__ = [
    "approval_rules",
    "chart_of_accounts",
    "journal_entries",
    "op_management",
]
