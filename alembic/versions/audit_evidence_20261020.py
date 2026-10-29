"""GoBD-Belegnachweise: Tabelle ``domain_shared.audit_evidence`` anlegen.

Revision ID: audit_evidence_20261020
Revises: merge_hr_tax_20261019

``app/api/v1/endpoints/audit_evidence.py`` las und schrieb diese Tabelle, keine Migration legte sie an. Auf jeder
frischen Installation fielen deshalb alle Belegnachweise in einen Arbeitsspeicher-Ersatz: ``gobd-check`` meldete
"GoBD-konform" aus dem Speicher, nach einem Neustart waren die Nachweise weg (20.10.2026).
"""
from alembic import op

revision = "audit_evidence_20261020"
down_revision = "merge_hr_tax_20261019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.audit_evidence (
            audit_entry_id  VARCHAR(64)  NOT NULL,
            tenant_id       VARCHAR(80)  NOT NULL,
            aggregate_type  VARCHAR(80)  NOT NULL DEFAULT '',
            aggregate_id    VARCHAR(128) NOT NULL DEFAULT '',
            action          VARCHAR(80)  NOT NULL DEFAULT '',
            evidence_refs   JSONB        NOT NULL DEFAULT '[]'::jsonb,
            schema_version  INTEGER      NOT NULL DEFAULT 1,
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tenant_id, audit_entry_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_evidence_aggregat "
               "ON domain_shared.audit_evidence (tenant_id, aggregate_type, aggregate_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.audit_evidence")
