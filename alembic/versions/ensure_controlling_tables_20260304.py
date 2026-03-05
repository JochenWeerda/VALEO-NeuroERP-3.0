"""ensure controlling tables exist

Revision ID: ensure_controlling_tables_20260304
Revises: b7c8d9e0f1a2
Create Date: 2026-03-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "ensure_controlling_tables_20260304"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_controlling"))

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_controlling.kpi_definitions (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                kpi_code VARCHAR(80) NOT NULL,
                name VARCHAR(120) NOT NULL,
                description TEXT,
                formula TEXT,
                target_value NUMERIC(18,4),
                unit VARCHAR(30),
                ampel_logic JSONB NOT NULL DEFAULT '{}'::jsonb,
                filters JSONB NOT NULL DEFAULT '{}'::jsonb,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_controlling_kpi_code UNIQUE (tenant_id, kpi_code),
                CONSTRAINT fk_controlling_kpi_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE
            )
            """
        )
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_controlling_kpi_tenant_active ON domain_controlling.kpi_definitions (tenant_id, is_active)"))

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_controlling.dashboard_configs (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                dashboard_code VARCHAR(80) NOT NULL,
                name VARCHAR(120) NOT NULL,
                description TEXT,
                layout JSONB NOT NULL DEFAULT '{}'::jsonb,
                default_filters JSONB NOT NULL DEFAULT '{}'::jsonb,
                role_scope JSONB NOT NULL DEFAULT '[]'::jsonb,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_controlling_dashboard_code UNIQUE (tenant_id, dashboard_code),
                CONSTRAINT fk_controlling_dashboard_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE
            )
            """
        )
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_controlling_dashboards_tenant_active ON domain_controlling.dashboard_configs (tenant_id, is_active)"))

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_controlling.dashboard_widgets (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                dashboard_id VARCHAR NOT NULL,
                widget_type VARCHAR(40) NOT NULL,
                title VARCHAR(120) NOT NULL,
                kpi_id VARCHAR,
                position_x INTEGER NOT NULL DEFAULT 0,
                position_y INTEGER NOT NULL DEFAULT 0,
                size_w INTEGER NOT NULL DEFAULT 4,
                size_h INTEGER NOT NULL DEFAULT 3,
                settings JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT fk_controlling_widget_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE,
                CONSTRAINT fk_controlling_widget_dashboard FOREIGN KEY (dashboard_id)
                    REFERENCES domain_controlling.dashboard_configs(id) ON DELETE CASCADE,
                CONSTRAINT fk_controlling_widget_kpi FOREIGN KEY (kpi_id)
                    REFERENCES domain_controlling.kpi_definitions(id) ON DELETE SET NULL
            )
            """
        )
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_controlling_widgets_dashboard ON domain_controlling.dashboard_widgets (tenant_id, dashboard_id)"))

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_controlling.kpi_timeseries (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                kpi_id VARCHAR NOT NULL,
                period_start TIMESTAMPTZ NOT NULL,
                period_end TIMESTAMPTZ NOT NULL,
                value NUMERIC(18,4) NOT NULL,
                dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
                source VARCHAR(60),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT fk_controlling_timeseries_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE,
                CONSTRAINT fk_controlling_timeseries_kpi FOREIGN KEY (kpi_id)
                    REFERENCES domain_controlling.kpi_definitions(id) ON DELETE CASCADE
            )
            """
        )
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_controlling_timeseries_kpi_period ON domain_controlling.kpi_timeseries (tenant_id, kpi_id, period_start DESC)"))

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_controlling.controlling_actions (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                kpi_id VARCHAR,
                dashboard_id VARCHAR,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                owner_user_id VARCHAR,
                status VARCHAR(20) NOT NULL DEFAULT 'open',
                due_date TIMESTAMPTZ,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT chk_controlling_actions_status CHECK (status IN ('open', 'in_progress', 'done', 'cancelled')),
                CONSTRAINT fk_controlling_actions_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE,
                CONSTRAINT fk_controlling_actions_kpi FOREIGN KEY (kpi_id)
                    REFERENCES domain_controlling.kpi_definitions(id) ON DELETE SET NULL,
                CONSTRAINT fk_controlling_actions_dashboard FOREIGN KEY (dashboard_id)
                    REFERENCES domain_controlling.dashboard_configs(id) ON DELETE SET NULL
            )
            """
        )
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_controlling_actions_status_due ON domain_controlling.controlling_actions (tenant_id, status, due_date)"))


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS domain_controlling.ix_controlling_actions_status_due"))
    op.execute(sa.text("DROP TABLE IF EXISTS domain_controlling.controlling_actions"))
    op.execute(sa.text("DROP INDEX IF EXISTS domain_controlling.ix_controlling_timeseries_kpi_period"))
    op.execute(sa.text("DROP TABLE IF EXISTS domain_controlling.kpi_timeseries"))
    op.execute(sa.text("DROP INDEX IF EXISTS domain_controlling.ix_controlling_widgets_dashboard"))
    op.execute(sa.text("DROP TABLE IF EXISTS domain_controlling.dashboard_widgets"))
    op.execute(sa.text("DROP INDEX IF EXISTS domain_controlling.ix_controlling_dashboards_tenant_active"))
    op.execute(sa.text("DROP TABLE IF EXISTS domain_controlling.dashboard_configs"))
    op.execute(sa.text("DROP INDEX IF EXISTS domain_controlling.ix_controlling_kpi_tenant_active"))
    op.execute(sa.text("DROP TABLE IF EXISTS domain_controlling.kpi_definitions"))
