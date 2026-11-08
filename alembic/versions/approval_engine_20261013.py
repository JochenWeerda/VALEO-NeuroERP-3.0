"""Freigaben fuer buchungs- und stornorelevante Vorgaenge (APPROVAL-001).

Revision ID: approval_engine_20261013
Revises: docflow_einkauf_20261013

Entscheidung des Auftraggebers vom 13.10.2026: Buchen und Stornieren unterliegen einer risikobasierten
Freigabe. Eine Freigabe ist an Mandant, Vorgang, Version, Aktion, Betrag und Ablaufzeit gebunden; der Abdruck
des Inhalts macht sie ungueltig, sobald sich Freigaberelevantes aendert. Die Tabelle ist allgemein gehalten
(``subject_type``), damit Zahlung und Hauptbuch dieselbe Stelle benutzen koennen.

Eine Freigabe wird nicht geloescht. Jede Entscheidung steht zusaetzlich im unveraenderlichen Kommandoprotokoll.
"""

from alembic import op

revision = "approval_engine_20261013"
down_revision = "docflow_einkauf_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE domain_docflow.approvals (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id VARCHAR(64) NOT NULL,
            subject_type VARCHAR(40) NOT NULL,
            subject_id VARCHAR(64) NOT NULL,
            subject_version INTEGER NOT NULL,
            action VARCHAR(20) NOT NULL,
            amount NUMERIC(18, 2) NOT NULL,
            risk VARCHAR(2) NOT NULL CHECK (risk IN ('R3', 'R4')),
            fingerprint VARCHAR(64) NOT NULL,
            status VARCHAR(12) NOT NULL DEFAULT 'requested'
                CHECK (status IN ('requested', 'granted', 'denied', 'consumed', 'expired', 'invalidated')),
            reason TEXT,
            requested_by VARCHAR(100) NOT NULL,
            requested_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
            decided_by VARCHAR(100),
            decided_at TIMESTAMPTZ,
            decision_note TEXT,
            expires_at TIMESTAMPTZ NOT NULL,
            consumed_at TIMESTAMPTZ,
            -- Funktionstrennung auch in der Datenbank: Wer anfragt, entscheidet nicht.
            CONSTRAINT approvals_funktionstrennung CHECK (decided_by IS NULL OR decided_by <> requested_by)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_approvals_subject ON domain_docflow.approvals (tenant_id, subject_type, subject_id, action, status)"
    )
    op.execute(
        """
        CREATE FUNCTION domain_docflow.freigabe_nicht_loeschen() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                RETURN OLD;
            END IF;
            RAISE EXCEPTION 'Eine Freigabe wird nicht geloescht.' USING ERRCODE = 'restrict_violation';
        END $$
        """
    )
    op.execute(
        "CREATE TRIGGER approvals_nicht_loeschen BEFORE DELETE ON domain_docflow.approvals "
        "FOR EACH ROW EXECUTE FUNCTION domain_docflow.freigabe_nicht_loeschen()"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docflow.approvals")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.freigabe_nicht_loeschen()")
