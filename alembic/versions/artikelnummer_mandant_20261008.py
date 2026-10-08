"""Artikelnummer je Mandant eindeutig statt systemweit.

Revision ID: artikelnummer_mandant_20261008
Revises: lieferschein_abgleich_20261007

``001_initial_schema`` legte ``articles_article_number_key UNIQUE (article_number)``
an: Hatte ein Mandant den Artikel "KAS-27", konnte kein zweiter ihn je anlegen —
die Artikelanlage prueft Dubletten schon je Mandant, die Datenbank lehnte ab.
In der gewachsenen Entwicklungsdatenbank fehlte die Eindeutigkeit dagegen ganz.

Jetzt gilt ``UNIQUE NULLS NOT DISTINCT (tenant_id, article_number)``. Gibt es
innerhalb eines Mandanten doppelte Nummern, bricht die Migration ab und nennt sie,
statt Daten umzuschreiben. Das ``downgrade`` stellt die systemweite Regel bewusst
nicht wieder her: Sobald zwei Mandanten dieselbe Nummer fuehren, ist sie nicht
mehr erfuellbar.
"""

from alembic import op
from sqlalchemy import text

revision = "artikelnummer_mandant_20261008"
down_revision = "lieferschein_abgleich_20261007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    verbindung = op.get_bind()
    dubletten = verbindung.execute(text(
        "SELECT tenant_id, article_number, count(*) FROM domain_inventory.articles "
        "GROUP BY tenant_id, article_number HAVING count(*) > 1 LIMIT 20"
    )).all()
    if dubletten:
        liste = ", ".join(f"{t or '(ohne Mandant)'}/{n} x{c}" for t, n, c in dubletten)
        raise RuntimeError(f"Doppelte Artikelnummern je Mandant, bitte zuerst bereinigen: {liste}")

    op.execute("ALTER TABLE domain_inventory.articles DROP CONSTRAINT IF EXISTS articles_article_number_key")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_articles_mandant_nummer'
                  AND conrelid = 'domain_inventory.articles'::regclass
            ) THEN
                ALTER TABLE domain_inventory.articles
                    ADD CONSTRAINT uq_articles_mandant_nummer
                    UNIQUE NULLS NOT DISTINCT (tenant_id, article_number);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_inventory.articles DROP CONSTRAINT IF EXISTS uq_articles_mandant_nummer")
