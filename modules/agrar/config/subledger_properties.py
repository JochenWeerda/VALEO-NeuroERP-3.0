"""
Subledger-Systemeigenschaften.
Workflow: Kreditorische Debitoren, Jahresabschluss, Geschäftsmodell → Subledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SubledgerType(str, Enum):
    """
    Subledger-Buckets für Erzeuger-Salden.
    Statt 26xxxx Nebenkonten pro Landwirt: 1 Business Partner, mehrere Buckets.
    """
    # Rohwaren-Verbindlichkeit (stehen gelassene Gutschriften)
    AP_PRODUCER_CLEARING = "AP_PRODUCER_CLEARING"
    # Erzeuger-Verrechnung
    SETTLEMENT_VERRECHNUNG = "SETTLEMENT_VERRECHNUNG"
    # Fremdware Lager
    STORAGE = "STORAGE"
    # Betriebsmittel-Forderungen
    AR = "AR"
    # Erhaltene Anzahlungen
    ADVANCE_PAYMENTS = "ADVANCE_PAYMENTS"
    # Zinsen
    INTEREST = "INTEREST"


@dataclass
class SubledgerAccountMapping:
    """SKR03-Konten-Mapping für Subledger-Buckets."""
    ar_account: str = "1400"  # Debitoren-Sammelkonto (Forderungen)
    creditor_debtor_account: str = "1415"  # Erhaltene Anzahlungen / Guthaben (kreditorische Debitoren)
    storage_account: str = "3300"  # Fremdware Lager
    ap_producer_account: str = "1600"  # Verbindlichkeiten aus Lieferungen (Kreditoren)
    interest_account: str = "2690"  # Zinsen

    @classmethod
    def from_dict(cls, d: dict) -> SubledgerAccountMapping:
        return cls(
            ar_account=d.get("ar_account", "1400"),
            creditor_debtor_account=d.get("creditor_debtor_account", "1415"),
            storage_account=d.get("storage_account", "3300"),
            ap_producer_account=d.get("ap_producer_account", "1600"),
            interest_account=d.get("interest_account", "2690"),
        )


DEFAULT_ACCOUNT_MAPPING = SubledgerAccountMapping()


ACCEPTANCE_MODE_SUBLEDGER_MAP = {
    "PURCHASE_AT_DELIVERY_PTBF": SubledgerType.AP_PRODUCER_CLEARING,
    "STORAGE_ONLY": SubledgerType.STORAGE,
    "ADVANCE_ON_STORAGE": SubledgerType.ADVANCE_PAYMENTS,
}


def get_subledger_for_acceptance_mode(acceptance_mode: str) -> SubledgerType:
    """
    Ermittelt den Subledger-Bucket für ein Geschäftsmodell.
    """
    return ACCEPTANCE_MODE_SUBLEDGER_MAP.get(
        acceptance_mode,
        SubledgerType.AP_PRODUCER_CLEARING,
    )


def get_account_for_subledger(
    subledger: SubledgerType,
    mapping: Optional[SubledgerAccountMapping] = None,
) -> str:
    """
    Ermittelt das Hauptkonto (SKR03) für einen Subledger-Bucket.
    """
    m = mapping or DEFAULT_ACCOUNT_MAPPING
    return {
        SubledgerType.AP_PRODUCER_CLEARING: m.ap_producer_account,
        SubledgerType.SETTLEMENT_VERRECHNUNG: m.ar_account,
        SubledgerType.STORAGE: m.storage_account,
        SubledgerType.AR: m.ar_account,
        SubledgerType.ADVANCE_PAYMENTS: m.creditor_debtor_account,
        SubledgerType.INTEREST: m.interest_account,
    }.get(subledger, m.ar_account)


# System-Property-Keys für tenant-spezifische Overrides
SYSTEM_PROPERTY_KEYS = [
    "SUBLEDGER_AR_ACCOUNT",
    "SUBLEDGER_CREDITOR_DEBITOR_ACCOUNT",
    "SUBLEDGER_STORAGE_ACCOUNT",
    "SUBLEDGER_AP_PRODUCER_ACCOUNT",
    "SUBLEDGER_INTEREST_ACCOUNT",
    "STICHTAG_UMGLIEDERUNG_ENABLED",
    "STICHTAG_UMGLIEDERUNG_AUTO_REVERSAL",
    "ACCEPTANCE_MODE_DEFAULT",
]


def build_account_mapping_from_properties(properties: dict[str, str]) -> SubledgerAccountMapping:
    """
    Erstellt SubledgerAccountMapping aus tenant-spezifischen Systemeigenschaften.
    """
    return SubledgerAccountMapping(
        ar_account=properties.get("SUBLEDGER_AR_ACCOUNT", "1400"),
        creditor_debtor_account=properties.get("SUBLEDGER_CREDITOR_DEBITOR_ACCOUNT", "1415"),
        storage_account=properties.get("SUBLEDGER_STORAGE_ACCOUNT", "3300"),
        ap_producer_account=properties.get("SUBLEDGER_AP_PRODUCER_ACCOUNT", "1600"),
        interest_account=properties.get("SUBLEDGER_INTEREST_ACCOUNT", "2690"),
    )
