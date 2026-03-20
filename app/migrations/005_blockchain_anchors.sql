CREATE TABLE IF NOT EXISTS domain_shared.blockchain_anchors (
    anchor_id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
    subject_type VARCHAR(64) NOT NULL,
    subject_ref VARCHAR(255) NOT NULL,
    network_profile VARCHAR(64) NOT NULL,
    payload_hash_algorithm VARCHAR(32) NOT NULL DEFAULT 'SHA-256',
    canonical_payload_hash VARCHAR(64) NOT NULL,
    private_payload_hash VARCHAR(64),
    anchor_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    adapter_hint JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(32) NOT NULL DEFAULT 'prepared',
    evidence_ref TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_tenant_created
    ON domain_shared.blockchain_anchors (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_subject
    ON domain_shared.blockchain_anchors (subject_type, subject_ref);

CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_network
    ON domain_shared.blockchain_anchors (network_profile, status);

CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_payload_hash
    ON domain_shared.blockchain_anchors (canonical_payload_hash);
