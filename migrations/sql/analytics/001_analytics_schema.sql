-- =====================================================
-- VALEO NeuroERP 3.0 - Analytics Core Schema
-- Generated for MSOA migration with branded types
-- Includes Reports and Dashboards management
-- =====================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================================================
-- Reports Table
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('sales', 'inventory', 'financial', 'customer', 'operational')),
    query TEXT NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}'::jsonb,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Dashboards Table
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics.dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    widgets JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_by VARCHAR(100) NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT false,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Report Executions Table (for caching and history)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics.report_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES analytics.reports(id) ON DELETE CASCADE,
    executed_by VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}'::jsonb,
    result_data JSONB,
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'error', 'timeout')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Dashboard Views Table (for analytics)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics.dashboard_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID NOT NULL REFERENCES analytics.dashboards(id) ON DELETE CASCADE,
    viewed_by VARCHAR(100) NOT NULL,
    view_duration_seconds INTEGER,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_analytics_reports_type ON analytics.reports(type);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_created_by ON analytics.reports(created_by);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_is_public ON analytics.reports(is_public);

CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_created_by ON analytics.dashboards(created_by);
CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_is_public ON analytics.dashboards(is_public);
CREATE INDEX IF NOT EXISTS idx_analytics_dashboards_tags ON analytics.dashboards USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_analytics_report_executions_report_id ON analytics.report_executions(report_id);
CREATE INDEX IF NOT EXISTS idx_analytics_report_executions_created_at ON analytics.report_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_report_executions_status ON analytics.report_executions(status);

CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_views_dashboard_id ON analytics.dashboard_views(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_views_created_at ON analytics.dashboard_views(created_at);

-- =====================================================
-- Updated At Triggers
-- =====================================================
CREATE OR REPLACE FUNCTION analytics.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analytics_reports_updated_at
    BEFORE UPDATE ON analytics.reports
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

CREATE TRIGGER update_analytics_dashboards_updated_at
    BEFORE UPDATE ON analytics.dashboards
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

-- =====================================================
-- Initial Seed Data
-- =====================================================
INSERT INTO analytics.reports (name, type, query, created_by, is_public) VALUES
    ('Sales Summary', 'sales', 'SELECT SUM(total) as total_sales FROM erp.orders WHERE status = ''delivered''', 'system', true),
    ('Inventory Status', 'inventory', 'SELECT p.name, i.quantity, i.available_quantity FROM erp.products p JOIN erp.inventory i ON p.id = i.product_id', 'system', true),
    ('Top Customers', 'customer', 'SELECT customer_id, SUM(total) as total_spent FROM erp.orders WHERE status = ''delivered'' GROUP BY customer_id ORDER BY total_spent DESC LIMIT 10', 'system', true)
ON CONFLICT DO NOTHING;

INSERT INTO analytics.dashboards (name, description, widgets, created_by, is_public) VALUES
    ('Executive Overview', 'High-level business metrics dashboard',
     '[{"type": "metric", "title": "Total Sales", "query": "SELECT SUM(total) FROM erp.orders"}, {"type": "chart", "title": "Sales Trend", "query": "SELECT DATE(order_date), SUM(total) FROM erp.orders GROUP BY DATE(order_date)"}]'::jsonb,
     'system', true),
    ('Inventory Dashboard', 'Real-time inventory monitoring',
     '[{"type": "table", "title": "Low Stock Items", "query": "SELECT p.name, i.available_quantity FROM erp.products p JOIN erp.inventory i ON p.id = i.product_id WHERE i.available_quantity < i.reorder_level"}]'::jsonb,
     'system', true)
ON CONFLICT DO NOTHING;