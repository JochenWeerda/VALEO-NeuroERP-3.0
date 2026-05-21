"""Fachliche Vertiefung Wave 8: Rohwarengruppen, Rohware-Qualitäten, Zu-/Abschlag-Staffeln

Revision ID: fachliche_vertiefung_wave8_20260521
Revises: fachliche_vertiefung_wave7_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave8_20260521"
down_revision = "fachliche_vertiefung_wave7_20260521"
branch_labels = None
depends_on = None


def upgrade():
    # ── Rohwarengruppen [RWG] ─────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohwarengruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            artikel_nr      TEXT,
            ek_aktiv        BOOLEAN NOT NULL DEFAULT TRUE,
            vk_aktiv        BOOLEAN NOT NULL DEFAULT FALSE,
            waehrung        TEXT NOT NULL DEFAULT 'EUR',
            mengeneinheit   TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)

    # ── Abrechnungsschemata (Sorten) ─────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_abrechnungsschemata (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            schema_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.rohwarengruppen(id),
            artikel_nr      TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, schema_nr)
        )
    """)

    # ── Rohware-Qualitäten (Analysewert-Definitionen) [ROHQU] ────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_qualitaeten (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            qualitaet_nr    TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.rohwarengruppen(id),
            schema_id       TEXT REFERENCES domain_shared.rohware_abrechnungsschemata(id),
            basis_wert      NUMERIC(12,4),
            basis_wert_bis  NUMERIC(12,4),
            einheit         TEXT,
            position_typ    TEXT NOT NULL DEFAULT 'qualitaet',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, qualitaet_nr)
        )
    """)

    # ── Rohware Zu-/Abschlag-Staffeln ────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_za_staffeln (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            staffel_nr      TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.rohwarengruppen(id),
            qualitaet_id    TEXT REFERENCES domain_shared.rohware_qualitaeten(id),
            ergebnis_typ    TEXT NOT NULL DEFAULT 'preiszuschlag',
            abrechnung_typ  TEXT NOT NULL DEFAULT 'einfacher_umrechnungsfaktor',
            basiserweiterung NUMERIC(12,4) DEFAULT 0,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, staffel_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_za_staffel_zeilen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            staffel_id      TEXT NOT NULL REFERENCES domain_shared.rohware_za_staffeln(id),
            zeile_nr        INTEGER NOT NULL,
            bis_wert        NUMERIC(12,4) NOT NULL,
            umrechnungsfaktor NUMERIC(12,6) NOT NULL,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (staffel_id, zeile_nr)
        )
    """)

    # ── Rohware-Analysewert-Korrektur-Tabellen ────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_analysewert_korrekturen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            korrektur_nr    TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            gruppe_id       TEXT NOT NULL REFERENCES domain_shared.rohwarengruppen(id),
            werte_in        TEXT NOT NULL DEFAULT 'prozentsatz',
            skala_typ       TEXT NOT NULL DEFAULT 'fixskala',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, korrektur_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.rohware_analysewert_korrektur_zeilen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            korrektur_id    TEXT NOT NULL REFERENCES domain_shared.rohware_analysewert_korrekturen(id),
            zeile_nr        INTEGER NOT NULL,
            index_wert      NUMERIC(12,4) NOT NULL,
            korrektur_wert  NUMERIC(12,6) NOT NULL,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (korrektur_id, zeile_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_analysewert_korrektur_zeilen")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_analysewert_korrekturen")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_za_staffel_zeilen")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_za_staffeln")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_qualitaeten")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohware_abrechnungsschemata")
    op.execute("DROP TABLE IF EXISTS domain_shared.rohwarengruppen")
