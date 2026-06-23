"""DOM-CON-004 — Kontrakt Lifecycle, Fixing, Settlement Tabellen

Revision ID: kontrakt_lifecycle_fixing_20260623
Revises: controlling_budget_abschluss_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "kontrakt_lifecycle_fixing_20260623"
down_revision = "controlling_budget_abschluss_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_kontrakte")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_lifecycle (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            kontrakt_id     TEXT NOT NULL UNIQUE,
            tenant_id       TEXT NOT NULL,
            kontrakt_nr     TEXT NOT NULL,
            artikel_id      TEXT NOT NULL,
            menge_t         NUMERIC(12,3) NOT NULL,
            preis_eur_t     NUMERIC(12,4) NOT NULL,
            lieferant_id    TEXT NOT NULL,
            periode         TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'ENTWURF',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_status_log (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            kontrakt_id     TEXT NOT NULL,
            tenant_id       TEXT NOT NULL,
            old_status      TEXT NOT NULL DEFAULT '',
            new_status      TEXT NOT NULL,
            operator        TEXT NOT NULL,
            grund           TEXT NOT NULL DEFAULT '',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_fixings (
            id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            kontrakt_id             TEXT NOT NULL,
            tenant_id               TEXT NOT NULL,
            fixing_datum            TEXT NOT NULL,
            fixing_preis_eur_t      NUMERIC(12,4) NOT NULL,
            menge_t                 NUMERIC(12,3) NOT NULL,
            markt                   TEXT NOT NULL DEFAULT 'KASSA',
            referenz                TEXT NOT NULL DEFAULT '',
            operator                TEXT NOT NULL DEFAULT 'system',
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_settlements (
            id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            kontrakt_id                 TEXT NOT NULL,
            tenant_id                   TEXT NOT NULL,
            lieferung_datum             TEXT NOT NULL,
            gelieferte_menge_t          NUMERIC(12,3) NOT NULL,
            abrechnungspreis_eur_t      NUMERIC(12,4) NOT NULL,
            netto_eur                   NUMERIC(14,2) NOT NULL,
            referenz                    TEXT NOT NULL DEFAULT '',
            status                      TEXT NOT NULL DEFAULT 'OFFEN',
            storno_grund                TEXT NOT NULL DEFAULT '',
            operator                    TEXT NOT NULL DEFAULT 'system',
            created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at                  TIMESTAMPTZ
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_kontrakte.kontrakt_settlements")
    op.execute("DROP TABLE IF EXISTS domain_kontrakte.kontrakt_fixings")
    op.execute("DROP TABLE IF EXISTS domain_kontrakte.kontrakt_status_log")
    op.execute("DROP TABLE IF EXISTS domain_kontrakte.kontrakt_lifecycle")
