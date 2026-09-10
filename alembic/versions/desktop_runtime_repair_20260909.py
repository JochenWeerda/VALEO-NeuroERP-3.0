"""Repair missing historical tables in a database already stamped at head.

Table definitions copied from the named historical migrations below. Only
CREATE TABLE/INDEX/SCHEMA statements are replayed, with IF NOT EXISTS. Existing
rows and tables are retained; historical demo seeds are deliberately excluded.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "desktop_runtime_repair_20260909"
down_revision = "inv_movement_type_register_20260825"
branch_labels = None
depends_on = None


def _create_table(name, *columns, schema=None, **kwargs):
    # Alembic 1.13 does not support create_table(if_not_exists=True).
    if not sa.inspect(op.get_bind()).has_table(name, schema=schema):
        op.create_table(name, *columns, schema=schema, **kwargs)


def _create_index(name, table_name, columns, schema=None, **kwargs):
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name, schema=schema)
    if not any(index["name"] == name for index in indexes):
        op.create_index(name, table_name, columns, schema=schema, **kwargs)


# Source: admin_api_keys_20260215.py
def _admin_api_keys_20260215() -> None:
    _create_table(
        "api_keys",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=24), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column(
            "scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "ip_allowlist",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_api_keys_tenant_name"),
        sa.CheckConstraint(
            "status IN ('active','revoked','expired')", name="chk_api_keys_status"
        ),
        sa.CheckConstraint(
            "rate_limit_per_minute IS NULL OR rate_limit_per_minute > 0",
            name="chk_api_keys_rate_limit_positive",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_api_keys_tenant_status",
        "api_keys",
        ["tenant_id", "status"],
        unique=False,
        schema="domain_shared",
    )
    _create_index(
        "ix_api_keys_prefix",
        "api_keys",
        ["key_prefix"],
        unique=False,
        schema="domain_shared",
    )


# Source: admin_devices_output_profiles_20260215.py
def _admin_devices_output_profiles_20260215() -> None:
    _create_table(
        "admin_devices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("device_type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("vendor", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("station_code", sa.String(length=80), nullable=True),
        sa.Column("connection_uri", sa.String(length=255), nullable=True),
        sa.Column(
            "capabilities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "device_type IN ('printer','scanner')", name="chk_admin_devices_type"
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_devices_tenant_type_active",
        "admin_devices",
        ["tenant_id", "device_type", "is_active"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_device_mappings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("device_id", sa.String(), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column(
            "output_format", sa.String(length=20), nullable=False, server_default="pdf"
        ),
        sa.Column("copies", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["domain_shared.admin_devices.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "copies >= 1 AND copies <= 20", name="chk_admin_device_mappings_copies"
        ),
        sa.CheckConstraint(
            "output_format IN ('pdf','zpl','epl','raw')",
            name="chk_admin_device_mappings_format",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "device_id",
            "document_type",
            "process_code",
            "output_format",
            name="uq_admin_device_mappings_device_doc_process_format",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_device_mappings_tenant_doc_process",
        "admin_device_mappings",
        ["tenant_id", "document_type", "process_code"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_output_templates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("template_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column(
            "output_format", sa.String(length=20), nullable=False, server_default="pdf"
        ),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "template_code", name="uq_admin_output_templates_tenant_code"
        ),
        sa.CheckConstraint(
            "output_format IN ('pdf','zpl','epl','html','txt')",
            name="chk_admin_output_templates_format",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_output_templates_tenant_doc",
        "admin_output_templates",
        ["tenant_id", "document_type", "is_active"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_output_template_versions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("template_id", sa.String(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("change_note", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["domain_shared.admin_output_templates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "template_id",
            "version_no",
            name="uq_admin_output_template_versions_template_version",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_output_template_versions_tenant_template",
        "admin_output_template_versions",
        ["tenant_id", "template_id", "version_no"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_output_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("profile_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column("template_id", sa.String(), nullable=True),
        sa.Column("device_id", sa.String(), nullable=True),
        sa.Column(
            "output_channel",
            sa.String(length=20),
            nullable=False,
            server_default="print",
        ),
        sa.Column(
            "archive_mode", sa.String(length=20), nullable=False, server_default="dms"
        ),
        sa.Column("archive_retention_days", sa.Integer(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["domain_shared.admin_output_templates.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["domain_shared.admin_devices.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "profile_code", name="uq_admin_output_profiles_tenant_code"
        ),
        sa.CheckConstraint(
            "output_channel IN ('print','email','dms','pdf')",
            name="chk_admin_output_profiles_channel",
        ),
        sa.CheckConstraint(
            "archive_mode IN ('none','dms','worm')",
            name="chk_admin_output_profiles_archive_mode",
        ),
        sa.CheckConstraint(
            "archive_retention_days IS NULL OR archive_retention_days >= 0",
            name="chk_admin_output_profiles_retention_non_negative",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_output_profiles_tenant_doc_process",
        "admin_output_profiles",
        ["tenant_id", "document_type", "process_code", "is_active"],
        unique=False,
        schema="domain_shared",
    )


# Source: admin_mobile_routing_connectors_20260215.py
def _admin_mobile_routing_connectors_20260215() -> None:
    _create_table(
        "admin_stations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("station_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "station_type",
            sa.String(length=30),
            nullable=False,
            server_default="workstation",
        ),
        sa.Column("location_name", sa.String(length=120), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "station_code", name="uq_admin_stations_tenant_code"
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_stations_tenant_active",
        "admin_stations",
        ["tenant_id", "is_active", "station_type"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_station_devices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("station_id", sa.String(), nullable=False),
        sa.Column("device_id", sa.String(), nullable=False),
        sa.Column("device_role", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_fallback", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["station_id"], ["domain_shared.admin_stations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["domain_shared.admin_devices.id"], ondelete="CASCADE"
        ),
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
    _create_index(
        "ix_admin_station_devices_tenant_station_role",
        "admin_station_devices",
        ["tenant_id", "station_id", "device_role", "priority"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_routing_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("station_id", sa.String(), nullable=True),
        sa.Column("device_id", sa.String(), nullable=True),
        sa.Column("output_profile_id", sa.String(), nullable=True),
        sa.Column(
            "conditions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["station_id"], ["domain_shared.admin_stations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["domain_shared.admin_devices.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["output_profile_id"],
            ["domain_shared.admin_output_profiles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "rule_code", name="uq_admin_routing_rules_tenant_code"
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_routing_rules_tenant_doc_proc",
        "admin_routing_rules",
        ["tenant_id", "document_type", "process_code", "is_active", "priority"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_scan_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("profile_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "source_type", sa.String(length=20), nullable=False, server_default="camera"
        ),
        sa.Column("target_action", sa.String(length=80), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "barcode_formats",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "parse_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "validation_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "error_mode", sa.String(length=20), nullable=False, server_default="dialog"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "profile_code", name="uq_admin_scan_profiles_tenant_code"
        ),
        sa.CheckConstraint(
            "source_type IN ('camera','rugged','scanner')",
            name="chk_admin_scan_profiles_source_type",
        ),
        sa.CheckConstraint(
            "error_mode IN ('dialog','quarantine','reject')",
            name="chk_admin_scan_profiles_error_mode",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_scan_profiles_tenant_active",
        "admin_scan_profiles",
        ["tenant_id", "is_active", "source_type"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_mobile_devices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("device_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "device_type",
            sa.String(length=30),
            nullable=False,
            server_default="smartphone",
        ),
        sa.Column(
            "ownership_type",
            sa.String(length=20),
            nullable=False,
            server_default="company",
        ),
        sa.Column(
            "platform", sa.String(length=20), nullable=False, server_default="android"
        ),
        sa.Column("os_version", sa.String(length=60), nullable=True),
        sa.Column("app_version", sa.String(length=60), nullable=True),
        sa.Column("station_id", sa.String(), nullable=True),
        sa.Column("scan_profile_id", sa.String(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "capabilities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["station_id"], ["domain_shared.admin_stations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["scan_profile_id"],
            ["domain_shared.admin_scan_profiles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "device_code", name="uq_admin_mobile_devices_tenant_code"
        ),
        sa.CheckConstraint(
            "status IN ('active','blocked','retired')",
            name="chk_admin_mobile_devices_status",
        ),
        sa.CheckConstraint(
            "ownership_type IN ('company','byod')",
            name="chk_admin_mobile_devices_ownership",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_mobile_devices_tenant_status",
        "admin_mobile_devices",
        ["tenant_id", "status", "is_active"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_connector_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("config_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("connector_type", sa.String(length=40), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
        sa.Column(
            "auth_type", sa.String(length=30), nullable=False, server_default="api_key"
        ),
        sa.Column(
            "credentials",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "mapping",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "retry_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("last_health_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "config_code", name="uq_admin_connector_configs_tenant_code"
        ),
        sa.CheckConstraint(
            "status IN ('active','inactive','error')",
            name="chk_admin_connector_configs_status",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_connector_configs_tenant_type_status",
        "admin_connector_configs",
        ["tenant_id", "connector_type", "status"],
        unique=False,
        schema="domain_shared",
    )
    _create_table(
        "admin_connector_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("connector_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ok"),
        sa.Column("message", sa.String(length=255), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["connector_id"],
            ["domain_shared.admin_connector_configs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('ok','warning','error')",
            name="chk_admin_connector_events_status",
        ),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_connector_events_tenant_connector_time",
        "admin_connector_events",
        ["tenant_id", "connector_id", "created_at"],
        unique=False,
        schema="domain_shared",
    )


# Source: inventory_charge_lineage_20260215.py
def _inventory_charge_lineage_20260215() -> None:
    _create_table(
        "charge_lineage_links",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("from_charge", sa.String(length=64), nullable=False),
        sa.Column("to_charge", sa.String(length=64), nullable=False),
        sa.Column(
            "process_type", sa.String(length=20), nullable=False, server_default="mix"
        ),
        sa.Column("quantity_share", sa.Numeric(14, 3), nullable=False),
        sa.Column("share_percent", sa.Numeric(7, 3), nullable=True),
        sa.Column("source_movement_id", sa.String(), nullable=True),
        sa.Column("target_movement_id", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["source_movement_id"],
            ["domain_inventory.inventory_stock_movements.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["target_movement_id"],
            ["domain_inventory.inventory_stock_movements.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "process_type IN ('mix','withdrawal','split','transfer')",
            name="chk_charge_lineage_process_type",
        ),
        sa.CheckConstraint(
            "quantity_share > 0", name="chk_charge_lineage_qty_positive"
        ),
        sa.CheckConstraint(
            "share_percent IS NULL OR (share_percent >= 0 AND share_percent <= 100)",
            name="chk_charge_lineage_share_range",
        ),
        schema="domain_inventory",
    )
    _create_index(
        "ix_charge_lineage_tenant_to_charge",
        "charge_lineage_links",
        ["tenant_id", "to_charge"],
        unique=False,
        schema="domain_inventory",
    )
    _create_index(
        "ix_charge_lineage_tenant_from_charge",
        "charge_lineage_links",
        ["tenant_id", "from_charge"],
        unique=False,
        schema="domain_inventory",
    )


# Source: consignment_storage_fee_engine_20260215.py
def _consignment_storage_fee_engine_20260215() -> None:
    _create_table(
        "consignment_storage_fee_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column(
            "run_type",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'post'"),
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'running'"),
        ),
        sa.Column("idempotency_key", sa.String(length=120), nullable=True),
        sa.Column("posting_date", sa.Date(), nullable=True),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'EUR'"),
        ),
        sa.Column(
            "total_items", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(14, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("journal_entry_id", sa.String(length=64), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "run_type IN ('preview', 'post')",
            name="chk_consignment_storage_fee_runs_run_type",
        ),
        sa.CheckConstraint(
            "status IN ('running', 'posted', 'failed', 'preview')",
            name="chk_consignment_storage_fee_runs_status",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "period_month",
            "run_type",
            name="uq_consignment_storage_fee_runs_tenant_period_type",
        ),
        schema="domain_inventory",
    )
    _create_index(
        "ix_consignment_storage_fee_runs_tenant_period",
        "consignment_storage_fee_runs",
        ["tenant_id", "period_month"],
        unique=False,
        schema="domain_inventory",
    )
    _create_table(
        "consignment_storage_fee_charges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("owner_partner_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("warehouse_id", sa.String(length=64), nullable=False),
        sa.Column("charge", sa.String(length=64), nullable=True),
        sa.Column("basis_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("monthly_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'EUR'"),
        ),
        sa.Column(
            "calculation_details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["domain_inventory.consignment_storage_fee_runs.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "basis_quantity >= 0",
            name="chk_consignment_storage_fee_charges_basis_qty_non_negative",
        ),
        sa.CheckConstraint(
            "monthly_rate >= 0",
            name="chk_consignment_storage_fee_charges_rate_non_negative",
        ),
        sa.CheckConstraint(
            "amount >= 0",
            name="chk_consignment_storage_fee_charges_amount_non_negative",
        ),
        schema="domain_inventory",
    )
    _create_index(
        "ix_consignment_storage_fee_charges_run_id",
        "consignment_storage_fee_charges",
        ["run_id"],
        unique=False,
        schema="domain_inventory",
    )
    _create_index(
        "ix_consignment_storage_fee_charges_owner_partner_id",
        "consignment_storage_fee_charges",
        ["owner_partner_id"],
        unique=False,
        schema="domain_inventory",
    )
    _create_index(
        "ix_consignment_storage_fee_charges_tenant_owner_article",
        "consignment_storage_fee_charges",
        ["tenant_id", "owner_partner_id", "article_id"],
        unique=False,
        schema="domain_inventory",
    )


# Source: hr_training_onboarding_module_20260215.py
def _hr_training_onboarding_module_20260215() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_hr"))
    _create_table(
        "training_courses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("course_code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("topic", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "mandatory", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")
        ),
        sa.Column("validity_months", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column(
            "delivery_mode",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'classroom'"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "course_code", name="uq_hr_training_courses_tenant_course_code"
        ),
        sa.CheckConstraint(
            "delivery_mode IN ('classroom','elearning','blended','external')",
            name="ck_hr_training_courses_delivery_mode",
        ),
        sa.CheckConstraint(
            "validity_months IS NULL OR validity_months >= 0",
            name="ck_hr_training_courses_validity_months_non_negative",
        ),
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_training_courses_tenant_active",
        "training_courses",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_hr",
    )
    _create_table(
        "training_assignments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("assigned_by", sa.String(length=80), nullable=True),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'assigned'"),
        ),
        sa.Column("score_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_url", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["domain_hr.training_courses.id"],
            ondelete="CASCADE",
            name="fk_hr_training_assignments_course",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "course_id",
            "employee_ref",
            name="uq_hr_training_assignments_tenant_course_employee",
        ),
        sa.CheckConstraint(
            "status IN ('assigned','in_progress','completed','overdue','waived')",
            name="ck_hr_training_assignments_status",
        ),
        sa.CheckConstraint(
            "score_percent IS NULL OR (score_percent >= 0 AND score_percent <= 100)",
            name="ck_hr_training_assignments_score_range",
        ),
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_training_assignments_tenant_employee",
        "training_assignments",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )
    _create_table(
        "employee_certificates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("certificate_type", sa.String(length=80), nullable=False),
        sa.Column("certificate_name", sa.String(length=160), nullable=False),
        sa.Column("certificate_number", sa.String(length=120), nullable=True),
        sa.Column("issuer", sa.String(length=160), nullable=True),
        sa.Column("issued_at", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'valid'"),
        ),
        sa.Column("document_url", sa.String(length=255), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('valid','expired','revoked','pending_renewal')",
            name="ck_hr_employee_certificates_status",
        ),
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_employee_certificates_tenant_employee",
        "employee_certificates",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_employee_certificates_valid_until",
        "employee_certificates",
        ["tenant_id", "valid_until"],
        unique=False,
        schema="domain_hr",
    )
    _create_table(
        "qualification_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("role_code", sa.String(length=80), nullable=False),
        sa.Column(
            "qualification_level",
            sa.String(length=40),
            nullable=False,
            server_default=sa.text("'basic'"),
        ),
        sa.Column(
            "skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "employee_ref",
            "role_code",
            name="uq_hr_qualification_profiles_tenant_employee_role",
        ),
        sa.CheckConstraint(
            "qualification_level IN ('basic','advanced','expert')",
            name="ck_hr_qualification_profiles_level",
        ),
        schema="domain_hr",
    )
    _create_table(
        "onboarding_checklists",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("checklist_code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("role_scope", sa.String(length=80), nullable=True),
        sa.Column(
            "tasks",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "checklist_code",
            name="uq_hr_onboarding_checklists_tenant_code",
        ),
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_onboarding_checklists_tenant_active",
        "onboarding_checklists",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_hr",
    )
    _create_table(
        "onboarding_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("checklist_id", sa.String(), nullable=False),
        sa.Column("employee_ref", sa.String(length=80), nullable=False),
        sa.Column("assigned_by", sa.String(length=80), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'not_started'"),
        ),
        sa.Column(
            "progress_percent",
            sa.Numeric(5, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "state",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["checklist_id"],
            ["domain_hr.onboarding_checklists.id"],
            ondelete="CASCADE",
            name="fk_hr_onboarding_runs_checklist",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "checklist_id",
            "employee_ref",
            name="uq_hr_onboarding_runs_tenant_checklist_employee",
        ),
        sa.CheckConstraint(
            "status IN ('not_started','in_progress','completed','cancelled')",
            name="ck_hr_onboarding_runs_status",
        ),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_hr_onboarding_runs_progress",
        ),
        schema="domain_hr",
    )
    _create_index(
        "idx_hr_onboarding_runs_tenant_employee",
        "onboarding_runs",
        ["tenant_id", "employee_ref", "status"],
        unique=False,
        schema="domain_hr",
    )


# Source: log_frachtbriefe_20260626.py
def _log_frachtbriefe_20260626() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_logistics")
    _create_table(
        "frachtbriefe",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("nummer", sa.String(60), nullable=False),
        sa.Column("kennzeichen", sa.String(20), nullable=True),
        sa.Column("artikel", sa.String(120), nullable=True),
        sa.Column("menge", sa.Numeric(12, 3), nullable=True),
        sa.Column("absender", sa.String(120), nullable=True),
        sa.Column("empfaenger", sa.String(120), nullable=True),
        sa.Column("datum", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="erstellt"),
        sa.Column("tour_id", sa.String(36), nullable=True),
        sa.Column("lieferschein_ref", sa.String(60), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('erstellt','unterwegs','zugestellt','storniert')",
            name="chk_frachtbriefe_status",
        ),
        sa.UniqueConstraint(
            "tenant_id", "nummer", name="uq_frachtbriefe_tenant_nummer"
        ),
        schema="domain_logistics",
    )
    _create_index(
        "ix_frachtbriefe_tenant_datum",
        "frachtbriefe",
        ["tenant_id", "datum"],
        schema="domain_logistics",
    )


# Source: einkauf_ls_opportunities_repair_20260626.py
def _opportunities() -> None:
    op.execute(
        sa.text(
            "\n        CREATE TABLE IF NOT EXISTS opportunities (\n            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,\n            tenant_id           VARCHAR(64),\n            title               VARCHAR(255)    NOT NULL,\n            stage               TEXT            NOT NULL DEFAULT 'LEAD',\n            probability         FLOAT           DEFAULT 25,\n            expected_close_date DATE,\n            amount              NUMERIC,\n            stage_history       JSONB           NOT NULL DEFAULT '[]'::jsonb,\n            customer_id         VARCHAR(64),\n            customer_name       VARCHAR(255),\n            assigned_to         VARCHAR(120),\n            notes               TEXT,\n            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),\n            updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()\n        )\n    "
        )
    )
    op.execute(
        sa.text(
            "\n        CREATE INDEX IF NOT EXISTS ix_opportunities_tenant_stage\n            ON opportunities (tenant_id, stage)\n    "
        )
    )
    op.execute(
        sa.text(
            "\n        CREATE INDEX IF NOT EXISTS ix_opportunities_customer\n            ON opportunities (customer_id)\n    "
        )
    )
    op.execute(
        sa.text(
            "\n        CREATE INDEX IF NOT EXISTS ix_opportunities_assigned\n            ON opportunities (assigned_to)\n    "
        )
    )


# Source: admin_report_permissions_20260215.py
def _admin_report_permissions_20260215() -> None:
    _create_table(
        "admin_report_permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(length=64), nullable=False),
        sa.Column("report_key", sa.String(length=120), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("can_export", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "role_id", "report_key", name="uq_admin_report_permissions_role_report"),
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_report_permissions_tenant_role",
        "admin_report_permissions",
        ["tenant_id", "role_id", "active"],
        unique=False,
        schema="domain_shared",
    )
    _create_index(
        "ix_admin_report_permissions_tenant_report",
        "admin_report_permissions",
        ["tenant_id", "report_key", "active"],
        unique=False,
        schema="domain_shared",
    )


def upgrade() -> None:
    _admin_report_permissions_20260215()
    _admin_api_keys_20260215()
    _admin_devices_output_profiles_20260215()
    _admin_mobile_routing_connectors_20260215()
    _inventory_charge_lineage_20260215()
    _consignment_storage_fee_engine_20260215()
    _hr_training_onboarding_module_20260215()
    _log_frachtbriefe_20260626()
    _opportunities()
    op.execute(
        "ALTER TABLE domain_shared.users ADD COLUMN IF NOT EXISTS preferences JSONB NOT NULL DEFAULT '{}'::jsonb"
    )


def downgrade() -> None:
    raise RuntimeError(
        "Additive repair: automatic downgrade would delete pre-existing business tables."
    )
