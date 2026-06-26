"""ALEMBIC-MERGE-001: Admin-Mobile + Charge-Lineage Repair-Migration.

Die Migrations admin_devices_output_profiles_20260215, admin_mobile_routing_connectors_20260215,
admin_api_keys_20260215 und inventory_charge_lineage_20260215 liegen in Parallel-Branches
ausserhalb der Hauptkette. Diese Repair-Migration legt alle betroffenen Tabellen
idempotent (IF NOT EXISTS) in der Hauptkette an.

Revision ID: admin_mobile_repair_20260626
Revises: log_frachtbriefe_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "admin_mobile_repair_20260626"
down_revision = "log_frachtbriefe_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── domain_shared schema ────────────────────────────────────────────────
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_shared"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_inventory"))

    # admin_devices (from admin_devices_output_profiles_20260215)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_devices (
            id          VARCHAR NOT NULL PRIMARY KEY,
            tenant_id   VARCHAR NOT NULL,
            device_type VARCHAR(20) NOT NULL,
            name        VARCHAR(120) NOT NULL,
            vendor      VARCHAR(120),
            model       VARCHAR(120),
            station_code VARCHAR(80),
            ip_address  VARCHAR(60),
            mac_address VARCHAR(40),
            serial_number VARCHAR(80),
            firmware_version VARCHAR(60),
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            settings    JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_devices_type CHECK (device_type IN ('printer','scanner'))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_devices_tenant_type_active
            ON domain_shared.admin_devices (tenant_id, device_type, is_active)
    """))

    # admin_device_mappings
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_device_mappings (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            device_id       VARCHAR NOT NULL,
            context_type    VARCHAR(60) NOT NULL,
            context_value   VARCHAR(120),
            copies          INTEGER NOT NULL DEFAULT 1,
            is_default      BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_device_mappings_copies CHECK (copies >= 1 AND copies <= 20)
        )
    """))

    # admin_output_profiles
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_output_profiles (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            profile_code    VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            output_type     VARCHAR(30) NOT NULL DEFAULT 'pdf',
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            settings        JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # admin_output_templates
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_output_templates (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            template_code   VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            document_type   VARCHAR(60) NOT NULL,
            engine          VARCHAR(30) NOT NULL DEFAULT 'jinja2',
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # admin_output_template_versions
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_output_template_versions (
            id              VARCHAR NOT NULL PRIMARY KEY,
            template_id     VARCHAR NOT NULL,
            version         INTEGER NOT NULL DEFAULT 1,
            content         TEXT,
            is_active       BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # admin_report_permissions
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_report_permissions (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            report_code     VARCHAR(80) NOT NULL,
            role            VARCHAR(80) NOT NULL,
            can_view        BOOLEAN NOT NULL DEFAULT TRUE,
            can_export      BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))

    # admin_api_keys
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_api_keys (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            key_hash        VARCHAR(128) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            scopes          JSONB NOT NULL DEFAULT '[]'::jsonb,
            expires_at      TIMESTAMPTZ,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            last_used_at    TIMESTAMPTZ,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_api_keys_tenant_hash
            ON domain_shared.admin_api_keys (tenant_id, key_hash)
    """))

    # admin_stations
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_stations (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            station_code    VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            station_type    VARCHAR(30) NOT NULL DEFAULT 'workstation',
            location_name   VARCHAR(120),
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            settings        JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_stations_tenant_code
            ON domain_shared.admin_stations (tenant_id, station_code)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_stations_tenant_active
            ON domain_shared.admin_stations (tenant_id, is_active, station_type)
    """))

    # admin_station_devices
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_station_devices (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            station_id      VARCHAR NOT NULL,
            device_id       VARCHAR NOT NULL,
            device_role     VARCHAR(40) NOT NULL,
            priority        INTEGER NOT NULL DEFAULT 1,
            is_fallback     BOOLEAN NOT NULL DEFAULT FALSE,
            settings        JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_station_devices_priority CHECK (priority >= 1)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_station_devices_tenant_station_role
            ON domain_shared.admin_station_devices (tenant_id, station_id, device_role, priority)
    """))

    # admin_routing_rules
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_routing_rules (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            rule_code       VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            document_type   VARCHAR(60) NOT NULL,
            process_code    VARCHAR(60) NOT NULL,
            priority        INTEGER NOT NULL DEFAULT 100,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            station_id      VARCHAR,
            device_id       VARCHAR,
            output_profile_id VARCHAR,
            conditions      JSONB NOT NULL DEFAULT '{}'::jsonb,
            actions         JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_routing_rules_tenant_code
            ON domain_shared.admin_routing_rules (tenant_id, rule_code)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_routing_rules_tenant_doc_proc
            ON domain_shared.admin_routing_rules (tenant_id, document_type, process_code, is_active, priority)
    """))

    # admin_scan_profiles
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_scan_profiles (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            profile_code    VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            source_type     VARCHAR(20) NOT NULL DEFAULT 'camera',
            target_action   VARCHAR(80) NOT NULL,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            barcode_formats JSONB NOT NULL DEFAULT '[]'::jsonb,
            parse_rules     JSONB NOT NULL DEFAULT '{}'::jsonb,
            validation_rules JSONB NOT NULL DEFAULT '{}'::jsonb,
            error_mode      VARCHAR(20) NOT NULL DEFAULT 'dialog',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_scan_profiles_source_type
                CHECK (source_type IN ('camera','rugged','scanner')),
            CONSTRAINT chk_admin_scan_profiles_error_mode
                CHECK (error_mode IN ('dialog','quarantine','reject'))
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_scan_profiles_tenant_code
            ON domain_shared.admin_scan_profiles (tenant_id, profile_code)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_scan_profiles_tenant_active
            ON domain_shared.admin_scan_profiles (tenant_id, is_active, source_type)
    """))

    # admin_mobile_devices
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_mobile_devices (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            device_code     VARCHAR(80) NOT NULL,
            name            VARCHAR(120) NOT NULL,
            device_type     VARCHAR(30) NOT NULL DEFAULT 'smartphone',
            ownership_type  VARCHAR(20) NOT NULL DEFAULT 'company',
            platform        VARCHAR(20) NOT NULL DEFAULT 'android',
            os_version      VARCHAR(60),
            app_version     VARCHAR(60),
            station_id      VARCHAR,
            scan_profile_id VARCHAR,
            status          VARCHAR(20) NOT NULL DEFAULT 'active',
            last_sync_at    TIMESTAMPTZ,
            capabilities    JSONB NOT NULL DEFAULT '{}'::jsonb,
            settings        JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_mobile_devices_status
                CHECK (status IN ('active','blocked','retired')),
            CONSTRAINT chk_admin_mobile_devices_ownership
                CHECK (ownership_type IN ('company','byod'))
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_mobile_devices_tenant_code
            ON domain_shared.admin_mobile_devices (tenant_id, device_code)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_mobile_devices_tenant_status
            ON domain_shared.admin_mobile_devices (tenant_id, status, is_active)
    """))

    # admin_connector_configs
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_connector_configs (
            id                  VARCHAR NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR NOT NULL,
            config_code         VARCHAR(80) NOT NULL,
            name                VARCHAR(120) NOT NULL,
            connector_type      VARCHAR(40) NOT NULL,
            status              VARCHAR(20) NOT NULL DEFAULT 'active',
            auth_type           VARCHAR(30) NOT NULL DEFAULT 'api_key',
            credentials         JSONB NOT NULL DEFAULT '{}'::jsonb,
            scopes              JSONB NOT NULL DEFAULT '[]'::jsonb,
            mapping             JSONB NOT NULL DEFAULT '{}'::jsonb,
            retry_policy        JSONB NOT NULL DEFAULT '{}'::jsonb,
            rate_limit_per_minute INTEGER,
            last_health_at      TIMESTAMPTZ,
            last_error          TEXT,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_connector_configs_status
                CHECK (status IN ('active','inactive','error'))
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_admin_connector_configs_tenant_code
            ON domain_shared.admin_connector_configs (tenant_id, config_code)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_connector_configs_tenant_type_status
            ON domain_shared.admin_connector_configs (tenant_id, connector_type, status)
    """))

    # admin_connector_events
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.admin_connector_events (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            connector_id    VARCHAR NOT NULL,
            event_type      VARCHAR(60) NOT NULL,
            status          VARCHAR(20) NOT NULL DEFAULT 'ok',
            message         VARCHAR(255),
            payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
            retry_count     INTEGER NOT NULL DEFAULT 0,
            next_retry_at   TIMESTAMPTZ,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_admin_connector_events_status
                CHECK (status IN ('ok','warning','error'))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_admin_connector_events_tenant_connector_time
            ON domain_shared.admin_connector_events (tenant_id, connector_id, created_at)
    """))

    # ── domain_inventory: charge_lineage_links ──────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_inventory.charge_lineage_links (
            id                  VARCHAR NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64) NOT NULL,
            article_id          VARCHAR(64) NOT NULL,
            from_charge         VARCHAR(64) NOT NULL,
            to_charge           VARCHAR(64) NOT NULL,
            process_type        VARCHAR(20) NOT NULL DEFAULT 'mix',
            quantity_share      NUMERIC(14,3) NOT NULL,
            share_percent       NUMERIC(7,3),
            source_movement_id  VARCHAR,
            target_movement_id  VARCHAR,
            notes               TEXT,
            created_by          VARCHAR(100),
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_charge_lineage_process_type
                CHECK (process_type IN ('mix','withdrawal','split','transfer')),
            CONSTRAINT chk_charge_lineage_qty_positive
                CHECK (quantity_share > 0),
            CONSTRAINT chk_charge_lineage_share_range
                CHECK (share_percent IS NULL OR (share_percent >= 0 AND share_percent <= 100))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_charge_lineage_tenant_to_charge
            ON domain_inventory.charge_lineage_links (tenant_id, to_charge)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_charge_lineage_tenant_from_charge
            ON domain_inventory.charge_lineage_links (tenant_id, from_charge)
    """))

    # ── domain_inventory: storage_fee_runs ─────────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_inventory.storage_fee_runs (
            id              VARCHAR NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            run_date        DATE NOT NULL,
            warehouse_id    VARCHAR,
            status          VARCHAR(20) NOT NULL DEFAULT 'pending',
            total_fees      NUMERIC(14,2),
            processed_lots  INTEGER NOT NULL DEFAULT 0,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_storage_fee_runs_status
                CHECK (status IN ('pending','running','completed','failed'))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_storage_fee_runs_tenant_date
            ON domain_inventory.storage_fee_runs (tenant_id, run_date)
    """))


def downgrade() -> None:
    # Repair-Migrations werden nicht rueckgaengig gemacht (IF NOT EXISTS Pattern)
    pass
