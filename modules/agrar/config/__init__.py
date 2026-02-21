"""
Agrar-Modul Konfiguration.
Subledger-Systemeigenschaften, Konten-Mapping, Geschäftsmodell → Subledger.
"""

from .subledger_properties import (
    SubledgerType,
    SubledgerAccountMapping,
    ACCEPTANCE_MODE_SUBLEDGER_MAP,
    DEFAULT_ACCOUNT_MAPPING,
    get_subledger_for_acceptance_mode,
    get_account_for_subledger,
)

__all__ = [
    "SubledgerType",
    "SubledgerAccountMapping",
    "ACCEPTANCE_MODE_SUBLEDGER_MAP",
    "DEFAULT_ACCOUNT_MAPPING",
    "get_subledger_for_acceptance_mode",
    "get_account_for_subledger",
]
