-- =====================================================
-- VALEO NeuroERP 3.0 - Order Management Schema
-- Ported from legacy ERP initialisation (erp_test_data.sql)
-- Adapted for branded identifiers (UUID) and MSOA schema layout
-- =====================================================

CREATE SCHEMA IF NOT EXISTS erp;

-- =====================================================
-- Orders
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_number VARCHAR(50) NOT NULL,
    debtor_number VARCHAR(50) NOT NULL,
    document_date DATE NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('offer', 'order', 'delivery', 'invoice')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'confirmed', 'delivered', 'invoiced')),
    net_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    vat_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    currency CHAR(3) NOT NULL DEFAULT 'EUR',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_number)
);

-- =====================================================
-- Order Positions
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.order_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES erp.orders(id) ON DELETE CASCADE,
    article_number VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    quantity NUMERIC(10,2) NOT NULL DEFAULT 1.00,
    unit VARCHAR(20) NOT NULL DEFAULT 'piece',
    unit_price NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    discount NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    net_price NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Contacts (Sales/Purchase)
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    representative VARCHAR(100) NOT NULL,
    contact_type VARCHAR(20) NOT NULL CHECK (contact_type IN ('sales', 'purchase')),
    appointment_date DATE,
    order_quantity INTEGER NOT NULL DEFAULT 0,
    remaining_quantity INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'planned')) DEFAULT 'active',
    phone VARCHAR(20),
    email VARCHAR(100),
    last_contact DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Deliveries
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_number VARCHAR(50) UNIQUE NOT NULL,
    order_id UUID REFERENCES erp.orders(id) ON DELETE SET NULL,
    delivery_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'shipped', 'delivered', 'returned')) DEFAULT 'pending',
    shipping_address TEXT,
    tracking_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Documents
-- =====================================================
CREATE TABLE IF NOT EXISTS erp.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('offer', 'order', 'delivery', 'invoice')),
    reference_id UUID NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'final', 'archived')) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_erp_orders_customer_number ON erp.orders(customer_number);
CREATE INDEX IF NOT EXISTS idx_erp_orders_debtor_number ON erp.orders(debtor_number);
CREATE INDEX IF NOT EXISTS idx_erp_orders_document_date ON erp.orders(document_date);
CREATE INDEX IF NOT EXISTS idx_erp_orders_status ON erp.orders(status);
CREATE INDEX IF NOT EXISTS idx_erp_orders_document_type ON erp.orders(document_type);

CREATE INDEX IF NOT EXISTS idx_erp_order_positions_order_id ON erp.order_positions(order_id);
CREATE INDEX IF NOT EXISTS idx_erp_order_positions_article_number ON erp.order_positions(article_number);

CREATE INDEX IF NOT EXISTS idx_erp_contacts_contact_number ON erp.contacts(contact_number);
CREATE INDEX IF NOT EXISTS idx_erp_contacts_name ON erp.contacts(name);
CREATE INDEX IF NOT EXISTS idx_erp_contacts_representative ON erp.contacts(representative);
CREATE INDEX IF NOT EXISTS idx_erp_contacts_status ON erp.contacts(status);
CREATE INDEX IF NOT EXISTS idx_erp_contacts_contact_type ON erp.contacts(contact_type);

CREATE INDEX IF NOT EXISTS idx_erp_deliveries_delivery_number ON erp.deliveries(delivery_number);
CREATE INDEX IF NOT EXISTS idx_erp_deliveries_order_id ON erp.deliveries(order_id);
CREATE INDEX IF NOT EXISTS idx_erp_deliveries_status ON erp.deliveries(status);

CREATE INDEX IF NOT EXISTS idx_erp_documents_reference_id ON erp.documents(reference_id);
CREATE INDEX IF NOT EXISTS idx_erp_documents_document_type ON erp.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_erp_documents_status ON erp.documents(status);

-- =====================================================
-- Trigger for updated_at maintenance
-- =====================================================
CREATE OR REPLACE FUNCTION erp.touch_updated_at()
RETURNS TRIGGER AS 3585
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
3585 LANGUAGE plpgsql;

CREATE TRIGGER erp_orders_touch_update
    BEFORE UPDATE ON erp.orders
    FOR EACH ROW
    EXECUTE FUNCTION erp.touch_updated_at();

CREATE TRIGGER erp_order_positions_touch_update
    BEFORE UPDATE ON erp.order_positions
    FOR EACH ROW
    EXECUTE FUNCTION erp.touch_updated_at();

CREATE TRIGGER erp_contacts_touch_update
    BEFORE UPDATE ON erp.contacts
    FOR EACH ROW
    EXECUTE FUNCTION erp.touch_updated_at();

CREATE TRIGGER erp_deliveries_touch_update
    BEFORE UPDATE ON erp.deliveries
    FOR EACH ROW
    EXECUTE FUNCTION erp.touch_updated_at();

CREATE TRIGGER erp_documents_touch_update
    BEFORE UPDATE ON erp.documents
    FOR EACH ROW
    EXECUTE FUNCTION erp.touch_updated_at();
