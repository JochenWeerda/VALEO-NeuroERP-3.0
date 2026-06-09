"""crm_capture_inbox — Klärfall-Inbox für nicht zuordenbare Auto-Captures (KIM)

Auto-erfasste Kommunikation (Telefon/E-Mail/WhatsApp), die KEINEM Kunden
zugeordnet werden konnte (`unresolved`), landet hier statt still verloren zu
gehen. Aussendienst/Innendienst ordnet sie manuell einem Kunden zu → dann wird
der Kontakt regulär in public.kunden_kontakte angelegt.

Revision ID: crm_capture_inbox_kim_20260609
Revises: crm_contacts_ext_kim_s4_20260609
Create Date: 2026-06-09
"""

from __future__ import annotations

from alembic import op

revision = "crm_capture_inbox_kim_20260609"
down_revision = "crm_contacts_ext_kim_s4_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_capture_inbox (
            id            UUID PRIMARY KEY,
            tenant_id     UUID NOT NULL,
            channel       VARCHAR(16) NOT NULL,          -- telefon | email | whatsapp | brief | fax
            direction     VARCHAR(8)  NOT NULL DEFAULT 'ein',  -- ein | aus
            peer          VARCHAR(256),                  -- Telefonnummer/E-Mail der Gegenseite
            betreff       VARCHAR(256),
            zusammenfassung TEXT,
            content       TEXT,
            verweis       VARCHAR(128),                  -- externe ID (Call-/Message-ID) für Idempotenz
            status        VARCHAR(12) NOT NULL DEFAULT 'offen',  -- offen | zugeordnet | verworfen
            kunden_nr     VARCHAR(32),                   -- gesetzt bei Zuordnung
            kontakt_id    UUID,                          -- angelegter kunden_kontakte-Eintrag
            resolved_by   VARCHAR(64),
            resolved_at   TIMESTAMPTZ,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at    TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_capture_inbox_status "
        "ON public.crm_capture_inbox (tenant_id, status, created_at DESC)"
    )
    # Idempotenz: gleicher verweis pro Tenant nur einmal in der Inbox.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_crm_capture_inbox_verweis "
        "ON public.crm_capture_inbox (tenant_id, verweis) WHERE verweis IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ux_crm_capture_inbox_verweis")
    op.execute("DROP INDEX IF EXISTS public.ix_crm_capture_inbox_status")
    op.execute("DROP TABLE IF EXISTS public.crm_capture_inbox")
