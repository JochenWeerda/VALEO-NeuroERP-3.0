-- CRM Tables for PostgreSQL
-- Direct SQL execution as Alembic-Fallback

-- CRM Contacts
CREATE TABLE IF NOT EXISTS crm_contacts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    type VARCHAR(20) NOT NULL,
    address_street VARCHAR(255),
    address_zip VARCHAR(10),
    address_city VARCHAR(100),
    address_country VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(36) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_crm_contacts_name ON crm_contacts(name);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_company ON crm_contacts(company);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_email ON crm_contacts(email);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_tenant ON crm_contacts(tenant_id);

-- CRM Leads
CREATE TABLE IF NOT EXISTS crm_leads (
    id VARCHAR(36) PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    source VARCHAR(100),
    potential NUMERIC(12, 2) DEFAULT 0,
    priority VARCHAR(20),
    status VARCHAR(20) NOT NULL,
    assigned_to VARCHAR(100),
    expected_close_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(36) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_crm_leads_company ON crm_leads(company);
CREATE INDEX IF NOT EXISTS idx_crm_leads_status ON crm_leads(status);
CREATE INDEX IF NOT EXISTS idx_crm_leads_tenant ON crm_leads(tenant_id);

-- CRM Activities
CREATE TABLE IF NOT EXISTS crm_activities (
    id VARCHAR(36) PRIMARY KEY,
    contact_id VARCHAR(36) REFERENCES crm_contacts(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    subject VARCHAR(255),
    notes TEXT,
    status VARCHAR(20),
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(36) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_crm_activities_contact ON crm_activities(contact_id);
CREATE INDEX IF NOT EXISTS idx_crm_activities_date ON crm_activities(date);
CREATE INDEX IF NOT EXISTS idx_crm_activities_tenant ON crm_activities(tenant_id);

-- CRM Betriebsprofile
CREATE TABLE IF NOT EXISTS crm_betriebsprofile (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    betriebsform VARCHAR(100),
    flaeche_ha NUMERIC(10, 2),
    tierbestand INTEGER,
    contact_id VARCHAR(36) REFERENCES crm_contacts(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(36) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_crm_betriebsprofile_name ON crm_betriebsprofile(name);
CREATE INDEX IF NOT EXISTS idx_crm_betriebsprofile_tenant ON crm_betriebsprofile(tenant_id);

