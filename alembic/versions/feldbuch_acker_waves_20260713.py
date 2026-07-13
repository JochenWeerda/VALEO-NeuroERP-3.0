"""Ackerschlagkartei wave fields (AS-W1/W2/W4/W5/W6).

Adds nutrient, plant-protection, harvest fields to feldbuch_massnahmen and
fertiliser-need / Nmin / soil-analysis fields to feldbuch_schlaege.

Revision ID: feldbuch_acker_waves_20260713
Revises: rations_integrations_20260712
"""
from alembic import op

revision = "feldbuch_acker_waves_20260713"
down_revision = "rations_integrations_20260712"
branch_labels = None
depends_on = None

_MASSNAHME_COLS = [
    ("n_kg", "DOUBLE PRECISION"),
    ("p2o5_kg", "DOUBLE PRECISION"),
    ("k2o_kg", "DOUBLE PRECISION"),
    ("mgo_kg", "DOUBLE PRECISION"),
    ("s_kg", "DOUBLE PRECISION"),
    ("duenger_form", "VARCHAR(1)"),
    ("kosten_eur", "DOUBLE PRECISION"),
    ("wirkungsbereich", "VARCHAR(30)"),
    ("begruendung", "VARCHAR(300)"),
    ("ertrag_dt_ha", "DOUBLE PRECISION"),
    ("qualitaet", "VARCHAR(100)"),
    ("erloes_eur", "DOUBLE PRECISION"),
    ("nebenleistung_eur", "DOUBLE PRECISION"),
]

_SCHLAG_COLS = [
    ("n_sollwert_kg_ha", "DOUBLE PRECISION"),
    ("ertragsniveau_dt_ha", "DOUBLE PRECISION"),
    ("nmin_fruehjahr_kg_ha", "DOUBLE PRECISION"),
    ("nmin_in_bedarf", "BOOLEAN"),
    ("boden_p2o5_mg", "DOUBLE PRECISION"),
    ("boden_k2o_mg", "DOUBLE PRECISION"),
    ("boden_mgo_mg", "DOUBLE PRECISION"),
    ("boden_ph", "DOUBLE PRECISION"),
    ("boden_datum", "TIMESTAMPTZ"),
    ("versorgungsstufe", "VARCHAR(1)"),
]


def upgrade() -> None:
    for col, typ in _MASSNAHME_COLS:
        op.execute(f"ALTER TABLE domain_agrar.feldbuch_massnahmen ADD COLUMN IF NOT EXISTS {col} {typ}")
    for col, typ in _SCHLAG_COLS:
        op.execute(f"ALTER TABLE domain_agrar.feldbuch_schlaege ADD COLUMN IF NOT EXISTS {col} {typ}")


def downgrade() -> None:
    for col, _ in _MASSNAHME_COLS:
        op.execute(f"ALTER TABLE domain_agrar.feldbuch_massnahmen DROP COLUMN IF EXISTS {col}")
    for col, _ in _SCHLAG_COLS:
        op.execute(f"ALTER TABLE domain_agrar.feldbuch_schlaege DROP COLUMN IF EXISTS {col}")
