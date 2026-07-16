"""Report types consulting/target_actual/trend (FEED-REP-040).

Revision ID: feed_reports_types_20260716
Revises: feed_reports_20260716
"""

from alembic import op

revision = "feed_reports_types_20260716"
down_revision = "feed_reports_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      DROP CONSTRAINT IF EXISTS feeding_reports_report_type_check""")
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      ADD CONSTRAINT feeding_reports_report_type_check
      CHECK (report_type IN ('feeding_plan','consulting','target_actual','trend'))""")


def downgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      DROP CONSTRAINT IF EXISTS feeding_reports_report_type_check""")
    op.execute("""ALTER TABLE domain_agrar.feeding_reports
      ADD CONSTRAINT feeding_reports_report_type_check
      CHECK (report_type IN ('feeding_plan'))""")
