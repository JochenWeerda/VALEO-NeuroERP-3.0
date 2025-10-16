-- Create CRM Activities Table (ohne Foreign Keys)
CREATE TABLE IF NOT EXISTS domain_crm.activities (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    customer VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    description TEXT,
    tenant_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create CRM Farm Profiles Table (ohne Foreign Keys)
CREATE TABLE IF NOT EXISTS domain_crm.farm_profiles (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    farm_name VARCHAR(200) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    total_area FLOAT NOT NULL,
    crops JSONB DEFAULT '[]'::jsonb,
    livestock JSONB DEFAULT '[]'::jsonb,
    location JSONB,
    certifications JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    tenant_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_activities_date ON domain_crm.activities(date);
CREATE INDEX IF NOT EXISTS idx_activities_status ON domain_crm.activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_type ON domain_crm.activities(type);

CREATE INDEX IF NOT EXISTS idx_farm_profiles_owner ON domain_crm.farm_profiles(owner);
CREATE INDEX IF NOT EXISTS idx_farm_profiles_farm_name ON domain_crm.farm_profiles(farm_name);

-- Insert test data for Activities
INSERT INTO domain_crm.activities (id, type, title, customer, contact_person, date, status, assigned_to, description, tenant_id) VALUES
('activity_1', 'meeting', 'Jahresgespräch 2025', 'Musterfirma GmbH', 'Max Mustermann', NOW() + INTERVAL '30 days', 'planned', 'Hans Mueller', 'Wichtiges Jahresgespräch mit Neukunden', 'system'),
('activity_2', 'call', 'Telefon-Follow-up Schmidt GmbH', 'Schmidt GmbH', 'Anna Schmidt', NOW() + INTERVAL '7 days', 'planned', 'Maria Weber', 'Angebot besprechen', 'system'),
('activity_3', 'email', 'Angebot versenden', 'Bio-Hof Müller', 'Thomas Müller', NOW() - INTERVAL '2 days', 'completed', 'Hans Mueller', 'Jahresangebot für Saatgut versendet', 'system'),
('activity_4', 'note', 'Kundengespräch dokumentiert', 'Agrar Schmidt', 'Werner Schmidt', NOW(), 'completed', 'Hans Mueller', 'Notizen vom heutigen Besuch', 'system');

-- Insert test data for Farm Profiles
INSERT INTO domain_crm.farm_profiles (id, farm_name, owner, total_area, crops, livestock, location, certifications, notes, tenant_id) VALUES
('farm_1', 'Bio-Hof Schmidt', 'Hans Schmidt', 150.5, 
 '[{"crop": "Weizen", "area": 80}, {"crop": "Gerste", "area": 45}, {"crop": "Raps", "area": 25.5}]'::jsonb,
 '[{"type": "Milchkühe", "count": 60}, {"type": "Kälber", "count": 15}]'::jsonb,
 '{"latitude": 52.520008, "longitude": 13.404954, "address": "Hauptstraße 123, 12345 Teststadt, Deutschland"}'::jsonb,
 '["Bio", "QS", "HACCP"]'::jsonb,
 'Traditionsreicher Betrieb seit 1950', 'system'),
 
('farm_2', 'Hof Müller', 'Thomas Müller', 85.0,
 '[{"crop": "Mais", "area": 50}, {"crop": "Sonnenblumen", "area": 35}]'::jsonb,
 '[{"type": "Schweine", "count": 200}]'::jsonb,
 '{"latitude": 51.165691, "longitude": 10.451526, "address": "Dorfstraße 45, 34567 Musterstadt, Deutschland"}'::jsonb,
 '["QS"]'::jsonb,
 'Spezialisiert auf Schweinezucht', 'system'),
 
('farm_3', 'Gemüsehof Weber', 'Maria Weber', 25.0,
 '[{"crop": "Kartoffeln", "area": 10}, {"crop": "Möhren", "area": 8}, {"crop": "Kohl", "area": 7}]'::jsonb,
 '[]'::jsonb,
 '{"latitude": 53.551086, "longitude": 9.993682, "address": "Feldweg 7, 20095 Hamburg, Deutschland"}'::jsonb,
 '["Bio", "GAP"]'::jsonb,
 'Bio-Gemüsebau mit Direktvermarktung', 'system');

