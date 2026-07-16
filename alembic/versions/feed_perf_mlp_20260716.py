"""MLP/Milchguete metrics on the daily feeding series (FEED-PERF-033).

Revision ID: feed_perf_mlp_20260716
Revises: feldbuch_open_gaps_20260716
"""

from alembic import op

revision = "feed_perf_mlp_20260716"
down_revision = "feldbuch_open_gaps_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_controlling_daily
      ADD COLUMN IF NOT EXISTS milk_urea_mg_dl NUMERIC(8,2)""")
    op.execute("""ALTER TABLE domain_agrar.feeding_controlling_daily
      ADD COLUMN IF NOT EXISTS somatic_cell_count_k NUMERIC(10,1)""")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_agrar.feeding_controlling_daily DROP COLUMN IF EXISTS somatic_cell_count_k")
    op.execute("ALTER TABLE domain_agrar.feeding_controlling_daily DROP COLUMN IF EXISTS milk_urea_mg_dl")
