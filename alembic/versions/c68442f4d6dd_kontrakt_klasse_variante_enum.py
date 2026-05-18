"""kontrakt_klasse_variante_enum

Revision ID: c68442f4d6dd
Revises: warehouse_wms_structure_20260517
Create Date: 2026-05-18 14:54:32.275380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c68442f4d6dd'
down_revision: Union[str, None] = 'warehouse_wms_structure_20260517'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Erstelle PostgreSQL-Enum-Typ für KontraktVariante
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE domain_agrar.kontrakt_variante AS ENUM "
        "    ('FIXPREIS', 'BASIS', 'PRAEMIE', 'POOLPREIS'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    )
    # Füge CHECK-Constraint auf der bestehenden varchar-Spalte hinzu
    # (als Alternative zu einer vollständigen Typumwandlung, um Datenmigrationsrisiken zu minimieren)
    op.execute(
        "ALTER TABLE domain_agrar.kontrakt_klassen "
        "  ADD CONSTRAINT kontrakt_klassen_variante_check "
        "  CHECK (variante IN ('FIXPREIS', 'BASIS', 'PRAEMIE', 'POOLPREIS'));"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_agrar.kontrakt_klassen "
        "  DROP CONSTRAINT IF EXISTS kontrakt_klassen_variante_check;"
    )
    op.execute(
        "DROP TYPE IF EXISTS domain_agrar.kontrakt_variante;"
    )
