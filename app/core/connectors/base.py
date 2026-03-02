"""
FIBU Connector – Basis-DTOs und Parser-Interface.
Einheitliches normalisiertes Format für Lohn (PAYROLL) und VALEO Suite Anlagen / Asset Ledger (ASSET_LEDGER).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class NormalizedLine:
    """Eine Buchungszeile (Soll oder Haben)."""
    account: str  # Kontonummer oder account_id
    dc: str  # "D" Soll, "C" Haben
    amount: Decimal
    tax_code: Optional[str] = None
    cost_center: Optional[str] = None
    cost_object: Optional[str] = None
    currency: str = "EUR"


@dataclass
class NormalizedItem:
    """Ein normalisierter Beleg (ein Datensatz aus Import)."""
    booking_date: str  # YYYY-MM-DD
    document_no: str
    text: str
    lines: List[NormalizedLine]
    # Asset Ledger optional
    asset_no: Optional[str] = None
    asset_name: Optional[str] = None
    posting_type: Optional[str] = None  # depr, acq, disposal


def validate_item_balance(item: NormalizedItem) -> Optional[str]:
    """Prüft Soll=Haben. Gibt Fehlermeldung zurück oder None."""
    total_d = sum(l.amount for l in item.lines if l.dc == "D")
    total_c = sum(l.amount for l in item.lines if l.dc == "C")
    if abs(total_d - total_c) > Decimal("0.01"):
        return f"Soll={total_d} != Haben={total_c}"
    return None


class ConnectorParser:
    """Interface für Connector-Parser."""

    def detect(self, raw: bytes, settings: Dict[str, Any]) -> bool:
        """Erkennt, ob die Datei zu diesem Parser passt."""
        raise NotImplementedError

    def parse(self, raw: bytes, settings: Dict[str, Any], mapping: Dict[str, Any]) -> List[NormalizedItem]:
        """Parst die Datei in normalisierte Items."""
        raise NotImplementedError
