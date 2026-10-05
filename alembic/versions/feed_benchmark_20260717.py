"""Benchmark report type (FEED-PERF-044).

Revision ID: feed_benchmark_20260717
Revises: feed_herd_snapshots_20260717
"""

from alembic import op

revision = "feed_benchmark_20260717"
down_revision = "feed_herd_snapshots_20260717"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      DROP CONSTRAINT IF EXISTS feeding_reports_report_type_check""")
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      ADD CONSTRAINT feeding_reports_report_type_check
      CHECK (report_type IN ('feeding_plan','consulting','target_actual','trend','benchmark'))""")


def downgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      DROP CONSTRAINT IF EXISTS feeding_reports_report_type_check""")
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      ADD CONSTRAINT feeding_reports_report_type_check
      CHECK (report_type IN ('feeding_plan','consulting','target_actual','trend'))""")
