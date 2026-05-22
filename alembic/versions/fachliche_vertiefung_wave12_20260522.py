"""Fachliche Vertiefung Wave 12: Zu-/Abschlaggruppen/-klassen, Vertreterprovisionen

Revision ID: fachliche_vertiefung_wave12_20260522
Revises: fachliche_vertiefung_wave11_20260522
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave12_20260522"
down_revision = "fachliche_vertiefung_wave11_20260522"
branch_labels = None
depends_on = None


def upgrade():
    # ── Zu-/Abschlaggruppen [ZAGR] ────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zu_abschlaggruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            richtung        TEXT NOT NULL DEFAULT 'vk',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr, richtung)
        )
    """)

    # ── Zu-/Abschlagklassen [ZAKL] ────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zu_abschlagklassen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            klasse_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            richtung        TEXT NOT NULL DEFAULT 'vk',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, klasse_nr, richtung)
        )
    """)

    # ── Zu-/Abschlag-Konditionen (Gruppe × Klasse → Wert) ────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zu_abschlag_konditionen (
            id              TEXT PRIMARY KEY,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.zu_abschlaggruppen(id),
            klasse_id       TEXT NOT NULL REFERENCES domain_shared.zu_abschlagklassen(id),
            kondition_typ   TEXT NOT NULL DEFAULT 'prozent',
            wert            NUMERIC(10,4) NOT NULL,
            gueltig_ab      DATE NOT NULL,
            gueltig_bis     DATE,
            beschreibung    TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # ── Vertreter-Provisionsgruppen ───────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.vertreter_provisionsgruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            richtung        TEXT NOT NULL DEFAULT 'vk',
            provisionstyp   TEXT NOT NULL DEFAULT 'fix',
            provisionssatz  NUMERIC(6,4),
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr, richtung)
        )
    """)

    # ── Vertreter-Provisionsstaffeln ──────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.vertreter_provisionsstaffeln (
            id              TEXT PRIMARY KEY,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.vertreter_provisionsgruppen(id),
            vertreterklasse TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.vertreter_staffel_zeilen (
            id              TEXT PRIMARY KEY,
            staffel_id      TEXT NOT NULL REFERENCES domain_shared.vertreter_provisionsstaffeln(id),
            zeile_nr        INTEGER NOT NULL,
            ab_wert         NUMERIC(12,4) NOT NULL,
            provisionssatz  NUMERIC(6,4) NOT NULL,
            UNIQUE (staffel_id, zeile_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.vertreter_staffel_zeilen")
    op.execute("DROP TABLE IF EXISTS domain_shared.vertreter_provisionsstaffeln")
    op.execute("DROP TABLE IF EXISTS domain_shared.vertreter_provisionsgruppen")
    op.execute("DROP TABLE IF EXISTS domain_shared.zu_abschlag_konditionen")
    op.execute("DROP TABLE IF EXISTS domain_shared.zu_abschlagklassen")
    op.execute("DROP TABLE IF EXISTS domain_shared.zu_abschlaggruppen")
