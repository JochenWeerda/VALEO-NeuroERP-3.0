"""Versioned measure lifecycle, notifications and report drafts (FEED-CONS-032).

Revision ID: feed_consulting_measures_20260716
Revises: feed_mixer_feedback_20260716
"""

from alembic import op

revision = "feed_consulting_measures_20260716"
down_revision = "feed_mixer_feedback_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_measure_versions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      measure_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_actual_measures(id),
      version INTEGER NOT NULL CHECK (version>0),
      status VARCHAR(30) NOT NULL CHECK (status IN
        ('open','in_progress','review_due','completed','cancelled')),
      owner_subject VARCHAR(160) NOT NULL, due_date DATE NOT NULL,
      reminder_date DATE, escalation_status VARCHAR(30) NOT NULL DEFAULT 'none'
        CHECK (escalation_status IN ('none','attention','escalated')),
      effectiveness VARCHAR(30) CHECK
        (effectiveness IN ('effective','partial','ineffective')),
      effectiveness_result TEXT, reason TEXT NOT NULL,
      changed_by VARCHAR(160) NOT NULL, changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,measure_id,version)
    )""")
    op.execute("""INSERT INTO domain_agrar.feeding_measure_versions
      (id,tenant_id,measure_id,version,status,owner_subject,due_date,reason,changed_by,changed_at)
      SELECT 'mv-'||m.id,m.tenant_id,m.id,1,'open',m.owner_subject,m.due_date,m.reason,
             m.created_by,m.created_at
      FROM domain_agrar.feeding_actual_measures m
      ON CONFLICT (tenant_id,measure_id,version) DO NOTHING""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_notifications (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      recipient_subject VARCHAR(160) NOT NULL, event_type VARCHAR(120) NOT NULL,
      aggregate_id VARCHAR NOT NULL, title VARCHAR(240) NOT NULL, body TEXT NOT NULL,
      deep_link VARCHAR(500) NOT NULL, dedupe_key VARCHAR(240) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(), read_at TIMESTAMPTZ,
      UNIQUE (tenant_id,dedupe_key)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.consulting_case_measures (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      case_id VARCHAR NOT NULL REFERENCES domain_agrar.consulting_cases(id),
      measure_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_actual_measures(id),
      linked_by VARCHAR(160) NOT NULL, linked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,case_id,measure_id)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.consulting_report_drafts (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      case_id VARCHAR NOT NULL REFERENCES domain_agrar.consulting_cases(id),
      version INTEGER NOT NULL CHECK (version>0), content JSONB NOT NULL,
      content_hash VARCHAR(64) NOT NULL, reason TEXT NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,case_id,version), UNIQUE (tenant_id,case_id,content_hash)
    )""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_consulting_measure()
      RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
        RAISE EXCEPTION 'measure lifecycle and report records are append-only';
      END; $$""")
    for table in (
        "feeding_measure_versions",
        "consulting_case_measures",
        "consulting_report_drafts",
    ):
        op.execute(
            f"DROP TRIGGER IF EXISTS trg_immutable_{table} ON domain_agrar.{table}"
        )  # noqa: S608
        op.execute(f"""CREATE TRIGGER trg_immutable_{table} BEFORE UPDATE OR DELETE
          ON domain_agrar.{table} FOR EACH ROW
          EXECUTE FUNCTION domain_agrar.guard_immutable_consulting_measure()""")  # noqa: S608


def downgrade() -> None:
    for table in (
        "consulting_report_drafts",
        "consulting_case_measures",
        "feeding_measure_versions",
    ):
        op.execute(
            f"DROP TRIGGER IF EXISTS trg_immutable_{table} ON domain_agrar.{table}"
        )  # noqa: S608
        op.execute(f"DROP TABLE IF EXISTS domain_agrar.{table}")  # noqa: S608
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_notifications")
    op.execute(
        "DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_consulting_measure()"
    )
