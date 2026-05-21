-- scripts/init.sql (DEV)
-- Läuft nur beim ersten Start bei leerem Volume

\connect valeo_neuro_erp;

-- Extensions für eure App-DB
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- Keycloak Role erstellen (wenn nicht vorhanden)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'keycloak') THEN
    CREATE ROLE keycloak WITH LOGIN PASSWORD 'keycloak_dev_2024';
  END IF;
END $$;

-- Keycloak DB erstellen (wenn nicht vorhanden).
-- CREATE DATABASE darf nicht in einem DO/Transaktionsblock laufen.
SELECT 'CREATE DATABASE keycloak OWNER keycloak'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'keycloak')
\gexec

-- Sicherheitshalber: Rechte setzen (OWNER reicht meist, aber ist ok)
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;

-- Domain Schemas für Multi-Schema Design
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_erp;
CREATE SCHEMA IF NOT EXISTS domain_finance;
CREATE SCHEMA IF NOT EXISTS domain_ops;
CREATE SCHEMA IF NOT EXISTS domain_portal;
CREATE SCHEMA IF NOT EXISTS domain_log;
CREATE SCHEMA IF NOT EXISTS domain_agrar;
