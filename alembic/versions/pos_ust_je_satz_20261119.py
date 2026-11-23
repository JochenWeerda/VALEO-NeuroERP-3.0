"""Kassiervorgaenge fuehren ihren Bruttobetrag je Umsatzsteuersatz (M3, POS-Umsatzsteuer).

``domain_docflow.pos_fiscal_transactions`` hielt je Vorgang nur ``gross_total``. Der Tagesabschluss buchte deshalb den
ganzen Bruttoumsatz auf das Erloeskonto - ohne Umsatzsteuer (Erloese um die Steuer zu hoch, UStVA ohne Kassensteuer).
Die TSE meldet die Betraege je Satz ohnehin (DSFinV-K ``amounts_per_vat_rate``); jetzt werden sie mitgespeichert.

Altvorgaenge bekommen ein leeres Objekt: Ihre Saetze sind nicht bekannt und werden nicht erfunden. Ein Tagesabschluss
mit solchen Vorgaengen wird abgewiesen, statt eine Steuer anzunehmen.
"""
from alembic import op

revision = "pos_ust_je_satz_20261119"
down_revision = "finance_router_altspeicher_entfernen_20261123"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE domain_docflow.pos_fiscal_transactions
        ADD COLUMN IF NOT EXISTS vat_breakdown jsonb NOT NULL DEFAULT '{}'::jsonb
    """)


def downgrade():
    op.execute("ALTER TABLE domain_docflow.pos_fiscal_transactions DROP COLUMN IF EXISTS vat_breakdown")
