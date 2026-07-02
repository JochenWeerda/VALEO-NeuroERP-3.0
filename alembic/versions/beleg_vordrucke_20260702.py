"""admin: beleg_vordrucke — Druckvorlagen-Editor für Papier/PDF-Ausdrucke

Vorlagen für Wiegeschein, Stundenzettel, Fahrtenbuch, Belege, (Geschenk-)
Gutscheine, Rabatt-Coupons, Info-Schreiben, Handouts, Sackanhänger u. a.
Layout als JSONB-Elementliste (text/feld/linie/rechteck/qrcode) mit
mm-Koordinaten, renderbar über POST /admin/vordrucke/{id}/render.

Revision ID: beleg_vordrucke_20260702
Revises: hr_applications_table_20260702
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op

revision = "beleg_vordrucke_20260702"
down_revision = "hr_applications_table_20260702"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.beleg_vordrucke (
            id            VARCHAR(36)  PRIMARY KEY,
            tenant_id     VARCHAR(64)  NOT NULL,
            name          VARCHAR(200) NOT NULL,
            kategorie     VARCHAR(40)  NOT NULL DEFAULT 'sonstig',
            beschreibung  TEXT,
            papierformat  VARCHAR(20)  NOT NULL DEFAULT 'A4',
            ausrichtung   VARCHAR(10)  NOT NULL DEFAULT 'hoch',
            layout        JSONB        NOT NULL DEFAULT '[]'::jsonb,
            beispieldaten JSONB        NOT NULL DEFAULT '{}'::jsonb,
            aktiv         BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_beleg_vordrucke_tenant_kategorie
            ON domain_shared.beleg_vordrucke (tenant_id, kategorie)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.beleg_vordrucke")
