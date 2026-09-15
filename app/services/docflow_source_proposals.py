"""Read-only source proposals over existing contracts and customer-owned stock.

No reservation, movement or invoice is created by this module. Quantities are
snapshots of recorded rest/stock, not a promise about concurrent reservations.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.infrastructure.models import Article, BusinessPartner, Customer


class ProposalLine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_id: str = Field(min_length=1, max_length=80)
    article_id: str | None = Field(default=None, max_length=80)
    article_number: str | None = Field(default=None, max_length=80)
    quantity: Decimal = Field(gt=0, max_digits=16, decimal_places=3)
    unit: str = Field(min_length=1, max_length=20)
    charge: str | None = Field(default=None, max_length=64)
    bio: bool | None = None
    contract_reference: str | None = Field(default=None, max_length=80)


class SourceProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    party_id: str = Field(min_length=1, max_length=80)
    direction: Literal["incoming", "outgoing"]
    document_date: date
    warehouse_id: str | None = Field(default=None, max_length=80)
    lines: list[ProposalLine] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_lines(self):
        if len({line.line_id for line in self.lines}) != len(self.lines):
            raise ValueError("line_id must be unique")
        return self


def unit_factor(source: str, target: str) -> Decimal | None:
    aliases = {"tonne": "t", "tonnen": "t", "stk": "st", "stück": "st"}
    source = aliases.get(source.strip().lower(), source.strip().lower())
    target = aliases.get(target.strip().lower(), target.strip().lower())
    if source == target:
        return Decimal(1)
    mass = {"kg": Decimal(1), "t": Decimal(1000)}
    return mass[source] / mass[target] if source in mass and target in mass else None


def build_proposals(request: SourceProposalRequest, candidates: list[dict], tenant_id: str) -> dict:
    """Deterministic projection; budgets are shared across lines, separate by source kind."""
    budgets: dict[str, Decimal] = {}
    result = []
    for line in request.lines:
        groups = []
        for kind in ("contract", "foreign_stock"):
            if kind == "foreign_stock" and request.direction != "outgoing":
                continue  # Incoming custody is a deposit, not a withdrawal.
            remaining = line.quantity
            proposals = []
            compatible = []
            for item in candidates:
                if item["kind"] != kind or item["tenant_id"] != tenant_id or item["party_id"] != request.party_id:
                    continue
                if not line.article_id or item["article_id"] != line.article_id:
                    continue
                if kind == "contract":
                    sides = {"VERKAUF"} if request.direction == "outgoing" else {"EINKAUF", "ZUKAUF"}
                    if item["contract_type"] not in sides or item["status"] != "OFFEN":
                        continue
                    if item.get("valid_from") and item["valid_from"] > request.document_date:
                        continue
                    if item.get("valid_to") and item["valid_to"] < request.document_date:
                        continue
                    if line.bio is not None and item.get("bio") != line.bio:
                        continue
                else:
                    if item["status"] not in {"eingelagert", "teilausgelagert"}:
                        continue
                    if item.get("storage_type") != "fremdware":
                        continue  # Commission/pool goods do not establish customer ownership.
                    if request.warehouse_id and item.get("warehouse_id") != request.warehouse_id:
                        continue
                    if line.charge and item.get("charge") != line.charge:
                        continue
                    if line.bio is not None:
                        continue  # Foreign storage has no verified quality field.
                factor = unit_factor(item["unit"] or "", line.unit)
                if factor is None or not item["unit"]:
                    continue
                compatible.append((item, factor))
            compatible.sort(key=lambda pair: (
                pair[0]["reference"] != line.contract_reference,
                pair[0].get("valid_to") or date.max,
                pair[0]["reference"], pair[0]["source_id"],
            ))
            for item, factor in compatible:
                key = kind + ":" + item["source_id"]
                available = max(Decimal(0), budgets.get(key, Decimal(str(item["quantity"]))))
                quantity = min(remaining, available * factor)
                if quantity <= 0:
                    continue
                budgets[key] = available - quantity / factor
                remaining -= quantity
                proposals.append({
                    "source_id": item["source_id"], "reference": item["reference"],
                    "quantity": str(quantity), "unit": line.unit,
                    "recorded_remaining": str(available * factor),
                    "owner_id": item["party_id"] if kind == "foreign_stock" else None,
                    "warehouse_id": item.get("warehouse_id"), "charge": item.get("charge"),
                    "reason": ("Partner, Artikel, Kontraktseite und Zeitraum passen" if kind == "contract"
                               else "Kundeneigentum, Artikel und Lagerbestand passen"),
                    "billing": "goods" if kind == "contract" else "services_only",
                })
                if remaining == 0:
                    break
            groups.append({"kind": kind, "proposals": proposals, "uncovered_quantity": str(remaining)})
        result.append({"line_id": line.line_id, "article_number": line.article_number,
                       "unit": line.unit, "groups": groups})
    return {"lines": result, "read_only": True, "reservation_checked": False,
            "notice": "Vorschlag aus gebuchter Restmenge; keine Reservierung oder Buchung. Vor Ausfuehrung erneut pruefen."}


class DocflowSourceProposalService:
    def __init__(self, db: Session, tenant_id: str):
        self.db, self.tenant_id = db, tenant_id

    def propose(self, request: SourceProposalRequest) -> dict:
        # Canonical partner or explicit CRM customer bridge; never fuzzy name matching.
        partner = self.db.query(BusinessPartner).filter(
            BusinessPartner.tenant_id == self.tenant_id,
            BusinessPartner.partner_id == request.party_id,
        ).first()
        if partner is None and request.direction == "outgoing":
            customer = self.db.query(Customer).filter(
                Customer.tenant_id == self.tenant_id, Customer.id == request.party_id,
            ).first()
            if customer and customer.business_partner_id:
                partner = self.db.query(BusinessPartner).filter(
                    BusinessPartner.tenant_id == self.tenant_id,
                    BusinessPartner.partner_id == customer.business_partner_id,
                ).first()
        if partner is None:
            return {"lines": [], "read_only": True, "reservation_checked": False,
                    "notice": "Partner nicht eindeutig in den Stammdaten gefunden; bitte Partner-ID verwenden."}
        request = request.model_copy(deep=True)
        request.party_id = partner.partner_id
        ids = [line.article_id for line in request.lines if line.article_id]
        numbers = [line.article_number for line in request.lines if line.article_number]
        articles = self.db.query(Article).filter(Article.tenant_id == self.tenant_id,
            or_(Article.id.in_(ids), Article.article_number.in_(numbers))).all()
        for line in request.lines:
            matches = [article for article in articles if
                       (article.id == line.article_id if line.article_id else article.article_number == line.article_number)]
            line.article_id = matches[0].id if len(matches) == 1 else None
        article_ids = list({line.article_id for line in request.lines if line.article_id})
        if not article_ids:
            return {"lines": [], "read_only": True, "reservation_checked": False,
                    "notice": "Artikel nicht eindeutig in den Stammdaten gefunden; Artikelnummer oder ID verwenden."}
        params = {"tid": self.tenant_id, "party": request.party_id, "articles": article_ids}
        contracts = self.db.execute(text("""
            SELECT c.tenant_id, c.party_id, c.contract_type, c.status,
                   c.contract_no AS reference, l.line_id AS source_id, l.article_id,
                   c.unit, c.valid_from::date AS valid_from, c.valid_to::date AS valid_to,
                   l.is_bio AS bio, l.qty_contract - COALESCE(m.quantity, 0) AS quantity
            FROM domain_ops.kon_contract c
            JOIN domain_ops.kon_contract_line l
              ON l.contract_id=c.contract_id AND l.tenant_id=c.tenant_id
            LEFT JOIN (
              SELECT contract_id, line_id, SUM(quantity) AS quantity
              FROM domain_ops.kon_contract_movement WHERE tenant_id=:tid
              GROUP BY contract_id, line_id
            ) m ON m.contract_id=c.contract_id AND m.line_id=l.line_id
            WHERE c.tenant_id=:tid AND c.party_id=:party AND l.article_id = ANY(:articles)
              AND c.status='OFFEN'
        """), params).mappings().all()
        candidates = [{**dict(row), "kind": "contract"} for row in contracts]
        if request.direction == "outgoing":
            stocks = self.db.execute(text("""
                SELECT tenant_id, eigentuemer_id AS party_id, id::text AS source_id,
                       einlagerungs_nr AS reference, article_id, einheit AS unit,
                       menge_aktuell AS quantity, status, warehouse_id, charge,
                       einlagerungstyp AS storage_type
                FROM domain_einkauf.fremdwaren_einlagerung
                WHERE tenant_id=:tid AND eigentuemer_id=:party
                  AND article_id = ANY(:articles)
                  AND status IN ('eingelagert', 'teilausgelagert')
            """), params).mappings().all()
            candidates.extend({**dict(row), "kind": "foreign_stock"} for row in stocks)
        return build_proposals(request, candidates, self.tenant_id)
