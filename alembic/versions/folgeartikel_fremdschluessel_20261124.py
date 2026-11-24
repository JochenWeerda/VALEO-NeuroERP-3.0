"""Folgeartikel referenziell: Artikel und Folgeartikel muessen im selben Mandanten existieren (24.11.2026).

Revision ID: folgeartikel_fremdschluessel_20261124
Revises: journal_status_pflicht_20261124

Coverage-Matrix L3 -> VALEO (docs/design/artikelmodell-zuordnung-aeins-l3.md, 6.1): ``domain_shared.artikel_folgeartikel``
fuehrte Artikel- und Folgeartikelnummer als freien Text - ein Folgeartikel konnte auf einen Artikel zeigen, den es
nicht oder nur in einem anderen Mandanten gibt. Jetzt zusammengesetzte Fremdschluessel auf
``domain_inventory.articles (tenant_id, article_number)`` (vorhandene Eindeutigkeit); eine Umnummerierung des Artikels
wandert mit, das Loeschen des Artikels nimmt seine Folgeartikel-Zuordnung mit. Bestand 24.11.2026: keine Zeilen (frisch
wie gewachsen).
"""
from __future__ import annotations

from alembic import op

revision = "folgeartikel_fremdschluessel_20261124"
down_revision = "journal_status_pflicht_20261124"
branch_labels = None
depends_on = None

TABELLE = "domain_shared.artikel_folgeartikel"
ZIEL = "domain_inventory.articles (tenant_id, article_number)"


def upgrade() -> None:
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT fk_folgeartikel_artikel FOREIGN KEY (tenant_id, artikel_nr) "
               f"REFERENCES {ZIEL} ON UPDATE CASCADE ON DELETE CASCADE")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT fk_folgeartikel_folge FOREIGN KEY (tenant_id, folge_artikel_nr) "
               f"REFERENCES {ZIEL} ON UPDATE CASCADE ON DELETE CASCADE")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_folgeartikel_verschieden CHECK (artikel_nr <> folge_artikel_nr)")


def downgrade() -> None:
    for name in ("ck_folgeartikel_verschieden", "fk_folgeartikel_folge", "fk_folgeartikel_artikel"):
        op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS {name}")
