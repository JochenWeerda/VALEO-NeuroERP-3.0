"""Fuhrpark: additive tenant_id fuer Masken-CRUD (CE+MCP Isolation).

Revision ID: fuhrpark_tenant_ce_20261009
Revises: postfach_microsoft_20261008

Die vier Fuhrpark-Stammtabellen hatten keine ``tenant_id``. MCP-Writes blieben
deshalb ``blocked_missing_tenant``. Additive Spalte inkl. Backfill
``legacy-unassigned``, Mandanten-Indizes und tenant-scoped Unique-Keys
(Kennzeichen / Terminart / Rechnungsnummer).
"""

from alembic import op
from sqlalchemy import text

revision = "fuhrpark_tenant_ce_20261009"
down_revision = "postfach_microsoft_20261008"
branch_labels = None
depends_on = None

_TABLES = (
    "ops_fahrzeuge",
    "ops_fuhrpark_terminarten",
    "ops_fuhrpark_rechnungen",
    "ops_fuhrpark_ausgehende_dokumente",
)


def _has_column(conn, table: str, column: str = "tenant_id") -> bool:
    return conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'domain_ops'
              AND table_name = :table
              AND column_name = :column
            """
        ),
        {"table": table, "column": column},
    ).scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()

    for table in _TABLES:
        if not _has_column(conn, table):
            op.execute(
                f"ALTER TABLE domain_ops.{table} "
                "ADD COLUMN tenant_id VARCHAR(120)"
            )
        op.execute(
            f"UPDATE domain_ops.{table} "
            "SET tenant_id = 'legacy-unassigned' "
            "WHERE tenant_id IS NULL OR btrim(tenant_id) = ''"
        )
        op.execute(
            f"ALTER TABLE domain_ops.{table} "
            "ALTER COLUMN tenant_id SET DEFAULT 'legacy-unassigned'"
        )
        op.execute(
            f"ALTER TABLE domain_ops.{table} "
            "ALTER COLUMN tenant_id SET NOT NULL"
        )
        op.execute(
            f"CREATE INDEX IF NOT EXISTS ix_{table}_tenant_id "
            f"ON domain_ops.{table} (tenant_id)"
        )

    # Kennzeichen je Mandant (statt systemweit)
    op.execute(
        "ALTER TABLE domain_ops.ops_fahrzeuge "
        "DROP CONSTRAINT IF EXISTS ops_fahrzeuge_kennzeichen_key"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_ops_fahrzeuge_tenant_kennzeichen'
                  AND conrelid = 'domain_ops.ops_fahrzeuge'::regclass
            ) THEN
                ALTER TABLE domain_ops.ops_fahrzeuge
                    ADD CONSTRAINT uq_ops_fahrzeuge_tenant_kennzeichen
                    UNIQUE (tenant_id, kennzeichen);
            END IF;
        END $$;
        """
    )

    # Terminart je Mandant
    op.execute(
        "ALTER TABLE domain_ops.ops_fuhrpark_terminarten "
        "DROP CONSTRAINT IF EXISTS ops_fuhrpark_terminarten_terminart_key"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_ops_fuhrpark_terminarten_tenant_name'
                  AND conrelid = 'domain_ops.ops_fuhrpark_terminarten'::regclass
            ) THEN
                ALTER TABLE domain_ops.ops_fuhrpark_terminarten
                    ADD CONSTRAINT uq_ops_fuhrpark_terminarten_tenant_name
                    UNIQUE (tenant_id, terminart);
            END IF;
        END $$;
        """
    )

    # Rechnungsnummer je Mandant
    op.execute(
        "ALTER TABLE domain_ops.ops_fuhrpark_rechnungen "
        "DROP CONSTRAINT IF EXISTS ops_fuhrpark_rechnungen_rechnungs_nr_key"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_ops_fuhrpark_rechnungen_tenant_nr'
                  AND conrelid = 'domain_ops.ops_fuhrpark_rechnungen'::regclass
            ) THEN
                ALTER TABLE domain_ops.ops_fuhrpark_rechnungen
                    ADD CONSTRAINT uq_ops_fuhrpark_rechnungen_tenant_nr
                    UNIQUE (tenant_id, rechnungs_nr);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_ops.ops_fahrzeuge "
        "DROP CONSTRAINT IF EXISTS uq_ops_fahrzeuge_tenant_kennzeichen"
    )
    op.execute(
        "ALTER TABLE domain_ops.ops_fuhrpark_terminarten "
        "DROP CONSTRAINT IF EXISTS uq_ops_fuhrpark_terminarten_tenant_name"
    )
    op.execute(
        "ALTER TABLE domain_ops.ops_fuhrpark_rechnungen "
        "DROP CONSTRAINT IF EXISTS uq_ops_fuhrpark_rechnungen_tenant_nr"
    )
    for table in _TABLES:
        op.execute(f"DROP INDEX IF EXISTS domain_ops.ix_{table}_tenant_id")
        op.execute(f"ALTER TABLE domain_ops.{table} DROP COLUMN IF EXISTS tenant_id")
