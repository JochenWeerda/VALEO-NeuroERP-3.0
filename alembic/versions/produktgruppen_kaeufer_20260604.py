"""Käuferlogik je Produktgruppe + echte Signal-Herkunft.

Revision ID: produktgruppen_kaeufer_20260604
Revises: kunden_kaeufer_profil_20260604
Create Date: 2026-06-04

Ein Betrieb kann je Produktgruppe unterschiedlich „ticken" (bei Dünger Preis-
vergleicher, bei Kälbermilch Beratungskäufer). Daher hält die Bezug-Tabelle
optional eine produktgruppenspezifische Käufergruppe + deren Begründung/Quelle.
Ist `buying_group` NULL, gilt die globale Käufergruppe des Betriebs.
Additiv/idempotent.
"""

from alembic import op

revision = "produktgruppen_kaeufer_20260604"
down_revision = "kunden_kaeufer_profil_20260604"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug ADD COLUMN IF NOT EXISTS buying_group VARCHAR(40)")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug ADD COLUMN IF NOT EXISTS buying_group_reason TEXT")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug ADD COLUMN IF NOT EXISTS buying_group_source VARCHAR(16)")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug ADD COLUMN IF NOT EXISTS buying_group_confidence NUMERIC(4,3)")


def downgrade() -> None:
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug DROP COLUMN IF EXISTS buying_group_confidence")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug DROP COLUMN IF EXISTS buying_group_source")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug DROP COLUMN IF EXISTS buying_group_reason")
    op.execute("ALTER TABLE public.kunden_produktgruppen_bezug DROP COLUMN IF EXISTS buying_group")
