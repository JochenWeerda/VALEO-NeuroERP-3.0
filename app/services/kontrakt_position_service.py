"""
Rohwaren-Positionsmonitor: Long/Short-Berechnung pro Artikel.

Fachliche Logik (Landhandel / Agrargenossenschaft):
  Verkaufskontrakte (VERKAUF) = Lieferverpflichtung gegenueber Kunden
    → Ware muss beschafft werden → SELL-Seite
  Einkaufs-/Zukaufskontrakte (EINKAUF, ZUKAUF) = Beschaffungssicherung
    → Ware ist gesichert → BUY-Seite

  Netto-Position = BUY (Rest) - SELL (Rest)
    Positiv = Long  (Ueberdeckung, Ware am Lager/gesichert)
    Negativ = Short (Unterdeckung → Boersenrisiko bei steigenden Preisen!)

  Zusaetzlich: gewichteter Durchschnittspreis pro Seite (EK vs. VK)
  → Spread = VK-avg minus EK-avg  (positiv = Marge, negativ = Verlust)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.domains.operations.models import KonContract, KonContractLine, KonContractMovement


SELL_TYPES = {"VERKAUF"}
BUY_TYPES = {"EINKAUF", "ZUKAUF"}
OPEN_STATUSES = {"OFFEN"}


@dataclass
class ArticlePosition:
    article_id: str
    article_desc: str

    buy_contract_qty: Decimal = Decimal("0")
    buy_moved_qty: Decimal = Decimal("0")
    buy_rest_qty: Decimal = Decimal("0")
    buy_avg_price: Optional[Decimal] = None
    buy_contract_count: int = 0

    sell_contract_qty: Decimal = Decimal("0")
    sell_moved_qty: Decimal = Decimal("0")
    sell_rest_qty: Decimal = Decimal("0")
    sell_avg_price: Optional[Decimal] = None
    sell_contract_count: int = 0

    @property
    def net_position(self) -> Decimal:
        return self.buy_rest_qty - self.sell_rest_qty

    @property
    def signal(self) -> str:
        """LONG / SHORT / BALANCED"""
        net = self.net_position
        if net > 0:
            return "LONG"
        elif net < 0:
            return "SHORT"
        return "BALANCED"

    @property
    def spread(self) -> Optional[Decimal]:
        if self.sell_avg_price is not None and self.buy_avg_price is not None:
            return self.sell_avg_price - self.buy_avg_price
        return None

    @property
    def coverage_pct(self) -> Optional[float]:
        if self.sell_rest_qty > 0:
            return float(self.buy_rest_qty / self.sell_rest_qty * 100)
        return None

    def to_dict(self) -> dict:
        return {
            "article_id": self.article_id,
            "article_desc": self.article_desc,
            "buy_contract_qty": float(self.buy_contract_qty),
            "buy_moved_qty": float(self.buy_moved_qty),
            "buy_rest_qty": float(self.buy_rest_qty),
            "buy_avg_price": float(self.buy_avg_price) if self.buy_avg_price is not None else None,
            "buy_contract_count": self.buy_contract_count,
            "sell_contract_qty": float(self.sell_contract_qty),
            "sell_moved_qty": float(self.sell_moved_qty),
            "sell_rest_qty": float(self.sell_rest_qty),
            "sell_avg_price": float(self.sell_avg_price) if self.sell_avg_price is not None else None,
            "sell_contract_count": self.sell_contract_count,
            "net_position": float(self.net_position),
            "signal": self.signal,
            "spread": float(self.spread) if self.spread is not None else None,
            "coverage_pct": round(self.coverage_pct, 1) if self.coverage_pct is not None else None,
        }


@dataclass
class PositionSummary:
    positions: list[ArticlePosition] = field(default_factory=list)
    total_short_articles: int = 0
    total_long_articles: int = 0
    total_balanced_articles: int = 0
    most_critical: Optional[ArticlePosition] = None

    def to_dict(self) -> dict:
        return {
            "positions": [p.to_dict() for p in self.positions],
            "total_short_articles": self.total_short_articles,
            "total_long_articles": self.total_long_articles,
            "total_balanced_articles": self.total_balanced_articles,
            "most_critical": self.most_critical.to_dict() if self.most_critical else None,
        }


class KontraktPositionService:
    """Berechnet Long/Short-Positionen pro Artikel ueber alle offenen Kontrakte."""

    def __init__(self, db: Session):
        self.db = db

    def compute_positions(
        self,
        tenant_id: str,
        article_ids: Optional[list[str]] = None,
        include_done: bool = False,
    ) -> PositionSummary:
        allowed_statuses = set(OPEN_STATUSES)
        if include_done:
            allowed_statuses.add("ERLEDIGT")

        base_q = (
            self.db.query(
                KonContractLine.article_id,
                KonContractLine.description1,
                KonContract.contract_type,
                KonContractLine.line_id,
                KonContractLine.qty_contract,
                KonContractLine.unit_price,
                KonContract.contract_id,
            )
            .join(KonContract, KonContract.contract_id == KonContractLine.contract_id)
            .filter(
                KonContract.tenant_id == tenant_id,
                KonContract.status.in_(allowed_statuses),
            )
        )
        if article_ids:
            base_q = base_q.filter(KonContractLine.article_id.in_(article_ids))

        rows = base_q.all()

        article_map: dict[str, ArticlePosition] = {}

        line_ids = [r.line_id for r in rows]
        _contract_ids = list({r.contract_id for r in rows})  # noqa: F841

        moved_by_line = self._moved_by_line(tenant_id, line_ids) if line_ids else {}

        for row in rows:
            art_id = row.article_id
            if art_id not in article_map:
                article_map[art_id] = ArticlePosition(
                    article_id=art_id,
                    article_desc=row.description1 or art_id,
                )
            pos = article_map[art_id]

            qty_contract = Decimal(str(row.qty_contract or 0))
            qty_moved = Decimal(str(moved_by_line.get(row.line_id, 0)))
            qty_rest = max(Decimal("0"), qty_contract - qty_moved)
            price = Decimal(str(row.unit_price)) if row.unit_price else None

            is_sell = row.contract_type in SELL_TYPES

            if is_sell:
                pos.sell_contract_qty += qty_contract
                pos.sell_moved_qty += qty_moved
                pos.sell_rest_qty += qty_rest
                pos.sell_contract_count += 1
                if price is not None:
                    pos.sell_avg_price = self._running_avg(
                        pos.sell_avg_price, pos.sell_contract_count - 1, price
                    )
            else:
                pos.buy_contract_qty += qty_contract
                pos.buy_moved_qty += qty_moved
                pos.buy_rest_qty += qty_rest
                pos.buy_contract_count += 1
                if price is not None:
                    pos.buy_avg_price = self._running_avg(
                        pos.buy_avg_price, pos.buy_contract_count - 1, price
                    )

        positions = sorted(article_map.values(), key=lambda p: p.net_position)

        summary = PositionSummary(positions=positions)
        for p in positions:
            if p.signal == "SHORT":
                summary.total_short_articles += 1
            elif p.signal == "LONG":
                summary.total_long_articles += 1
            else:
                summary.total_balanced_articles += 1

        short_items = [p for p in positions if p.signal == "SHORT"]
        if short_items:
            summary.most_critical = short_items[0]

        return summary

    def _moved_by_line(self, tenant_id: str, line_ids: list[str]) -> dict[str, Decimal]:
        results = (
            self.db.query(
                KonContractMovement.line_id,
                func.coalesce(func.sum(KonContractMovement.quantity), 0).label("total_moved"),
            )
            .filter(
                KonContractMovement.tenant_id == tenant_id,
                KonContractMovement.line_id.in_(line_ids),
            )
            .group_by(KonContractMovement.line_id)
            .all()
        )
        return {r.line_id: Decimal(str(r.total_moved)) for r in results}

    @staticmethod
    def _running_avg(
        current_avg: Optional[Decimal], prev_count: int, new_value: Decimal
    ) -> Decimal:
        if current_avg is None or prev_count == 0:
            return new_value
        return (current_avg * prev_count + new_value) / (prev_count + 1)
