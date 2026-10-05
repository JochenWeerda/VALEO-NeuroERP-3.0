"""Document return worklist and immutable status audit.

Revision ID: docflow_returns_20260821
Revises: mde_inbox_hardening_20260821
"""
from alembic import op

revision = "docflow_returns_20260821"
down_revision = "mde_inbox_hardening_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE TABLE domain_docflow.document_return_cases (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, header_id TEXT NOT NULL,
        artifact_id TEXT, subject_type TEXT NOT NULL DEFAULT 'process', subject_ref TEXT,
        contact_ref TEXT, assigned_user TEXT NOT NULL, tags JSONB NOT NULL DEFAULT '[]',
        shipping_status TEXT NOT NULL DEFAULT 'not_sent', return_status TEXT NOT NULL DEFAULT 'expected',
        due_at TIMESTAMPTZ, sent_at TIMESTAMPTZ, returned_at TIMESTAMPTZ, source_route TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        FOREIGN KEY (header_id) REFERENCES domain_docflow.document_headers(id),
        FOREIGN KEY (artifact_id) REFERENCES domain_docflow.document_artifacts(id),
        CHECK (subject_type IN ('customer','personnel','contact','process')),
        CHECK (shipping_status IN ('not_sent','sent','delivered','failed')),
        CHECK (return_status IN ('expected','received','verified','rejected','waived','closed'))
      );
      CREATE INDEX ix_docreturn_worklist ON domain_docflow.document_return_cases
        (tenant_id, return_status, assigned_user, created_at DESC);
      CREATE TABLE domain_docflow.document_return_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, case_id TEXT NOT NULL REFERENCES domain_docflow.document_return_cases(id),
        action TEXT NOT NULL, old_value TEXT, new_value TEXT, actor TEXT NOT NULL, reason TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX ix_docreturn_audit ON domain_docflow.document_return_audit (tenant_id, case_id, created_at);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docflow.document_return_audit; DROP TABLE IF EXISTS domain_docflow.document_return_cases;")
