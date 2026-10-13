"""Artikel tragen Steuerschluessel statt eines Prozentsatzes.

Revision ID: artikel_steuerschluessel_20261013
Revises: vat_codes_entfernt_20261012

Jeder Beleg nimmt Satz und Konten aus ``domain_erp.tax_keys``. Die Position eines Belegs bekommt ihren
Steuerschluessel vom Artikel — bisher trug der Artikel nur ``mehrwertsteuer_prozent``, und die Masken
setzten 19 ein, wenn nichts da stand. Ein Artikel braucht zwei Schluessel: einen fuer Verkaufsbelege
(Umsatzsteuer) und einen fuer Eingangsbelege (Vorsteuer).

``mehrwertsteuer_prozent`` bleibt als Abbild des Satzes des Verkaufsschluessels fuer alle, die den Satz lesen.
Bestehende Artikel werden hier nicht zugeordnet: Das macht ``scripts/artikel_steuerschluessel_zuordnen.py``
je Mandant, mit Trockenlauf, und nur dort, wo genau ein Schluessel zum Satz passt.
"""

from alembic import op

revision = "artikel_steuerschluessel_20261013"
down_revision = "vat_codes_entfernt_20261012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_inventory.articles "
        "ADD COLUMN IF NOT EXISTS steuerschluessel_verkauf VARCHAR(2), "
        "ADD COLUMN IF NOT EXISTS steuerschluessel_einkauf VARCHAR(2)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_inventory.articles "
        "DROP COLUMN IF EXISTS steuerschluessel_verkauf, DROP COLUMN IF EXISTS steuerschluessel_einkauf"
    )
