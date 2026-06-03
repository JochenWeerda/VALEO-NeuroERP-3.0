"""WhatsApp Bestell-Inbox — eingehende Freitext-Bestellungen + AI-Extraktion.

Revision ID: whatsapp_bestell_inbox_20260603
Revises: kunden_kontakte_20260603
Create Date: 2026-06-03

Erfasst eingehende Bestellnachrichten (z. B. aus der Verkaufs-WhatsApp-Gruppe als
Copy-Paste) als Posteingang. Eine LLM-Extraktion (Claude) zerlegt den Freitext in
Kunde/Artikel/Menge/Termin/Silo/Preis (`parsed` JSONB); nach Verkäufer-Bestätigung
entsteht ein vorbelegter Beleg + ein Kontakt am Kunden (Brücke in den Flow Spine).
Additiv/idempotent.
"""

from alembic import op

revision = "whatsapp_bestell_inbox_20260603"
down_revision = "kunden_kontakte_20260603"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.whatsapp_bestellungen (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            raw_text        TEXT NOT NULL,
            absender        VARCHAR(120),          -- wer hat es gepostet/weitergeleitet
            quelle          VARCHAR(20) NOT NULL DEFAULT 'whatsapp', -- whatsapp|email|telefon|manuell
            eingegangen_am  TIMESTAMPTZ NOT NULL DEFAULT now(),
            status          VARCHAR(20) NOT NULL DEFAULT 'neu',  -- neu|geparst|bestaetigt|verworfen
            parsed          JSONB,                 -- extrahierte Struktur
            kunden_nr       VARCHAR(20) REFERENCES public.kunden(kunden_nr) ON DELETE SET NULL,
            kunde_text      VARCHAR(200),          -- wie im Text genannt
            beleg_typ       VARCHAR(20),           -- angebot|auftrag|lieferschein|rechnung
            beleg_ref       VARCHAR(120),          -- erzeugte Beleg-Referenz
            engine          VARCHAR(20),           -- claude|heuristik
            confidence      NUMERIC(4,3),
            tenant_id       VARCHAR(64) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_wa_bestell_status ON public.whatsapp_bestellungen (tenant_id, status, eingegangen_am DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_wa_bestell_kunde ON public.whatsapp_bestellungen (kunden_nr) WHERE kunden_nr IS NOT NULL")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.whatsapp_bestellungen CASCADE")
