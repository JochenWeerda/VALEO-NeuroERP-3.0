"""HR planning tables — employee_time_profiles, calendar_events, payroll_exports,
campaign_capacity_plans, field_service_plans, driver_timesheets.

These tables back the personal/HR planning endpoints in
``app/services/personal_service.py`` (work plan, calendar, payroll export,
campaign capacity, field service, driver timesheets). The endpoints already
existed but had no schema migration, so every call returned HTTP 500
(``UndefinedTable``). This migration creates the missing tables in the existing
``domain_hr`` schema, following its conventions (VARCHAR id/tenant_id,
TIMESTAMPTZ timestamps, JSONB for structured columns).

Revision ID: hr_planning_tables_20260625
Revises: wf_cockpit_persist_20260625
Create Date: 2026-06-25
"""
from alembic import op

revision = "hr_planning_tables_20260625"
down_revision = "wf_cockpit_persist_20260625"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_hr")

    # ── employee_time_profiles ────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.employee_time_profiles (
            id                  VARCHAR PRIMARY KEY,
            tenant_id           VARCHAR NOT NULL,
            employee_ref        VARCHAR(120) NOT NULL,
            display_name        VARCHAR(255),
            role_code           VARCHAR(80),
            role_label          VARCHAR(255),
            location_code       VARCHAR(80),
            department          VARCHAR(255),
            manager_ref         VARCHAR(120),
            employment_type     VARCHAR(80),
            weekly_hours        NUMERIC(6,2),
            time_model          VARCHAR(80),
            cost_center         VARCHAR(80),
            payroll_group       VARCHAR(80),
            qualifications      JSONB NOT NULL DEFAULT '[]'::jsonb,
            can_drive           BOOLEAN NOT NULL DEFAULT FALSE,
            driver_card_id      VARCHAR(120),
            vehicle_refs        JSONB NOT NULL DEFAULT '[]'::jsonb,
            calendar_provider   VARCHAR(80),
            status              VARCHAR(40) NOT NULL DEFAULT 'active',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_etp_tenant ON domain_hr.employee_time_profiles (tenant_id)"
    )

    # ── calendar_events ───────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.calendar_events (
            id                  VARCHAR PRIMARY KEY,
            tenant_id           VARCHAR NOT NULL,
            source_system       VARCHAR(80),
            provider            VARCHAR(80),
            external_event_ref  VARCHAR(255),
            event_type          VARCHAR(80),
            title               VARCHAR(255),
            employee_ref        VARCHAR(120),
            resource_ref        VARCHAR(120),
            starts_at           TIMESTAMPTZ,
            ends_at             TIMESTAMPTZ,
            timezone            VARCHAR(80),
            visibility          VARCHAR(40),
            status              VARCHAR(40) NOT NULL DEFAULT 'confirmed',
            sync_state          VARCHAR(40),
            conflict_level      VARCHAR(40),
            source_ref          VARCHAR(255),
            metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_cal_tenant_time ON domain_hr.calendar_events (tenant_id, starts_at)"
    )

    # ── payroll_exports ───────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.payroll_exports (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            period_from     DATE NOT NULL,
            period_to       DATE NOT NULL,
            target_system   VARCHAR(80),
            status          VARCHAR(40) NOT NULL DEFAULT 'Draft',
            items           JSONB NOT NULL DEFAULT '[]'::jsonb,
            blockers        JSONB NOT NULL DEFAULT '[]'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by      VARCHAR(120)
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_payroll_tenant ON domain_hr.payroll_exports (tenant_id)"
    )

    # ── campaign_capacity_plans ───────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.campaign_capacity_plans (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            campaign_code   VARCHAR(80) NOT NULL,
            name            VARCHAR(255),
            period_from     DATE NOT NULL,
            period_to       DATE NOT NULL,
            location_code   VARCHAR(80),
            role_demand     JSONB NOT NULL DEFAULT '{}'::jsonb,
            expected_volume NUMERIC(12,2),
            status          VARCHAR(40) NOT NULL DEFAULT 'Draft',
            findings        JSONB NOT NULL DEFAULT '[]'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_campaign_tenant ON domain_hr.campaign_capacity_plans (tenant_id)"
    )

    # ── field_service_plans ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.field_service_plans (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            employee_ref    VARCHAR(120),
            customer_ref    VARCHAR(120),
            territory_code  VARCHAR(80),
            campaign_code   VARCHAR(80),
            visit_type      VARCHAR(80),
            starts_at       TIMESTAMPTZ,
            ends_at         TIMESTAMPTZ,
            status          VARCHAR(40) NOT NULL DEFAULT 'planned',
            conflicts       JSONB NOT NULL DEFAULT '[]'::jsonb,
            notes           TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_fsp_tenant_time ON domain_hr.field_service_plans (tenant_id, starts_at)"
    )

    # ── driver_timesheets ─────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.driver_timesheets (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            entry_date      DATE NOT NULL,
            driver_name     VARCHAR(255),
            vehicle_plate   VARCHAR(80),
            tours           JSONB NOT NULL DEFAULT '[]'::jsonb,
            total_hours     NUMERIC(6,2) NOT NULL DEFAULT 0,
            overtime_hours  NUMERIC(6,2) NOT NULL DEFAULT 0,
            signature_data  TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_hr_driver_ts_tenant ON domain_hr.driver_timesheets (tenant_id, entry_date)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_hr.driver_timesheets")
    op.execute("DROP TABLE IF EXISTS domain_hr.field_service_plans")
    op.execute("DROP TABLE IF EXISTS domain_hr.campaign_capacity_plans")
    op.execute("DROP TABLE IF EXISTS domain_hr.payroll_exports")
    op.execute("DROP TABLE IF EXISTS domain_hr.calendar_events")
    op.execute("DROP TABLE IF EXISTS domain_hr.employee_time_profiles")
