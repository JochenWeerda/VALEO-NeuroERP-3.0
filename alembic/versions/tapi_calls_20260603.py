"""TAPI/Telefonie — eingehende Anrufe für Click-to-Customer-Popup.

Revision ID: tapi_calls_20260603
Revises: whatsapp_bestell_inbox_20260603
Create Date: 2026-06-03

Ein lokaler TAPI-Bridge-Dienst (Windows-Telefonie) meldet eingehende Anrufe per
POST an /crm/tapi/incoming; die Rufnummer wird gegen public.kunden.tel aufgelöst.
Das Frontend pollt offene Anrufe und zeigt ein Kunden-Popup. Additiv/idempotent.
"""

from alembic import op

revision = "tapi_calls_20260603"
down_revision = "whatsapp_bestell_inbox_20260603"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.tapi_calls (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            caller      VARCHAR(40) NOT NULL,          -- Rufnummer des Anrufers
            called      VARCHAR(40),                   -- angerufene Nebenstelle
            richtung    VARCHAR(10) NOT NULL DEFAULT 'ein',
            kunden_nr   VARCHAR(20) REFERENCES public.kunden(kunden_nr) ON DELETE SET NULL,
            kunde_name  VARCHAR(200),
            status      VARCHAR(12) NOT NULL DEFAULT 'klingelt', -- klingelt|angenommen|erledigt
            acked       BOOLEAN NOT NULL DEFAULT FALSE,
            tenant_id   VARCHAR(64) NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_tapi_pending ON public.tapi_calls (tenant_id, acked, created_at DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.tapi_calls CASCADE")
