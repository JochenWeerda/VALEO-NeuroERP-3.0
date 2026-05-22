"""Fachliche Vertiefung Wave 10: Erlöskennziffern, Warengruppen, Zahlungsbedingungen

Revision ID: fachliche_vertiefung_wave10_20260521
Revises: fachliche_vertiefung_wave9_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave10_20260521"
down_revision = "fachliche_vertiefung_wave9_20260521"
branch_labels = None
depends_on = None


def upgrade():
    # ── Warengruppen 3-stufig ─────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.hauptwarengruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.oberwarengruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            haupt_id        TEXT NOT NULL REFERENCES domain_shared.hauptwarengruppen(id),
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.warengruppen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            gruppe_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            ober_id         TEXT NOT NULL REFERENCES domain_shared.oberwarengruppen(id),
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, gruppe_nr)
        )
    """)

    # ── Erlöskennziffern [EKZS] ───────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.erloeskennziffern (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            ekz_nr          TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, ekz_nr)
        )
    """)

    # ── Erlöskontenzuordnung [EKZZ] ───────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.erloeskontenzuordnung (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            ekz_id          TEXT NOT NULL REFERENCES domain_shared.erloeskennziffern(id),
            gueltig_ab      DATE NOT NULL,
            steuerschluessel TEXT,
            erlösklasse     TEXT,
            steuergruppe    TEXT,
            buchungsklasse  TEXT,
            konto_erloese   TEXT,
            konto_aufwand   TEXT,
            konto_umsatzsteuer TEXT,
            konto_vorsteuer TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, ekz_id, gueltig_ab, steuerschluessel, erlösklasse, buchungsklasse)
        )
    """)

    # ── Zahlungsbedingungen [ZABD] ────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.zahlungsbedingungen (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            zabd_nr         TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            zahlungsziel_tage INTEGER NOT NULL DEFAULT 30,
            skonto1_tage    INTEGER,
            skonto1_prozent NUMERIC(6,4),
            skonto2_tage    INTEGER,
            skonto2_prozent NUMERIC(6,4),
            netto_tage      INTEGER DEFAULT 30,
            manuelles_datum BOOLEAN NOT NULL DEFAULT FALSE,
            zahlungsart     TEXT NOT NULL DEFAULT 'ueberweisung',
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, zabd_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.zahlungsbedingungen")
    op.execute("DROP TABLE IF EXISTS domain_shared.erloeskontenzuordnung")
    op.execute("DROP TABLE IF EXISTS domain_shared.erloeskennziffern")
    op.execute("DROP TABLE IF EXISTS domain_shared.warengruppen")
    op.execute("DROP TABLE IF EXISTS domain_shared.oberwarengruppen")
    op.execute("DROP TABLE IF EXISTS domain_shared.hauptwarengruppen")
