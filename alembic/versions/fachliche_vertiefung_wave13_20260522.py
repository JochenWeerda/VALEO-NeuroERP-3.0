"""Fachliche Vertiefung Wave 13: Zahlungsformulare, Zinsgruppen, Leergutarten

Revision ID: fachliche_vertiefung_wave13_20260522
Revises: fachliche_vertiefung_wave12_20260522
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave13_20260522"
down_revision = "fachliche_vertiefung_wave12_20260522"
branch_labels = None
depends_on = None


def upgrade():
    # ── Zahlungsformulare [FIZAF] ─────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zahlungsformulare (
            id                  TEXT PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            formular_nr         TEXT NOT NULL,
            bezeichnung         TEXT NOT NULL,
            formularklasse      TEXT NOT NULL DEFAULT 'ausgang',
            bank_blz            TEXT,
            bank_iban           TEXT,
            formulareinrichtung TEXT,
            aktiv               BOOLEAN NOT NULL DEFAULT TRUE,
            created_at          TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, formular_nr)
        )
    """)

    # ── Zinsgruppen ───────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zinsgruppen (
            id                          TEXT PRIMARY KEY,
            tenant_id                   TEXT NOT NULL,
            gruppe_nr                   TEXT NOT NULL,
            bezeichnung                 TEXT NOT NULL,
            zinssatz                    NUMERIC(7,4) NOT NULL,
            zinsmethode                 TEXT NOT NULL DEFAULT 'act_360',
            schwellwert_tage            INTEGER NOT NULL DEFAULT 0,
            konto_zinsen                TEXT,
            konto_zinsabschlagsteuer    TEXT,
            aktiv                       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at                  TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)

    # ── Leergutarten ──────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.leergutarten (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            art_nr          TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            leergut_typ     TEXT NOT NULL DEFAULT 'palette',
            pfandwert       NUMERIC(10,2),
            konto_leergut   TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, art_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.leergutarten")
    op.execute("DROP TABLE IF EXISTS domain_shared.zinsgruppen")
    op.execute("DROP TABLE IF EXISTS domain_shared.zahlungsformulare")
