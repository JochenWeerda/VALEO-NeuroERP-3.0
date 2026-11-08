"""Steuerkonten: Kategorie ``tax`` auf die Kategorien des Kontenplan-Schemas umstellen.

Revision ID: tax_account_category_20261019
Revises: harvest_rule_store_20261015

Die SKR03-Saat der Steuerschluessel (``app/finance/steuerschluessel.py``) legte Vor- und Umsatzsteuerkonten mit der
Kategorie ``tax`` an. Das Kontenplan-Schema (``app/api/v1/schemas/finance.py``) kennt sie nicht; das Lesen des
Kontenplans scheiterte fuer betroffene Mandanten an der Validierung. Vorsteuer ist ein kurzfristiger Vermoegenswert,
Umsatzsteuer eine kurzfristige Verbindlichkeit — so wie die Kontenart der Zeile es schon sagt.
"""
from alembic import op

revision = "tax_account_category_20261019"
down_revision = "harvest_rule_store_20261015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE domain_erp.chart_of_accounts
           SET category = CASE WHEN account_type = 'asset' THEN 'current_assets' ELSE 'current_liabilities' END
         WHERE category = 'tax'
    """)


def downgrade() -> None:
    # Bewusst ohne Rueckweg: ``tax`` war nie eine gueltige Kategorie.
    pass
