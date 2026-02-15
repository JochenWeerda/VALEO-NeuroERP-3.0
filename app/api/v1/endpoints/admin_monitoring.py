"""Admin monitoring endpoints."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

router = APIRouter()


class AdminAlert(BaseModel):
    id: str
    level: Literal["critical", "warning", "info"]
    type: str
    message: str
    timestamp: str


class AdminAlertsResponse(BaseModel):
    active: int
    critical: int
    warning: int
    system_status: Literal["online", "degraded", "offline"]
    items: list[AdminAlert]


@router.get("/alerts", response_model=AdminAlertsResponse)
def list_admin_monitoring_alerts(db: Session = Depends(get_db)):
    alerts: list[AdminAlert] = []
    today_iso = date.today().isoformat()

    # 1) Health probe (DB reachability in current request context)
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        alerts.append(
            AdminAlert(
                id="db-unreachable",
                level="critical",
                type="Datenbank nicht erreichbar",
                message="Health-Check fehlgeschlagen: Datenbankverbindung nicht verfuegbar.",
                timestamp=today_iso,
            )
        )

    # 2) Inventory critical stock candidates
    try:
        rows = db.execute(
            text(
                """
                SELECT article_number, COALESCE(name, article_number) AS name, current_stock, min_stock
                FROM domain_inventory.articles
                WHERE min_stock IS NOT NULL
                  AND current_stock IS NOT NULL
                  AND current_stock < min_stock
                ORDER BY (min_stock - current_stock) DESC
                LIMIT 3
                """
            )
        ).fetchall()
        for idx, row in enumerate(rows):
            alerts.append(
                AdminAlert(
                    id=f"stock-{idx}",
                    level="warning",
                    type="Lagerbestand kritisch",
                    message=(
                        f"Artikel {row.article_number} ({row.name}) unter Mindestbestand: "
                        f"{float(row.current_stock):.2f} < {float(row.min_stock):.2f}"
                    ),
                    timestamp=today_iso,
                )
            )
    except Exception:
        # Table may not exist in all environments; keep endpoint resilient.
        pass

    # 3) Overdue open items snapshot
    try:
        overdue_row = db.execute(
            text(
                """
                SELECT COUNT(*) AS cnt
                FROM offene_posten
                WHERE faelligkeit < CURRENT_DATE
                  AND COALESCE(offen, 0) > 0
                """
            )
        ).first()
        overdue_count = int(overdue_row.cnt if overdue_row else 0)
        if overdue_count > 0:
            alerts.append(
                AdminAlert(
                    id="overdue-open-items",
                    level="warning",
                    type="Offene Posten ueberfaellig",
                    message=f"{overdue_count} offene Posten sind ueberfaellig.",
                    timestamp=today_iso,
                )
            )
    except Exception:
        pass

    if not alerts:
        alerts.append(
            AdminAlert(
                id="system-ok",
                level="info",
                type="Systemstatus",
                message="Keine kritischen Hinweise aus den aktuell angebundenen Monitoring-Quellen.",
                timestamp=today_iso,
            )
        )

    critical = sum(1 for item in alerts if item.level == "critical")
    warning = sum(1 for item in alerts if item.level == "warning")
    system_status: Literal["online", "degraded", "offline"]
    if critical > 0:
        system_status = "offline"
    elif warning > 0:
        system_status = "degraded"
    else:
        system_status = "online"

    return AdminAlertsResponse(
        active=len(alerts),
        critical=critical,
        warning=warning,
        system_status=system_status,
        items=alerts,
    )

