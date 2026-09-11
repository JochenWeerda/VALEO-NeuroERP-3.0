"""Add domain_agrar.harvest_acceptances columns used by Sammelabrechnung.

Revision ID: agrar_harvest_acceptances_sammel_20260911
Revises: agrar_sammelabrechnungen_20260911
"""

from alembic import op

revision = "agrar_harvest_acceptances_sammel_20260911"
down_revision = "agrar_sammelabrechnungen_20260911"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    # Minimal-Schema fuer Rohware-Sammelabrechnung-Berechnung.
    # Volle Inventory-Annahme bleibt domain_inventory.harvest_acceptances.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_agrar.harvest_acceptances (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR,
          lieferant_id VARCHAR,
          artikel_nr VARCHAR(80),
          menge_netto_kg DOUBLE PRECISION NOT NULL DEFAULT 0,
          qualitaet_feuchte DOUBLE PRECISION,
          qualitaet_besatz DOUBLE PRECISION,
          preis_eur_t DOUBLE PRECISION NOT NULL DEFAULT 0,
          erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_agrar.harvest_acceptances")
