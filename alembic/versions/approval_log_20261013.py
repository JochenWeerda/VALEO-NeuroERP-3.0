"""Unveraenderliches Freigabeprotokoll fuer alle Bereiche (APPROVAL-001).

Revision ID: approval_log_20261013
Revises: approval_engine_20261013

Die Approval Engine gilt nicht nur fuer DocFlow-Belege: Eingangsrechnungen der Finanzbuchhaltung und die
Verkaufsgutschrift schliessen sich an. Ihr Protokoll steht deshalb an einer Stelle, unabhaengig vom Speicher des
Vorgangs. DocFlow-Belege tragen den Eintrag zusaetzlich in ihrem Kommandoprotokoll.
"""

from alembic import op

revision = "approval_log_20261013"
down_revision = "approval_engine_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE domain_docflow.approval_log (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id VARCHAR(64) NOT NULL,
            subject_type VARCHAR(40) NOT NULL,
            subject_id VARCHAR(64) NOT NULL,
            approval_id VARCHAR(36),
            event VARCHAR(40) NOT NULL,
            actor VARCHAR(100),
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            logged_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_approval_log_subject ON domain_docflow.approval_log (tenant_id, subject_type, subject_id, logged_at)"
    )
    op.execute(
        "CREATE TRIGGER approval_log_unveraenderlich BEFORE UPDATE OR DELETE ON domain_docflow.approval_log "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.statushistorie_unveraenderlich()"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docflow.approval_log")
