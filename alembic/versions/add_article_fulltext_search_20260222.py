"""Add PostgreSQL fulltext search for articles

Revision ID: f1a2b3c4d5e6
Revises: 6c69769c28cb
Create Date: 2026-02-22

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f1a2b3c4d5e6"
down_revision = "6c69769c28cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pg_trgm extension for fuzzy fallback
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Add tsvector column via raw SQL (Alembic has no native tsvector type)
    op.execute(
        "ALTER TABLE domain_inventory.articles "
        "ADD COLUMN IF NOT EXISTS search_vector tsvector"
    )

    # Create GIN index on search_vector
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_articles_search_vector "
        "ON domain_inventory.articles USING GIN (search_vector)"
    )

    # Create trigram index on name for fuzzy fallback
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_articles_name_trgm "
        "ON domain_inventory.articles USING GIN (name gin_trgm_ops)"
    )

    # Create trigger function with weighted fields
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_inventory.articles_search_vector_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('german', coalesce(NEW.article_number, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(NEW.name, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(NEW.suchbegriff, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(NEW.short_description, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(NEW.matchcode2, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(NEW.barcode, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(NEW.description, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(NEW.hersteller, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(NEW.warengruppe, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(NEW.description2, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(NEW.ean_code, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(NEW.lieferanten_artikelnummer, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(NEW.kunden_artikelnummer, '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute(
        "DROP TRIGGER IF EXISTS trg_articles_search_vector_update "
        "ON domain_inventory.articles"
    )
    op.execute("""
        CREATE TRIGGER trg_articles_search_vector_update
        BEFORE INSERT OR UPDATE ON domain_inventory.articles
        FOR EACH ROW
        EXECUTE FUNCTION domain_inventory.articles_search_vector_update();
    """)

    # Backfill existing rows
    op.execute("""
        UPDATE domain_inventory.articles SET
            search_vector =
                setweight(to_tsvector('german', coalesce(article_number, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(name, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(suchbegriff, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(short_description, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(matchcode2, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(barcode, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(description, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(hersteller, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(warengruppe, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(description2, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(ean_code, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(lieferanten_artikelnummer, '')), 'D') ||
                setweight(to_tsvector('german', coalesce(kunden_artikelnummer, '')), 'D');
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_articles_search_vector_update "
        "ON domain_inventory.articles"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS domain_inventory.articles_search_vector_update()"
    )
    op.execute("DROP INDEX IF EXISTS domain_inventory.ix_articles_search_vector")
    op.execute("DROP INDEX IF EXISTS domain_inventory.ix_articles_name_trgm")
    op.execute(
        "ALTER TABLE domain_inventory.articles DROP COLUMN IF EXISTS search_vector"
    )
