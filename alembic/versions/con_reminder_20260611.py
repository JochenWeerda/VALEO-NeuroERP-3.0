"""DOM-CON-004.3 — Kontraktmahnung (append-only Mahnungs-Log).

Revision ID: con_reminder_20260611
Revises: con_fixing_matif_20260611

Mahnungen zu überfällig-untererfüllten Kontrakten: append-only Log je Kontrakt
(Mahnstufe, Text, Bediener). Engagement-Sicht selbst ist read-only (keine Tabelle).
Idempotent (``CREATE TABLE IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "con_reminder_20260611"
down_revision: Union[str, Sequence[str], None] = "con_fixing_matif_20260611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_ops.kon_contract_reminder (
            reminder_id   VARCHAR(64) NOT NULL,
            contract_id   VARCHAR(64) NOT NULL,
            mahnstufe     INTEGER     NOT NULL DEFAULT 1,
            offen_menge   DECIMAL(14, 3),
            text          TEXT,
            bediener      VARCHAR(100),
            tenant_id     VARCHAR(64) NOT NULL,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_kon_contract_reminder PRIMARY KEY (reminder_id)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kon_contract_reminder_contract "
        "ON domain_ops.kon_contract_reminder (contract_id, tenant_id);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.kon_contract_reminder;")
