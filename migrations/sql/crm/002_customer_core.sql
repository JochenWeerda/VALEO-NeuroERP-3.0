CREATE TABLE IF NOT EXISTS crm.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_number VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'company',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(120),
    postal_code VARCHAR(20),
    country VARCHAR(120),
    industry VARCHAR(120),
    company_size VARCHAR(120),
    annual_revenue NUMERIC(18,2),
    tax_id VARCHAR(120),
    vat_number VARCHAR(120),
    sales_rep_id VARCHAR(120),
    lead_source VARCHAR(120),
    lead_score INTEGER,
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ,
    CHECK (type IN ('company', 'individual', 'partner', 'distributor')),
    CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX IF NOT EXISTS idx_crm_customers_number ON crm.customers(customer_number);
CREATE INDEX IF NOT EXISTS idx_crm_customers_status ON crm.customers(status);
CREATE INDEX IF NOT EXISTS idx_crm_customers_type ON crm.customers(type);

CREATE OR REPLACE FUNCTION crm.touch_updated_at()
RETURNS TRIGGER AS 3598
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
3598 LANGUAGE plpgsql;

CREATE TRIGGER crm_customers_touch_update
    BEFORE UPDATE ON crm.customers
    FOR EACH ROW
    EXECUTE FUNCTION crm.touch_updated_at();
