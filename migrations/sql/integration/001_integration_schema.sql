-- =====================================================
-- VALEO NeuroERP 3.0 - Integration Core Schema
-- Generated for MSOA migration with branded types
-- Includes Webhooks and Sync Jobs management
-- =====================================================

CREATE SCHEMA IF NOT EXISTS integration;

-- =====================================================
-- Webhooks Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration.webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(500) NOT NULL,
    events TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    secret VARCHAR(255),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'failed')) DEFAULT 'active',
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_delivery TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Sync Jobs Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration.sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(100) NOT NULL,
    target VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')) DEFAULT 'pending',
    last_sync TIMESTAMPTZ,
    error_message TEXT,
    records_processed INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Webhook Deliveries Table (for tracking)
-- =====================================================
CREATE TABLE IF NOT EXISTS integration.webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES integration.webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'retrying')) DEFAULT 'success',
    response_code INTEGER,
    response_body TEXT,
    delivered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- API Connections Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration.api_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    auth_type VARCHAR(20) NOT NULL CHECK (auth_type IN ('none', 'basic', 'bearer', 'api_key', 'oauth2')) DEFAULT 'none',
    auth_config JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'error')) DEFAULT 'active',
    last_tested TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_integration_webhooks_status ON integration.webhooks(status);
CREATE INDEX IF NOT EXISTS idx_integration_webhooks_events ON integration.webhooks USING GIN(events);

CREATE INDEX IF NOT EXISTS idx_integration_sync_jobs_status ON integration.sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_integration_sync_jobs_source_target ON integration.sync_jobs(source, target);

CREATE INDEX IF NOT EXISTS idx_integration_webhook_deliveries_webhook_id ON integration.webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_integration_webhook_deliveries_status ON integration.webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_integration_webhook_deliveries_delivered_at ON integration.webhook_deliveries(delivered_at);

CREATE INDEX IF NOT EXISTS idx_integration_api_connections_provider ON integration.api_connections(provider);
CREATE INDEX IF NOT EXISTS idx_integration_api_connections_status ON integration.api_connections(status);

-- =====================================================
-- Updated At Triggers
-- =====================================================
CREATE OR REPLACE FUNCTION integration.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_integration_webhooks_updated_at
    BEFORE UPDATE ON integration.webhooks
    FOR EACH ROW EXECUTE FUNCTION integration.update_updated_at_column();

CREATE TRIGGER update_integration_sync_jobs_updated_at
    BEFORE UPDATE ON integration.sync_jobs
    FOR EACH ROW EXECUTE FUNCTION integration.update_updated_at_column();

CREATE TRIGGER update_integration_api_connections_updated_at
    BEFORE UPDATE ON integration.api_connections
    FOR EACH ROW EXECUTE FUNCTION integration.update_updated_at_column();

-- =====================================================
-- Initial Seed Data
-- =====================================================
INSERT INTO integration.webhooks (url, events, status) VALUES
    ('https://api.example.com/webhooks/orders', ARRAY['order.created', 'order.updated'], 'active'),
    ('https://webhook.site/test-integration', ARRAY['customer.created', 'product.updated'], 'active')
ON CONFLICT DO NOTHING;

INSERT INTO integration.sync_jobs (source, target, status) VALUES
    ('crm', 'analytics', 'pending'),
    ('erp', 'analytics', 'pending'),
    ('legacy-system', 'erp', 'pending')
ON CONFLICT DO NOTHING;

INSERT INTO integration.api_connections (name, provider, base_url, auth_type, status) VALUES
    ('Shopify API', 'shopify', 'https://shopify-store.myshopify.com/admin/api/2023-10', 'bearer', 'active'),
    ('SAP Integration', 'sap', 'https://sap-system.company.com/api', 'basic', 'inactive'),
    ('Stripe Payments', 'stripe', 'https://api.stripe.com/v1', 'bearer', 'active')
ON CONFLICT DO NOTHING;