"""Create domain_agrar.sammelabrechnungen for Rohware-Sammelabrechnung.

Revision ID: agrar_sammelabrechnungen_20260911
Revises: desktop_runtime_repair_20260909
"""

from alembic import op

revision = "agrar_sammelabrechnungen_20260911"
down_revision = "desktop_runtime_repair_20260909"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_agrar.sammelabrechnungen (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          bezeichnung VARCHAR(200) NOT NULL,
          abrechnungsperiode VARCHAR(7) NOT NULL,
          harvest_acceptance_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
          abrechnungsschema_id VARCHAR,
          sammeldatum DATE,
          status VARCHAR(20) NOT NULL DEFAULT 'ENTWURF',
          positionen JSONB NOT NULL DEFAULT '[]'::jsonb,
          summe_menge_kg DOUBLE PRECISION NOT NULL DEFAULT 0,
          summe_betrag_eur DOUBLE PRECISION NOT NULL DEFAULT 0,
          erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          CONSTRAINT ck_sammelabrechnung_status
            CHECK (status IN ('ENTWURF', 'BERECHNET', 'GEBUCHT'))
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_sammelabrechnungen_tenant_erstellt
          ON domain_agrar.sammelabrechnungen (tenant_id, erstellt_am DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_sammelabrechnungen_tenant_erstellt")
    op.execute("DROP TABLE IF EXISTS domain_agrar.sammelabrechnungen")
