-- Migration: Knowledge Improvement Proposals
-- Version: 003
-- Date: 2026-03-19

CREATE SCHEMA IF NOT EXISTS domain_shared;

CREATE TABLE IF NOT EXISTS domain_shared.knowledge_improvement_proposals (
    proposal_id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
    target_knowledge_id VARCHAR NULL REFERENCES domain_shared.knowledge_objects(knowledge_id) ON DELETE SET NULL,
    titel VARCHAR(255) NOT NULL,
    typ VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'EINGEREICHT',
    beschreibung TEXT NOT NULL DEFAULT '',
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    zielrollen JSONB NOT NULL DEFAULT '[]'::jsonb,
    format VARCHAR(32) NOT NULL,
    inhalt TEXT NOT NULL,
    strukturierte_daten JSONB NOT NULL DEFAULT '{}'::jsonb,
    quelle VARCHAR(255) NOT NULL DEFAULT 'improvement-workflow',
    vorgeschlagen_von_typ VARCHAR(32) NOT NULL DEFAULT 'human',
    vorgeschlagen_von_ref VARCHAR(255) NOT NULL DEFAULT 'unknown',
    vorgeschlagen_von_rolle VARCHAR(128) NULL,
    kanal VARCHAR(32) NULL,
    begruendung TEXT NOT NULL DEFAULT '',
    reviewer_ref VARCHAR(255) NULL,
    reviewer_rolle VARCHAR(128) NULL,
    review_notiz TEXT NULL,
    reviewed_at TIMESTAMPTZ NULL,
    applied_knowledge_id VARCHAR NULL,
    applied_version INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_tenant
    ON domain_shared.knowledge_improvement_proposals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_target
    ON domain_shared.knowledge_improvement_proposals(target_knowledge_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_status
    ON domain_shared.knowledge_improvement_proposals(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_typ
    ON domain_shared.knowledge_improvement_proposals(typ);
CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_tags_gin
    ON domain_shared.knowledge_improvement_proposals USING GIN(tags);
