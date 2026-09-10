"""Repair the missing admin_report_permissions table on a DB stamped at head.

Same situation as ``desktop_runtime_repair_20260909``: the database carries the
head revision, but the table from ``admin_report_permissions_20260215`` is not
present, so ``GET /api/v1/admin/report-permissions`` fails with UndefinedTable.

Additive only: the table definition is replayed from the named historical
migration and created solely when it is absent. Existing rows are retained;
applied migrations are not rewritten.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "admin_report_permissions_repair_20260910"
down_revision = "desktop_runtime_repair_20260909"
branch_labels = None
depends_on = None

_SCHEMA = "domain_shared"
_TABLE = "admin_report_permissions"


def _has_table() -> bool:
    return sa.inspect(op.get_bind()).has_table(_TABLE, schema=_SCHEMA)


def _create_index(name, columns) -> None:
    indexes = sa.inspect(op.get_bind()).get_indexes(_TABLE, schema=_SCHEMA)
    if not any(index["name"] == name for index in indexes):
        op.create_index(name, _TABLE, columns, unique=False, schema=_SCHEMA)


# Source: admin_report_permissions_20260215.py
def upgrade() -> None:
    if not _has_table():
        op.create_table(
            _TABLE,
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False),
            sa.Column("role_id", sa.String(length=64), nullable=False),
            sa.Column("report_key", sa.String(length=120), nullable=False),
            sa.Column(
                "can_view", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column(
                "can_export", sa.Boolean(), nullable=False, server_default=sa.text("false")
            ),
            sa.Column(
                "allowed_scopes",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "filters",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column(
                "active", sa.Boolean(), nullable=False, server_default=sa.text("true")
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
                "tenant_id",
                "role_id",
                "report_key",
                name="uq_admin_report_permissions_role_report",
            ),
            schema=_SCHEMA,
        )

    _create_index(
        "ix_admin_report_permissions_tenant_role", ["tenant_id", "role_id", "active"]
    )
    _create_index(
        "ix_admin_report_permissions_tenant_report",
        ["tenant_id", "report_key", "active"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Additive repair: automatic downgrade would delete pre-existing business data."
    )
