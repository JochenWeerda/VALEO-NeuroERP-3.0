"""crm_contacts_ext — Ansprechpartner-Erweiterung (KIM-S4)

Werbe-/Marketingpräferenz-Matrix je Ansprechpartner (nein/Firma/Privat) sowie
DSGVO-Pseudonymisierungs-Marker auf kunden_ansprechpartner.

Revision ID: crm_contacts_ext_kim_s4_20260609
Revises: crm_gifts_kim_s3_20260609
Create Date: 2026-06-09
"""

from __future__ import annotations

from alembic import op

revision = "crm_contacts_ext_kim_s4_20260609"
down_revision = "crm_gifts_kim_s3_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_contact_marketing_prefs (
            id              UUID PRIMARY KEY,
            tenant_id       UUID NOT NULL,
            contact_id      VARCHAR(64) NOT NULL,
            kunden_nr       VARCHAR(32),
            category_code   VARCHAR(64) NOT NULL,
            category_label  VARCHAR(128),
            preference      VARCHAR(16) NOT NULL DEFAULT 'none',
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, contact_id, category_code)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_contact_marketing_prefs_contact "
        "ON public.crm_contact_marketing_prefs (tenant_id, contact_id)"
    )
    # DSGVO-Pseudonymisierungs-Marker (tolerant — Tabelle existiert produktiv).
    op.execute(
        "ALTER TABLE public.kunden_ansprechpartner "
        "ADD COLUMN IF NOT EXISTS pseudonymized_at TIMESTAMPTZ"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE public.kunden_ansprechpartner DROP COLUMN IF EXISTS pseudonymized_at")
    op.execute("DROP INDEX IF EXISTS public.ix_crm_contact_marketing_prefs_contact")
    op.execute("DROP TABLE IF EXISTS public.crm_contact_marketing_prefs")
