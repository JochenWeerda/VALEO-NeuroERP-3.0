"""Ausgangsrechnung und Rechnungsposition als eigene Objekte

Die Ausgangsrechnung war im Belegfluss bisher kein Gegenstand: Aus einem
Lieferschein wurde ein Journalsatz und ein offener Posten, beide ueber den
ganzen Beleg. Damit gab es nichts, worauf eine Positionszuordnung haette
zeigen koennen — und keine Stelle, an der nachlesbar waere, woher eine
berechnete Menge kommt.

``sales_invoice_lines.line_no`` ist der Schluessel, auf den
``doc_allocations.target_line_id`` zeigt. Deshalb ist er je Rechnung eindeutig
und wird nicht umnummeriert: Eine Umnummerierung liesse bestehende Zuordnungen
ins Leere zeigen.

Ausdruecklich **keine** Herkunftsspalte an der Position. Sie waere wieder die
1:1-Annahme, die das Mengenmodell aufloest — eine Rechnungsposition kann aus
mehreren Lieferscheinpositionen gespeist sein. Die Beziehung lebt in
``doc_allocations``, mit Menge, Einheit und Restmengenfuehrung.

Revision ID: sales_invoice_lines_20260915
Revises: doc_allocations_20260915
Create Date: 2026-09-15
"""

import sqlalchemy as sa
from alembic import op

revision = "sales_invoice_lines_20260915"
down_revision = "doc_allocations_20260915"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_sales")

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_sales.sales_invoices (
              id             VARCHAR PRIMARY KEY,
              tenant_id      VARCHAR(120) NOT NULL,
              invoice_number VARCHAR(60)  NOT NULL,
              customer_id    VARCHAR(120) NOT NULL,
              invoice_date   DATE         NOT NULL,
              due_date       DATE,
              currency       VARCHAR(3)   NOT NULL DEFAULT 'EUR',
              status         VARCHAR(20)  NOT NULL DEFAULT 'entwurf',
              net_amount     NUMERIC(18,2) NOT NULL DEFAULT 0,
              vat_amount     NUMERIC(18,2) NOT NULL DEFAULT 0,
              gross_amount   NUMERIC(18,2) NOT NULL DEFAULT 0,
              note           TEXT,
              created_by     VARCHAR(120),
              created_at     TIMESTAMPTZ DEFAULT NOW(),
              updated_at     TIMESTAMPTZ DEFAULT NOW()
            );

            -- Eine Rechnungsnummer gibt es je Mandant genau einmal. Ohne diese
            -- Grenze koennte ein zweiter Lauf dieselbe Nummer vergeben, und
            -- zwei Belege trueegen denselben Namen.
            CREATE UNIQUE INDEX IF NOT EXISTS uq_sales_invoice_number
              ON domain_sales.sales_invoices (tenant_id, invoice_number);

            CREATE INDEX IF NOT EXISTS ix_sales_invoice_customer
              ON domain_sales.sales_invoices (tenant_id, customer_id);

            CREATE TABLE IF NOT EXISTS domain_sales.sales_invoice_lines (
              id             VARCHAR PRIMARY KEY,
              tenant_id      VARCHAR(120) NOT NULL,
              invoice_id     VARCHAR NOT NULL
                             REFERENCES domain_sales.sales_invoices(id)
                             ON DELETE CASCADE,
              line_no        VARCHAR(120) NOT NULL,
              article_id     VARCHAR(120),
              article_number VARCHAR(80),
              description    VARCHAR(255),
              quantity       NUMERIC(18,6) NOT NULL,
              unit           VARCHAR(20)  NOT NULL,
              unit_price     NUMERIC(18,4) NOT NULL DEFAULT 0,
              net_amount     NUMERIC(18,2) NOT NULL DEFAULT 0,
              vat_rate       NUMERIC(5,2),
              created_at     TIMESTAMPTZ DEFAULT NOW(),
              updated_at     TIMESTAMPTZ DEFAULT NOW(),
              CONSTRAINT ck_sales_invoice_line_qty_positive CHECK (quantity > 0)
            );

            -- Die Positionsnummer ist das Ziel der Mengenzuordnungen. Zweimal
            -- dieselbe Nummer in einer Rechnung liesse nicht mehr erkennen,
            -- auf welche der beiden eine Zuordnung zeigt.
            CREATE UNIQUE INDEX IF NOT EXISTS uq_sales_invoice_line_no
              ON domain_sales.sales_invoice_lines (tenant_id, invoice_id, line_no);

            CREATE INDEX IF NOT EXISTS ix_sales_invoice_line_article
              ON domain_sales.sales_invoice_lines (tenant_id, article_id);
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_sales.sales_invoice_lines")
    op.execute("DROP TABLE IF EXISTS domain_sales.sales_invoices")
