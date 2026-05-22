"""Fachliche Vertiefung Wave 11: Partiestamm, Forderungsgruppen, Periodische Buchungen

Revision ID: fachliche_vertiefung_wave11_20260522
Revises: fachliche_vertiefung_wave10_20260521
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave11_20260522"
down_revision = "fachliche_vertiefung_wave10_20260521"
branch_labels = None
depends_on = None


def upgrade():
    # ── Partiegruppen [PGR] ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.partiegruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)

    # ── Partiestamm [PAR] ─────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.partiestamm (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            partie_nr       TEXT NOT NULL,
            bezeichnung     TEXT,
            artikel_nr      TEXT NOT NULL,
            lager_nr        TEXT,
            partie_typ      TEXT NOT NULL DEFAULT 'artikelstamm',
            gruppe_id       TEXT REFERENCES domain_shared.partiegruppen(id),
            erntejahr       INTEGER,
            herkunftsland   TEXT,
            status          TEXT NOT NULL DEFAULT 'aktiv',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, partie_nr)
        )
    """)

    # ── Forderungsgruppen [FORG] ──────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.forderungsgruppen (
            id                      TEXT PRIMARY KEY,
            tenant_id               TEXT NOT NULL,
            gruppe_nr               TEXT NOT NULL,
            bezeichnung             TEXT NOT NULL,
            konto_forderungen       TEXT,
            konto_verbindlichkeiten TEXT,
            konto_sammel_1          TEXT,
            konto_sammel_2          TEXT,
            konto_sammel_3          TEXT,
            aktiv                   BOOLEAN NOT NULL DEFAULT TRUE,
            created_at              TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)

    # ── Periodische Buchungen [WZA] ───────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.periodische_buchungen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            vorgangsklasse  TEXT NOT NULL DEFAULT 'ZA',
            konto           TEXT NOT NULL,
            gegenkonto      TEXT NOT NULL,
            buchungstext    TEXT,
            betrag          NUMERIC(15,2) NOT NULL,
            turnus          TEXT NOT NULL DEFAULT 'monatlich',
            gueltig_ab      DATE NOT NULL,
            gueltig_bis     DATE,
            gesperrt        BOOLEAN NOT NULL DEFAULT FALSE,
            kostenstelle    TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now()
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.periodische_buchungen")
    op.execute("DROP TABLE IF EXISTS domain_shared.forderungsgruppen")
    op.execute("DROP TABLE IF EXISTS domain_shared.partiestamm")
    op.execute("DROP TABLE IF EXISTS domain_shared.partiegruppen")
