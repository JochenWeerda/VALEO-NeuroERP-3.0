"""Ist-Bezug je Betrieb × Produktgruppe (rollierend 12 M) — Durchdringungs-CRM.

Revision ID: kunden_produktgruppen_bezug_20260603
Revises: tapi_calls_20260603
Create Date: 2026-06-03

Die Ist-Seite des Bedarfsdeckungs-Cockpits: was bezieht ein Betrieb je
Produktgruppe tatsächlich bei uns (rollierend 12 Monate). Differenz zum
objektiven Jahresbedarf (Potenzial) = Bedarfslücke = zentrales Vertriebsobjekt.

`quelle` macht die Herkunft explizit ('verkauf' = aus Belegen aggregiert,
'geschaetzt' = modelliert) — so kann die echte Aggregation später andocken,
ohne das Schema zu ändern. Additiv/idempotent.
"""

from alembic import op

revision = "kunden_produktgruppen_bezug_20260603"
down_revision = "tapi_calls_20260603"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_produktgruppen_bezug (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kunden_nr       VARCHAR(20) NOT NULL REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            produktgruppe   VARCHAR(40) NOT NULL,     -- key aus PRODUKTGRUPPEN
            menge_12m       NUMERIC(14,2),            -- bezogene Menge (Einheit gruppenabhängig)
            umsatz_12m_eur  NUMERIC(14,2) NOT NULL DEFAULT 0,
            db_12m_eur      NUMERIC(14,2),            -- Deckungsbeitrag/Marge 12 M
            letzter_bezug   DATE,
            quelle          VARCHAR(16) NOT NULL DEFAULT 'geschaetzt', -- verkauf|geschaetzt
            tenant_id       VARCHAR(64) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (kunden_nr, produktgruppe, tenant_id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kpb_kunde ON public.kunden_produktgruppen_bezug (kunden_nr)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_produktgruppen_bezug CASCADE")
