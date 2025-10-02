-- VALEO NeuroERP 3.0 - Finance Domain AP/AR Invoice Schema
-- Accounts Payable and Accounts Receivable invoice tables
-- Migration: 003_ap_ar_invoice_schema.sql

-- ===== ACCOUNTS PAYABLE INVOICES =====

CREATE TABLE finance_ap_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    vendor_id VARCHAR(255) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'RECEIVED' CHECK (status IN ('RECEIVED', 'APPROVED', 'PAID', 'OVERDUE', 'CANCELLED')),
    payment_terms VARCHAR(255),
    description TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_ap_amounts CHECK (subtotal >= 0 AND tax_amount >= 0 AND total_amount >= 0),
    CONSTRAINT valid_ap_dates CHECK (issue_date <= due_date)
);

-- Indexes for AP invoices
CREATE INDEX idx_finance_ap_invoices_tenant ON finance_ap_invoices(tenant_id);
CREATE INDEX idx_finance_ap_invoices_vendor ON finance_ap_invoices(vendor_id);
CREATE INDEX idx_finance_ap_invoices_status ON finance_ap_invoices(status);
CREATE INDEX idx_finance_ap_invoices_due_date ON finance_ap_invoices(due_date);
CREATE INDEX idx_finance_ap_invoices_number ON finance_ap_invoices(invoice_number);

-- ===== ACCOUNTS RECEIVABLE INVOICES =====

CREATE TABLE finance_ar_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED')),
    payment_terms VARCHAR(255),
    description TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_ar_amounts CHECK (subtotal >= 0 AND tax_amount >= 0 AND total_amount >= 0),
    CONSTRAINT valid_ar_dates CHECK (issue_date <= due_date)
);

-- Indexes for AR invoices
CREATE INDEX idx_finance_ar_invoices_tenant ON finance_ar_invoices(tenant_id);
CREATE INDEX idx_finance_ar_invoices_customer ON finance_ar_invoices(customer_id);
CREATE INDEX idx_finance_ar_invoices_status ON finance_ar_invoices(status);
CREATE INDEX idx_finance_ar_invoices_due_date ON finance_ar_invoices(due_date);
CREATE INDEX idx_finance_ar_invoices_number ON finance_ar_invoices(invoice_number);

-- ===== AP INVOICE LINE ITEMS =====

CREATE TABLE finance_ap_invoice_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES finance_ap_invoices(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(12,4) NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,4) NOT NULL,
    line_total DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    account_id UUID REFERENCES finance_accounts(id),
    cost_center VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_ap_line_amounts CHECK (quantity >= 0 AND unit_price >= 0 AND line_total >= 0 AND tax_amount >= 0),
    CONSTRAINT valid_ap_line_number CHECK (line_number > 0)
);

-- Indexes for AP invoice lines
CREATE INDEX idx_finance_ap_lines_invoice ON finance_ap_invoice_lines(invoice_id);
CREATE INDEX idx_finance_ap_lines_account ON finance_ap_invoice_lines(account_id);

-- ===== AR INVOICE LINE ITEMS =====

CREATE TABLE finance_ar_invoice_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES finance_ar_invoices(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(12,4) NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,4) NOT NULL,
    line_total DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    account_id UUID REFERENCES finance_accounts(id),
    cost_center VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_ar_line_amounts CHECK (quantity >= 0 AND unit_price >= 0 AND line_total >= 0 AND tax_amount >= 0),
    CONSTRAINT valid_ar_line_number CHECK (line_number > 0)
);

-- Indexes for AR invoice lines
CREATE INDEX idx_finance_ar_lines_invoice ON finance_ar_invoice_lines(invoice_id);
CREATE INDEX idx_finance_ar_lines_account ON finance_ar_invoice_lines(account_id);

-- ===== TRIGGERS =====

-- Updated_at triggers
CREATE TRIGGER update_finance_ap_invoices_updated_at
    BEFORE UPDATE ON finance_ap_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_finance_ar_invoices_updated_at
    BEFORE UPDATE ON finance_ar_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit triggers
CREATE TRIGGER audit_finance_ap_invoices
    AFTER INSERT OR UPDATE OR DELETE ON finance_ap_invoices
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_ar_invoices
    AFTER INSERT OR UPDATE OR DELETE ON finance_ar_invoices
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_ap_invoice_lines
    AFTER INSERT OR UPDATE OR DELETE ON finance_ap_invoice_lines
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_ar_invoice_lines
    AFTER INSERT OR UPDATE OR DELETE ON finance_ar_invoice_lines
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

-- ===== ROW LEVEL SECURITY =====

-- Enable RLS
ALTER TABLE finance_ap_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_ar_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_ap_invoice_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_ar_invoice_lines ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY tenant_isolation_ap_invoices ON finance_ap_invoices
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_ar_invoices ON finance_ar_invoices
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_ap_lines ON finance_ap_invoice_lines
    FOR ALL USING (
        invoice_id IN (
            SELECT id FROM finance_ap_invoices
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY tenant_isolation_ar_lines ON finance_ar_invoice_lines
    FOR ALL USING (
        invoice_id IN (
            SELECT id FROM finance_ar_invoices
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

-- ===== VIEWS =====

-- AP Invoice Summary View
CREATE VIEW finance_ap_invoice_summary AS
SELECT
    i.id,
    i.tenant_id,
    i.invoice_number,
    i.vendor_id,
    i.vendor_name,
    i.issue_date,
    i.due_date,
    i.currency,
    i.total_amount,
    i.status,
    i.payment_terms,
    COUNT(l.id) as line_count,
    SUM(l.line_total) as subtotal,
    SUM(l.tax_amount) as tax_total,
    i.created_at,
    i.updated_at
FROM finance_ap_invoices i
LEFT JOIN finance_ap_invoice_lines l ON l.invoice_id = i.id
GROUP BY i.id, i.tenant_id, i.invoice_number, i.vendor_id, i.vendor_name,
         i.issue_date, i.due_date, i.currency, i.total_amount, i.status,
         i.payment_terms, i.created_at, i.updated_at;

-- AR Invoice Summary View
CREATE VIEW finance_ar_invoice_summary AS
SELECT
    i.id,
    i.tenant_id,
    i.invoice_number,
    i.customer_id,
    i.customer_name,
    i.issue_date,
    i.due_date,
    i.currency,
    i.total_amount,
    i.status,
    i.payment_terms,
    COUNT(l.id) as line_count,
    SUM(l.line_total) as subtotal,
    SUM(l.tax_amount) as tax_total,
    i.created_at,
    i.updated_at
FROM finance_ar_invoices i
LEFT JOIN finance_ar_invoice_lines l ON l.invoice_id = i.id
GROUP BY i.id, i.tenant_id, i.invoice_number, i.customer_id, i.customer_name,
         i.issue_date, i.due_date, i.currency, i.total_amount, i.status,
         i.payment_terms, i.created_at, i.updated_at;

-- ===== COMMENTS =====

COMMENT ON TABLE finance_ap_invoices IS 'Accounts Payable invoices - vendor invoices to be paid';
COMMENT ON TABLE finance_ar_invoices IS 'Accounts Receivable invoices - customer invoices to be collected';
COMMENT ON TABLE finance_ap_invoice_lines IS 'Line items for AP invoices with detailed accounting information';
COMMENT ON TABLE finance_ar_invoice_lines IS 'Line items for AR invoices with detailed accounting information';

COMMENT ON VIEW finance_ap_invoice_summary IS 'AP invoice summary with line counts and totals';
COMMENT ON VIEW finance_ar_invoice_summary IS 'AR invoice summary with line counts and totals';

-- ===== PERFORMANCE OPTIMIZATION =====

-- Analyze new tables
ANALYZE finance_ap_invoices;
ANALYZE finance_ar_invoices;
ANALYZE finance_ap_invoice_lines;
ANALYZE finance_ar_invoice_lines;

-- ===== MIGRATION METADATA =====

INSERT INTO schema_migrations (version, description, applied_at) VALUES
('003_ap_ar_invoice_schema', 'AP and AR invoice tables with line items and accounting integration', NOW());