"""Kunden→BusinessPartner Identitäts-Brücke (Phase 1 Stammdaten-Konsolidierung).

Revision ID: kunden_bp_bridge_20260601
Revises: ustva_voranmeldungen_20260527
Create Date: 2026-06-01

Additive Brücke: public.kunden erhält die technische BP-Identität
``business_partner_id`` (UUID → domain_crm.business_partners.partner_id) sowie
``legacy_kunden_nr`` für Alt-/Importnummern. ``kunden_nr`` bleibt fachlicher
Primärschlüssel. Rein additiv, idempotent, ohne Datenbewegung — der FK-Constraint
und das Backfill erfolgen in Phase 2 (nach Merge), hier nur Spalten + Index.
"""

from alembic import op

revision = "kunden_bp_bridge_20260601"
down_revision = "ustva_voranmeldungen_20260527"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.kunden ADD COLUMN IF NOT EXISTS business_partner_id UUID")
    op.execute("ALTER TABLE public.kunden ADD COLUMN IF NOT EXISTS legacy_kunden_nr VARCHAR(64)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_kunden_business_partner_id "
        "ON public.kunden (business_partner_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_kunden_business_partner_id")
    op.execute("ALTER TABLE public.kunden DROP COLUMN IF EXISTS legacy_kunden_nr")
    op.execute("ALTER TABLE public.kunden DROP COLUMN IF EXISTS business_partner_id")
