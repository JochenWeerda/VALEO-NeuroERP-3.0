"""
Commodity Position Snapshot Service (optional cache for matrix performance).
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.domains.operations.models import PosPositionSnapshot
from app.services.position_service import PositionCalculationService


class PositionSnapshotService:
    def __init__(self, db: Session):
        self.db = db
        self._pos_svc = PositionCalculationService(db)

    def refresh_snapshot(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        as_of_date: date,
        period_mode: str,
        period_from: str,
        period_to: str,
        article_ids: Optional[list[str]] = None,
        view_mode: str = "physisch_disponiert",
    ) -> int:
        """
        Berechnet Matrix neu und schreibt/überschreibt Snapshot-Zeilen für den Kontext.
        Entfernt bestehende Snapshots für (tenant_id, branch_id, as_of_date, period_mode).
        """
        q = self.db.query(PosPositionSnapshot).filter(
            PosPositionSnapshot.tenant_id == tenant_id,
            PosPositionSnapshot.as_of_date == as_of_date,
            PosPositionSnapshot.period_mode == period_mode,
        )
        if branch_id is None:
            q = q.filter(PosPositionSnapshot.branch_id.is_(None))
        else:
            q = q.filter(PosPositionSnapshot.branch_id == branch_id)
        q.delete(synchronize_session=False)
        self.db.flush()

        matrix = self._pos_svc.calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=period_mode,
            period_from=period_from,
            period_to=period_to,
            article_ids=article_ids,
            view_mode=view_mode,
        )
        count = 0
        for row in matrix.rows:
            for cell in row.cells:
                snap = PosPositionSnapshot(
                    snapshot_id=uuid7(),
                    tenant_id=tenant_id,
                    branch_id=branch_id,
                    as_of_date=as_of_date,
                    period_mode=period_mode,
                    article_id=row.article_id,
                    period_key=cell.period_key,
                    qty_buy_open=cell.qty_buy_open,
                    qty_sell_open=cell.qty_sell_open,
                    qty_net=cell.qty_net,
                    qty_tolerance=cell.qty_tolerance,
                    severity=cell.severity,
                )
                self.db.add(snap)
                count += 1
        self.db.flush()
        return count

    def get_or_refresh(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        as_of_date: date,
        period_mode: str,
        period_from: str,
        period_to: str,
        article_ids: Optional[list[str]] = None,
        use_cache: bool = True,
        view_mode: str = "physisch_disponiert",
    ):
        """
        Liefert Matrix-Daten. Bei use_cache=True: aus Snapshot falls vorhanden, sonst on-the-fly.
        Bei use_cache=False oder kein Snapshot: refresh_snapshot + MatrixResult aus PositionCalculationService.
        """
        if use_cache:
            q = self.db.query(PosPositionSnapshot).filter(
                PosPositionSnapshot.tenant_id == tenant_id,
                PosPositionSnapshot.as_of_date == as_of_date,
                PosPositionSnapshot.period_mode == period_mode,
            )
            if branch_id is None:
                q = q.filter(PosPositionSnapshot.branch_id.is_(None))
            else:
                q = q.filter(PosPositionSnapshot.branch_id == branch_id)
            existing = q.first()
            if not existing:
                use_cache = False
        if not use_cache:
            self.refresh_snapshot(
                tenant_id=tenant_id,
                branch_id=branch_id,
                as_of_date=as_of_date,
                period_mode=period_mode,
                period_from=period_from,
                period_to=period_to,
                article_ids=article_ids,
                view_mode=view_mode,
            )
        return self._pos_svc.calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=period_mode,
            period_from=period_from,
            period_to=period_to,
            article_ids=article_ids,
            view_mode=view_mode,
        )
