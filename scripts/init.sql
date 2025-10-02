-- VALEO-NeuroERP Database Initialization
-- This script runs on first database startup

-- Create development database if it doesn't exist
-- (Already created via POSTGRES_DB environment variable)

-- Create additional roles for different environments
CREATE ROLE valeo_readonly;
CREATE ROLE valeo_app;
CREATE ROLE valeo_migration;

-- Grant permissions
GRANT CONNECT ON DATABASE valeo_neuro_erp TO valeo_readonly;
GRANT CONNECT ON DATABASE valeo_neuro_erp TO valeo_app;
GRANT CONNECT ON DATABASE valeo_neuro_erp TO valeo_migration;

-- Create schemas for clean architecture
CREATE SCHEMA IF NOT EXISTS domain AUTHORIZATION valeo_dev;
CREATE SCHEMA IF NOT EXISTS infrastructure AUTHORIZATION valeo_dev;
CREATE SCHEMA IF NOT EXISTS shared AUTHORIZATION valeo_dev;

-- Grant schema permissions
GRANT USAGE ON SCHEMA domain TO valeo_readonly, valeo_app, valeo_migration;
GRANT USAGE ON SCHEMA infrastructure TO valeo_readonly, valeo_app, valeo_migration;
GRANT USAGE ON SCHEMA shared TO valeo_readonly, valeo_app, valeo_migration;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";

-- Create audit trigger function for data integrity
CREATE OR REPLACE FUNCTION audit_trigger_function() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'VALEO-NeuroERP database initialized successfully';
END $$;