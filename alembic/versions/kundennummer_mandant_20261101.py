"""Kundennummer (= Debitorennummer) je Mandant eindeutig statt systemweit.

Revision ID: kundennummer_mandant_20261101
Revises: gdpr_request_process_20261031

``001_initial_schema`` legte ``customers_customer_number_key UNIQUE (customer_number)``
an: Fuehrte ein Mandant den Debitor "10001", konnte kein zweiter ihn je anlegen. Seit
01.11.2026 ist ``domain_crm.customers`` der fuehrende Debitorenstamm, und die Anlage
prueft die Nummer je Mandant. In der gewachsenen Entwicklungsdatenbank fehlte die
Eindeutigkeit ganz.

Jetzt gilt ``UNIQUE (tenant_id, customer_number)`` (beide Spalten NOT NULL). Gibt es
innerhalb eines Mandanten doppelte Nummern, bricht die Migration ab und nennt sie,
statt Daten umzuschreiben. Das ``downgrade`` stellt die systemweite Regel bewusst
nicht wieder her: Sobald zwei Mandanten dieselbe Nummer fuehren, ist sie nicht mehr
erfuellbar.
"""

from alembic import op
from sqlalchemy import text

revision = "kundennummer_mandant_20261101"
down_revision = "gdpr_request_process_20261031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    verbindung = op.get_bind()
    dubletten = verbindung.execute(text(
        "SELECT tenant_id, customer_number, count(*) FROM domain_crm.customers "
        "GROUP BY tenant_id, customer_number HAVING count(*) > 1 LIMIT 20"
    )).all()
    if dubletten:
        liste = ", ".join(f"{t or '(ohne Mandant)'}/{n} x{c}" for t, n, c in dubletten)
        raise RuntimeError(f"Doppelte Kundennummern je Mandant, bitte zuerst bereinigen: {liste}")

    op.execute("ALTER TABLE domain_crm.customers DROP CONSTRAINT IF EXISTS customers_customer_number_key")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_customers_mandant_nummer'
                  AND conrelid = 'domain_crm.customers'::regclass
            ) THEN
                ALTER TABLE domain_crm.customers
                    ADD CONSTRAINT uq_customers_mandant_nummer UNIQUE (tenant_id, customer_number);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_crm.customers DROP CONSTRAINT IF EXISTS uq_customers_mandant_nummer")
