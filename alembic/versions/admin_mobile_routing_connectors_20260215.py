"""admin stations, routing, mobile scan and connectors

Revision ID: admin_mobile_routing_connectors_20260215
Revises: admin_devices_output_profiles_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "admin_mobile_routing_connectors_20260215"
down_revision = "admin_devices_output_profiles_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_stations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("station_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("station_type", sa.String(length=30), nullable=False, server_default="workstation"),
        sa.Column("location_name", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "station_code", name="uq_admin_stations_tenant_code"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_stations_tenant_active",
        "admin_stations",
        ["tenant_id", "is_active", "station_type"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_station_devices",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("device_role", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_fallback", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["station_id"], ["domain_shared.admin_stations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["domain_shared.admin_devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "station_id",
            "device_id",
            "device_role",
            name="uq_admin_station_devices_station_device_role",
        ),
        sa.CheckConstraint("priority >= 1", name="chk_admin_station_devices_priority"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_station_devices_tenant_station_role",
        "admin_station_devices",
        ["tenant_id", "station_id", "device_role", "priority"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_routing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("station_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("output_profile_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["station_id"], ["domain_shared.admin_stations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_id"], ["domain_shared.admin_devices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["output_profile_id"], ["domain_shared.admin_output_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "rule_code", name="uq_admin_routing_rules_tenant_code"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_routing_rules_tenant_doc_proc",
        "admin_routing_rules",
        ["tenant_id", "document_type", "process_code", "is_active", "priority"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_scan_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("profile_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False, server_default="camera"),
        sa.Column("target_action", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("barcode_formats", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("parse_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("validation_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("error_mode", sa.String(length=20), nullable=False, server_default="dialog"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "profile_code", name="uq_admin_scan_profiles_tenant_code"),
        sa.CheckConstraint("source_type IN ('camera','rugged','scanner')", name="chk_admin_scan_profiles_source_type"),
        sa.CheckConstraint("error_mode IN ('dialog','quarantine','reject')", name="chk_admin_scan_profiles_error_mode"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_scan_profiles_tenant_active",
        "admin_scan_profiles",
        ["tenant_id", "is_active", "source_type"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_mobile_devices",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("device_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("device_type", sa.String(length=30), nullable=False, server_default="smartphone"),
        sa.Column("ownership_type", sa.String(length=20), nullable=False, server_default="company"),
        sa.Column("platform", sa.String(length=20), nullable=False, server_default="android"),
        sa.Column("os_version", sa.String(length=60), nullable=True),
        sa.Column("app_version", sa.String(length=60), nullable=True),
        sa.Column("station_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("scan_profile_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["station_id"], ["domain_shared.admin_stations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["scan_profile_id"], ["domain_shared.admin_scan_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "device_code", name="uq_admin_mobile_devices_tenant_code"),
        sa.CheckConstraint("status IN ('active','blocked','retired')", name="chk_admin_mobile_devices_status"),
        sa.CheckConstraint("ownership_type IN ('company','byod')", name="chk_admin_mobile_devices_ownership"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_mobile_devices_tenant_status",
        "admin_mobile_devices",
        ["tenant_id", "status", "is_active"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_connector_configs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("config_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("connector_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("auth_type", sa.String(length=30), nullable=False, server_default="api_key"),
        sa.Column("credentials", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("mapping", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("retry_policy", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("last_health_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "config_code", name="uq_admin_connector_configs_tenant_code"),
        sa.CheckConstraint("status IN ('active','inactive','error')", name="chk_admin_connector_configs_status"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_connector_configs_tenant_type_status",
        "admin_connector_configs",
        ["tenant_id", "connector_type", "status"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_connector_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("connector_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ok"),
        sa.Column("message", sa.String(length=255), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["connector_id"], ["domain_shared.admin_connector_configs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('ok','warning','error')", name="chk_admin_connector_events_status"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_connector_events_tenant_connector_time",
        "admin_connector_events",
        ["tenant_id", "connector_id", "created_at"],
        unique=False,
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_admin_connector_events_tenant_connector_time", table_name="admin_connector_events", schema="domain_shared")
    op.drop_table("admin_connector_events", schema="domain_shared")
    op.drop_index("ix_admin_connector_configs_tenant_type_status", table_name="admin_connector_configs", schema="domain_shared")
    op.drop_table("admin_connector_configs", schema="domain_shared")
    op.drop_index("ix_admin_mobile_devices_tenant_status", table_name="admin_mobile_devices", schema="domain_shared")
    op.drop_table("admin_mobile_devices", schema="domain_shared")
    op.drop_index("ix_admin_scan_profiles_tenant_active", table_name="admin_scan_profiles", schema="domain_shared")
    op.drop_table("admin_scan_profiles", schema="domain_shared")
    op.drop_index("ix_admin_routing_rules_tenant_doc_proc", table_name="admin_routing_rules", schema="domain_shared")
    op.drop_table("admin_routing_rules", schema="domain_shared")
    op.drop_index("ix_admin_station_devices_tenant_station_role", table_name="admin_station_devices", schema="domain_shared")
    op.drop_table("admin_station_devices", schema="domain_shared")
    op.drop_index("ix_admin_stations_tenant_active", table_name="admin_stations", schema="domain_shared")
    op.drop_table("admin_stations", schema="domain_shared")
