"""crm_notifications — internes Benachrichtigungs-/Postfach-System fuer KIM (KIM-L3-BACKEND-001)

Persistente interne Benachrichtigungen (In-App-Postfach) sowie protokollierte externe
Fachberater-Mails, ausgeloest aus dem Kontakt-CC im KIM-Cockpit.

Revision ID: crm_notifications_kim_l3_backend_20260609
Revises: crm360_o2c_delivery_20260608
Create Date: 2026-06-09
"""

from __future__ import annotations

from alembic import op

revision = "crm_notifications_kim_l3_backend_20260609"
down_revision = "crm360_o2c_delivery_20260608"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_notifications (
            id           UUID PRIMARY KEY,
            tenant_id    UUID NOT NULL,
            kunden_nr    VARCHAR(32),
            kontakt_id   UUID,
            sender       VARCHAR(64),
            recipient    VARCHAR(256) NOT NULL,
            channel      VARCHAR(16)  NOT NULL DEFAULT 'internal',
            betreff      VARCHAR(512),
            kommentar    TEXT,
            status       VARCHAR(16)  NOT NULL DEFAULT 'unread',
            created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
            read_at      TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_notifications_recipient "
        "ON public.crm_notifications (tenant_id, recipient, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_notifications_kunde "
        "ON public.crm_notifications (tenant_id, kunden_nr)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ix_crm_notifications_kunde")
    op.execute("DROP INDEX IF EXISTS public.ix_crm_notifications_recipient")
    op.execute("DROP TABLE IF EXISTS public.crm_notifications")
