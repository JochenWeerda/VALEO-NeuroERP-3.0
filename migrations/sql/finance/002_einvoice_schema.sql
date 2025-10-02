-- VALEO NeuroERP 3.0 - Finance Domain E-Invoice Schema
-- ZUGFeRD/XRechnung compliance tables and validation
-- Migration: 002_einvoice_schema.sql

-- ===== E-INVOICE DOCUMENTS =====

CREATE TABLE finance_einvoice_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL UNIQUE,
    kind VARCHAR(20) NOT NULL CHECK (kind IN ('PDFA3', 'XML', 'UBL', 'CII')),
    mimetype VARCHAR(100) NOT NULL,
    storage_ref TEXT NOT NULL, -- S3 path or file system path
    sha256_hash CHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    profile VARCHAR(50), -- ZUGFeRD-EN16931, XRechnung-2.x, etc.
    schema_version VARCHAR(20),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_sha256 CHECK (length(sha256_hash) = 64)
);

-- Indexes for documents
CREATE INDEX idx_finance_einv_docs_tenant ON finance_einvoice_documents(tenant_id);
CREATE INDEX idx_finance_einv_docs_kind ON finance_einvoice_documents(kind);
CREATE INDEX idx_finance_einv_docs_profile ON finance_einvoice_documents(profile);
CREATE INDEX idx_finance_einv_docs_hash ON finance_einvoice_documents(sha256_hash);

-- ===== VALIDATION RESULTS =====

CREATE TABLE finance_einvoice_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    document_id UUID NOT NULL REFERENCES finance_einvoice_documents(id),
    validator_name VARCHAR(100) NOT NULL, -- XMLSchema, Schematron, PDFA3, etc.
    validator_version VARCHAR(20) NOT NULL,
    validation_result JSONB NOT NULL,
    passed BOOLEAN NOT NULL,
    error_count INTEGER NOT NULL DEFAULT 0,
    warning_count INTEGER NOT NULL DEFAULT 0,
    execution_time_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT positive_counts CHECK (error_count >= 0 AND warning_count >= 0)
);

-- Indexes for validations
CREATE INDEX idx_finance_einv_validations_tenant ON finance_einvoice_validations(tenant_id);
CREATE INDEX idx_finance_einv_validations_document ON finance_einvoice_validations(document_id);
CREATE INDEX idx_finance_einv_validations_passed ON finance_einvoice_validations(passed);
CREATE INDEX idx_finance_einv_validations_validator ON finance_einvoice_validations(validator_name);

-- ===== E-INVOICE PROFILES =====

CREATE TABLE finance_einvoice_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    profile_name VARCHAR(50) NOT NULL,
    standard VARCHAR(20) NOT NULL CHECK (standard IN ('ZUGFeRD', 'XRECHNUNG', 'PEPPOL')),
    version VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    configuration JSONB NOT NULL, -- Schema mappings, validation rules, etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_tenant_profile UNIQUE (tenant_id, profile_name)
);

-- Indexes for profiles
CREATE INDEX idx_finance_einv_profiles_tenant ON finance_einvoice_profiles(tenant_id);
CREATE INDEX idx_finance_einv_profiles_standard ON finance_einvoice_profiles(standard);
CREATE INDEX idx_finance_einv_profiles_active ON finance_einvoice_profiles(is_active) WHERE is_active = true;

-- ===== AP INVOICE EXTENSIONS =====

ALTER TABLE finance_ap_invoices
ADD COLUMN zferd_profile TEXT,
ADD COLUMN xml_ref UUID REFERENCES finance_einvoice_documents(id),
ADD COLUMN pdfa3_ref UUID REFERENCES finance_einvoice_documents(id),
ADD COLUMN schema_version TEXT,
ADD COLUMN validation_status TEXT CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID', 'ERROR')),
ADD COLUMN einvoice_metadata JSONB DEFAULT '{}';

-- Indexes for AP invoices
CREATE INDEX idx_finance_ap_invoices_zferd_profile ON finance_ap_invoices(zferd_profile);
CREATE INDEX idx_finance_ap_invoices_xml_ref ON finance_ap_invoices(xml_ref);
CREATE INDEX idx_finance_ap_invoices_pdfa3_ref ON finance_ap_invoices(pdfa3_ref);
CREATE INDEX idx_finance_ap_invoices_validation_status ON finance_ap_invoices(validation_status);

-- ===== AR INVOICE EXTENSIONS =====

ALTER TABLE finance_ar_invoices
ADD COLUMN zferd_profile TEXT,
ADD COLUMN xml_ref UUID REFERENCES finance_einvoice_documents(id),
ADD COLUMN pdfa3_ref UUID REFERENCES finance_einvoice_documents(id),
ADD COLUMN schema_version TEXT,
ADD COLUMN validation_status TEXT CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID', 'ERROR')),
ADD COLUMN einvoice_metadata JSONB DEFAULT '{}';

-- Indexes for AR invoices
CREATE INDEX idx_finance_ar_invoices_zferd_profile ON finance_ar_invoices(zferd_profile);
CREATE INDEX idx_finance_ar_invoices_xml_ref ON finance_ar_invoices(xml_ref);
CREATE INDEX idx_finance_ar_invoices_pdfa3_ref ON finance_ar_invoices(pdfa3_ref);
CREATE INDEX idx_finance_ar_invoices_validation_status ON finance_ar_invoices(validation_status);

-- ===== NORMALIZED E-INVOICE DATA =====

CREATE TABLE finance_einvoice_normalized (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL,
    invoice_id UUID NOT NULL, -- References either AP or AR invoice
    invoice_type VARCHAR(10) NOT NULL CHECK (invoice_type IN ('AP', 'AR')),
    normalized_data JSONB NOT NULL,
    normalization_version VARCHAR(20) NOT NULL,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    normalization_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Foreign keys will be added after invoice tables are created
    -- CONSTRAINT fk_ap_invoice FOREIGN KEY (invoice_id) REFERENCES finance_ap_invoices(id)
    -- CONSTRAINT fk_ar_invoice FOREIGN KEY (invoice_id) REFERENCES finance_ar_invoices(id)
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for normalized data
CREATE INDEX idx_finance_einv_normalized_tenant ON finance_einvoice_normalized(tenant_id);
CREATE INDEX idx_finance_einv_normalized_invoice ON finance_einvoice_normalized(invoice_type, invoice_id);
CREATE INDEX idx_finance_einv_normalized_confidence ON finance_einvoice_normalized(confidence_score);

-- ===== VIEWS FOR E-INVOICE QUERIES =====

-- E-Invoice Summary View
CREATE VIEW finance_einvoice_summary AS
SELECT
    d.id as document_id,
    d.document_id as document_number,
    d.kind,
    d.mimetype,
    d.profile,
    d.schema_version,
    d.created_at as document_created_at,
    ap.id as ap_invoice_id,
    ar.id as ar_invoice_id,
    COALESCE(ap.status, ar.status) as invoice_status,
    v.passed as validation_passed,
    v.validator_name,
    v.created_at as validation_date
FROM finance_einvoice_documents d
LEFT JOIN finance_ap_invoices ap ON ap.xml_ref = d.id OR ap.pdfa3_ref = d.id
LEFT JOIN finance_ar_invoices ar ON ar.xml_ref = d.id OR ar.pdfa3_ref = d.id
LEFT JOIN finance_einvoice_validations v ON v.document_id = d.id
WHERE v.created_at = (
    SELECT MAX(created_at)
    FROM finance_einvoice_validations v2
    WHERE v2.document_id = d.id
);

-- Validation Statistics View
CREATE VIEW finance_einvoice_validation_stats AS
SELECT
    tenant_id,
    validator_name,
    DATE(created_at) as validation_date,
    COUNT(*) as total_validations,
    COUNT(*) FILTER (WHERE passed = true) as passed_validations,
    COUNT(*) FILTER (WHERE passed = false) as failed_validations,
    ROUND(
        COUNT(*) FILTER (WHERE passed = true) * 100.0 / COUNT(*),
        2
    ) as success_rate
FROM finance_einvoice_validations
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY tenant_id, validator_name, DATE(created_at)
ORDER BY validation_date DESC, tenant_id, validator_name;

-- ===== FUNCTIONS =====

-- Function to validate ZUGFeRD profile
CREATE OR REPLACE FUNCTION validate_zugferd_profile(profile TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN profile IN ('ZUGFeRD-BASIC', 'ZUGFeRD-EN16931', 'ZUGFeRD-EXTENDED');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to validate XRechnung profile
CREATE OR REPLACE FUNCTION validate_xrechnung_profile(profile TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN profile IN ('XRechnung-2.0', 'XRechnung-2.1', 'XRechnung-2.2', 'XRechnung-2.3');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get document profile from XML content
CREATE OR REPLACE FUNCTION extract_einvoice_profile(xml_content TEXT)
RETURNS TEXT AS $$
DECLARE
    profile TEXT;
BEGIN
    -- Extract profile from XML (simplified implementation)
    -- In production, this would use proper XML parsing

    -- Check for ZUGFeRD profile
    IF xml_content LIKE '%ZUGFeRD%' THEN
        IF xml_content LIKE '%EN 16931%' THEN
            RETURN 'ZUGFeRD-EN16931';
        ELSIF xml_content LIKE '%EXTENDED%' THEN
            RETURN 'ZUGFeRD-EXTENDED';
        ELSE
            RETURN 'ZUGFeRD-BASIC';
        END IF;
    END IF;

    -- Check for XRechnung profile
    IF xml_content LIKE '%XRechnung%' THEN
        RETURN 'XRechnung-2.3'; -- Default to latest version
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ===== TRIGGERS =====

-- Trigger to update updated_at on profiles
CREATE TRIGGER update_finance_einv_profiles_updated_at
    BEFORE UPDATE ON finance_einvoice_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at on AP invoices
CREATE TRIGGER update_finance_ap_invoices_updated_at
    BEFORE UPDATE ON finance_ap_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at on AR invoices
CREATE TRIGGER update_finance_ar_invoices_updated_at
    BEFORE UPDATE ON finance_ar_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===== AUDIT TRAIL EXTENSIONS =====

-- Extend audit trail function for e-invoice tables
CREATE OR REPLACE FUNCTION create_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    table_name TEXT := TG_TABLE_NAME;
    record_id UUID := COALESCE(NEW.id, OLD.id);
    tenant_id TEXT;
BEGIN
    -- Extract tenant_id based on table structure
    CASE table_name
        WHEN 'finance_einvoice_documents' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        WHEN 'finance_einvoice_validations' THEN
            SELECT COALESCE(d.tenant_id, 'SYSTEM') INTO tenant_id
            FROM finance_einvoice_documents d
            WHERE d.id = COALESCE(NEW.document_id, OLD.document_id);
        WHEN 'finance_einvoice_profiles' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        WHEN 'finance_ap_invoices' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
        WHEN 'finance_ar_invoices' THEN tenant_id := COALESCE(NEW.tenant_id, OLD.tenant_id);
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

-- Apply audit triggers to e-invoice tables
CREATE TRIGGER audit_finance_einv_documents
    AFTER INSERT OR UPDATE OR DELETE ON finance_einvoice_documents
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_einv_validations
    AFTER INSERT OR UPDATE OR DELETE ON finance_einvoice_validations
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_finance_einv_profiles
    AFTER INSERT OR UPDATE OR DELETE ON finance_einvoice_profiles
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

-- Note: AP and AR invoice audit triggers are already created in the base schema

-- ===== ROW LEVEL SECURITY =====

-- Enable RLS on e-invoice tables
ALTER TABLE finance_einvoice_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_einvoice_validations ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_einvoice_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_einvoice_normalized ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for e-invoice tables
CREATE POLICY tenant_isolation_einv_docs ON finance_einvoice_documents
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_einv_validations ON finance_einvoice_validations
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_einv_profiles ON finance_einvoice_profiles
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_einv_normalized ON finance_einvoice_normalized
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

-- ===== INITIAL DATA =====

-- Insert default e-invoice profiles
INSERT INTO finance_einvoice_profiles (tenant_id, profile_name, standard, version, configuration) VALUES

-- ZUGFeRD Profiles
('DEFAULT', 'ZUGFeRD-BASIC', 'ZUGFeRD', '2.1.1',
 '{"schema": "CII", "conformance": "BASIC", "validation": {"xml": true, "schematron": true}}'),

('DEFAULT', 'ZUGFeRD-EN16931', 'ZUGFeRD', '2.1.1',
 '{"schema": "CII", "conformance": "EN16931", "validation": {"xml": true, "schematron": true, "en16931": true}}'),

('DEFAULT', 'ZUGFeRD-EXTENDED', 'ZUGFeRD', '2.1.1',
 '{"schema": "CII", "conformance": "EXTENDED", "validation": {"xml": true, "schematron": true, "en16931": true}}'),

-- XRechnung Profiles
('DEFAULT', 'XRechnung-2.3', 'XRECHNUNG', '2.3',
 '{"schema": "UBL", "conformance": "XRECHNUNG", "validation": {"xml": true, "schematron": true, "xrechnung": true}}'),

('DEFAULT', 'XRechnung-2.2', 'XRECHNUNG', '2.2',
 '{"schema": "UBL", "conformance": "XRECHNUNG", "validation": {"xml": true, "schematron": true, "xrechnung": true}}'),

-- PEPPOL Profile
('DEFAULT', 'PEPPOL-BIS', 'PEPPOL', '3.0',
 '{"schema": "UBL", "conformance": "PEPPOL", "validation": {"xml": true, "schematron": true, "peppol": true}}');

-- ===== PERFORMANCE OPTIMIZATION =====

-- Analyze new tables
ANALYZE finance_einvoice_documents;
ANALYZE finance_einvoice_validations;
ANALYZE finance_einvoice_profiles;
ANALYZE finance_einvoice_normalized;

-- Add foreign key constraints for normalized data
ALTER TABLE finance_einvoice_normalized
ADD CONSTRAINT fk_ap_invoice FOREIGN KEY (invoice_id)
REFERENCES finance_ap_invoices(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE finance_einvoice_normalized
ADD CONSTRAINT fk_ar_invoice FOREIGN KEY (invoice_id)
REFERENCES finance_ar_invoices(id) DEFERRABLE INITIALLY DEFERRED;

-- ===== COMMENTS =====

COMMENT ON TABLE finance_einvoice_documents IS 'E-Invoice documents (PDF/A-3, XML, UBL) with integrity hashes';
COMMENT ON TABLE finance_einvoice_validations IS 'Validation results for e-invoice documents';
COMMENT ON TABLE finance_einvoice_profiles IS 'Supported e-invoice profiles and their configurations';
COMMENT ON TABLE finance_einvoice_normalized IS 'Normalized e-invoice data for processing';

COMMENT ON VIEW finance_einvoice_summary IS 'Summary of e-invoice documents with validation status';
COMMENT ON VIEW finance_einvoice_validation_stats IS 'Validation statistics and success rates';

-- ===== MIGRATION METADATA =====

INSERT INTO schema_migrations (version, description, applied_at) VALUES
('002_einvoice_schema', 'E-Invoice schema for ZUGFeRD/XRechnung compliance', NOW());