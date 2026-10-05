-- Initialize Event-Bus Database Schema
-- Outbox Pattern & Saga State Management

-- Outbox Table for Transactional Messaging
CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(200) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    payload TEXT NOT NULL,
    metadata JSONB,
    tenant_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    INDEX idx_outbox_published (published_at) WHERE published_at IS NULL,
    INDEX idx_outbox_created (created_at),
    INDEX idx_outbox_tenant (tenant_id)
);

-- Saga State Table
CREATE TABLE IF NOT EXISTS saga_state (
    saga_id UUID PRIMARY KEY,
    saga_type VARCHAR(100) NOT NULL,
    current_step VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- STARTED, COMPLETED, COMPENSATING, FAILED
    payload JSONB NOT NULL,
    compensation_data JSONB,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    error TEXT,
    INDEX idx_saga_status (status),
    INDEX idx_saga_type (saga_type),
    INDEX idx_saga_updated (updated_at)
);

-- Saga Step Execution Log
CREATE TABLE IF NOT EXISTS saga_steps (
    id UUID PRIMARY KEY,
    saga_id UUID NOT NULL REFERENCES saga_state(saga_id) ON DELETE CASCADE,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- PENDING, SUCCESS, FAILED, COMPENSATED
    execution_order INTEGER NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    compensated_at TIMESTAMP,
    INDEX idx_saga_steps_saga (saga_id),
    INDEX idx_saga_steps_status (status)
);

-- Event Processing Locks (for distributed workers)
CREATE TABLE IF NOT EXISTS event_locks (
    lock_id VARCHAR(200) PRIMARY KEY,
    locked_by VARCHAR(100) NOT NULL,
    locked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_event_locks_expires (expires_at)
);

-- Idempotency Keys (for exactly-once processing)
CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(200) PRIMARY KEY,
    event_id UUID NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    result JSONB,
    INDEX idx_idempotency_processed (processed_at)
);

-- Create function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for saga_state
CREATE TRIGGER update_saga_state_updated_at BEFORE UPDATE ON saga_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO valeo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO valeo;

