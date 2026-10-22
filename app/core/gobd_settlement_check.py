"""
GoBD Settlement-Vollständigkeitsprüfung — Wave 20 AP4

Maschinenlesbare Prüfung ob eine Abrechnung alle GoBD-Pflichtfelder
trägt, bevor sie als GoBD-konformer Buchungsbeleg gilt.

Rechtsgrundlage: §§ 146, 147 AO, GoBD Rz. 83-89, 102-112
(Vollständigkeit, Unveränderbarkeit, Nachvollziehbarkeit von Buchungen)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


GOBD_CHECK_SCHEMA_VERSION = 1


class GoBDViolationCode(str, Enum):
    MISSING_BELEG_NR = "MISSING_BELEG_NR"           # §146 AO: Belegnummer fehlt
    MISSING_BUCHUNGSDATUM = "MISSING_BUCHUNGSDATUM"  # §146 AO: Buchungsdatum fehlt
    MISSING_BETRAG = "MISSING_BETRAG"                # GoBD Rz. 83: Betrag fehlt oder 0
    MISSING_WAEHRUNG = "MISSING_WAEHRUNG"            # GoBD Rz. 83: Waehrung fehlt
    MISSING_GEGENKONTO = "MISSING_GEGENKONTO"        # GoBD Rz. 86: Gegenkonto fehlt
    MISSING_AUDIT_HASH = "MISSING_AUDIT_HASH"        # GoBD Rz. 108: kein Hash vorhanden
    MISSING_TENANT_ID = "MISSING_TENANT_ID"          # Mandant nicht zuordenbar
    MISSING_CUSTOMER_ID = "MISSING_CUSTOMER_ID"      # Lieferant/Kunde nicht zuordenbar
    MISSING_PROCESS_REF = "MISSING_PROCESS_REF"      # Prozessreferenz fehlt
    INVALID_STATUS = "INVALID_STATUS"                # Status nicht buchungsreif


@dataclass
class GoBDViolation:
    code: GoBDViolationCode
    field_name: str
    description: str
    gobd_ref: str     # z.B. "§146 AO" oder "GoBD Rz. 83"


@dataclass
class GoBDSettlementContext:
    """Eingabe-Kontext fuer den GoBD-Check."""

    settlement_id: str
    tenant_id: Optional[str]
    customer_id: Optional[str]
    beleg_nr: Optional[str]           # Belegnummer (GoBD: unveraenderliche ID)
    buchungsdatum: Optional[str]      # ISO-8601
    gross_amount: Optional[float]
    currency: Optional[str]
    gegenkonto: Optional[str]         # Sachkonto-Nummer
    audit_chain_head_hash: Optional[str]   # SHA-256 aus Wave-20-AP1
    current_status: Optional[str]          # muss "VERBUCHT" fuer Buchungsreife sein
    process_definition_key: Optional[str]
    workflow_version: Optional[str]


@dataclass
class GoBDSettlementCheckResult:
    settlement_id: str
    compliant: bool
    violations: list[GoBDViolation] = field(default_factory=list)
    schema_version: int = GOBD_CHECK_SCHEMA_VERSION

    @property
    def violation_codes(self) -> list[str]:
        return [v.code.value for v in self.violations]

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "compliant": self.compliant,
            "violation_count": len(self.violations),
            "violations": [
                {
                    "code": v.code.value,
                    "field_name": v.field_name,
                    "description": v.description,
                    "gobd_ref": v.gobd_ref,
                }
                for v in self.violations
            ],
            "schema_version": self.schema_version,
        }


def check_gobd_settlement(ctx: GoBDSettlementContext) -> GoBDSettlementCheckResult:
    """
    Prueft ob ein Settlement alle GoBD-Pflichtfelder traegt.

    Gibt eine maschinenlesbare Liste von Verstössen zurueck.
    `compliant=True` bedeutet: keine Verstösse — buchungsfähig unter GoBD.
    """
    violations: list[GoBDViolation] = []

    if not ctx.tenant_id:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_TENANT_ID,
            field_name="tenant_id",
            description="Mandanten-ID fehlt — Buchung kann nicht zugeordnet werden.",
            gobd_ref="GoBD Rz. 39",
        ))

    if not ctx.customer_id:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_CUSTOMER_ID,
            field_name="customer_id",
            description="Kunden-/Lieferanten-ID fehlt — kein Gegenkontobezug.",
            gobd_ref="GoBD Rz. 86",
        ))

    if not ctx.beleg_nr:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_BELEG_NR,
            field_name="beleg_nr",
            description="Belegnummer fehlt — GoBD-Buchungsnachweis unvollständig.",
            gobd_ref="§146 AO",
        ))

    if not ctx.buchungsdatum:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_BUCHUNGSDATUM,
            field_name="buchungsdatum",
            description="Buchungsdatum fehlt — zeitliche Zuordnung nicht möglich.",
            gobd_ref="§146 AO",
        ))

    if ctx.gross_amount is None or ctx.gross_amount == 0.0:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_BETRAG,
            field_name="gross_amount",
            description="Buchungsbetrag fehlt oder ist 0 — keine nachvollziehbare Buchung.",
            gobd_ref="GoBD Rz. 83",
        ))

    if not ctx.currency:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_WAEHRUNG,
            field_name="currency",
            description="Währungsangabe fehlt.",
            gobd_ref="GoBD Rz. 83",
        ))

    if not ctx.gegenkonto:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_GEGENKONTO,
            field_name="gegenkonto",
            description="Sachkonto-Gegenkonto fehlt — doppelte Buchführung nicht erfüllbar.",
            gobd_ref="GoBD Rz. 86",
        ))

    if not ctx.audit_chain_head_hash:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_AUDIT_HASH,
            field_name="audit_chain_head_hash",
            description="Audit-Hash fehlt — GoBD-Unveränderbarkeitsnachweis nicht erbringbar.",
            gobd_ref="GoBD Rz. 108-112",
        ))

    if not ctx.process_definition_key or not ctx.workflow_version:
        violations.append(GoBDViolation(
            code=GoBDViolationCode.MISSING_PROCESS_REF,
            field_name="process_definition_key",
            description="Prozessreferenz fehlt — Nachvollziehbarkeit des Buchungswegs nicht gegeben.",
            gobd_ref="GoBD Rz. 102",
        ))

    return GoBDSettlementCheckResult(
        settlement_id=ctx.settlement_id,
        compliant=len(violations) == 0,
        violations=violations,
    )


def build_stub_gobd_check(settlement_id: str) -> GoBDSettlementCheckResult:
    """
    Stub-Ergebnis fuer einen Settlement dessen Details noch nicht geladen sind.
    Gibt einen nicht-konformen Status mit erklaerenden Violations zurueck.
    """
    return check_gobd_settlement(GoBDSettlementContext(
        settlement_id=settlement_id,
        tenant_id=None,
        customer_id=None,
        beleg_nr=None,
        buchungsdatum=None,
        gross_amount=None,
        currency=None,
        gegenkonto=None,
        audit_chain_head_hash=None,
        current_status=None,
        process_definition_key=None,
        workflow_version=None,
    ))
