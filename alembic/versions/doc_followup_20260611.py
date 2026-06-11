"""DOM-DOC-004.3 — Bescheid/Rückmeldung + Wiedervorlage am Vorgang.

Revision ID: doc_followup_20260611
Revises: doc_artifact_version_20260611

Neue Tabelle domain_docflow.document_followups: Bescheide, Rückmeldungen und
Wiedervorlagen je Dokument/Vorgang (mit Fälligkeit + Erledigt-Status).
Idempotent (``CREATE TABLE IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "doc_followup_20260611"
down_revision: Union[str, Sequence[str], None] = "doc_artifact_version_20260611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_docflow.document_followups (
            id           VARCHAR(64) NOT NULL,
            tenant_id    VARCHAR(64) NOT NULL,
            header_id    VARCHAR(64) NOT NULL,
            art          VARCHAR(20) NOT NULL DEFAULT 'wiedervorlage',
            betreff      VARCHAR(255),
            text         TEXT,
            faellig_am   DATE,
            status       VARCHAR(20) NOT NULL DEFAULT 'offen',
            erledigt_at  TIMESTAMPTZ,
            erledigt_von VARCHAR(100),
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_by   VARCHAR(100),
            CONSTRAINT pk_document_followups PRIMARY KEY (id)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_followups_header "
        "ON domain_docflow.document_followups (header_id, tenant_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_followups_offen "
        "ON domain_docflow.document_followups (tenant_id, status, faellig_am);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docflow.document_followups;")
