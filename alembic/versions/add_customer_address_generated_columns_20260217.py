"""add_customer_address_generated_columns

Revision ID: customer_address_generated_cols
Revises: sales_delivery_notes_branches_audit_20260216
Create Date: 2026-02-17 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'customer_address_generated_cols'
down_revision: Union[str, None] = 'sales_delivery_notes_branches_audit_20260216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add generated columns for address fields extracted from JSONB.
    This allows normal indexing for common search patterns while maintaining
    the flexibility of JSONB for additional address fields.
    
    Supports both:
    - JSONB objects: {"city": "Berlin", "postalCode": "10115", "country": "DE"}
    - String addresses: "Hauptstraße 123, 48143 Münster" (extracts PLZ and city via regex)
    """
    # Add generated columns for address components
    # These columns are computed from the JSONB address field
    op.execute("""
        ALTER TABLE domain_crm.customers
        ADD COLUMN IF NOT EXISTS address_country VARCHAR(3)
        GENERATED ALWAYS AS (
            CASE 
                WHEN address IS NULL THEN NULL
                WHEN address::text = 'null' THEN NULL
                WHEN jsonb_typeof(address) = 'object' THEN COALESCE(
                    address->>'country',
                    address->>'countryCode',
                    address->>'country_code'
                )
                ELSE NULL
            END
        ) STORED;
    """)
    
    op.execute("""
        ALTER TABLE domain_crm.customers
        ADD COLUMN IF NOT EXISTS address_postal_code VARCHAR(20)
        GENERATED ALWAYS AS (
            CASE 
                WHEN address IS NULL THEN NULL
                WHEN address::text = 'null' THEN NULL
                WHEN jsonb_typeof(address) = 'object' THEN COALESCE(
                    address->>'postalCode',
                    address->>'postal_code',
                    address->>'zip',
                    address->>'zipCode',
                    address->>'plz'
                )
                WHEN jsonb_typeof(address) = 'string' THEN 
                    -- Extract PLZ from string like "Hauptstraße 123, 48143 Münster"
                    -- Pattern: 5-digit PLZ (German format) or similar
                    -- Remove quotes from JSONB string first
                    (regexp_match(trim(both '"' from address::text), '\\b([0-9]{5})\\b'))[1]
                ELSE NULL
            END
        ) STORED;
    """)
    
    op.execute("""
        ALTER TABLE domain_crm.customers
        ADD COLUMN IF NOT EXISTS address_city VARCHAR(120)
        GENERATED ALWAYS AS (
            CASE 
                WHEN address IS NULL THEN NULL
                WHEN address::text = 'null' THEN NULL
                WHEN jsonb_typeof(address) = 'object' THEN COALESCE(
                    address->>'city',
                    address->>'ort',
                    address->>'locality'
                )
                WHEN jsonb_typeof(address) = 'string' THEN 
                    -- Extract city from string like "Hauptstraße 123, 48143 Münster"
                    -- Pattern: Text after PLZ (5 digits) and space
                    -- Remove quotes from JSONB string first
                    TRIM((regexp_match(trim(both '"' from address::text), '\\b[0-9]{5}\\s+([A-ZÄÖÜa-zäöüß\\s-]+)'))[1])
                ELSE NULL
            END
        ) STORED;
    """)
    
    # Add normal indexes on generated columns for fast search
    op.create_index(
        'idx_customers_address_country',
        'customers',
        ['address_country'],
        schema='domain_crm',
        postgresql_where=sa.text('address_country IS NOT NULL')
    )
    
    op.create_index(
        'idx_customers_address_postal_code',
        'customers',
        ['address_postal_code'],
        schema='domain_crm',
        postgresql_where=sa.text('address_postal_code IS NOT NULL')
    )
    
    op.create_index(
        'idx_customers_address_city',
        'customers',
        ['address_city'],
        schema='domain_crm',
        postgresql_where=sa.text('address_city IS NOT NULL')
    )
    
    # Composite index for common search patterns (city + postal code)
    op.create_index(
        'idx_customers_address_city_postal',
        'customers',
        ['address_city', 'address_postal_code'],
        schema='domain_crm',
        postgresql_where=sa.text('address_city IS NOT NULL AND address_postal_code IS NOT NULL')
    )
    
    # GIN index on JSONB for complex queries (if not already exists)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_customers_address_gin 
        ON domain_crm.customers 
        USING GIN (address)
        WHERE address IS NOT NULL;
    """)


def downgrade() -> None:
    """Remove generated columns and indexes."""
    # Drop indexes first
    op.drop_index('idx_customers_address_gin', table_name='customers', schema='domain_crm', if_exists=True)
    op.drop_index('idx_customers_address_city_postal', table_name='customers', schema='domain_crm', if_exists=True)
    op.drop_index('idx_customers_address_city', table_name='customers', schema='domain_crm', if_exists=True)
    op.drop_index('idx_customers_address_postal_code', table_name='customers', schema='domain_crm', if_exists=True)
    op.drop_index('idx_customers_address_country', table_name='customers', schema='domain_crm', if_exists=True)
    
    # Drop generated columns
    op.execute("ALTER TABLE domain_crm.customers DROP COLUMN IF EXISTS address_city;")
    op.execute("ALTER TABLE domain_crm.customers DROP COLUMN IF EXISTS address_postal_code;")
    op.execute("ALTER TABLE domain_crm.customers DROP COLUMN IF EXISTS address_country;")

