"""Pruefkorb des Controllers: Befunde der Kontroll-Engine (FIN-CONTROL-001).

Revision ID: control_findings_20261013
Revises: approval_log_20261013

Entscheidung des Auftraggebers vom 13.10.2026: Der Finanzbuchhalter bucht Routine selbst; eine zentrale
Kontroll-Engine meldet Auffaelligkeiten. Eine Warnung laesst den Vorgang zu und legt den Befund hier ab; ein
kritischer Befund sperrt bis zur unabhaengigen Freigabe und steht danach ebenfalls hier.

Ein Befund wird nicht geloescht. Geprueft wird er einmal, von einer anderen Person als der, die gebucht hat.
"""

from alembic import op

revision = "control_findings_20261013"
down_revision = "approval_log_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE domain_docflow.control_findings (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id VARCHAR(64) NOT NULL,
            subject_type VARCHAR(40) NOT NULL,
            subject_id VARCHAR(64) NOT NULL,
            action VARCHAR(20) NOT NULL,
            code VARCHAR(40) NOT NULL,
            severity VARCHAR(10) NOT NULL CHECK (severity IN ('warnung', 'kritisch')),
            text TEXT NOT NULL,
            amount NUMERIC(18, 2),
            actor VARCHAR(100),
            approval_id VARCHAR(36),
            created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
            status VARCHAR(10) NOT NULL DEFAULT 'offen' CHECK (status IN ('offen', 'geprueft')),
            reviewed_by VARCHAR(100),
            reviewed_at TIMESTAMPTZ,
            review_note TEXT,
            -- Wer gebucht hat, prueft seinen Befund nicht selbst.
            CONSTRAINT control_findings_unabhaengig CHECK (reviewed_by IS NULL OR actor IS NULL OR reviewed_by <> actor),
            CONSTRAINT control_findings_einmal UNIQUE (tenant_id, subject_type, subject_id, action, code)
        )
        """
    )
    op.execute("CREATE INDEX ix_control_findings_offen ON domain_docflow.control_findings (tenant_id, status, created_at)")
    op.execute(
        "CREATE TRIGGER control_findings_nicht_loeschen BEFORE DELETE ON domain_docflow.control_findings "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.freigabe_nicht_loeschen()"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docflow.control_findings")
