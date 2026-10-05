"""Eine Lastschrift gehoert einem Haus.

``domain_shared.direct_debit_items`` wurde am 17.09. angelegt (Migration
``mask_frontend_bridges_20260917``) — **ohne** ``tenant_id``. Der Lauf war damit
nur durch seine ``run_id`` von anderen getrennt, und die kennt jeder, der sie
gesehen hat. ``direct_debits.py`` nahm den Mandanten entgegen und benutzte ihn
nicht: Auflisten, Einzelabruf (mit Name, IBAN, BIC, Mandatsreferenz und Betrag),
Export, Freigabe, Ausfuehrung und Storno liefen ueber Haeuser hinweg.

Die andere Haelfte des Codes (``finance_followup.py``, ``finance_actions.py``)
filtert seit immer nach ``tenant_id`` **und** ``debitor_id`` — Spalten, die es
nicht gab. Jede dieser Abfragen scheiterte still. Die beiden Haelften
widersprachen sich ueber die Form derselben Tabelle.

Diese Migration entscheidet den Widerspruch zugunsten des Lesepfads: Die
Tabelle bekommt die drei Spalten, die er annimmt — und ``sepa_mandates``, die
Tabelle, ohne die der Lastschriftenlauf ueberhaupt nichts sammeln kann, wird
angelegt.

``tenant_id`` ist ``NOT NULL`` ohne Nachfuellen moeglich, weil die Tabelle am
30.09.2026 in der Entwicklungs- **und** in der frischen Datenbank leer war. Eine
Lastschrift ohne Eigentuemer soll es nicht geben koennen, auch nicht als
Altbestand.

Revision ID: lastschrift_mandant_20260930
Revises: projektion_cursor_20260930
"""

from __future__ import annotations

from alembic import op

revision = "lastschrift_mandant_20260930"
down_revision = "projektion_cursor_20260930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tenant_id: erst nullbar anlegen, dann verschaerfen. Auf einer leeren
    # Tabelle ist das gleichbedeutend; auf einer Installation, auf der doch
    # Zeilen liegen, schlaegt der zweite Schritt fehl und zeigt das an,
    # statt die Zeilen einem beliebigen Haus zuzuschlagen.
    op.execute(
        """
        ALTER TABLE domain_shared.direct_debit_items
            ADD COLUMN IF NOT EXISTS tenant_id  VARCHAR(80),
            ADD COLUMN IF NOT EXISTS debitor_id VARCHAR(80),
            ADD COLUMN IF NOT EXISTS currency   VARCHAR(3) NOT NULL DEFAULT 'EUR'
        """
    )
    op.execute(
        """
        ALTER TABLE domain_shared.direct_debit_items
            ALTER COLUMN tenant_id SET NOT NULL
        """
    )

    # Gelesen wird immer "mein Haus, dieser Lauf". Der alte Index nur auf
    # run_id bleibt fuer die Aggregation ueber Laeufe brauchbar.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_direct_debit_items_tenant_run "
        "ON domain_shared.direct_debit_items (tenant_id, run_id)"
    )

    # ``domain_shared.sepa_mandates`` existierte nirgends — auch nicht in der
    # gewachsenen Entwicklungsdatenbank. Ohne sie scheitert der
    # Lastschriftenlauf (``finance_actions.run_direct_debit``) an seinem JOIN,
    # und die Vorschau kann kein Mandat pruefen.
    #
    # Die Spalten sind **nicht erfunden**, sondern die, die der Code nennt:
    # ``tenant_id``, ``debitor_id``, ``mandate_reference``, ``mandate_valid``,
    # ``mandate_expired_at``. Was ein vollstaendiges SEPA-Mandat darueber
    # hinaus braucht — Glaeubiger-Identifikationsnummer, Sequenztyp
    # (FRST/RCUR/OOFF/FNAL), Verfahren (CORE/B2B), Unterschriftsdatum, IBAN des
    # Zahlungspflichtigen — legt diese Migration **nicht** fest. Das ist eine
    # Fachentscheidung des Finanz-Owners und Voraussetzung fuer eine echte
    # pain.008; siehe Handshake in der Slice-Doku.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.sepa_mandates (
            id                 VARCHAR(64) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id          VARCHAR(80)  NOT NULL,
            debitor_id         VARCHAR(80)  NOT NULL,
            mandate_reference  VARCHAR(35)  NOT NULL,
            mandate_valid      BOOLEAN      NOT NULL DEFAULT TRUE,
            mandate_expired_at TIMESTAMPTZ,
            created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )
    # Eine Mandatsreferenz ist je Haus eindeutig — sie ist die Kennung, die in
    # der Lastschrift beim Zahlungspflichtigen und bei der Bank steht.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_sepa_mandates_tenant_reference "
        "ON domain_shared.sepa_mandates (tenant_id, mandate_reference)"
    )
    # Gelesen wird "hat dieser Debitor meines Hauses ein gueltiges Mandat?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_sepa_mandates_tenant_debitor "
        "ON domain_shared.sepa_mandates (tenant_id, debitor_id)"
    )


def downgrade() -> None:
    # Die Spalten zuruecknehmen wuerde den Mandantenbezug jeder vorhandenen
    # Lastschrift verlieren — und damit genau den Zustand wiederherstellen,
    # den diese Migration behebt. Kein DROP TABLE auf den Mandaten: Ein Mandat
    # ist die Einzugsermaechtigung eines Kunden, kein Zwischenstand.
    # Zurueckgenommen werden nur die Indizes.
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_direct_debit_items_tenant_run")
    op.execute("DROP INDEX IF EXISTS domain_shared.ux_sepa_mandates_tenant_reference")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_sepa_mandates_tenant_debitor")
