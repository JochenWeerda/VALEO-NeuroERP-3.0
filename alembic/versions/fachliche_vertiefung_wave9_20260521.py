"""Fachliche Vertiefung Wave 9: Betriebsstätten/Filialen, Individuelle Artikelnummern, Versandprofile

Revision ID: fachliche_vertiefung_wave9_20260521
Revises: fachliche_vertiefung_wave8_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave9_20260521"
down_revision = "fachliche_vertiefung_wave8_20260521"
branch_labels = None
depends_on = None


def upgrade():
    # ── Betriebsstätten/Filialen [FILS] ───────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.betriebsstaetten (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            filial_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            ist_zentrale    BOOLEAN NOT NULL DEFAULT FALSE,
            zentrale_filial_nr TEXT,
            ident_untergrenze INTEGER,
            ident_obergrenze  INTEGER,
            strasse         TEXT,
            plz             TEXT,
            ort             TEXT,
            land            TEXT,
            telefon         TEXT,
            email           TEXT,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, filial_nr)
        )
    """)

    # ── Individuelle Artikelnummern [INDIVART] ────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.individuelle_artikelnummern (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            artikel_nr      TEXT NOT NULL,
            partner_nr      TEXT NOT NULL,
            partner_typ     TEXT NOT NULL DEFAULT 'kunden',
            indiv_artikel_nr TEXT NOT NULL,
            indiv_bezeichnung TEXT,
            gueltig_von     DATE,
            gueltig_bis     DATE,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, artikel_nr, partner_nr, partner_typ)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_indiv_artikelnr_lookup
            ON domain_shared.individuelle_artikelnummern(tenant_id, partner_nr, indiv_artikel_nr)
    """)

    # ── Versandprofilstamm ────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.versandprofile (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            profil_nr       TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL,
            versandart      TEXT NOT NULL DEFAULT 'email',
            smtp_server     TEXT,
            smtp_port       INTEGER,
            smtp_benutzer   TEXT,
            absender_email  TEXT,
            absender_name   TEXT,
            cc_email        TEXT,
            bcc_email       TEXT,
            betreff_vorlage TEXT,
            archiv_kennzeichen BOOLEAN NOT NULL DEFAULT TRUE,
            aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, profil_nr)
        )
    """)

    # ── Avise (Lieferavisierungen) ────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.lieferavise (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            avis_nr         TEXT NOT NULL,
            lieferant_nr    TEXT,
            kunden_nr       TEXT,
            lieferschein_nr TEXT,
            avis_datum      DATE NOT NULL,
            lieferdatum_erwartet DATE,
            status          TEXT NOT NULL DEFAULT 'offen',
            artikel_nr      TEXT,
            menge           NUMERIC(18,6),
            mengeneinheit   TEXT,
            notiz           TEXT,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, avis_nr)
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS domain_shared.lieferavise")
    op.execute("DROP TABLE IF EXISTS domain_shared.versandprofile")
    op.execute("DROP TABLE IF EXISTS domain_shared.individuelle_artikelnummern")
    op.execute("DROP TABLE IF EXISTS domain_shared.betriebsstaetten")
