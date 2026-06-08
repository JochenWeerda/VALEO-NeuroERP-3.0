"""Repair canonical sales delivery-note tables for CRM360 O2C.

Revision ID: crm360_o2c_delivery_20260608
Revises: kunden_crm360_20260607
"""

from __future__ import annotations

from alembic import op


revision = "crm360_o2c_delivery_20260608"
down_revision = "kunden_crm360_20260607"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_sales")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_sales.delivery_notes (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            delivery_note_number VARCHAR(50) NOT NULL,
            customer_id VARCHAR,
            branch_id VARCHAR,
            sales_rep_id VARCHAR,
            operator_id VARCHAR,
            delivery_date DATE NOT NULL,
            delivery_time TIME,
            cost_center_id VARCHAR,
            truck_number INTEGER,
            is_credit_note BOOLEAN NOT NULL DEFAULT FALSE,
            is_self_pickup BOOLEAN NOT NULL DEFAULT FALSE,
            is_early_payment BOOLEAN NOT NULL DEFAULT FALSE,
            reference_invoice_number VARCHAR(50),
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            is_printed BOOLEAN NOT NULL DEFAULT FALSE,
            is_delivered BOOLEAN NOT NULL DEFAULT FALSE,
            invoice_number VARCHAR(50),
            totals JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by VARCHAR,
            updated_by VARCHAR,
            CONSTRAINT uq_delivery_notes_tenant_number UNIQUE (tenant_id, delivery_note_number)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_sales.delivery_note_positions (
            id VARCHAR PRIMARY KEY,
            delivery_note_id VARCHAR NOT NULL
                REFERENCES domain_sales.delivery_notes(id) ON DELETE CASCADE,
            pos_nr INTEGER NOT NULL,
            artikel_id VARCHAR,
            artikel_nr VARCHAR(50),
            bezeichnung VARCHAR(255),
            bezeichnung2 VARCHAR(255),
            menge NUMERIC(14, 3) NOT NULL,
            einheit VARCHAR(20),
            listenpreis NUMERIC(14, 4),
            rabatt NUMERIC(5, 2) NOT NULL DEFAULT 0,
            art VARCHAR(50),
            netto_preis NUMERIC(14, 4),
            netto_betrag NUMERIC(14, 2),
            niederlassung INTEGER,
            lagerhalle VARCHAR(80),
            lagerfach VARCHAR(80),
            charge VARCHAR(80),
            serien_nr VARCHAR(80),
            erloskonto VARCHAR(20),
            mwst_prozent NUMERIC(5, 2) NOT NULL DEFAULT 19,
            kontrakt_nr VARCHAR(50),
            skontierf BOOLEAN NOT NULL DEFAULT FALSE,
            fremdware BOOLEAN NOT NULL DEFAULT FALSE,
            gef_punkt VARCHAR(50),
            na_bio VARCHAR(50),
            muster_nr VARCHAR(50),
            strecke VARCHAR(50),
            zus_beleg VARCHAR(50),
            anerken VARCHAR(50),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_delivery_note_positions_pos_nr UNIQUE (delivery_note_id, pos_nr)
        )
        """
    )

    header_columns = {
        "created_by": "VARCHAR",
        "updated_by": "VARCHAR",
    }
    for column, sql_type in header_columns.items():
        op.execute(
            f"ALTER TABLE domain_sales.delivery_notes ADD COLUMN IF NOT EXISTS {column} {sql_type}"
        )

    position_columns = {
        "gef_punkt": "VARCHAR(50)",
        "na_bio": "VARCHAR(50)",
        "muster_nr": "VARCHAR(50)",
        "strecke": "VARCHAR(50)",
        "zus_beleg": "VARCHAR(50)",
        "anerken": "VARCHAR(50)",
    }
    for column, sql_type in position_columns.items():
        op.execute(
            f"ALTER TABLE domain_sales.delivery_note_positions ADD COLUMN IF NOT EXISTS {column} {sql_type}"
        )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_notes_tenant_id "
        "ON domain_sales.delivery_notes (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_notes_customer_id "
        "ON domain_sales.delivery_notes (customer_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_notes_delivery_date "
        "ON domain_sales.delivery_notes (delivery_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_notes_status "
        "ON domain_sales.delivery_notes (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_note_positions_delivery_note "
        "ON domain_sales.delivery_note_positions (delivery_note_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_note_positions_artikel_nr "
        "ON domain_sales.delivery_note_positions (artikel_nr)"
    )


def downgrade() -> None:
    # Repair migrations must not remove tables that may predate this revision.
    pass
