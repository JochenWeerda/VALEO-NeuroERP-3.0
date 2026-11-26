"""Personenkonto an der Journalzeile (M3, Nutzerentscheid 26.11.2026).

Revision ID: personenkonto_journalzeile_20261126
Revises: aufbewahrung_geltendes_recht_20261125

Buchungen auf die Sammelkonten Forderungen/Verbindlichkeiten aus Lieferungen und Leistungen trugen bisher nicht, zu
welchem Debitor oder Kreditor sie gehoeren. Ohne das gibt es keine Saldenliste je Personenkonto und keinen
monatlichen Saldenabgleich gegen L3. ``partner_konto`` fuehrt die Debitoren- bzw. Kreditorennummer des
Geschaeftspartners (``business_partners.debtor_account``/``creditor_account``, bei Uebernahme aus L3 die L3-Nummer).
"""
from __future__ import annotations

from alembic import op

revision = "personenkonto_journalzeile_20261126"
down_revision = "aufbewahrung_geltendes_recht_20261125"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_erp.journal_entry_lines ADD COLUMN IF NOT EXISTS partner_konto varchar(20)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_journal_entry_lines_partner_konto "
               "ON domain_erp.journal_entry_lines (tenant_id, partner_konto) WHERE partner_konto IS NOT NULL")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_journal_entry_lines_partner_konto")
    op.execute("ALTER TABLE domain_erp.journal_entry_lines DROP COLUMN IF EXISTS partner_konto")
