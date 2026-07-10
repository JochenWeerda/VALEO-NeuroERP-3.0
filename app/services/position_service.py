"""
Commodity Position Calculation Service.
Berechnet Long/Short-Positionen pro Artikel und Lieferperiode aus Kontrakten (KON_*).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.domains.operations.models import (
    KonContract,
    KonContractLine,
    KonContractMovement,
    PosPositionRule,
)
from app.services.kontrakte_service import KontraktRestmengenService

PERIOD_MODE_MONTH = "M"
PERIOD_MODE_WEEK = "W"
PERIOD_MODE_QUARTER = "Q"
SEVERITY_GREEN = "GREEN"
SEVERITY_YELLOW = "YELLOW"
SEVERITY_RED = "RED"
MAX_POSITION_PERIODS = 260


def _period_key(dt: Optional[datetime], period_mode: str) -> Optional[str]:
    """Liefert Period-Key (YYYY-MM, YYYY-Wnn oder YYYY-Qn)."""
    if not dt:
        return None
    d = dt.date() if hasattr(dt, "date") else dt
    if period_mode == PERIOD_MODE_MONTH:
        return d.strftime("%Y-%m")
    if period_mode == PERIOD_MODE_WEEK:
        iso = d.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    if period_mode == PERIOD_MODE_QUARTER:
        q = (d.month - 1) // 3 + 1
        return f"{d.year}-Q{q}"
    return d.strftime("%Y-%m")


def _periods_between(period_from: str, period_to: str, period_mode: str) -> list[str]:
    """Listet Period-Keys zwischen period_from und period_to inklusive."""
    out: list[str] = []
    if period_mode == PERIOD_MODE_MONTH:
        y, m = int(period_from[:4]), int(period_from[5:7])
        y2, m2 = int(period_to[:4]), int(period_to[5:7])
        for _ in range(MAX_POSITION_PERIODS):
            if (y, m) > (y2, m2):
                break
            out.append(f"{y}-{m:02d}")
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
        if (y, m) <= (y2, m2):
            raise ValueError("Period range is too large")
    elif period_mode == PERIOD_MODE_WEEK:
        # Parse YYYY-Wnn
        y1, w1 = int(period_from[:4]), int(period_from.split("-W")[1])
        y2, w2 = int(period_to[:4]), int(period_to.split("-W")[1])
        y, w = y1, w1
        for _ in range(MAX_POSITION_PERIODS):
            if (y, w) > (y2, w2):
                break
            out.append(f"{y}-W{w:02d}")
            w += 1
            if w > 52:
                y, w = y + 1, 1
        if (y, w) <= (y2, w2):
            raise ValueError("Period range is too large")
    else:
        # Quarter: YYYY-Qn
        y1, q1 = int(period_from[:4]), int(period_from.split("-Q")[1])
        y2, q2 = int(period_to[:4]), int(period_to.split("-Q")[1])
        y, q = y1, q1
        for _ in range(MAX_POSITION_PERIODS):
            if (y, q) > (y2, q2):
                break
            out.append(f"{y}-Q{q}")
            q += 1
            if q > 4:
                y, q = y + 1, 1
        if (y, q) <= (y2, q2):
            raise ValueError("Period range is too large")
    return out


@dataclass
class PeriodCell:
    period_key: str
    qty_buy_open: Decimal
    qty_sell_open: Decimal
    qty_net: Decimal
    severity: str
    qty_tolerance: Optional[Decimal] = None


@dataclass
class ArticleRow:
    article_id: str
    article_name: str
    unit: str
    sum_buy_open: Decimal
    sum_sell_open: Decimal
    sum_net: Decimal
    cells: list[PeriodCell] = field(default_factory=list)


@dataclass
class MatrixResult:
    period_keys: list[str]
    rows: list[ArticleRow]
    as_of_date: date
    period_mode: str


@dataclass
class ContractOpenItem:
    contract_id: str
    contract_no: str
    party_id: str
    position_no: int
    article_id: str
    qty_contract: Decimal
    qty_delivered: Decimal
    qty_rest: Decimal
    unit: str
    unit_price: Optional[Decimal]
    valid_to: Optional[datetime]
    clerk_id: Optional[str]


@dataclass
class MovementItem:
    movement_id: str
    contract_id: str
    order_no: Optional[str]
    delivery_note_no: Optional[str]
    invoice_no: Optional[str]
    movement_date: datetime
    quantity: Decimal
    unit_price: Optional[Decimal]
    route_no: Optional[str]


@dataclass
class TopCauser:
    contract_id: str
    contract_no: str
    contract_type: str
    qty_rest: Decimal
    share_pct: Optional[float]


@dataclass
class DrilldownResult:
    article_id: str
    article_name: str
    period_key: str
    branch_id: Optional[str]
    qty_buy_open: Decimal
    qty_sell_open: Decimal
    qty_net: Decimal
    severity: str
    buy_contracts: list[ContractOpenItem]
    sell_contracts: list[ContractOpenItem]
    movements: list[MovementItem]
    top_causers: list[TopCauser]


@dataclass
class KpiResult:
    short_cell_count: int
    max_short_qty: Decimal
    max_short_article_id: Optional[str]
    max_short_period_key: Optional[str]
    expiring_coverage_count: int


class PositionCalculationService:
    def __init__(self, db: Session):
        self.db = db
        self._rest_svc = KontraktRestmengenService(db)

    def _contract_period_key(self, c: KonContract, period_mode: str) -> Optional[str]:
        return _period_key(c.valid_to or c.valid_from, period_mode)

    def _open_contracts_query(
        self,
        tenant_id: str,
        as_of_date: date,
        branch_id: Optional[str],
        contract_types: list[str],
        view_mode: str = "physisch_disponiert",
    ):
        """Kontrakte zum Stichtag. view_mode: physisch_disponiert = nur OFFEN, inkl_archiv = OFFEN+ERLEDIGT."""
        statuses = ["OFFEN"]
        if view_mode == "inkl_archiv":
            statuses = ["OFFEN", "ERLEDIGT"]
        q = (
            self.db.query(KonContract)
            .filter(
                KonContract.tenant_id == tenant_id,
                KonContract.status.in_(statuses),
                KonContract.contract_type.in_(contract_types),
            )
        )
        if branch_id:
            q = q.filter(KonContract.branch_id == branch_id)
        as_of_dt = datetime.combine(as_of_date, datetime.min.time())
        q = q.filter(
            or_(
                KonContract.valid_to.is_(None),
                KonContract.valid_to >= as_of_dt,
            )
        )
        return q

    def _line_rest(self, tenant_id: str, contract_id: str, line_id: str) -> Decimal:
        snap = self._rest_svc.compute_rest(tenant_id, contract_id)
        return snap.line_rest.get(line_id, Decimal("0"))

    def _rule_for_article(self, tenant_id: str, article_id: str, as_of_date: date) -> Optional[PosPositionRule]:
        """Beste passende Regel fuer Artikel (ARTICLE scope) oder Default."""
        rule = (
            self.db.query(PosPositionRule)
            .filter(
                PosPositionRule.tenant_id == tenant_id,
                PosPositionRule.scope_type == "ARTICLE",
                PosPositionRule.scope_id == article_id,
                (PosPositionRule.active_from.is_(None)) | (PosPositionRule.active_from <= datetime.combine(as_of_date, datetime.max.time())),
                (PosPositionRule.active_to.is_(None)) | (PosPositionRule.active_to >= datetime.combine(as_of_date, datetime.min.time())),
            )
            .order_by(PosPositionRule.active_from.desc().nullsfirst())
            .first()
        )
        return rule

    def _severity(self, qty_net: Decimal, rule: Optional[PosPositionRule]) -> str:
        if rule is None:
            return SEVERITY_GREEN if qty_net >= 0 else SEVERITY_YELLOW
        tol = Decimal(str(rule.neg_tolerance_qty or 0))
        red_thr = rule.red_threshold
        yellow_thr = rule.yellow_threshold
        if red_thr is not None and qty_net < red_thr:
            return SEVERITY_RED
        if qty_net < tol:
            return SEVERITY_RED
        if qty_net < 0:
            return SEVERITY_YELLOW
        if yellow_thr is not None and qty_net < (yellow_thr if yellow_thr else 0):
            return SEVERITY_YELLOW
        return SEVERITY_GREEN

    def calculate_matrix(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        as_of_date: date,
        period_mode: str,
        period_from: str,
        period_to: str,
        article_ids: Optional[list[str]] = None,
        article_group_id: Optional[str] = None,
        view_mode: str = "physisch_disponiert",
    ) -> MatrixResult:
        period_keys = _periods_between(period_from, period_to, period_mode)
        if not period_keys:
            return MatrixResult(period_keys=[], rows=[], as_of_date=as_of_date, period_mode=period_mode)

        buy_contracts = self._open_contracts_query(
            tenant_id, as_of_date, branch_id, ["EINKAUF", "ZUKAUF"], view_mode=view_mode
        ).all()
        sell_contracts = self._open_contracts_query(
            tenant_id, as_of_date, branch_id, ["VERKAUF"], view_mode=view_mode
        ).all()

        # (article_id -> (period_key -> (buy, sell)))
        agg: dict[str, dict[str, tuple[Decimal, Decimal]]] = {}

        def add(article_id: str, period_key: str, buy: Decimal, sell: Decimal):
            if article_id not in agg:
                agg[article_id] = {pk: (Decimal("0"), Decimal("0")) for pk in period_keys}
            if period_key not in agg[article_id]:
                agg[article_id][period_key] = (Decimal("0"), Decimal("0"))
            b, s = agg[article_id][period_key]
            agg[article_id][period_key] = (b + buy, s + sell)

        for c in buy_contracts:
            pk = self._contract_period_key(c, period_mode)
            if not pk or pk not in period_keys:
                continue
            for line in self.db.query(KonContractLine).filter(
                KonContractLine.tenant_id == tenant_id,
                KonContractLine.contract_id == c.contract_id,
            ).all():
                rest = self._line_rest(tenant_id, c.contract_id, line.line_id)
                if article_ids and line.article_id not in article_ids:
                    continue
                add(line.article_id, pk, rest, Decimal("0"))

        for c in sell_contracts:
            pk = self._contract_period_key(c, period_mode)
            if not pk or pk not in period_keys:
                continue
            for line in self.db.query(KonContractLine).filter(
                KonContractLine.tenant_id == tenant_id,
                KonContractLine.contract_id == c.contract_id,
            ).all():
                rest = self._line_rest(tenant_id, c.contract_id, line.line_id)
                if article_ids and line.article_id not in article_ids:
                    continue
                add(line.article_id, pk, Decimal("0"), rest)

        rows: list[ArticleRow] = []
        for article_id in sorted(agg.keys()):
            rule = self._rule_for_article(tenant_id, article_id, as_of_date)
            tol = rule.neg_tolerance_qty if rule else None
            cells: list[PeriodCell] = []
            sum_buy = sum_sell = Decimal("0")
            for pk in period_keys:
                b, s = agg[article_id].get(pk, (Decimal("0"), Decimal("0")))
                net = b - s
                sum_buy += b
                sum_sell += s
                sev = self._severity(net, rule)
                cells.append(PeriodCell(period_key=pk, qty_buy_open=b, qty_sell_open=s, qty_net=net, severity=sev, qty_tolerance=tol))
            rows.append(
                ArticleRow(
                    article_id=article_id,
                    article_name=article_id,
                    unit="t",
                    sum_buy_open=sum_buy,
                    sum_sell_open=sum_sell,
                    sum_net=sum_buy - sum_sell,
                    cells=cells,
                )
            )
        return MatrixResult(period_keys=period_keys, rows=rows, as_of_date=as_of_date, period_mode=period_mode)

    def get_drilldown(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        article_id: str,
        period_key: str,
        as_of_date: date,
        period_mode: str,
        view_mode: str = "physisch_disponiert",
    ) -> Optional[DrilldownResult]:
        matrix = self.calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=period_mode,
            period_from=period_key,
            period_to=period_key,
            article_ids=[article_id],
            view_mode=view_mode,
        )
        if not matrix.rows:
            return None
        row = matrix.rows[0]
        cell = next((c for c in row.cells if c.period_key == period_key), None)
        if not cell:
            return None

        buy_list: list[ContractOpenItem] = []
        sell_list: list[ContractOpenItem] = []
        for c in self._open_contracts_query(tenant_id, as_of_date, branch_id, ["EINKAUF", "ZUKAUF"]).all():
            pk = self._contract_period_key(c, period_mode)
            if pk != period_key:
                continue
            for line in self.db.query(KonContractLine).filter(
                KonContractLine.tenant_id == tenant_id,
                KonContractLine.contract_id == c.contract_id,
                KonContractLine.article_id == article_id,
            ).all():
                rest = self._line_rest(tenant_id, c.contract_id, line.line_id)
                if rest <= 0:
                    continue
                moved = (
                    self.db.query(func.coalesce(func.sum(KonContractMovement.quantity), 0))
                    .filter(
                        KonContractMovement.tenant_id == tenant_id,
                        KonContractMovement.contract_id == c.contract_id,
                        KonContractMovement.line_id == line.line_id,
                    )
                    .scalar()
                )
                buy_list.append(
                    ContractOpenItem(
                        contract_id=c.contract_id,
                        contract_no=c.contract_no,
                        party_id=c.party_id,
                        position_no=line.position_no,
                        article_id=line.article_id,
                        qty_contract=Decimal(str(line.qty_contract or 0)),
                        qty_delivered=Decimal(str(moved or 0)),
                        qty_rest=rest,
                        unit=line.price_unit or c.unit or "t",
                        unit_price=line.unit_price,
                        valid_to=c.valid_to,
                        clerk_id=c.clerk_id,
                    )
                )
        for c in self._open_contracts_query(tenant_id, as_of_date, branch_id, ["VERKAUF"]).all():
            pk = self._contract_period_key(c, period_mode)
            if pk != period_key:
                continue
            for line in self.db.query(KonContractLine).filter(
                KonContractLine.tenant_id == tenant_id,
                KonContractLine.contract_id == c.contract_id,
                KonContractLine.article_id == article_id,
            ).all():
                rest = self._line_rest(tenant_id, c.contract_id, line.line_id)
                if rest <= 0:
                    continue
                moved = (
                    self.db.query(func.coalesce(func.sum(KonContractMovement.quantity), 0))
                    .filter(
                        KonContractMovement.tenant_id == tenant_id,
                        KonContractMovement.contract_id == c.contract_id,
                        KonContractMovement.line_id == line.line_id,
                    )
                    .scalar()
                )
                sell_list.append(
                    ContractOpenItem(
                        contract_id=c.contract_id,
                        contract_no=c.contract_no,
                        party_id=c.party_id,
                        position_no=line.position_no,
                        article_id=line.article_id,
                        qty_contract=Decimal(str(line.qty_contract or 0)),
                        qty_delivered=Decimal(str(moved or 0)),
                        qty_rest=rest,
                        unit=line.price_unit or c.unit or "t",
                        unit_price=line.unit_price,
                        valid_to=c.valid_to,
                        clerk_id=c.clerk_id,
                    )
                )

        contract_ids = [x.contract_id for x in buy_list + sell_list]
        movements: list[MovementItem] = []
        if contract_ids:
            for m in (
                self.db.query(KonContractMovement)
                .filter(
                    KonContractMovement.tenant_id == tenant_id,
                    KonContractMovement.contract_id.in_(contract_ids),
                )
                .order_by(KonContractMovement.movement_date.desc())
                .limit(100)
            ):
                movements.append(
                    MovementItem(
                        movement_id=m.movement_id,
                        contract_id=m.contract_id,
                        order_no=m.order_no,
                        delivery_note_no=m.delivery_note_no,
                        invoice_no=m.invoice_no,
                        movement_date=m.movement_date,
                        quantity=Decimal(str(m.quantity or 0)),
                        unit_price=m.unit_price,
                        route_no=m.route_no,
                    )
                )

        total_short = abs(cell.qty_net) if cell.qty_net < 0 else Decimal("0")
        top_causers: list[TopCauser] = []
        for item in sorted(sell_list, key=lambda x: x.qty_rest, reverse=True)[:5]:
            share = float((item.qty_rest / total_short * 100)) if total_short else None
            top_causers.append(
                TopCauser(
                    contract_id=item.contract_id,
                    contract_no=item.contract_no,
                    contract_type="VERKAUF",
                    qty_rest=item.qty_rest,
                    share_pct=share,
                )
            )

        return DrilldownResult(
            article_id=article_id,
            article_name=row.article_name,
            period_key=period_key,
            branch_id=branch_id,
            qty_buy_open=cell.qty_buy_open,
            qty_sell_open=cell.qty_sell_open,
            qty_net=cell.qty_net,
            severity=cell.severity,
            buy_contracts=buy_list,
            sell_contracts=sell_list,
            movements=movements,
            top_causers=top_causers,
        )

    def calculate_kpi(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        as_of_date: date,
        period_mode: str,
        period_from: str,
        period_to: str,
        article_ids: Optional[list[str]] = None,
        view_mode: str = "physisch_disponiert",
    ) -> KpiResult:
        matrix = self.calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=period_mode,
            period_from=period_from,
            period_to=period_to,
            article_ids=article_ids,
            view_mode=view_mode,
        )
        short_count = 0
        max_short = Decimal("0")
        max_article: Optional[str] = None
        max_period: Optional[str] = None
        for row in matrix.rows:
            for cell in row.cells:
                if cell.severity == SEVERITY_RED:
                    short_count += 1
                if cell.qty_net < 0 and abs(cell.qty_net) > max_short:
                    max_short = abs(cell.qty_net)
                    max_article = row.article_id
                    max_period = cell.period_key
        return KpiResult(
            short_cell_count=short_count,
            max_short_qty=max_short,
            max_short_article_id=max_article,
            max_short_period_key=max_period,
            expiring_coverage_count=0,
        )
