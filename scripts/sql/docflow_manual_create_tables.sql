-- Docflow-Tabellen manuell anlegen
-- Verwendung: Wenn alembic_version docflow_core (oder eine spätere Docflow-Revision) enthält,
-- die Tabellen aber fehlen (z. B. nach Restore/Split), dieses Skript einmal ausführen,
-- danach: alembic upgrade head
--
-- Idempotent: CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS (PostgreSQL 9.5+).
-- Reihenfolge: Schema → Tabellen in Abhängigkeitsreihenfolge.

CREATE SCHEMA IF NOT EXISTS domain_docflow;

-- ========== docflow_core_20260215 ==========
CREATE TABLE IF NOT EXISTS domain_docflow.number_series (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    doc_type VARCHAR(40) NOT NULL,
    year INTEGER NOT NULL,
    prefix VARCHAR(20) NOT NULL,
    counter INTEGER NOT NULL DEFAULT 1,
    width INTEGER NOT NULL DEFAULT 6,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT uq_docflow_number_series_scope UNIQUE (tenant_id, doc_type, year)
);

CREATE TABLE IF NOT EXISTS domain_docflow.document_headers (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    doc_type VARCHAR(40) NOT NULL,
    doc_number VARCHAR(80) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    source_system VARCHAR(40) NOT NULL DEFAULT 'docflow',
    source_ref VARCHAR(80),
    customer_id VARCHAR(64),
    supplier_id VARCHAR(64),
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    total_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_tax NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_gross NUMERIC(14,2) NOT NULL DEFAULT 0,
    document_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    posting_date DATE,
    version INTEGER NOT NULL DEFAULT 1,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    PRIMARY KEY (id),
    CONSTRAINT uq_docflow_header_number UNIQUE (tenant_id, doc_type, doc_number),
    CONSTRAINT chk_docflow_header_status CHECK (status IN ('draft','open','completed','posted','reversed','cancelled'))
);
CREATE INDEX IF NOT EXISTS ix_docflow_headers_tenant_type_created ON domain_docflow.document_headers (tenant_id, doc_type, created_at);
CREATE INDEX IF NOT EXISTS ix_docflow_headers_source ON domain_docflow.document_headers (source_system, source_ref);

CREATE TABLE IF NOT EXISTS domain_docflow.document_items (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    header_id VARCHAR(36) NOT NULL,
    line_number INTEGER NOT NULL,
    source_line_id VARCHAR(36),
    article_number VARCHAR(80) NOT NULL,
    description TEXT,
    quantity NUMERIC(14,3) NOT NULL,
    unit VARCHAR(20),
    unit_price NUMERIC(14,4) NOT NULL DEFAULT 0,
    discount_percent NUMERIC(7,3) NOT NULL DEFAULT 0,
    tax_rate NUMERIC(6,3) NOT NULL DEFAULT 0,
    line_total_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    line_total_tax NUMERIC(14,2) NOT NULL DEFAULT 0,
    line_total_gross NUMERIC(14,2) NOT NULL DEFAULT 0,
    batch_id VARCHAR(64),
    charge VARCHAR(64),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_docflow_items_header FOREIGN KEY (header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE CASCADE,
    CONSTRAINT uq_docflow_item_line UNIQUE (header_id, line_number),
    CONSTRAINT chk_docflow_item_qty_non_negative CHECK (quantity >= 0),
    CONSTRAINT chk_docflow_item_price_non_negative CHECK (unit_price >= 0),
    CONSTRAINT chk_docflow_item_discount_range CHECK (discount_percent >= 0 AND discount_percent <= 100),
    CONSTRAINT chk_docflow_item_tax_range CHECK (tax_rate >= 0 AND tax_rate <= 100)
);
CREATE INDEX IF NOT EXISTS ix_docflow_items_tenant_article ON domain_docflow.document_items (tenant_id, article_number);

CREATE TABLE IF NOT EXISTS domain_docflow.document_links (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    from_header_id VARCHAR(36) NOT NULL,
    to_header_id VARCHAR(36) NOT NULL,
    relation_type VARCHAR(40) NOT NULL,
    from_item_id VARCHAR(36),
    to_item_id VARCHAR(36),
    quantity_linked NUMERIC(14,3) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_docflow_links_from FOREIGN KEY (from_header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE CASCADE,
    CONSTRAINT fk_docflow_links_to FOREIGN KEY (to_header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE CASCADE,
    CONSTRAINT fk_docflow_links_from_item FOREIGN KEY (from_item_id) REFERENCES domain_docflow.document_items(id) ON DELETE SET NULL,
    CONSTRAINT fk_docflow_links_to_item FOREIGN KEY (to_item_id) REFERENCES domain_docflow.document_items(id) ON DELETE SET NULL,
    CONSTRAINT chk_docflow_link_qty_non_negative CHECK (quantity_linked >= 0)
);
CREATE INDEX IF NOT EXISTS ix_docflow_links_from_to ON domain_docflow.document_links (tenant_id, from_header_id, to_header_id);

CREATE TABLE IF NOT EXISTS domain_docflow.document_postings (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    header_id VARCHAR(36) NOT NULL,
    posting_type VARCHAR(20) NOT NULL,
    journal_entry_id VARCHAR(64),
    amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    idempotency_key VARCHAR(120),
    outbox_event_id VARCHAR(64),
    posted_by VARCHAR(100),
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_docflow_postings_header FOREIGN KEY (header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE CASCADE,
    CONSTRAINT chk_docflow_posting_type CHECK (posting_type IN ('post','reverse'))
);
CREATE INDEX IF NOT EXISTS ix_docflow_postings_header_posted ON domain_docflow.document_postings (tenant_id, header_id, posted_at);

CREATE TABLE IF NOT EXISTS domain_docflow.command_idempotency_keys (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    command_name VARCHAR(40) NOT NULL,
    resource_id VARCHAR(36) NOT NULL,
    idempotency_key VARCHAR(120) NOT NULL,
    response_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT uq_docflow_command_idempotency UNIQUE (tenant_id, command_name, resource_id, idempotency_key)
);

-- ========== docflow_pos_tse_compliance_20260215 ==========
CREATE TABLE IF NOT EXISTS domain_docflow.pos_receipt_compliance (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    header_id VARCHAR(36) NOT NULL,
    terminal_id VARCHAR(60) NOT NULL,
    cash_register_id VARCHAR(60),
    transaction_type VARCHAR(20) NOT NULL DEFAULT 'sale',
    payment_breakdown JSONB,
    tse_transaction_id VARCHAR(120) NOT NULL,
    tse_signature TEXT NOT NULL,
    tse_signature_counter BIGINT,
    transaction_started_at TIMESTAMPTZ NOT NULL,
    transaction_ended_at TIMESTAMPTZ NOT NULL,
    receipt_issued_at TIMESTAMPTZ NOT NULL,
    dsfinvk_export_batch_id VARCHAR(120),
    correction_type VARCHAR(20),
    original_header_id VARCHAR(36),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_pos_tse_header FOREIGN KEY (header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE CASCADE,
    CONSTRAINT fk_pos_tse_original FOREIGN KEY (original_header_id) REFERENCES domain_docflow.document_headers(id) ON DELETE SET NULL,
    CONSTRAINT uq_pos_tse_header UNIQUE (tenant_id, header_id),
    CONSTRAINT chk_pos_tse_transaction_type CHECK (transaction_type IN ('sale','storno','retoure','voucher_sale','voucher_redeem')),
    CONSTRAINT chk_pos_tse_correction_type CHECK (correction_type IS NULL OR correction_type IN ('storno','retoure')),
    CONSTRAINT chk_pos_tse_original_ref CHECK (
        (correction_type IS NULL AND original_header_id IS NULL) OR
        (correction_type IS NOT NULL AND original_header_id IS NOT NULL)
    )
);
CREATE INDEX IF NOT EXISTS ix_pos_tse_tenant_terminal_time ON domain_docflow.pos_receipt_compliance (tenant_id, terminal_id, transaction_ended_at);

-- ========== docflow_pos_admin_dsfinvk_20260215 ==========
CREATE TABLE IF NOT EXISTS domain_docflow.pos_terminals (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    terminal_code VARCHAR(60) NOT NULL,
    name VARCHAR(120) NOT NULL,
    location_name VARCHAR(120),
    branch_code VARCHAR(60),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unregistered_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT uq_pos_terminal_code UNIQUE (tenant_id, terminal_code)
);
CREATE INDEX IF NOT EXISTS ix_pos_terminals_tenant_active ON domain_docflow.pos_terminals (tenant_id, is_active);

CREATE TABLE IF NOT EXISTS domain_docflow.pos_tse_devices (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    terminal_id VARCHAR(36) NOT NULL,
    serial_number VARCHAR(120) NOT NULL,
    provider VARCHAR(120),
    api_endpoint VARCHAR(255),
    certificate_fingerprint VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    activation_date DATE,
    deactivation_date DATE,
    last_heartbeat_at TIMESTAMPTZ,
    settings JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_pos_tse_devices_terminal FOREIGN KEY (terminal_id) REFERENCES domain_docflow.pos_terminals(id) ON DELETE CASCADE,
    CONSTRAINT uq_pos_tse_serial UNIQUE (tenant_id, serial_number),
    CONSTRAINT chk_pos_tse_status CHECK (status IN ('active','inactive','retired'))
);
CREATE INDEX IF NOT EXISTS ix_pos_tse_devices_tenant_status ON domain_docflow.pos_tse_devices (tenant_id, status);

CREATE TABLE IF NOT EXISTS domain_docflow.pos_regulatory_notices (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    terminal_id VARCHAR(36),
    tse_device_id VARCHAR(36),
    notice_type VARCHAR(30) NOT NULL,
    notice_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    effective_date DATE NOT NULL,
    submitted_at TIMESTAMPTZ,
    reference_number VARCHAR(120),
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_pos_notices_terminal FOREIGN KEY (terminal_id) REFERENCES domain_docflow.pos_terminals(id) ON DELETE SET NULL,
    CONSTRAINT fk_pos_notices_tse FOREIGN KEY (tse_device_id) REFERENCES domain_docflow.pos_tse_devices(id) ON DELETE SET NULL,
    CONSTRAINT chk_pos_notice_type CHECK (notice_type IN ('install','change','decommission')),
    CONSTRAINT chk_pos_notice_status CHECK (notice_status IN ('draft','submitted','accepted','rejected'))
);
CREATE INDEX IF NOT EXISTS ix_pos_notices_tenant_effective ON domain_docflow.pos_regulatory_notices (tenant_id, effective_date);

CREATE TABLE IF NOT EXISTS domain_docflow.dsfinvk_exports (
    id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    period_from DATE NOT NULL,
    period_to DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    file_path VARCHAR(500),
    checksum_sha256 VARCHAR(64),
    row_count INTEGER NOT NULL DEFAULT 0,
    generated_by VARCHAR(100),
    generated_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT chk_dsfinvk_export_status CHECK (status IN ('running','completed','failed')),
    CONSTRAINT chk_dsfinvk_period CHECK (period_to >= period_from)
);
CREATE INDEX IF NOT EXISTS ix_dsfinvk_exports_tenant_period ON domain_docflow.dsfinvk_exports (tenant_id, period_from, period_to);
