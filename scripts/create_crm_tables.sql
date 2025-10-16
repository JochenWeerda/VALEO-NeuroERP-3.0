-- Create CRM Activities Table
CREATE TABLE IF NOT EXISTS domain_crm.activities (
    id VARCHAR PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    customer VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    description TEXT,
    tenant_id VARCHAR REFERENCES domain_shared.tenants(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create CRM Farm Profiles Table
CREATE TABLE IF NOT EXISTS domain_crm.farm_profiles (
    id VARCHAR PRIMARY KEY,
    farm_name VARCHAR(200) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    total_area FLOAT NOT NULL,
    crops JSONB,
    livestock JSONB,
    location JSONB,
    certifications JSONB,
    notes TEXT,
    tenant_id VARCHAR REFERENCES domain_shared.tenants(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_activities_date ON domain_crm.activities(date);
CREATE INDEX IF NOT EXISTS idx_activities_status ON domain_crm.activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_type ON domain_crm.activities(type);
CREATE INDEX IF NOT EXISTS idx_activities_customer ON domain_crm.activities(customer);

CREATE INDEX IF NOT EXISTS idx_farm_profiles_owner ON domain_crm.farm_profiles(owner);
CREATE INDEX IF NOT EXISTS idx_farm_profiles_farm_name ON domain_crm.farm_profiles(farm_name);

-- Grant permissions
GRANT ALL ON domain_crm.activities TO valeo_dev;
GRANT ALL ON domain_crm.farm_profiles TO valeo_dev;

