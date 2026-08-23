"""Service layer for Controlling module (KPIs, Dashboards, Widgets, Timeseries, Actions)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ConflictError, ValidationFailedError
from app.core.read_model_cache import invalidate_tenant_prefix


class ControllingSchemaError(Exception):
    """Raised when the controlling schema/tables are missing (dev/staging)."""


def _clean(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for k, v in list(out.items()):
        if isinstance(v, UUID):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
    return out


class ControllingService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _list(self, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return [_clean(dict(r)) for r in self.db.execute(text(sql), params).mappings().all()]
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return []

    def _exec(self, sql: str, params: dict[str, Any]) -> int:
        try:
            result = self.db.execute(text(sql), params)
            return result.rowcount
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc

    def _fetch_one(self, table: str, item_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(f"SELECT * FROM {table} WHERE tenant_id=:tenant_id AND id=:id"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            {"tenant_id": self.tenant_id, "id": item_id},
        ).mappings().first()
        return _clean(dict(row)) if row else {}

    # ── KPIs ─────────────────────────────────────────────────────────────────

    def list_kpis(self) -> list[dict[str, Any]]:
        return self._list(
            "SELECT * FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id ORDER BY kpi_code ASC",
            {"tenant_id": self.tenant_id},
        )

    def create_kpi(self, d: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_controlling.kpi_definitions
                    (id, tenant_id, kpi_code, name, description, formula, target_value, unit, ampel_logic, filters, is_active, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :kpi_code, :name, :description, :formula, :target_value, :unit, CAST(:ampel_logic AS jsonb), CAST(:filters AS jsonb), :is_active, NOW(), NOW())
                """),
                {
                    "id": item_id, "tenant_id": self.tenant_id,
                    "kpi_code": d["kpi_code"], "name": d["name"],
                    "description": d.get("description"), "formula": d.get("formula"),
                    "target_value": d.get("target_value"), "unit": d.get("unit"),
                    "ampel_logic": json.dumps(d.get("ampel_logic", {})),
                    "filters": json.dumps(d.get("filters", {})),
                    "is_active": bool(d.get("is_active", True)),
                },
            )
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc
        except Exception as exc:
            self.db.rollback()
            raise ConflictError(f"KPI conflict: {exc}") from exc
        self.db.commit()
        invalidate_tenant_prefix("ctrl_kpis", self.tenant_id)
        return self._fetch_one("domain_controlling.kpi_definitions", item_id)

    def update_kpi(self, item_id: str, d: dict[str, Any]) -> dict[str, Any]:
        rows = self._exec(
            """
            UPDATE domain_controlling.kpi_definitions
            SET kpi_code=:kpi_code, name=:name, description=:description, formula=:formula,
                target_value=:target_value, unit=:unit,
                ampel_logic=CAST(:ampel_logic AS jsonb), filters=CAST(:filters AS jsonb),
                is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """,
            {
                "tenant_id": self.tenant_id, "id": item_id,
                "kpi_code": d["kpi_code"], "name": d["name"],
                "description": d.get("description"), "formula": d.get("formula"),
                "target_value": d.get("target_value"), "unit": d.get("unit"),
                "ampel_logic": json.dumps(d.get("ampel_logic", {})),
                "filters": json.dumps(d.get("filters", {})),
                "is_active": bool(d.get("is_active", True)),
            },
        )
        if not rows:
            raise EntityNotFoundError("KPI", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_kpis", self.tenant_id)
        return self._fetch_one("domain_controlling.kpi_definitions", item_id)

    def delete_kpi(self, item_id: str) -> None:
        rows = self._exec(
            "DELETE FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": self.tenant_id, "id": item_id},
        )
        if not rows:
            raise EntityNotFoundError("KPI", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_kpis", self.tenant_id)

    # ── Dashboards ───────────────────────────────────────────────────────────

    def list_dashboards(self) -> list[dict[str, Any]]:
        return self._list(
            "SELECT * FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id ORDER BY dashboard_code ASC",
            {"tenant_id": self.tenant_id},
        )

    def create_dashboard(self, d: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_controlling.dashboard_configs
                    (id, tenant_id, dashboard_code, name, description, layout, default_filters, role_scope, is_active, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :dashboard_code, :name, :description, CAST(:layout AS jsonb), CAST(:default_filters AS jsonb), CAST(:role_scope AS jsonb), :is_active, NOW(), NOW())
                """),
                {
                    "id": item_id, "tenant_id": self.tenant_id,
                    "dashboard_code": d["dashboard_code"], "name": d["name"],
                    "description": d.get("description"),
                    "layout": json.dumps(d.get("layout", {})),
                    "default_filters": json.dumps(d.get("default_filters", {})),
                    "role_scope": json.dumps(d.get("role_scope", [])),
                    "is_active": bool(d.get("is_active", True)),
                },
            )
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc
        except Exception as exc:
            self.db.rollback()
            raise ConflictError(f"Dashboard conflict: {exc}") from exc
        self.db.commit()
        invalidate_tenant_prefix("ctrl_dashboards", self.tenant_id)
        return self._fetch_one("domain_controlling.dashboard_configs", item_id)

    def update_dashboard(self, item_id: str, d: dict[str, Any]) -> dict[str, Any]:
        rows = self._exec(
            """
            UPDATE domain_controlling.dashboard_configs
            SET dashboard_code=:dashboard_code, name=:name, description=:description,
                layout=CAST(:layout AS jsonb), default_filters=CAST(:default_filters AS jsonb),
                role_scope=CAST(:role_scope AS jsonb), is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """,
            {
                "tenant_id": self.tenant_id, "id": item_id,
                "dashboard_code": d["dashboard_code"], "name": d["name"],
                "description": d.get("description"),
                "layout": json.dumps(d.get("layout", {})),
                "default_filters": json.dumps(d.get("default_filters", {})),
                "role_scope": json.dumps(d.get("role_scope", [])),
                "is_active": bool(d.get("is_active", True)),
            },
        )
        if not rows:
            raise EntityNotFoundError("Dashboard", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_dashboards", self.tenant_id)
        return self._fetch_one("domain_controlling.dashboard_configs", item_id)

    def delete_dashboard(self, item_id: str) -> None:
        rows = self._exec(
            "DELETE FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": self.tenant_id, "id": item_id},
        )
        if not rows:
            raise EntityNotFoundError("Dashboard", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_dashboards", self.tenant_id)

    # ── Widgets ──────────────────────────────────────────────────────────────

    def list_widgets(self, dashboard_id: str) -> list[dict[str, Any]]:
        return self._list(
            "SELECT * FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND dashboard_id=:dashboard_id ORDER BY position_y, position_x",
            {"tenant_id": self.tenant_id, "dashboard_id": dashboard_id},
        )

    def create_widget(self, dashboard_id: str, d: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_controlling.dashboard_widgets
                    (id, tenant_id, dashboard_id, widget_type, title, kpi_id, position_x, position_y, size_w, size_h, settings, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :dashboard_id, :widget_type, :title, :kpi_id, :position_x, :position_y, :size_w, :size_h, CAST(:settings AS jsonb), NOW(), NOW())
                """),
                {
                    "id": item_id, "tenant_id": self.tenant_id, "dashboard_id": dashboard_id,
                    "widget_type": d["widget_type"], "title": d["title"], "kpi_id": d.get("kpi_id"),
                    "position_x": int(d.get("position_x", 0)), "position_y": int(d.get("position_y", 0)),
                    "size_w": int(d.get("size_w", 4)), "size_h": int(d.get("size_h", 3)),
                    "settings": json.dumps(d.get("settings", {})),
                },
            )
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc
        self.db.commit()
        return self._fetch_one("domain_controlling.dashboard_widgets", item_id)

    def update_widget(self, item_id: str, d: dict[str, Any]) -> dict[str, Any]:
        rows = self._exec(
            """
            UPDATE domain_controlling.dashboard_widgets
            SET widget_type=:widget_type, title=:title, kpi_id=:kpi_id,
                position_x=:position_x, position_y=:position_y, size_w=:size_w, size_h=:size_h,
                settings=CAST(:settings AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """,
            {
                "tenant_id": self.tenant_id, "id": item_id,
                "widget_type": d["widget_type"], "title": d["title"], "kpi_id": d.get("kpi_id"),
                "position_x": int(d.get("position_x", 0)), "position_y": int(d.get("position_y", 0)),
                "size_w": int(d.get("size_w", 4)), "size_h": int(d.get("size_h", 3)),
                "settings": json.dumps(d.get("settings", {})),
            },
        )
        if not rows:
            raise EntityNotFoundError("Widget", item_id)
        self.db.commit()
        return self._fetch_one("domain_controlling.dashboard_widgets", item_id)

    def delete_widget(self, item_id: str) -> None:
        rows = self._exec(
            "DELETE FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": self.tenant_id, "id": item_id},
        )
        if not rows:
            raise EntityNotFoundError("Widget", item_id)
        self.db.commit()

    # ── Timeseries ───────────────────────────────────────────────────────────

    def list_timeseries(self, kpi_id: Optional[str] = None) -> list[dict[str, Any]]:
        where = ["tenant_id=:tenant_id"]
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        if kpi_id:
            where.append("kpi_id=:kpi_id")
            params["kpi_id"] = kpi_id
        return self._list(
            f"SELECT * FROM domain_controlling.kpi_timeseries WHERE {' AND '.join(where)} ORDER BY period_start DESC",
            params,
        )

    def create_timeseries(self, d: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_controlling.kpi_timeseries
                    (id, tenant_id, kpi_id, period_start, period_end, value, dimensions, source, created_at)
                    VALUES
                    (:id, :tenant_id, :kpi_id, :period_start, :period_end, :value, CAST(:dimensions AS jsonb), :source, NOW())
                """),
                {
                    "id": item_id, "tenant_id": self.tenant_id,
                    "kpi_id": d["kpi_id"], "period_start": d["period_start"],
                    "period_end": d["period_end"], "value": d["value"],
                    "dimensions": json.dumps(d.get("dimensions", {})),
                    "source": d.get("source"),
                },
            )
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc
        self.db.commit()
        invalidate_tenant_prefix("ctrl_timeseries", self.tenant_id)
        return self._fetch_one("domain_controlling.kpi_timeseries", item_id)

    def delete_timeseries(self, item_id: str) -> None:
        rows = self._exec(
            "DELETE FROM domain_controlling.kpi_timeseries WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": self.tenant_id, "id": item_id},
        )
        if not rows:
            raise EntityNotFoundError("Timeseries", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_timeseries", self.tenant_id)

    # ── Actions ──────────────────────────────────────────────────────────────

    def list_actions(self, status: Optional[str] = None) -> list[dict[str, Any]]:
        where = ["tenant_id=:tenant_id"]
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        if status:
            where.append("status=:status")
            params["status"] = status
        return self._list(
            f"SELECT * FROM domain_controlling.controlling_actions WHERE {' AND '.join(where)} ORDER BY created_at DESC",
            params,
        )

    def create_action(self, d: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_controlling.controlling_actions
                    (id, tenant_id, kpi_id, dashboard_id, title, description, owner_user_id, status, due_date, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :kpi_id, :dashboard_id, :title, :description, :owner_user_id, :status, :due_date, NOW(), NOW())
                """),
                {
                    "id": item_id, "tenant_id": self.tenant_id,
                    "kpi_id": d.get("kpi_id"), "dashboard_id": d.get("dashboard_id"),
                    "title": d["title"], "description": d.get("description"),
                    "owner_user_id": d.get("owner_user_id"),
                    "status": d.get("status", "open"), "due_date": d.get("due_date"),
                },
            )
        except (OperationalError, ProgrammingError) as exc:
            self.db.rollback()
            raise ControllingSchemaError() from exc
        self.db.commit()
        invalidate_tenant_prefix("ctrl_actions", self.tenant_id)
        return self._fetch_one("domain_controlling.controlling_actions", item_id)

    def update_action(self, item_id: str, d: dict[str, Any]) -> dict[str, Any]:
        rows = self._exec(
            """
            UPDATE domain_controlling.controlling_actions
            SET kpi_id=:kpi_id, dashboard_id=:dashboard_id, title=:title, description=:description,
                owner_user_id=:owner_user_id, status=:status, due_date=:due_date, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """,
            {
                "tenant_id": self.tenant_id, "id": item_id,
                "kpi_id": d.get("kpi_id"), "dashboard_id": d.get("dashboard_id"),
                "title": d["title"], "description": d.get("description"),
                "owner_user_id": d.get("owner_user_id"),
                "status": d.get("status", "open"), "due_date": d.get("due_date"),
            },
        )
        if not rows:
            raise EntityNotFoundError("Action", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_actions", self.tenant_id)
        return self._fetch_one("domain_controlling.controlling_actions", item_id)

    def delete_action(self, item_id: str) -> None:
        rows = self._exec(
            "DELETE FROM domain_controlling.controlling_actions WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": self.tenant_id, "id": item_id},
        )
        if not rows:
            raise EntityNotFoundError("Action", item_id)
        self.db.commit()
        invalidate_tenant_prefix("ctrl_actions", self.tenant_id)
