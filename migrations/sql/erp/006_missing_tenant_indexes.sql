-- 006_missing_tenant_indexes.sql
-- Phase 4 Observability & Performance: fehlende Tenant-scoped Composite-Indexes
-- Idempotent via IF NOT EXISTS (PostgreSQL 9.5+)
-- Deploy-Order: nach 005_order_management_schema.sql

-- ── domain_sales ─────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_sales_delivery_notes_tenant_date
    ON domain_sales.delivery_notes (tenant_id, delivery_date);

CREATE INDEX IF NOT EXISTS idx_sales_delivery_notes_tenant_status
    ON domain_sales.delivery_notes (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_sales_orders_tenant_date
    ON domain_sales.orders (tenant_id, order_date);

CREATE INDEX IF NOT EXISTS idx_sales_orders_tenant_status
    ON domain_sales.orders (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_sales_credit_notes_tenant_date
    ON domain_sales.credit_notes (tenant_id, document_date);

-- ── domain_inventory ─────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_inventory_stock_movements_tenant_type
    ON domain_inventory.stock_movements (tenant_id, movement_type);

CREATE INDEX IF NOT EXISTS idx_inventory_stock_movements_tenant_date
    ON domain_inventory.stock_movements (tenant_id, movement_date);

CREATE INDEX IF NOT EXISTS idx_inventory_stock_tenant_article
    ON domain_inventory.stock (tenant_id, article_id);

-- ── domain_erp ───────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_erp_purchase_orders_tenant_status
    ON domain_erp.purchase_orders (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_erp_purchase_orders_tenant_date
    ON domain_erp.purchase_orders (tenant_id, order_date);

CREATE INDEX IF NOT EXISTS idx_erp_contracts_tenant_status
    ON domain_erp.contracts (tenant_id, status);

-- ── finanz (bereits teilweise in 003, Ergänzungen) ────────────────────────────

CREATE INDEX IF NOT EXISTS idx_finanz_buchungen_tenant_datum
    ON finanz.buchungen (tenant_id, buchungsdatum);

CREATE INDEX IF NOT EXISTS idx_finanz_debitoren_tenant_aktiv
    ON finanz.debitoren (tenant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_finanz_kreditoren_tenant_aktiv
    ON finanz.kreditoren (tenant_id, is_active);
