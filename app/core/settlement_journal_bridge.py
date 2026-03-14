"""
Settlement → Finance Journal-Entry Bridge — Wave 21 AP2

GoBD-konforme Erzeugung eines JournalEntryDraft aus einem genehmigten Settlement.
Der Draft traegt vollstaendige Soll/Haben-Saetze, Gegenkonto, Buchungsdatum
und Prozessreferenz und kann direkt in die FiBu uebergeben werden.

Architektur-Hinweis: Diese Bridge erzeugt NUR einen Draft (noch keine DB-Schreiboperation).
Die tatsaechliche Verbuchung erfolgt durch den FiBu-Layer (app/api/v1/endpoints/finance_actions.py).
Damit bleibt die Core-Schicht frei von Datenbankabhaengigkeiten.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional


JOURNAL_SCHEMA_VERSION = 1


class JournalSide(str, Enum):
    SOLL = "SOLL"    # Debit
    HABEN = "HABEN"  # Credit


@dataclass
class JournalLine:
    """Eine einzelne Buchungszeile (Soll oder Haben)."""

    konto: str               # Sachkontonummer (z.B. "1400" Lieferantenforderungen)
    konto_name: str
    side: JournalSide
    amount: Decimal          # immer positiv; Richtung durch side bestimmt
    currency: str = "EUR"
    cost_center: Optional[str] = None
    note: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "konto": self.konto,
            "konto_name": self.konto_name,
            "side": self.side.value,
            "amount": str(self.amount),
            "currency": self.currency,
            "cost_center": self.cost_center,
            "note": self.note,
        }


@dataclass
class JournalEntryDraft:
    """
    Entwurf eines FiBu-Buchungssatzes aus einem genehmigten Settlement.

    GoBD-Pflichtfelder (§ 146 AO, GoBD Rz. 83-86):
    - beleg_nr: Belegnummer (aus Settlement-ID abgeleitet)
    - buchungsdatum: Buchungsdatum
    - lines: Soll/Haben-Saetze (doppelte Buchfuehrung)
    - settlement_id: Referenz auf das Quell-Settlement
    - process_definition_key: Prozessreferenz (GoBD Rz. 102)
    """

    draft_id: str
    settlement_id: str
    tenant_id: str
    beleg_nr: str
    buchungsdatum: str                    # ISO-8601
    buchungstext: str
    lines: list[JournalLine] = field(default_factory=list)
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    audit_chain_ref: Optional[str] = None   # head_hash aus Wave-20 Audit-Kette
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: int = JOURNAL_SCHEMA_VERSION

    @property
    def soll_total(self) -> Decimal:
        return sum(l.amount for l in self.lines if l.side == JournalSide.SOLL)

    @property
    def haben_total(self) -> Decimal:
        return sum(l.amount for l in self.lines if l.side == JournalSide.HABEN)

    @property
    def balanced(self) -> bool:
        """Doppelte Buchfuehrung: Soll == Haben."""
        return self.soll_total == self.haben_total

    def as_dict(self) -> dict:
        return {
            "draft_id": self.draft_id,
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "beleg_nr": self.beleg_nr,
            "buchungsdatum": self.buchungsdatum,
            "buchungstext": self.buchungstext,
            "soll_total": str(self.soll_total),
            "haben_total": str(self.haben_total),
            "balanced": self.balanced,
            "lines": [l.as_dict() for l in self.lines],
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "audit_chain_ref": self.audit_chain_ref,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Standard-Kontenrahmen (SKR03-Anlehnung, landhandelsspezifisch)
# ---------------------------------------------------------------------------

_KONTO_LIEFERANTENVERBINDLICHKEIT = ("1600", "Lieferantenverbindlichkeiten Agrar")
_KONTO_WAREN_EINGANG = ("5200", "Wareneinkauf Agrar")
_KONTO_VORSTEUER = ("1576", "Abziehbare Vorsteuer 19%")
_KONTO_ABZUEGE = ("5280", "Abzuege Trocknung/Reinigung")


def build_settlement_journal_draft(
    *,
    settlement_id: str,
    tenant_id: str,
    gross_amount: Decimal,
    total_deductions: Decimal,
    net_amount: Decimal,
    currency: str = "EUR",
    buchungsdatum: Optional[str] = None,
    audit_chain_ref: Optional[str] = None,
    gegenkonto: str = _KONTO_LIEFERANTENVERBINDLICHKEIT[0],
    vat_rate: Decimal = Decimal("0"),   # 0 = Agrar-Regelbesteuerung ohne USt (§24 UStG)
) -> JournalEntryDraft:
    """
    Erzeugt einen ausgewogenen JournalEntryDraft fuer ein Settlement.

    Buchungslogik (ohne USt / §24 UStG Agrar-Pauschalierung):
      SOLL  5200 Wareneinkauf Agrar              gross_amount
      HABEN 5280 Abzuege Trocknung/Reinigung     total_deductions  (wenn > 0)
      HABEN 1600 Lieferantenverbindlichkeiten     net_amount

    Mit USt (Regelbesteuerung):
      SOLL  5200 Wareneinkauf                     gross_amount
      SOLL  1576 Vorsteuer                        vat_amount
      HABEN 5280 Abzuege                          total_deductions  (wenn > 0)
      HABEN 1600 Lieferantenverbindlichkeiten     net_amount + vat_amount
    """
    draft_id = f"JE-DRAFT-{settlement_id}"
    beleg_nr = f"BLG-{settlement_id}"
    bdate = buchungsdatum or date.today().isoformat()
    buchungstext = f"Agrar-Abrechnung {settlement_id}"

    lines: list[JournalLine] = []

    # Soll: Wareneinkauf
    lines.append(JournalLine(
        konto=_KONTO_WAREN_EINGANG[0],
        konto_name=_KONTO_WAREN_EINGANG[1],
        side=JournalSide.SOLL,
        amount=gross_amount,
        currency=currency,
        note="Rohwareneinkauf brutto",
    ))

    # Optionale USt (Regelbesteuerung)
    vat_amount = Decimal("0.00")
    if vat_rate > Decimal("0"):
        vat_amount = (net_amount * vat_rate / Decimal("100")).quantize(
            Decimal("0.01")
        )
        lines.append(JournalLine(
            konto=_KONTO_VORSTEUER[0],
            konto_name=_KONTO_VORSTEUER[1],
            side=JournalSide.SOLL,
            amount=vat_amount,
            currency=currency,
            note=f"Vorsteuer {vat_rate}%",
        ))

    # Haben: Abzuege (Trocknung/Reinigung)
    if total_deductions > Decimal("0"):
        lines.append(JournalLine(
            konto=_KONTO_ABZUEGE[0],
            konto_name=_KONTO_ABZUEGE[1],
            side=JournalSide.HABEN,
            amount=total_deductions,
            currency=currency,
            note="Abzuege Trocknung/Reinigung/Sonstiges",
        ))

    # Haben: Lieferantenverbindlichkeit (net + ggf. USt)
    lines.append(JournalLine(
        konto=gegenkonto,
        konto_name=_KONTO_LIEFERANTENVERBINDLICHKEIT[1],
        side=JournalSide.HABEN,
        amount=net_amount + vat_amount,
        currency=currency,
        note="Nettoforderung Lieferant",
    ))

    return JournalEntryDraft(
        draft_id=draft_id,
        settlement_id=settlement_id,
        tenant_id=tenant_id,
        beleg_nr=beleg_nr,
        buchungsdatum=bdate,
        buchungstext=buchungstext,
        lines=lines,
        audit_chain_ref=audit_chain_ref,
    )
