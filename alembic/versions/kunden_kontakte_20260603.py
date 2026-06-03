"""Kunden-Kontakte für das Kunden-Cockpit (Kontakthistorie + Wiedervorlage).

Revision ID: kunden_kontakte_20260603
Revises: kunden_milchvieh_profil_20260602
Create Date: 2026-06-03

Reiches Kontakt-Modell analog zur Legacy-CRM-KONTAKTE-Sicht: Richtung (ein/aus),
Art (Telefon/WhatsApp/E-Mail/persönlich/...), Kurzinfo, Notiz, Wiedervorlage
(Scheduler), Weiterleitung, Bediener und Verweis auf einen Beleg. Hängt über
kunden_nr an public.kunden. Additiv/idempotent.
"""

from alembic import op

revision = "kunden_kontakte_20260603"
down_revision = "kunden_milchvieh_profil_20260602"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_kontakte (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kunden_nr       VARCHAR(20) NOT NULL REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            richtung        VARCHAR(10) NOT NULL DEFAULT 'aus',   -- 'ein' | 'aus'
            art             VARCHAR(20) NOT NULL DEFAULT 'telefon', -- telefon|whatsapp|email|persoenlich|brief
            kurzinfo        VARCHAR(300),
            notiz           TEXT,
            wiedervorlage   DATE,
            weiterleitung_an VARCHAR(120),
            bediener        VARCHAR(120),
            verweis         VARCHAR(200),     -- Beleg-Referenz (z. B. "Angebot/Auftrag 2610098")
            erledigt        BOOLEAN NOT NULL DEFAULT FALSE,
            tenant_id       VARCHAR(64) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_kontakte_kunde ON public.kunden_kontakte (kunden_nr, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_kontakte_wvl ON public.kunden_kontakte (wiedervorlage) WHERE wiedervorlage IS NOT NULL AND erledigt = FALSE")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_kontakte CASCADE")
