from __future__ import annotations

import uuid as _uuid_mod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, text as _sql_text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.domains.operations.models import (
    KonAuditLog,
    KonContract,
    KonContractLine,
    KonContractMovement,
    KonNumberRange,
)


class KontraktSecurityService:
    ROLE_LESEN = "KONTRAKT_LESEN"
    ROLE_BEARBEITEN = "KONTRAKT_BEARBEITEN"
    ROLE_LOESCHEN = "KONTRAKT_LOESCHEN"
    ROLE_ADMIN = "KONTRAKT_ADMIN"

    @staticmethod
    def has_any_role(user_roles: list[str], *needed: str) -> bool:
        roles = set(user_roles or [])
        return bool(roles.intersection(set(needed)))


class KontraktValidationService:
    ALLOWED_TYPES = {"EINKAUF", "ZUKAUF", "VERKAUF"}
    ALLOWED_STATUS = {"OFFEN", "ERLEDIGT", "STORNIERT"}
    ALLOWED_QTY_TYPES = {"GESAMTKONTRAKT", "EINZELMENGEN"}

    @classmethod
    def validate_contract_type(cls, value: str) -> None:
        if value not in cls.ALLOWED_TYPES:
            raise ValueError(f"invalid contract_type: {value}")

    @classmethod
    def validate_status(cls, value: str) -> None:
        if value not in cls.ALLOWED_STATUS:
            raise ValueError(f"invalid status: {value}")

    @classmethod
    def validate_quantity_type(cls, value: str) -> None:
        if value not in cls.ALLOWED_QTY_TYPES:
            raise ValueError(f"invalid quantity_type: {value}")


class KontraktNumberRangeService:
    def __init__(self, db: Session):
        self.db = db

    def next_contract_no(self, tenant_id: str, contract_type: str, branch_id: Optional[str]) -> str:
        # row-level lock avoids duplicate numbers under parallel requests
        row = (
            self.db.query(KonNumberRange)
            .filter(
                KonNumberRange.tenant_id == tenant_id,
                KonNumberRange.contract_type == contract_type,
                KonNumberRange.branch_id.is_(branch_id) if branch_id is None else KonNumberRange.branch_id == branch_id,
            )
            .with_for_update()
            .first()
        )
        if not row:
            prefix = f"{contract_type[:3]}-{(branch_id or 'ALL')[:4].upper()}"
            row = KonNumberRange(
                id=uuid7(),
                tenant_id=tenant_id,
                contract_type=contract_type,
                branch_id=branch_id,
                prefix=prefix,
                next_number=1,
                padding=6,
            )
            self.db.add(row)
            self.db.flush()
        number = row.next_number
        row.next_number += 1
        return f"{row.prefix}-{str(number).zfill(row.padding)}"


@dataclass
class RestSnapshot:
    line_rest: dict[str, Decimal]
    contract_rest: Decimal


class KontraktRestmengenService:
    def __init__(self, db: Session):
        self.db = db

    def compute_rest(self, tenant_id: str, contract_id: str) -> RestSnapshot:
        lines = (
            self.db.query(KonContractLine)
            .filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id)
            .all()
        )
        line_rest: dict[str, Decimal] = {}
        contract_rest = Decimal("0")
        for line in lines:
            moved = (
                self.db.query(func.coalesce(func.sum(KonContractMovement.quantity), 0))
                .filter(
                    KonContractMovement.tenant_id == tenant_id,
                    KonContractMovement.contract_id == contract_id,
                    KonContractMovement.line_id == line.line_id,
                )
                .scalar()
            )
            qty_contract = Decimal(str(line.qty_contract or 0))
            qty_moved = Decimal(str(moved or 0))
            rest = qty_contract - qty_moved
            line_rest[line.line_id] = rest
            contract_rest += rest
        return RestSnapshot(line_rest=line_rest, contract_rest=contract_rest)

    def enforce_overdelivery(self, allow_overdelivery: bool, line_rest: Decimal, quantity_to_move: Decimal) -> None:
        if not allow_overdelivery and quantity_to_move > line_rest:
            raise ValueError("Movement exceeds remaining quantity")

    @staticmethod
    def determine_status_from_rest(
        allow_overdelivery: bool,
        current_status: str,
        contract_rest: Decimal,
    ) -> str:
        if current_status == "STORNIERT":
            return "STORNIERT"
        if allow_overdelivery:
            return current_status or "OFFEN"
        return "ERLEDIGT" if contract_rest <= Decimal("0") else "OFFEN"


class KontraktAuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_change(
        self,
        *,
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        field_name: str,
        action: str,
        changed_by: Optional[str],
        old_value: Optional[object],
        new_value: Optional[object],
    ) -> None:
        row = KonAuditLog(
            audit_id=uuid7(),
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=None if old_value is None else str(old_value),
            new_value=None if new_value is None else str(new_value),
            action=action,
            changed_by=changed_by,
        )
        self.db.add(row)

    def log_diff_for_contract(
        self,
        *,
        tenant_id: str,
        contract_id: str,
        changed_by: Optional[str],
        before: KonContract,
        after_payload: dict,
    ) -> None:
        for key, new_value in after_payload.items():
            old_value = getattr(before, key, None)
            if str(old_value) != str(new_value):
                self.log_change(
                    tenant_id=tenant_id,
                    entity_type="kon_contract",
                    entity_id=contract_id,
                    field_name=key,
                    action="UPDATE",
                    changed_by=changed_by,
                    old_value=old_value,
                    new_value=new_value,
                )


# ── Mapper / value helpers (moved from endpoint) ──────────────────────────────

def _num(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    result = str(value).strip()
    return result or None


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return _text(value)


def _date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ja", "y"}
    return bool(value)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [t for item in value if (t := _text(item))]
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    return []


def line_to_dict(line: KonContractLine, rest: Optional[Decimal] = None) -> dict[str, Any]:
    return {
        "line_id": line.line_id,
        "position_no": line.position_no,
        "article_id": line.article_id,
        "description1": line.description1,
        "description2": line.description2,
        "qty_contract": float(line.qty_contract or 0),
        "qty_remaining": float(rest) if rest is not None else None,
        "price_unit": line.price_unit,
        "unit_price": float(line.unit_price) if line.unit_price is not None else None,
        "discount_pct": float(line.discount_pct) if line.discount_pct is not None else None,
        "surcharge": float(line.surcharge) if line.surcharge is not None else None,
        "rebate_type": line.rebate_type,
        "is_bio": bool(line.is_bio),
        "is_matif": bool(line.is_matif),
    }


def _contract_reference_price(contract: KonContract, first_line_price: Optional[float]) -> Optional[float]:
    if first_line_price is not None and first_line_price > 0:
        return first_line_price
    if contract.min_price is not None:
        return float(contract.min_price)
    return None


def build_contract_steering(
    contract: KonContract,
    contract_rest: Decimal,
    first_line_price: Optional[float] = None,
) -> dict[str, Any]:
    conditions = contract.conditions_json or {}
    hedge_quantity_t = _num(conditions.get("hedge_quantity_t"))
    hedge_target_pct = _num(conditions.get("hedge_target_pct"))
    market_price_eur_t = _num(conditions.get("market_price_eur_t"))
    reference_price = _contract_reference_price(contract, first_line_price)
    rest_quantity = float(contract_rest)

    hedge_quote_pct = None
    if hedge_quantity_t is not None:
        total_qty = float(contract.total_quantity or 0)
        if total_qty > 0:
            hedge_quote_pct = min(100.0, (hedge_quantity_t / total_qty) * 100.0)

    hedge_gap_pct = None
    if hedge_target_pct is not None:
        hedge_gap_pct = round(max(0.0, hedge_target_pct - float(hedge_quote_pct or 0.0)), 2)

    market_price_delta_eur_t = None
    market_valuation_eur = None
    if market_price_eur_t is not None and reference_price is not None:
        market_price_delta_eur_t = round(market_price_eur_t - reference_price, 2)
        market_valuation_eur = round(market_price_delta_eur_t * rest_quantity, 2)

    dunning_level = int(_num(conditions.get("dunning_level")) or 0)
    dunning_blocked = _bool(conditions.get("dunning_blocked"))
    alternate_articles = _string_list(conditions.get("alternate_articles"))
    washout_quantity_t = _num(conditions.get("washout_quantity_t"))
    writeoff_quantity_t = _num(conditions.get("writeoff_quantity_t"))
    print_copy_count = int(_num(conditions.get("print_copy_count")) or 0)
    today = datetime.now(timezone.utc)
    dunning_due_at = _date(conditions.get("dunning_due_at")) or contract.valid_to
    dunning_candidate = bool(
        contract.status == "OFFEN"
        and not dunning_blocked
        and rest_quantity > 0
        and dunning_due_at is not None
        and dunning_due_at < today
    )
    return {
        "contract_class": _text(conditions.get("contract_class")),
        "contract_group": _text(conditions.get("contract_group")),
        "contract_variant": _text(conditions.get("contract_variant")),
        "disposition_flag": _text(conditions.get("disposition_flag")),
        "parity_code": _text(conditions.get("parity_code")),
        "parity_label": _text(conditions.get("parity_label")),
        "fallback_route": _text(conditions.get("fallback_route")),
        "alternate_articles": alternate_articles,
        "print_template": _text(conditions.get("print_template")),
        "print_channel": _text(conditions.get("print_channel")),
        "print_copy_count": print_copy_count,
        "last_printed_at": _iso(conditions.get("last_printed_at")),
        "print_ready": bool(_text(conditions.get("print_template")) and _text(conditions.get("print_channel"))),
        "washout_status": _text(conditions.get("washout_status")),
        "washout_quantity_t": washout_quantity_t,
        "washout_reason": _text(conditions.get("washout_reason")),
        "writeoff_quantity_t": writeoff_quantity_t,
        "writeoff_reason": _text(conditions.get("writeoff_reason")),
        "writeoff_candidate": bool((writeoff_quantity_t or 0) > 0 or (washout_quantity_t or 0) > 0),
        "hedge_strategy": _text(conditions.get("hedge_strategy")),
        "hedge_market": _text(conditions.get("hedge_market")),
        "hedge_status": _text(conditions.get("hedge_status")),
        "hedge_target_pct": hedge_target_pct,
        "hedge_quantity_t": hedge_quantity_t,
        "hedge_quote_pct": hedge_quote_pct,
        "hedge_gap_pct": hedge_gap_pct,
        "market_price_source": _text(conditions.get("market_price_source")),
        "market_price_eur_t": market_price_eur_t,
        "market_price_date": _iso(conditions.get("market_price_date")),
        "market_price_delta_eur_t": market_price_delta_eur_t,
        "market_valuation_eur": market_valuation_eur,
        "reference_price_eur_t": reference_price,
        "dunning_level": dunning_level,
        "dunning_blocked": dunning_blocked,
        "dunning_due_at": _iso(dunning_due_at),
        "dunning_last_at": _iso(conditions.get("dunning_last_at")),
        "dunning_candidate": dunning_candidate,
        "dunning_reason": _text(conditions.get("dunning_reason")),
    }


def contract_to_dict(contract: KonContract, line_out: list[dict[str, Any]], contract_rest: Decimal) -> dict[str, Any]:
    first_line_price = _num(line_out[0].get("unit_price")) if line_out else None
    steering = build_contract_steering(contract, contract_rest, first_line_price)
    return {
        "contract_id": contract.contract_id,
        "contract_no": contract.contract_no,
        "contract_type": contract.contract_type,
        "branch_id": contract.branch_id,
        "clerk_id": contract.clerk_id,
        "party_id": contract.party_id,
        "debitor_kto": contract.debitor_kto,
        "kreditor_kto": contract.kreditor_kto,
        "contract_date": contract.contract_date,
        "valid_from": contract.valid_from,
        "valid_to": contract.valid_to,
        "quantity_type": contract.quantity_type,
        "total_quantity": float(contract.total_quantity or 0),
        "unit": contract.unit,
        "allow_overdelivery": bool(contract.allow_overdelivery),
        "status": contract.status,
        "notes": contract.notes,
        "payment_terms": contract.payment_terms,
        "conditions_json": contract.conditions_json or {},
        "pricing_model": contract.pricing_model,
        "min_price": float(contract.min_price) if contract.min_price is not None else None,
        "premium_type": contract.premium_type,
        "premium_value": float(contract.premium_value) if contract.premium_value is not None else None,
        "basis_reference": contract.basis_reference,
        "pricing_window_from": contract.pricing_window_from,
        "pricing_window_to": contract.pricing_window_to,
        "rest_quantity": float(contract_rest),
        "steering": steering,
        "created_at": contract.created_at,
        "created_by": contract.created_by,
        "updated_at": contract.updated_at,
        "updated_by": contract.updated_by,
        "lines": line_out,
    }


# ── Disposition helpers (moved from endpoint) ─────────────────────────────────

def ensure_disposition_table(db: Session) -> None:
    """Erstellt domain_agrar.kontrakt_dispositionen falls die Tabelle fehlt."""
    try:
        db.execute(_sql_text("""
            CREATE TABLE IF NOT EXISTS domain_agrar.kontrakt_dispositionen (
                id               TEXT PRIMARY KEY,
                kontrakt_id      TEXT NOT NULL,
                disposition_nr   INTEGER NOT NULL,
                kontrakt_nr      TEXT NOT NULL,
                kontrakt_pos_nr  INTEGER NOT NULL DEFAULT 1,
                geplantes_lieferdatum TEXT,
                lieferdatum      TEXT,
                menge            NUMERIC(18,3) NOT NULL,
                freigabe         BOOLEAN NOT NULL DEFAULT FALSE,
                wiegeschein_nr   TEXT,
                bemerkung        TEXT,
                status           TEXT NOT NULL DEFAULT 'OFFEN',
                created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """))
        db.commit()
    except Exception:
        db.rollback()


def list_dispositionen_db(db: Session, kontrakt_id: str) -> list[dict[str, Any]]:
    rows = db.execute(
        _sql_text(
            "SELECT id, kontrakt_id, disposition_nr, kontrakt_nr, kontrakt_pos_nr, "
            "geplantes_lieferdatum, lieferdatum, menge, freigabe, wiegeschein_nr, "
            "bemerkung, status, created_at, updated_at "
            "FROM domain_agrar.kontrakt_dispositionen "
            "WHERE kontrakt_id = :kid ORDER BY disposition_nr ASC"
        ),
        {"kid": kontrakt_id},
    ).fetchall()
    return [
        {
            "id": r[0], "kontrakt_id": r[1], "disposition_nr": r[2],
            "kontrakt_nr": r[3], "kontrakt_pos_nr": r[4],
            "geplantes_lieferdatum": r[5], "lieferdatum": r[6],
            "menge": float(r[7]) if r[7] is not None else None,
            "freigabe": bool(r[8]), "wiegeschein_nr": r[9], "bemerkung": r[10],
            "status": r[11],
            "created_at": r[12].isoformat() if r[12] else None,
            "updated_at": r[13].isoformat() if r[13] else None,
        }
        for r in rows
    ]


def create_disposition_db(db: Session, kontrakt_id: str, payload: Any) -> dict[str, Any]:
    ensure_disposition_table(db)
    new_id = str(_uuid_mod.uuid4())
    db.execute(
        _sql_text("""
            INSERT INTO domain_agrar.kontrakt_dispositionen (
                id, kontrakt_id, disposition_nr, kontrakt_nr, kontrakt_pos_nr,
                geplantes_lieferdatum, lieferdatum, menge, freigabe,
                wiegeschein_nr, bemerkung, status, created_at, updated_at
            ) VALUES (
                :id, :kontrakt_id,
                COALESCE((SELECT MAX(disposition_nr) FROM domain_agrar.kontrakt_dispositionen
                           WHERE kontrakt_id = :kontrakt_id), 0) + 1,
                :kontrakt_nr, :kontrakt_pos_nr,
                :geplantes_lieferdatum, :lieferdatum, :menge, :freigabe,
                :wiegeschein_nr, :bemerkung,
                CASE WHEN :freigabe THEN 'FREIGEGEBEN' ELSE 'OFFEN' END,
                now(), now()
            )
        """),
        {
            "id": new_id, "kontrakt_id": kontrakt_id,
            "kontrakt_nr": payload.kontrakt_nr, "kontrakt_pos_nr": payload.kontrakt_pos_nr,
            "geplantes_lieferdatum": payload.geplantes_lieferdatum,
            "lieferdatum": payload.lieferdatum, "menge": payload.menge,
            "freigabe": payload.freigabe,
            "wiegeschein_nr": payload.wiegeschein_nr, "bemerkung": payload.bemerkung,
        },
    )
    db.commit()
    row = db.execute(
        _sql_text("SELECT id, disposition_nr, status FROM domain_agrar.kontrakt_dispositionen WHERE id = :id"),
        {"id": new_id},
    ).fetchone()
    return {
        "id": row[0] if row else new_id,
        "kontrakt_id": kontrakt_id,
        "disposition_nr": row[1] if row else 1,
        "kontrakt_nr": payload.kontrakt_nr,
        "kontrakt_pos_nr": payload.kontrakt_pos_nr,
        "menge": payload.menge,
        "freigabe": payload.freigabe,
        "status": row[2] if row else ("FREIGEGEBEN" if payload.freigabe else "OFFEN"),
    }
