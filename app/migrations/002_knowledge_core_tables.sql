-- Migration: Central Knowledge Core Tables
-- Version: 002
-- Date: 2026-03-19

CREATE SCHEMA IF NOT EXISTS domain_shared;

CREATE TABLE IF NOT EXISTS domain_shared.knowledge_objects (
    knowledge_id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
    titel VARCHAR(255) NOT NULL,
    typ VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    beschreibung TEXT NOT NULL DEFAULT '',
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    zielrollen JSONB NOT NULL DEFAULT '[]'::jsonb,
    agentenfreigabe BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domain_shared.knowledge_versions (
    id VARCHAR PRIMARY KEY,
    knowledge_id VARCHAR NOT NULL REFERENCES domain_shared.knowledge_objects(knowledge_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    format VARCHAR(32) NOT NULL,
    inhalt TEXT NOT NULL,
    strukturierte_daten JSONB NOT NULL DEFAULT '{}'::jsonb,
    quelle VARCHAR(255) NOT NULL DEFAULT 'system',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_knowledge_object_version UNIQUE (knowledge_id, version)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_objects_tenant ON domain_shared.knowledge_objects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_typ ON domain_shared.knowledge_objects(typ);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_status ON domain_shared.knowledge_objects(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_tags_gin ON domain_shared.knowledge_objects USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_zielrollen_gin ON domain_shared.knowledge_objects USING GIN(zielrollen);
CREATE INDEX IF NOT EXISTS idx_knowledge_versions_lookup ON domain_shared.knowledge_versions(knowledge_id, version DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_versions_payload_gin ON domain_shared.knowledge_versions USING GIN(strukturierte_daten);
