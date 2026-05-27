"""Admin monitoring endpoints."""

from __future__ import annotations

import json
from datetime import date
from typing import Literal
from uuid import uuid4

from fastapi import Response, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....services.security_observability import security_observer

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


class SecurityMonitoringSummary(BaseModel):
    status: Literal["ok", "warning", "critical"]
    event_count: int
    blocked_count: int
    denied_count: int
    critical_count: int
    top_categories: dict[str, int]
    channel_count: int
    rule_count: int
    recent_events: list[dict]


class MonitoringRuleIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    metric: str = Field(..., min_length=1, max_length=80)
    level: Literal["critical", "warning", "info"] = "warning"
    threshold: float | None = None
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq"] = "gte"
    active: bool = True
    escalation_minutes: int = Field(default=30, ge=0, le=10080)
    channel_ids: list[str] = Field(default_factory=list)


class MonitoringRuleOut(MonitoringRuleIn):
    id: str


class MonitoringChannelIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    channel_type: Literal["email", "sms", "webhook", "chatops"] = "email"
    target: str = Field(..., min_length=1, max_length=255)
    active: bool = True


class MonitoringChannelOut(MonitoringChannelIn):
    id: str


class SchedulerJobIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    cron: str = Field(..., min_length=5, max_length=120)
    process: str = Field(..., min_length=1, max_length=80)
    active: bool = True
    retry_max: int = Field(default=3, ge=0, le=100)
    timeout_seconds: int = Field(default=300, ge=10, le=86400)
    channel_ids: list[str] = Field(default_factory=list)


class SchedulerJobOut(SchedulerJobIn):
    id: str


def _load_tenant_settings(db: Session, tenant_id: str) -> dict:
    row = db.execute(
        text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")
    raw = row[0]
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _save_tenant_settings(db: Session, tenant_id: str, settings: dict) -> None:
    db.execute(
        text("UPDATE domain_shared.tenants SET settings = :settings, updated_at = NOW() WHERE id = :tenant_id"),
        {"tenant_id": tenant_id, "settings": json.dumps(settings)},
    )


def _monitoring_cfg(settings: dict) -> dict:
    cfg = settings.get("admin_monitoring")
    if not isinstance(cfg, dict):
        cfg = {}
    cfg.setdefault("rules", [])
    cfg.setdefault("channels", [])
    cfg.setdefault("scheduler_jobs", [])
    return cfg


def _find_by_id(items: list[dict], item_id: str) -> int:
    for idx, item in enumerate(items):
        if str(item.get("id")) == str(item_id):
            return idx
    return -1


def _tenant_visible_security_events(tenant_id: str, limit: int = 20) -> list[dict]:
    return [
        event
        for event in security_observer.get_recent_events(limit)
        if event.get("tenant_id") in (None, tenant_id)
    ]


def _build_security_alerts(tenant_id: str, limit: int = 5) -> list[AdminAlert]:
    alerts: list[AdminAlert] = []
    for idx, event in enumerate(reversed(_tenant_visible_security_events(tenant_id, limit))):
        level = "critical" if event["severity"] == "critical" else ("warning" if event["outcome"] in {"blocked", "denied"} else "info")
        alerts.append(
            AdminAlert(
                id=f"security-{idx}",
                level=level,
                type=f"Security {event['category']}",
                message=event["message"],
                timestamp=event["timestamp"],
            )
        )
    return alerts


@router.get("/alerts", response_model=AdminAlertsResponse, summary="Admin monitoring alerts auflisten")
def list_admin_monitoring_alerts(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
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
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    alerts.extend(_build_security_alerts(tenant_id))

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


@router.get("/security-summary", response_model=SecurityMonitoringSummary, summary="Security monitoring summary abrufen")
def get_security_monitoring_summary(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    cfg = _monitoring_cfg(_load_tenant_settings(db, tenant_id))
    visible_events = _tenant_visible_security_events(tenant_id, limit=20)
    visible_metrics = {
        "blocked_count": sum(1 for event in visible_events if event["outcome"] == "blocked"),
        "denied_count": sum(1 for event in visible_events if event["outcome"] == "denied"),
        "critical_count": sum(1 for event in visible_events if event["severity"] == "critical"),
    }
    top_categories: dict[str, int] = {}
    for event in visible_events:
        top_categories[event["category"]] = top_categories.get(event["category"], 0) + 1

    status: Literal["ok", "warning", "critical"] = "ok"
    if visible_metrics["blocked_count"] or visible_metrics["denied_count"]:
        status = "warning"
    if visible_metrics["critical_count"]:
        status = "critical"

    return SecurityMonitoringSummary(
        status=status,
        event_count=len(visible_events),
        blocked_count=visible_metrics["blocked_count"],
        denied_count=visible_metrics["denied_count"],
        critical_count=visible_metrics["critical_count"],
        top_categories=top_categories,
        channel_count=len(cfg["channels"]),
        rule_count=len(cfg["rules"]),
        recent_events=visible_events,
    )


@router.get("/rules", response_model=list[MonitoringRuleOut], summary="Monitoring rules auflisten")
def list_monitoring_rules(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    cfg = _monitoring_cfg(_load_tenant_settings(db, tenant_id))
    return [MonitoringRuleOut(**item) for item in cfg["rules"] if isinstance(item, dict)]


@router.post("/rules", response_model=MonitoringRuleOut, status_code=201, summary="Monitoring rule anlegen")
def create_monitoring_rule(payload: MonitoringRuleIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    item = {"id": str(uuid4()), **payload.model_dump()}
    cfg["rules"].append(item)
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return MonitoringRuleOut(**item)


@router.put("/rules/{rule_id}", response_model=MonitoringRuleOut, summary="Monitoring rule aktualisieren")
def update_monitoring_rule(rule_id: str, payload: MonitoringRuleIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["rules"], rule_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Monitoring rule not found")
    item = {"id": rule_id, **payload.model_dump()}
    cfg["rules"][idx] = item
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return MonitoringRuleOut(**item)


@router.delete("/rules/{rule_id}", status_code=204, response_class=Response, response_model=None, summary="Monitoring rule löschen")
def delete_monitoring_rule(rule_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["rules"], rule_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Monitoring rule not found")
    del cfg["rules"][idx]
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return None


@router.get("/channels", response_model=list[MonitoringChannelOut], summary="Monitoring channels auflisten")
def list_monitoring_channels(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    cfg = _monitoring_cfg(_load_tenant_settings(db, tenant_id))
    return [MonitoringChannelOut(**item) for item in cfg["channels"] if isinstance(item, dict)]


@router.post("/channels", response_model=MonitoringChannelOut, status_code=201, summary="Monitoring channel anlegen")
def create_monitoring_channel(payload: MonitoringChannelIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    item = {"id": str(uuid4()), **payload.model_dump()}
    cfg["channels"].append(item)
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return MonitoringChannelOut(**item)


@router.put("/channels/{channel_id}", response_model=MonitoringChannelOut, summary="Monitoring channel aktualisieren")
def update_monitoring_channel(channel_id: str, payload: MonitoringChannelIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["channels"], channel_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Monitoring channel not found")
    item = {"id": channel_id, **payload.model_dump()}
    cfg["channels"][idx] = item
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return MonitoringChannelOut(**item)


@router.delete("/channels/{channel_id}", status_code=204, response_class=Response, response_model=None, summary="Monitoring channel löschen")
def delete_monitoring_channel(channel_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["channels"], channel_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Monitoring channel not found")
    del cfg["channels"][idx]
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return None


@router.get("/scheduler-jobs", response_model=list[SchedulerJobOut], summary="Scheduler jobs auflisten")
def list_scheduler_jobs(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    cfg = _monitoring_cfg(_load_tenant_settings(db, tenant_id))
    return [SchedulerJobOut(**item) for item in cfg["scheduler_jobs"] if isinstance(item, dict)]


@router.post("/scheduler-jobs", response_model=SchedulerJobOut, status_code=201, summary="Scheduler job anlegen")
def create_scheduler_job(payload: SchedulerJobIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    item = {"id": str(uuid4()), **payload.model_dump()}
    cfg["scheduler_jobs"].append(item)
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return SchedulerJobOut(**item)


@router.put("/scheduler-jobs/{job_id}", response_model=SchedulerJobOut, summary="Scheduler job aktualisieren")
def update_scheduler_job(job_id: str, payload: SchedulerJobIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["scheduler_jobs"], job_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Scheduler job not found")
    item = {"id": job_id, **payload.model_dump()}
    cfg["scheduler_jobs"][idx] = item
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return SchedulerJobOut(**item)


@router.delete("/scheduler-jobs/{job_id}", status_code=204, response_class=Response, response_model=None, summary="Scheduler job löschen")
def delete_scheduler_job(job_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    settings = _load_tenant_settings(db, tenant_id)
    cfg = _monitoring_cfg(settings)
    idx = _find_by_id(cfg["scheduler_jobs"], job_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Scheduler job not found")
    del cfg["scheduler_jobs"][idx]
    settings["admin_monitoring"] = cfg
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return None
