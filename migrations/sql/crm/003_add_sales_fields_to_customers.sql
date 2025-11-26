-- Migration: Add Sales fields to customers table
-- SALES-CRM-02: Kunden-/Kontaktstamm (Sales-Sicht)
-- Date: 2025-01-24
-- 
-- Hinweis: Nur neue Felder werden hinzugefügt. Bestehende Felder werden über Mapping verwendet:
-- - customer_segment: Bereits vorhanden, wird zu analytics.segment gemappt
-- - industry: Wird aus crm-core gemappt
-- - region: Wird aus crm-core gemappt
-- - customer_price_list: Wird über customer.price_list_id verwaltet

-- Add new fields to public.customers (tatsächliche Tabelle in der Datenbank)
ALTER TABLE public.customers
ADD COLUMN IF NOT EXISTS price_group VARCHAR(50),
ADD COLUMN IF NOT EXISTS tax_category VARCHAR(50);

-- Add comments
COMMENT ON COLUMN public.customers.price_group IS 'Price group: standard, premium, wholesale, retail';
COMMENT ON COLUMN public.customers.tax_category IS 'Tax category: standard, reduced, zero, reverse_charge, exempt';

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_customers_price_group ON public.customers(price_group);
CREATE INDEX IF NOT EXISTS idx_customers_tax_category ON public.customers(tax_category);

