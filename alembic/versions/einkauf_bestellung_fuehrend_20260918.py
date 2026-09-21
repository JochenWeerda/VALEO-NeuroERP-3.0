"""L3-Felder und drei Bestellfaelle an domain_einkauf.bestellungen.

Die native Maske las Spalten, die es am ORM nicht gab, und die Rollout-SQL
las Spalten, die es an der Tabelle nicht gab. Diese Revision legt die
fehlenden Kopffelder (Bestellfall, Ladetermin, Skontostaffel, Kette) und
Positionsfelder (Lieferantenartikel, Gebinde, Gewicht, Lagerfach) an und
legt die Kommunikationstabelle an, die der Tab-Endpunkt schon abfragte.

Revision ID: einkauf_bestellung_fuehrend_20260918
Revises: audit_attestations_20260917
Create Date: 2026-09-18
"""

from __future__ import annotations

from alembic import op

revision = "einkauf_bestellung_fuehrend_20260918"
down_revision = "audit_attestations_20260917"
branch_labels = None
depends_on = None

_KOPF = (
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS bestellfall VARCHAR(32) DEFAULT 'bestand_abgleich'",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS ansprechpartner VARCHAR(200)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS kreditor_konto VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS lieferant_nr VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS kostenstelle VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS kommission VARCHAR(100)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS ladetermin DATE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS ladetermin_ab DATE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS lade_datum DATE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS incoterms VARCHAR(10)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS lieferadresse TEXT",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS zahlungsbedingung VARCHAR(80)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS skonto1_tage INTEGER",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS skonto1_prozent NUMERIC(5,2)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS skonto2_tage INTEGER",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS skonto2_prozent NUMERIC(5,2)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS netto_tage INTEGER",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS fremdwaehrung VARCHAR(3)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS umrechnungsfaktor NUMERIC(12,6)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS anfrage_nr VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS angebot_nr VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS auftrag_nr VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS abverkauf_horizont VARCHAR(20)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS bedarfsmenge NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS mindestbestellmenge NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS maximalbestellmenge NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS artikelgruppe VARCHAR(80)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS lagerplatz_opt BOOLEAN DEFAULT FALSE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS fracht_opt BOOLEAN DEFAULT FALSE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS opportunitaetskostensatz NUMERIC(14,4)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS palettenstellplatz_kosten NUMERIC(14,4)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS lagerkosten_satz NUMERIC(14,4)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS verkaufsbeleg_id VARCHAR(64)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS kunden_id VARCHAR(64)",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS direktlieferung BOOLEAN DEFAULT FALSE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS ueberschlag_lager BOOLEAN DEFAULT FALSE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS neuer_artikel BOOLEAN DEFAULT FALSE",
    "ALTER TABLE domain_einkauf.bestellungen ADD COLUMN IF NOT EXISTS innovationshinweis TEXT",
)

_POS = (
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS gebinde_menge NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS gebinde_einheit VARCHAR(20)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS gebinde_schluessel VARCHAR(20)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS gewicht_kg NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS kontrakt_nr VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS lagerhalle VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS lagerfach VARCHAR(50)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS mindestmenge NUMERIC(14,3)",
    "ALTER TABLE domain_einkauf.bestellung_positionen ADD COLUMN IF NOT EXISTS maximalmenge NUMERIC(14,3)",
)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_einkauf")
    for stmt in _KOPF + _POS:
        op.execute(stmt)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_einkauf.bestellung_kommunikation (
            id            VARCHAR(36) PRIMARY KEY,
            tenant_id     VARCHAR(64) NOT NULL,
            bestellung_id VARCHAR(36) NOT NULL,
            kanal         VARCHAR(40),
            empfaenger    VARCHAR(255),
            versendet_am  TIMESTAMPTZ,
            status        VARCHAR(40),
            betreff       TEXT
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_ek_best_komm_bestellung
            ON domain_einkauf.bestellung_kommunikation (tenant_id, bestellung_id)
        """
    )
    op.execute(
        """
        COMMENT ON COLUMN domain_einkauf.bestellungen.bestellfall IS
            'bestand_abgleich | direktlieferung | innovation'
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_einkauf.bestellung_kommunikation")
