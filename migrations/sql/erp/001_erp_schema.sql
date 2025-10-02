-- =====================================================
-- VALEO NeuroERP 3.0 - ERP Core Schema
-- Generated for MSOA migration with branded types
-- Includes Products, Orders, and Inventory management
-- =====================================================

CREATE SCHEMA IF NOT EXISTS erp;

-- =====================================================
-- Products Table
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'discontinued')) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Orders Table
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID NOT NULL, -- References CRM customer
    items JSONB NOT NULL DEFAULT '[]'::jsonb, -- OrderItem array
    subtotal NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    tax NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    total NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')) DEFAULT 'pending',
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Inventory Table
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES erp.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    reorder_level INTEGER NOT NULL DEFAULT 10,
    reorder_quantity INTEGER NOT NULL DEFAULT 50,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_erp_products_sku ON erp.products(sku);
CREATE INDEX IF NOT EXISTS idx_erp_products_category ON erp.products(category);
CREATE INDEX IF NOT EXISTS idx_erp_products_status ON erp.products(status);

CREATE INDEX IF NOT EXISTS idx_erp_orders_customer_id ON erp.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_erp_orders_status ON erp.orders(status);
CREATE INDEX IF NOT EXISTS idx_erp_orders_order_date ON erp.orders(order_date);

CREATE INDEX IF NOT EXISTS idx_erp_inventory_product_id ON erp.inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_erp_inventory_available_quantity ON erp.inventory(available_quantity);

-- =====================================================
-- Updated At Triggers
-- =====================================================
CREATE OR REPLACE FUNCTION erp.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_erp_products_updated_at
    BEFORE UPDATE ON erp.products
    FOR EACH ROW EXECUTE FUNCTION erp.update_updated_at_column();

CREATE TRIGGER update_erp_orders_updated_at
    BEFORE UPDATE ON erp.orders
    FOR EACH ROW EXECUTE FUNCTION erp.update_updated_at_column();

CREATE TRIGGER update_erp_inventory_updated_at
    BEFORE UPDATE ON erp.inventory
    FOR EACH ROW EXECUTE FUNCTION erp.update_updated_at_column();

-- =====================================================
-- Initial Seed Data
-- =====================================================
INSERT INTO erp.products (name, sku, price, category, description, status) VALUES
    ('Sample Product 1', 'SP001', 29.99, 'Electronics', 'A sample electronic product', 'active'),
    ('Sample Product 2', 'SP002', 49.99, 'Clothing', 'A sample clothing item', 'active'),
    ('Sample Product 3', 'SP003', 19.99, 'Books', 'A sample book', 'active')
ON CONFLICT (sku) DO NOTHING;

-- Initialize inventory for sample products
INSERT INTO erp.inventory (product_id, quantity, reorder_level, reorder_quantity)
SELECT id, 100, 10, 50 FROM erp.products WHERE sku IN ('SP001', 'SP002', 'SP003')
ON CONFLICT (product_id) DO NOTHING;