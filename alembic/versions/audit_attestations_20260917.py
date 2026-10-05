"""Die Attestierung bekommt ihre Tabelle.

Ein gebuchter Lieferschein darf nur mit Begruendung nachgedruckt werden — die
Begruendung wird nach ``domain_audit.attestations`` geschrieben. Die Tabelle
gab es nie, und der INSERT steht ungeschuetzt im Druckpfad: Jeder Nachdruck
eines gebuchten Lieferscheins lief in einen 500, und der Lieferschein blieb
ungedruckt. Die Governance war damit nicht streng, sondern kaputt.

Revision ID: audit_attestations_20260917
Revises: dsgvo_loeschantraege_20260917
Create Date: 2026-09-17
"""

from __future__ import annotations

from alembic import op

revision = "audit_attestations_20260917"
down_revision = "dsgvo_loeschantraege_20260917"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_audit")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_audit.attestations (
            id           VARCHAR(64)  PRIMARY KEY,
            tenant_id    VARCHAR(64)  NOT NULL,
            entity_type  VARCHAR(64)  NOT NULL,
            entity_id    VARCHAR(64)  NOT NULL,
            action       VARCHAR(64)  NOT NULL,
            reason       TEXT         NOT NULL,
            created_by   VARCHAR(128) NOT NULL,
            created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )
    # Die Frage an diese Tabelle lautet immer: „Wer hat diesen Beleg wann und
    # warum noch einmal gedruckt?" — genau darauf liegt der Index.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_attestations_entity "
        "ON domain_audit.attestations (tenant_id, entity_type, entity_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_audit.ix_attestations_entity")
    op.execute("DROP TABLE IF EXISTS domain_audit.attestations")
