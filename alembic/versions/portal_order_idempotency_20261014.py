"""Portal-Bestellungen: Spalte idempotency_key, eindeutig je Mandant und Kunde.

Das Modell ``CustomerOrder`` kannte die Spalte seit C3 (Idempotenz der Portalbestellung), keine Migration legte sie
an. Auf einer frischen Installation antworteten deshalb alle Bestellwege des Portalshops 500 — Liste, Detail,
Anlegen, Abgleich, Beobachtung. Der Schluessel stammt vom Client und ist nur je Mandant und Kunde eindeutig.
"""
from alembic import op

revision = "portal_order_idempotency_20261014"
down_revision = "portal_kundenzugaenge_20261014"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    ALTER TABLE domain_portal.customer_orders ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(128);
    CREATE UNIQUE INDEX IF NOT EXISTS ux_customer_orders_idempotency
      ON domain_portal.customer_orders (tenant_id, customer_id, idempotency_key);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS domain_portal.ux_customer_orders_idempotency")
    op.execute("ALTER TABLE domain_portal.customer_orders DROP COLUMN IF EXISTS idempotency_key")
