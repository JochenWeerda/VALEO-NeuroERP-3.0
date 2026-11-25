"""Mengeneinheiten-Stamm mit den Feldern der Grundmengeneinheit nach a.eins (24.11.2026).

Revision ID: mengeneinheit_aeins_felder_20261124
Revises: mahnstufen_verlauf_entfernen_20261123

Nutzerauftrag: Vorschlaege der a.eins-Hilfe zu Mengeneinheiten uebernehmen ("Mengeneinheit als Grundeinheit").
``domain_shared.artikel_mengeneinheiten`` kannte nur Kuerzel, Bezeichnung, Basiseinheit, Faktor und Dezimalstellen.
Neu: Nummer (hoechstens 4 Stellen), Langtext, ISO-Name, DataNorm-Kurzbezeichnung, Statistikkennzeichen,
Preisbezug (Einheit und Menge - Bestand in kg, Preis je 100 kg) und UN-Mengeneinheit nach UN/ECE Recommendation 20
(E-Rechnung, openTRANS). "Rundung bei Umrechnung" ist die vorhandene Spalte ``dezimalstellen``, jetzt 0 bis 4.
"""
from __future__ import annotations

from alembic import op

revision = "mengeneinheit_aeins_felder_20261124"
down_revision = "mahnstufen_verlauf_entfernen_20261123"
branch_labels = None
depends_on = None

TABELLE = "domain_shared.artikel_mengeneinheiten"
SPALTEN = (
    ("nummer", "integer"),
    ("langtext", "varchar(80)"),
    ("iso_name", "varchar(20)"),
    ("datanorm_kurz", "varchar(10)"),
    ("statistikkennzeichen", "varchar(20)"),
    ("preisbezug_einheit", "varchar(10)"),
    ("preisbezug_menge", "numeric(14,4)"),
    ("un_code", "varchar(3)"),
)


def upgrade() -> None:
    for name, typ in SPALTEN:
        op.execute(f"ALTER TABLE {TABELLE} ADD COLUMN IF NOT EXISTS {name} {typ}")
    op.execute(f"UPDATE {TABELLE} SET dezimalstellen = 4 WHERE dezimalstellen > 4")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_mengeneinheit_nummer CHECK (nummer BETWEEN 1 AND 9999)")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_mengeneinheit_rundung CHECK (dezimalstellen BETWEEN 0 AND 4)")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_mengeneinheit_preisbezug CHECK (preisbezug_menge > 0)")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_mengeneinheit_un_code CHECK (un_code ~ '^[A-Z0-9]{{2,3}}$')")
    op.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS uq_mengeneinheit_nummer ON {TABELLE} (tenant_id, nummer) "
               "WHERE nummer IS NOT NULL")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_shared.uq_mengeneinheit_nummer")
    for name in ("un_code", "preisbezug", "rundung", "nummer"):
        op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS ck_mengeneinheit_{name}")
    for name, _ in reversed(SPALTEN):
        op.execute(f"ALTER TABLE {TABELLE} DROP COLUMN IF EXISTS {name}")
