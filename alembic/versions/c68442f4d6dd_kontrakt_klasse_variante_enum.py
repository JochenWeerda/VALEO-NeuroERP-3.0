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
    # Schema sicherstellen
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    # Tabelle anlegen falls nicht vorhanden
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_agrar.kontrakt_klassen (
            id VARCHAR NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            beschreibung TEXT,
            variante VARCHAR(30) NOT NULL,
            paritaet VARCHAR(10) NOT NULL,
            incoterm_ort VARCHAR(255),
            notiz TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            tenant_id VARCHAR(120) NOT NULL DEFAULT 'default',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)

    # Erstelle PostgreSQL-Enum-Typ für KontraktVariante
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE domain_agrar.kontrakt_variante AS ENUM "
        "    ('FIXPREIS', 'BASIS', 'PRAEMIE', 'POOLPREIS'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    )
    # CHECK-Constraint nur hinzufügen wenn er noch nicht existiert
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'kontrakt_klassen_variante_check'
                  AND conrelid = 'domain_agrar.kontrakt_klassen'::regclass
            ) THEN
                ALTER TABLE domain_agrar.kontrakt_klassen
                    ADD CONSTRAINT kontrakt_klassen_variante_check
                    CHECK (variante IN ('FIXPREIS', 'BASIS', 'PRAEMIE', 'POOLPREIS'));
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_agrar.kontrakt_klassen "
        "  DROP CONSTRAINT IF EXISTS kontrakt_klassen_variante_check;"
    )
    op.execute(
        "DROP TYPE IF EXISTS domain_agrar.kontrakt_variante;"
    )
