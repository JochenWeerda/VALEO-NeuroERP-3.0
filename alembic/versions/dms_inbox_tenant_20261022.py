"""dms_inbox: additive tenant_id fuer Queue-Isolation.

Revision ID: dms_inbox_tenant_20261022
Revises: portal_interessenten_preise_20261020

domain_shared.dms_inbox hatte keine Mandantenspalte; die Launcher-Inbox-Queue
las alle pending-Zeilen. Additive Spalte inkl. Backfill ``legacy-unassigned``
und Index. Schreibpfad (Mayan-Webhook) bleibt ausserhalb dieses Diffs.
"""

from alembic import op
from sqlalchemy import text

revision = "dms_inbox_tenant_20261022"
down_revision = "portal_interessenten_preise_20261020"
branch_labels = None
depends_on = None


def _has_column(conn, column: str = "tenant_id") -> bool:
    return conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'domain_shared'
              AND table_name = 'dms_inbox'
              AND column_name = :column
            """
        ),
        {"column": column},
    ).scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if not conn.execute(text("SELECT to_regclass('domain_shared.dms_inbox')")).scalar():
        return

    if not _has_column(conn):
        op.execute(
            "ALTER TABLE domain_shared.dms_inbox "
            "ADD COLUMN tenant_id VARCHAR(120)"
        )

    op.execute(
        """
        UPDATE domain_shared.dms_inbox
        SET tenant_id = 'legacy-unassigned'
        WHERE tenant_id IS NULL OR btrim(tenant_id) = ''
        """
    )
    op.execute(
        "ALTER TABLE domain_shared.dms_inbox "
        "ALTER COLUMN tenant_id SET DEFAULT 'legacy-unassigned'"
    )
    op.execute(
        "ALTER TABLE domain_shared.dms_inbox "
        "ALTER COLUMN tenant_id SET NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_dms_inbox_tenant_status "
        "ON domain_shared.dms_inbox (tenant_id, status)"
    )


def downgrade() -> None:
    conn = op.get_bind()
    if not conn.execute(text("SELECT to_regclass('domain_shared.dms_inbox')")).scalar():
        return
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_dms_inbox_tenant_status")
    if _has_column(conn):
        op.execute("ALTER TABLE domain_shared.dms_inbox DROP COLUMN tenant_id")
