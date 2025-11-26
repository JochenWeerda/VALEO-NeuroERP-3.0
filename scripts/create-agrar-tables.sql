-- VALEO NeuroERP - Agrar Tabellen (PostgreSQL)
-- Created: 2025-10-16

-- PSM (Pflanzenschutzmittel) Produkte
CREATE TABLE IF NOT EXISTS agrar_psm_products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    active_ingredient VARCHAR(255),
    product_type VARCHAR(100),
    registration_number VARCHAR(100) UNIQUE,
    manufacturer VARCHAR(255),
    approval_status VARCHAR(50) DEFAULT 'active',
    application_areas TEXT,
    dosage_instructions TEXT,
    safety_interval_days INTEGER,
    water_protection_class VARCHAR(10),
    bee_hazard VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_psm_products_name ON agrar_psm_products(product_name);
CREATE INDEX idx_psm_products_regno ON agrar_psm_products(registration_number);
CREATE INDEX idx_psm_products_type ON agrar_psm_products(product_type);

-- PSM Abgabedokumentation
CREATE TABLE IF NOT EXISTS agrar_psm_documentation (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES agrar_psm_products(id) ON DELETE CASCADE,
    customer_id INTEGER,
    customer_name VARCHAR(255) NOT NULL,
    customer_address TEXT,
    quantity_liters DECIMAL(10,2),
    quantity_kg DECIMAL(10,2),
    sale_date DATE NOT NULL,
    application_purpose TEXT,
    application_area_hectares DECIMAL(10,2),
    sachkundenachweis_number VARCHAR(100),
    beratung_documented BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_psm_doc_product ON agrar_psm_documentation(product_id);
CREATE INDEX idx_psm_doc_customer ON agrar_psm_documentation(customer_id);
CREATE INDEX idx_psm_doc_date ON agrar_psm_documentation(sale_date);

-- Saatgut (Seed)
CREATE TABLE IF NOT EXISTS agrar_saatgut (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    crop_type VARCHAR(100),
    variety VARCHAR(100),
    certification VARCHAR(50),
    tkm DECIMAL(8,2),
    germination_rate DECIMAL(5,2),
    producer VARCHAR(255),
    batch_number VARCHAR(100),
    packaging_unit VARCHAR(50),
    price_per_unit DECIMAL(10,2),
    stock_quantity DECIMAL(10,2),
    harvest_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saatgut_name ON agrar_saatgut(product_name);
CREATE INDEX idx_saatgut_crop ON agrar_saatgut(crop_type);
CREATE INDEX idx_saatgut_batch ON agrar_saatgut(batch_number);

-- Düngemittel (Fertilizer)
CREATE TABLE IF NOT EXISTS agrar_duengemittel (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    composition VARCHAR(255),
    n_content DECIMAL(5,2),
    p_content DECIMAL(5,2),
    k_content DECIMAL(5,2),
    mg_content DECIMAL(5,2),
    s_content DECIMAL(5,2),
    organic_matter DECIMAL(5,2),
    manufacturer VARCHAR(255),
    packaging_unit VARCHAR(50),
    price_per_unit DECIMAL(10,2),
    stock_quantity DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_duengemittel_name ON agrar_duengemittel(product_name);
CREATE INDEX idx_duengemittel_type ON agrar_duengemittel(type);

