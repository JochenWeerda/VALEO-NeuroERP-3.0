-- VALEO-NeuroERP Database Schema
-- Designed for Clean Architecture with Domain-Driven Design
-- Compatible with VALEO-NeuroERP-3.0 domain services

-- =====================================================
-- SCHEMA DEFINITIONS
-- =====================================================

-- Domain schemas for clean architecture separation
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_erp;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS infrastructure;

-- Grant permissions
GRANT USAGE ON SCHEMA domain_crm TO valeo_dev;
GRANT USAGE ON SCHEMA domain_erp TO valeo_dev;
GRANT USAGE ON SCHEMA domain_inventory TO valeo_dev;
GRANT USAGE ON SCHEMA domain_shared TO valeo_dev;
GRANT USAGE ON SCHEMA infrastructure TO valeo_dev;

-- =====================================================
-- SHARED ENTITIES (Cross-domain)
-- =====================================================

-- Base entity for audit trails
CREATE TABLE IF NOT EXISTS domain_shared.base_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    version INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Users table (integrated with Keycloak)
CREATE TABLE IF NOT EXISTS domain_shared.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    roles TEXT[], -- Array of roles
    tenant_id UUID, -- For multi-tenancy
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tenants for multi-tenancy
CREATE TABLE IF NOT EXISTS domain_shared.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CRM DOMAIN
-- =====================================================

-- Customers
CREATE TABLE IF NOT EXISTS domain_crm.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    customer_number VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address JSONB,
    customer_type VARCHAR(50) DEFAULT 'business', -- business, private
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES domain_shared.users(id),
    updated_by UUID REFERENCES domain_shared.users(id)
);

-- Leads
CREATE TABLE IF NOT EXISTS domain_crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    customer_id UUID REFERENCES domain_crm.customers(id),
    lead_source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, qualified, lost, won
    estimated_value DECIMAL(15,2),
    probability DECIMAL(5,2), -- 0-100
    assigned_to UUID REFERENCES domain_shared.users(id),
    expected_close_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ERP DOMAIN - FINANCIAL ENTITIES
-- =====================================================

-- Chart of Accounts
CREATE TABLE IF NOT EXISTS domain_erp.chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- asset, liability, equity, revenue, expense
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Accounts
CREATE TABLE IF NOT EXISTS domain_erp.bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    account_number VARCHAR(50) UNIQUE NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    iban VARCHAR(34),
    bic VARCHAR(11),
    currency VARCHAR(3) DEFAULT 'EUR',
    balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal Entries (Buchungen)
CREATE TABLE IF NOT EXISTS domain_erp.journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    entry_number VARCHAR(50) UNIQUE NOT NULL,
    entry_date DATE NOT NULL,
    posting_date DATE NOT NULL,
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    reference VARCHAR(255),
    description TEXT,
    total_debit DECIMAL(15,2) DEFAULT 0,
    total_credit DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft', -- draft, posted, cancelled
    posted_by UUID REFERENCES domain_shared.users(id),
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal Entry Lines
CREATE TABLE IF NOT EXISTS domain_erp.journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES domain_erp.journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES domain_erp.chart_of_accounts(id),
    description VARCHAR(255),
    debit DECIMAL(15,2) DEFAULT 0,
    credit DECIMAL(15,2) DEFAULT 0,
    cost_center VARCHAR(100),
    project VARCHAR(100),
    line_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Debitors (Customers in accounting context)
CREATE TABLE IF NOT EXISTS domain_erp.debitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    customer_id UUID REFERENCES domain_crm.customers(id),
    debitor_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address JSONB,
    payment_terms VARCHAR(100) DEFAULT '30_days',
    credit_limit DECIMAL(15,2) DEFAULT 0,
    current_balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Creditors (Suppliers in accounting context)
CREATE TABLE IF NOT EXISTS domain_erp.creditors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    creditor_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address JSONB,
    payment_terms VARCHAR(100) DEFAULT '30_days',
    current_balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INVENTORY DOMAIN
-- =====================================================

-- Articles (Products)
CREATE TABLE IF NOT EXISTS domain_inventory.articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    article_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit VARCHAR(20) DEFAULT 'pcs',
    category VARCHAR(100),
    purchase_price DECIMAL(10,2),
    sales_price DECIMAL(10,2),
    minimum_stock INTEGER DEFAULT 0,
    maximum_stock INTEGER,
    current_stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Warehouses
CREATE TABLE IF NOT EXISTS domain_inventory.warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    warehouse_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stock Locations
CREATE TABLE IF NOT EXISTS domain_inventory.stock_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL REFERENCES domain_inventory.warehouses(id),
    location_code VARCHAR(50) NOT NULL,
    location_type VARCHAR(50) DEFAULT 'shelf', -- shelf, floor, bulk
    capacity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(warehouse_id, location_code)
);

-- Stock Movements
CREATE TABLE IF NOT EXISTS domain_inventory.stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    article_id UUID NOT NULL REFERENCES domain_inventory.articles(id),
    warehouse_id UUID NOT NULL REFERENCES domain_inventory.warehouses(id),
    location_id UUID REFERENCES domain_inventory.stock_locations(id),
    movement_type VARCHAR(50) NOT NULL, -- in, out, transfer, adjustment
    quantity INTEGER NOT NULL,
    reference_document VARCHAR(100),
    reason VARCHAR(255),
    performed_by UUID REFERENCES domain_shared.users(id),
    movement_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INFRASTRUCTURE TABLES
-- =====================================================

-- Event Store for Domain Events
CREATE TABLE IF NOT EXISTS infrastructure.event_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    event_metadata JSONB DEFAULT '{}',
    event_version INTEGER NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Outbox for reliable event publishing
CREATE TABLE IF NOT EXISTS infrastructure.outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    event_metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending', -- pending, published, failed
    published_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Log
CREATE TABLE IF NOT EXISTS infrastructure.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES domain_shared.users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- CRM Indexes
CREATE INDEX IF NOT EXISTS idx_customers_tenant ON domain_crm.customers(tenant_id);
CREATE INDEX IF NOT EXISTS idx_customers_number ON domain_crm.customers(customer_number);
CREATE INDEX IF NOT EXISTS idx_leads_customer ON domain_crm.leads(customer_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON domain_crm.leads(status);

-- ERP Indexes
CREATE INDEX IF NOT EXISTS idx_accounts_number ON domain_erp.chart_of_accounts(account_number);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON domain_erp.chart_of_accounts(account_type);
CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON domain_erp.journal_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_journal_entries_status ON domain_erp.journal_entries(status);
CREATE INDEX IF NOT EXISTS idx_journal_lines_entry ON domain_erp.journal_entry_lines(journal_entry_id);
CREATE INDEX IF NOT EXISTS idx_debitors_customer ON domain_erp.debitors(customer_id);
CREATE INDEX IF NOT EXISTS idx_creditors_number ON domain_erp.creditors(creditor_number);

-- Inventory Indexes
CREATE INDEX IF NOT EXISTS idx_articles_number ON domain_inventory.articles(article_number);
CREATE INDEX IF NOT EXISTS idx_articles_category ON domain_inventory.articles(category);
CREATE INDEX IF NOT EXISTS idx_stock_movements_article ON domain_inventory.stock_movements(article_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_date ON domain_inventory.stock_movements(movement_date);

-- Infrastructure Indexes
CREATE INDEX IF NOT EXISTS idx_event_store_aggregate ON infrastructure.event_store(aggregate_id, aggregate_type);
CREATE INDEX IF NOT EXISTS idx_outbox_status ON infrastructure.outbox(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON infrastructure.audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON infrastructure.audit_log(user_id);

-- =====================================================
-- TRIGGERS FOR AUDIT TRAILS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON domain_crm.customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON domain_crm.leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON domain_erp.journal_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_debitors_updated_at BEFORE UPDATE ON domain_erp.debitors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_creditors_updated_at BEFORE UPDATE ON domain_erp.creditors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON domain_inventory.articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_warehouses_updated_at BEFORE UPDATE ON domain_inventory.warehouses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outbox_updated_at BEFORE UPDATE ON infrastructure.outbox FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA SEEDING
-- =====================================================

-- Insert default tenant
INSERT INTO domain_shared.tenants (id, name, domain, settings) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'VALEO Default', 'valeo-neuro-erp.com', '{"currency": "EUR", "language": "de"}')
ON CONFLICT (id) DO NOTHING;

-- Insert default user (will be linked to Keycloak)
INSERT INTO domain_shared.users (id, keycloak_id, username, email, first_name, last_name, roles) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'admin-keycloak-id', 'admin', 'admin@valeo-neuro-erp.com', 'System', 'Administrator', ARRAY['admin', 'user'])
ON CONFLICT (id) DO NOTHING;

-- Insert sample chart of accounts
INSERT INTO domain_erp.chart_of_accounts (tenant_id, account_number, account_name, account_type, category) VALUES
('550e8400-e29b-41d4-a716-446655440000', '1000', 'Kasse', 'asset', 'current_assets'),
('550e8400-e29b-41d4-a716-446655440000', '1200', 'Bank', 'asset', 'current_assets'),
('550e8400-e29b-41d4-a716-446655440000', '1400', 'Forderungen aus Lieferungen', 'asset', 'receivables'),
('550e8400-e29b-41d4-a716-446655440000', '1600', 'Vorräte', 'asset', 'inventory'),
('550e8400-e29b-41d4-a716-446655440000', '2000', 'Verbindlichkeiten aus Lieferungen', 'liability', 'current_liabilities'),
('550e8400-e29b-41d4-a716-446655440000', '3000', 'Eigenkapital', 'equity', 'equity'),
('550e8400-e29b-41d4-a716-446655440000', '4000', 'Umsatzerlöse', 'revenue', 'revenue'),
('550e8400-e29b-41d4-a716-446655440000', '5000', 'Materialaufwand', 'expense', 'cost_of_goods_sold'),
('550e8400-e29b-41d4-a716-446655440000', '6000', 'Personalaufwand', 'expense', 'operating_expenses')
ON CONFLICT (account_number) DO NOTHING;

-- Insert sample bank account
INSERT INTO domain_erp.bank_accounts (tenant_id, account_number, bank_name, iban, currency) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'DE00123456789012345678', 'VALEO Bank', 'DE00123456789012345678', 'EUR')
ON CONFLICT (account_number) DO NOTHING;

-- Insert sample warehouse
INSERT INTO domain_inventory.warehouses (tenant_id, warehouse_code, name, address) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'MAIN', 'Hauptlager', '{"street": "Musterstraße 1", "city": "Musterstadt", "postal_code": "12345", "country": "DE"}')
ON CONFLICT (warehouse_code) DO NOTHING;

-- Insert sample articles
INSERT INTO domain_inventory.articles (tenant_id, article_number, name, unit, category, sales_price, minimum_stock) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'ART001', 'VALEO Produkt A', 'pcs', 'Elektronik', 99.99, 10),
('550e8400-e29b-41d4-a716-446655440000', 'ART002', 'VALEO Produkt B', 'pcs', 'Mechanik', 149.99, 5),
('550e8400-e29b-41d4-a716-446655440000', 'ART003', 'VALEO Dienstleistung', 'h', 'Service', 75.00, 0)
ON CONFLICT (article_number) DO NOTHING;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Customer balance view
CREATE OR REPLACE VIEW domain_crm.customer_balances AS
SELECT
    c.id,
    c.customer_number,
    c.company_name,
    c.contact_person,
    COALESCE(d.current_balance, 0) as balance
FROM domain_crm.customers c
LEFT JOIN domain_erp.debitors d ON c.id = d.customer_id
WHERE c.is_active = true;

-- Stock levels view
CREATE OR REPLACE VIEW domain_inventory.stock_levels AS
SELECT
    a.id,
    a.article_number,
    a.name,
    a.current_stock,
    a.minimum_stock,
    a.maximum_stock,
    CASE
        WHEN a.current_stock <= a.minimum_stock THEN 'critical'
        WHEN a.current_stock <= a.minimum_stock * 1.5 THEN 'low'
        ELSE 'normal'
    END as stock_status
FROM domain_inventory.articles a
WHERE a.is_active = true;

-- Account balances view
CREATE OR REPLACE VIEW domain_erp.account_balances AS
SELECT
    coa.account_number,
    coa.account_name,
    coa.account_type,
    COALESCE(SUM(jel.debit - jel.credit), 0) as balance
FROM domain_erp.chart_of_accounts coa
LEFT JOIN domain_erp.journal_entry_lines jel ON coa.id = jel.account_id
LEFT JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
WHERE je.status = 'posted' OR je.status IS NULL
GROUP BY coa.id, coa.account_number, coa.account_name, coa.account_type;

-- =====================================================
-- ROW LEVEL SECURITY (Optional)
-- =====================================================

-- Enable RLS on key tables
ALTER TABLE domain_crm.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_erp.journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_inventory.articles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (example - customize based on requirements)
CREATE POLICY tenant_isolation_customers ON domain_crm.customers
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_journal ON domain_erp.journal_entries
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_articles ON domain_inventory.articles
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- =====================================================
-- SCHEMA COMPLETION
-- =====================================================

-- Log schema creation completion
DO $$
BEGIN
    RAISE NOTICE 'VALEO-NeuroERP database schema created successfully at %', NOW();
END $$;