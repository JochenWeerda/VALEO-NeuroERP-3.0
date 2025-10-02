-- VALEO NeuroERP 3.0 - Finance Domain Database Schema
-- Core finance tables for ledger, accounts, journals, and periods
-- Migration: 001_finance_core_schema.sql

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===== TENANT ISOLATION =====
-- Row Level Security for multi-tenancy
ALTER DATABASE valero_neuroerp_finance SET row_security = on;

-- ===== CHART OF ACCOUNTS =====

CREATE TABLE finance_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    category VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    parent_account_id UUID REFERENCES finance_accounts(id),
    tax_code VARCHAR(20),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_tenant_account_number UNIQUE (tenant_id, account_number),
    CONSTRAINT valid_account_hierarchy CHECK (
        (parent_account_id IS NULL) OR
        (parent_account_id != id) -- Prevent self-reference
    )
);

-- Indexes for accounts
CREATE INDEX idx_finance_accounts_tenant ON finance_accounts(tenant_id);
CREATE INDEX idx_finance_accounts_number ON finance_accounts(account_number);
CREATE INDEX idx_finance_accounts_type ON finance_accounts(type);
CREATE INDEX idx_finance_accounts_active ON finance_accounts(is_active) WHERE is_active = true;

-- ===== ACCOUNTING PERIODS =====

CREATE TABLE finance_accounting_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    period VARCHAR(7) NOT NULL, -- YYYY-MM format
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'ADJUSTING')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    closed_at TIMESTAMP WITH TIME ZONE,
    closed_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_tenant_period UNIQUE (tenant_id, period),
    CONSTRAINT valid_period_dates CHECK (start_date < end_date),
    CONSTRAINT valid_closed_period CHECK (
        (status != 'CLOSED') OR (closed_at IS NOT NULL AND closed_by IS NOT NULL)
    )
);

-- Indexes for periods
CREATE INDEX idx_finance_periods_tenant ON finance_accounting_periods(tenant_id);
CREATE INDEX idx_finance_periods_status ON finance_accounting_periods(status);
CREATE INDEX idx_finance_periods_dates ON finance_accounting_periods(start_date, end_date);

-- ===== JOURNALS =====

CREATE TABLE finance_journals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    period VARCHAR(7) NOT NULL,
    journal_number VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'POSTED', 'CLOSED')),
    total_debit DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_credit DECIMAL(15,2) NOT NULL DEFAULT 0,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('AP', 'AR', 'BANK', 'MANUAL', 'AI')),
    source_reference VARCHAR(255) NOT NULL,
    posted_at TIMESTAMP WITH TIME ZONE,
    posted_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Foreign Keys
    FOREIGN KEY (tenant_id, period) REFERENCES finance_accounting_periods(tenant_id, period),

    -- Constraints
    CONSTRAINT valid_journal_balance CHECK (ABS(total_debit - total_credit) < 0.01),
    CONSTRAINT valid_posted_journal CHECK (
        (status != 'POSTED') OR (posted_at IS NOT NULL AND posted_by IS NOT NULL)
    )
);

-- Indexes for journals
CREATE INDEX idx_finance_journals_tenant ON finance_journals(tenant_id);
CREATE INDEX idx_finance_journals_period ON finance_journals(period);
CREATE INDEX idx_finance_journals_status ON finance_journals(status);
CREATE INDEX idx_finance_journals_number ON finance_journals(journal_number);
CREATE INDEX idx_finance_journals_source ON finance_journals(source_type, source_reference);

-- ===== JOURNAL ENTRIES =====

CREATE TABLE finance_journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_id UUID NOT NULL REFERENCES finance_journals(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES finance_accounts(id),
    debit DECIMAL(15,2) NOT NULL DEFAULT 0,
    credit DECIMAL(15,2) NOT NULL DEFAULT 0,
    description TEXT NOT NULL,
    cost_center VARCHAR(50),
    tax_code VARCHAR(20),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_entry_amount CHECK (debit >= 0 AND credit >= 0),
    CONSTRAINT entry_has_amount CHECK (debit > 0 OR credit > 0)
);

-- Indexes for entries
CREATE INDEX idx_finance_entries_journal ON finance_journal_entries(journal_id);
CREATE INDEX idx_finance_entries_account ON finance_journal_entries(account_id);
CREATE INDEX idx_finance_entries_cost_center ON finance_journal_entries(cost_center);
CREATE INDEX idx_finance_entries_tax_code ON finance_journal_entries(tax_code);

-- ===== AUDIT TRAIL =====

CREATE TABLE finance_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),

    -- Indexes
    INDEX idx_finance_audit_tenant (tenant_id),
    INDEX idx_finance_audit_table_record (table_name, record_id),
    INDEX idx_finance_audit_timestamp (changed_at),
    INDEX idx_finance_audit_user (changed_by)
);

-- ===== VIEWS FOR COMMON QUERIES =====

-- Trial Balance View
CREATE VIEW finance_trial_balance AS
SELECT
    p.period,
    p.tenant_id,
    a.account_id,
    a.account_number,
    a.name as account_name,
    COALESCE(SUM(je.debit), 0) as debit,
    COALESCE(SUM(je.credit), 0) as credit,
    COALESCE(SUM(je.debit) - SUM(je.credit), 0) as balance
FROM finance_accounting_periods p
CROSS JOIN finance_accounts a
LEFT JOIN finance_journals j ON j.tenant_id = p.tenant_id
    AND j.period = p.period
    AND j.status = 'POSTED'
LEFT JOIN finance_journal_entries je ON je.journal_id = j.id
    AND je.account_id = a.id
WHERE p.status = 'OPEN'
GROUP BY p.period, p.tenant_id, a.account_id, a.account_number, a.name
ORDER BY a.account_number;

-- Journal Summary View
CREATE VIEW finance_journal_summary AS
SELECT
    j.id,
    j.journal_number,
    j.period,
    j.tenant_id,
    j.description,
    j.status,
    j.total_debit,
    j.total_credit,
    j.source_type,
    j.source_reference,
    j.posted_at,
    j.posted_by,
    j.created_at,
    COUNT(je.id) as entry_count
FROM finance_journals j
LEFT JOIN finance_journal_entries je ON je.journal_id = j.id
GROUP BY j.id, j.journal_number, j.period, j.tenant_id, j.description,
         j.status, j.total_debit, j.total_credit, j.source_type,
         j.source_reference, j.posted_at, j.posted_by, j.created_at;

-- ===== FUNCTIONS =====

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_finance_accounts_updated_at
    BEFORE UPDATE ON finance_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_finance_journals_updated_at
    BEFORE UPDATE ON finance_journals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create audit trail entries
CREATE OR REPLACE FUNCTION create_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    table_name TEXT := TG_TABLE_NAME;
    record_id UUID := COALESCE(NEW.id, OLD.id);
    tenant_id TEXT;
BEGIN
    -- Extract tenant_id based on table structure
    CASE table_name
        WHEN 'finance_accounts' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        WHEN 'finance_accounting_periods' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        WHEN 'finance_journals' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        ELSE tenant_id := 'SYSTEM';
    END CASE;

    IF TG_OP = 'DELETE' THEN
        INSERT INTO finance_audit_trail (tenant_id, table_name, record_id, operation, old_values, changed_by)
        VALUES (tenant_id, table_name, record_id, TG_OP, row_to_json(OLD), 'SYSTEM');
        RETURN OLD;
    ELSE
        INSERT INTO finance_audit_trail (tenant_id, table_name, record_id, operation, old_values, new_values, changed_by)
        VALUES (tenant_id, table_name, record_id, TG_OP,
                CASE WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END,
                row_to_json(NEW), 'SYSTEM');
        RETURN NEW;
    END IF;
END;
$$ language 'plpgsql';

-- Apply audit triggers
CREATE TRIGGER audit_finance_accounts
    AFTER INSERT OR UPDATE OR DELETE ON finance_accounts
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_periods
    AFTER INSERT OR UPDATE OR DELETE ON finance_accounting_periods
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_journals
    AFTER INSERT OR UPDATE OR DELETE ON finance_journals
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_entries
    AFTER INSERT OR UPDATE OR DELETE ON finance_journal_entries
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

-- ===== ROW LEVEL SECURITY =====

-- Enable RLS on all tables
ALTER TABLE finance_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_accounting_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_journals ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_audit_trail ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (these would be customized based on authentication system)
-- For now, creating basic tenant isolation policies

CREATE POLICY tenant_isolation_accounts ON finance_accounts
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_periods ON finance_accounting_periods
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_journals ON finance_journals
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_entries ON finance_journal_entries
    FOR ALL USING (
        journal_id IN (
            SELECT id FROM finance_journals
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY tenant_isolation_audit ON finance_audit_trail
    FOR SELECT USING (tenant_id = current_setting('app.current_tenant', true));

-- ===== INITIAL DATA =====

-- Insert default chart of accounts (SKR-like structure)
INSERT INTO finance_accounts (tenant_id, account_number, name, type, category, is_active, tax_code, metadata) VALUES

-- Assets (1000-1999)
('DEFAULT', '1000', 'Kasse', 'ASSET', 'CASH', true, NULL, '{"level": 1}'),
('DEFAULT', '1200', 'Bank', 'ASSET', 'BANK', true, NULL, '{"level": 1}'),
('DEFAULT', '1400', 'Forderungen aus Lieferungen und Leistungen', 'ASSET', 'RECEIVABLES', true, NULL, '{"level": 1}'),
('DEFAULT', '1600', 'Verbindlichkeiten aus Lieferungen und Leistungen', 'LIABILITY', 'PAYABLES', true, NULL, '{"level": 1}'),

-- Equity (2000-2999)
('DEFAULT', '2000', 'Eigenkapital', 'EQUITY', 'EQUITY', true, NULL, '{"level": 1}'),

-- Revenue (4000-4999)
('DEFAULT', '4000', 'Umsatzerlöse', 'REVENUE', 'SALES', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '4100', 'Erlösschmälerungen', 'REVENUE', 'DISCOUNTS', true, 'DE-19', '{"level": 1}'),

-- Expenses (6000-6999)
('DEFAULT', '6000', 'Materialaufwand', 'EXPENSE', 'MATERIALS', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '6100', 'Personalaufwand', 'EXPENSE', 'PERSONNEL', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '6200', 'Raumkosten', 'EXPENSE', 'RENTAL', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '6300', 'Vertriebskosten', 'EXPENSE', 'SALES', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '6400', 'Verwaltungskosten', 'EXPENSE', 'ADMIN', true, 'DE-19', '{"level": 1}'),

-- Tax Accounts (1700-1799)
('DEFAULT', '1776', 'Umsatzsteuer 19%', 'LIABILITY', 'TAX', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '1775', 'Umsatzsteuer 7%', 'LIABILITY', 'TAX', true, 'DE-7', '{"level": 1}'),
('DEFAULT', '1780', 'Vorsteuer 19%', 'ASSET', 'TAX', true, 'DE-19', '{"level": 1}'),
('DEFAULT', '1781', 'Vorsteuer 7%', 'ASSET', 'TAX', true, 'DE-7', '{"level": 1}');

-- Insert current period
INSERT INTO finance_accounting_periods (tenant_id, period, status, start_date, end_date) VALUES
('DEFAULT', '2025-09', 'OPEN', '2025-09-01', '2025-09-30');

-- ===== COMMENTS =====

COMMENT ON TABLE finance_accounts IS 'Chart of Accounts - Account master data with hierarchical structure';
COMMENT ON TABLE finance_accounting_periods IS 'Accounting periods for financial reporting';
COMMENT ON TABLE finance_journals IS 'Journal headers with business transaction metadata';
COMMENT ON TABLE finance_journal_entries IS 'Individual journal entries (debits and credits)';
COMMENT ON TABLE finance_audit_trail IS 'Complete audit trail for compliance and traceability';

COMMENT ON VIEW finance_trial_balance IS 'Trial balance for open periods with current balances';
COMMENT ON VIEW finance_journal_summary IS 'Journal summary with entry counts and status information';

-- ===== PERFORMANCE OPTIMIZATION =====

-- Analyze tables for query planner
ANALYZE finance_accounts;
ANALYZE finance_accounting_periods;
ANALYZE finance_journals;
ANALYZE finance_journal_entries;
ANALYZE finance_audit_trail;

-- ===== MIGRATION METADATA =====

INSERT INTO schema_migrations (version, description, applied_at) VALUES
('001_finance_core_schema', 'Initial finance domain schema with ledger, accounts, journals, and periods', NOW());