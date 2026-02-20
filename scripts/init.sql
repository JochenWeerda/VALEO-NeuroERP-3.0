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

-- Keycloak DB erstellen (wenn nicht vorhanden)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'keycloak') THEN
    CREATE DATABASE keycloak OWNER keycloak;
  END IF;
END $$;

-- Sicherheitshalber: Rechte setzen (OWNER reicht meist, aber ist ok)
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
