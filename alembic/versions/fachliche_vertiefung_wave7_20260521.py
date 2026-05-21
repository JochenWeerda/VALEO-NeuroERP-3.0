"""Fachliche Vertiefung Wave 7: Daueraufträge, Individualpreise, Stücklisten/Rezepturen

Revision ID: fachliche_vertiefung_wave7_20260521
Revises: fachliche_vertiefung_wave6_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave7_20260521"
down_revision = "fachliche_vertiefung_wave6_20260521"
branch_labels = None
depends_on = None


def upgrade():
    # ── Daueraufträge [DAU] ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.dauerauftraege (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            da_nr           TEXT NOT NULL,
            kunden_nr       TEXT NOT NULL,
            bezeichnung     TEXT,
            -- Turnus
            da_anfang       DATE NOT NULL,
            da_naechster    DATE NOT NULL,
            da_ende         DATE,
            perioden_typ    TEXT NOT NULL DEFAULT 'monatlich',
            perioden_wert   INTEGER DEFAULT 1,
            -- Status
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            letzter_lauf    TIMESTAMP,
            erstellt_von    TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, da_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.dauerauftrag_positionen (
            id                  TEXT PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            dauerauftrag_id     TEXT NOT NULL REFERENCES domain_shared.dauerauftraege(id),
            pos_nr              INTEGER NOT NULL,
            artikel_nr          TEXT NOT NULL,
            menge               NUMERIC(18,6) NOT NULL,
            mengeneinheit       TEXT,
            preis_eur           NUMERIC(18,4),
            created_at          TIMESTAMP NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.dauerauftrag_ausfuehrungen (
            id                  TEXT PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            dauerauftrag_id     TEXT NOT NULL REFERENCES domain_shared.dauerauftraege(id),
            ausfuehrungs_datum  DATE NOT NULL,
            belegnummer         TEXT,
            status              TEXT NOT NULL DEFAULT 'erstellt',
            created_at          TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # ── Individualpreise [PRI/PRIE] ──────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.individualpreise (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            preis_typ       TEXT NOT NULL DEFAULT 'VK',
            artikel_nr      TEXT NOT NULL,
            partner_nr      TEXT,
            gueltig_von     DATE NOT NULL,
            gueltig_bis     DATE,
            preis_eur       NUMERIC(18,4) NOT NULL,
            mengeneinheit   TEXT,
            staffel_menge   NUMERIC(18,6) DEFAULT 0,
            waehrung        TEXT NOT NULL DEFAULT 'EUR',
            notiz           TEXT,
            erstellt_von    TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, preis_typ, artikel_nr, partner_nr, gueltig_von, staffel_menge)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_individualpreise_lookup
            ON domain_shared.individualpreise(tenant_id, preis_typ, artikel_nr, partner_nr, gueltig_von)
    """)

    # ── Stücklisten / Rezepturen Stamm [ARTSTLI] ─────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.stuecklisten (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            stueckliste_nr  TEXT NOT NULL,
            artikel_nr      TEXT NOT NULL,
            bezeichnung     TEXT,
            menge_basis     NUMERIC(18,6) NOT NULL DEFAULT 1,
            einheit         TEXT NOT NULL DEFAULT 'Stk',
            variable_komp   BOOLEAN NOT NULL DEFAULT FALSE,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, stueckliste_nr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.stuecklisten_positionen (
            id                  TEXT PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            stueckliste_id      TEXT NOT NULL REFERENCES domain_shared.stuecklisten(id),
            pos_nr              INTEGER NOT NULL,
            komponente_nr       TEXT NOT NULL,
            komponente_bez      TEXT,
            menge               NUMERIC(18,6) NOT NULL,
            einheit             TEXT,
            anteil_prozent      NUMERIC(7,4),
            optional            BOOLEAN NOT NULL DEFAULT FALSE,
            created_at          TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (stueckliste_id, pos_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.stuecklisten_positionen")
    op.execute("DROP TABLE IF EXISTS domain_shared.stuecklisten")
    op.execute("DROP TABLE IF EXISTS domain_shared.individualpreise")
    op.execute("DROP TABLE IF EXISTS domain_shared.dauerauftrag_ausfuehrungen")
    op.execute("DROP TABLE IF EXISTS domain_shared.dauerauftrag_positionen")
    op.execute("DROP TABLE IF EXISTS domain_shared.dauerauftraege")
