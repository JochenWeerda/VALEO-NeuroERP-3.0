"""Ackerschlagkartei Inkrement-1: Wirtschaftsjahr am Schlag.

Revision ID: feldbuch_inkrement1_20260716
Revises: feed_consulting_measures_20260716
"""

from alembic import op

revision = "feldbuch_inkrement1_20260716"
down_revision = "feed_consulting_measures_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_schlaege "
        "ADD COLUMN IF NOT EXISTS wirtschaftsjahr INTEGER"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_feldbuch_schlaege_wirtschaftsjahr "
        "ON domain_agrar.feldbuch_schlaege (wirtschaftsjahr)"
    )
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_massnahmen "
        "ADD COLUMN IF NOT EXISTS sachkunde_nummer VARCHAR(80)"
    )
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_massnahmen "
        "ADD COLUMN IF NOT EXISTS sachkunde_gueltig_bis TIMESTAMPTZ"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_massnahmen "
        "DROP COLUMN IF EXISTS sachkunde_gueltig_bis"
    )
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_massnahmen "
        "DROP COLUMN IF EXISTS sachkunde_nummer"
    )
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feldbuch_schlaege_wirtschaftsjahr")
    op.execute(
        "ALTER TABLE domain_agrar.feldbuch_schlaege DROP COLUMN IF EXISTS wirtschaftsjahr"
    )
