"""Basis des CRM GDPR-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen: sie wichen von den Modellen ab (IDs
varchar statt uuid, Enum-Spalten als varchar, abweichende Tabellen). Indizes, die nur die
Altkette kannte, sind in die Modelle uebernommen. Eigene Versionstabelle siehe env.py.

Revision ID: crm_gdpr_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "crm_gdpr_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_gdpr_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('request_type', sa.Enum('ACCESS', 'DELETION', 'PORTABILITY', 'OBJECTION', name='gdprrequesttype'), nullable=False),
    sa.Column('contact_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'CANCELLED', name='gdprrequeststatus'), nullable=False),
    sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('requested_by', sa.String(length=255), nullable=False),
    sa.Column('is_self_request', sa.Boolean(), nullable=False),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('verification_method', sa.Enum('EMAIL', 'ID_CARD', 'MANUAL', 'OTHER', name='verificationmethod'), nullable=True),
    sa.Column('verification_token', sa.UUID(), nullable=True),
    sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('response_file_path', sa.String(length=512), nullable=True),
    sa.Column('response_file_format', sa.String(length=10), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_gdpr_requests_contact_id'), 'crm_gdpr_requests', ['contact_id'], unique=False)
    op.create_index(op.f('ix_crm_gdpr_requests_request_type'), 'crm_gdpr_requests', ['request_type'], unique=False)
    op.create_index(op.f('ix_crm_gdpr_requests_status'), 'crm_gdpr_requests', ['status'], unique=False)
    op.create_index(op.f('ix_crm_gdpr_requests_tenant_id'), 'crm_gdpr_requests', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_crm_gdpr_requests_verification_token'), 'crm_gdpr_requests', ['verification_token'], unique=True)
    op.create_table('crm_privacy_erasure_audit',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('gdpr_request_id', sa.UUID(), nullable=True),
    sa.Column('decision_id', sa.UUID(), nullable=True),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('subject_ref', sa.String(length=255), nullable=False),
    sa.Column('actor_id', sa.String(length=255), nullable=True),
    sa.Column('policy_version', sa.String(length=128), nullable=False),
    sa.Column('decision', sa.String(length=64), nullable=True),
    sa.Column('reason_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('allowed_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('blocked_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('executed_action', sa.String(length=128), nullable=True),
    sa.Column('result', sa.String(length=64), nullable=False),
    sa.Column('correlation_id', sa.String(length=128), nullable=False),
    sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_privacy_erasure_audit_decision_id'), 'crm_privacy_erasure_audit', ['decision_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_audit_gdpr_request_id'), 'crm_privacy_erasure_audit', ['gdpr_request_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_audit_tenant_id'), 'crm_privacy_erasure_audit', ['tenant_id'], unique=False)
    op.create_index('ix_privacy_erasure_audit_request_created', 'crm_privacy_erasure_audit', ['gdpr_request_id', 'created_at'], unique=False)
    op.create_table('crm_privacy_erasure_decisions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('gdpr_request_id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('subject_id', sa.UUID(), nullable=False),
    sa.Column('decision', sa.String(length=64), nullable=False),
    sa.Column('allowed_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('blocked_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('reasons', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('policy_version', sa.String(length=128), nullable=False),
    sa.Column('requires_manual_review', sa.Boolean(), nullable=False),
    sa.Column('anonymize_only', sa.Boolean(), nullable=False),
    sa.Column('correlation_id_evaluate', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_privacy_erasure_decisions_expires_at'), 'crm_privacy_erasure_decisions', ['expires_at'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_decisions_gdpr_request_id'), 'crm_privacy_erasure_decisions', ['gdpr_request_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_decisions_subject_id'), 'crm_privacy_erasure_decisions', ['subject_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_decisions_tenant_id'), 'crm_privacy_erasure_decisions', ['tenant_id'], unique=False)
    op.create_index('ix_privacy_erasure_decision_tenant_req', 'crm_privacy_erasure_decisions', ['tenant_id', 'gdpr_request_id'], unique=False)
    op.create_table('crm_privacy_erasure_executions',
    sa.Column('idempotency_key', sa.String(length=512), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('gdpr_request_id', sa.UUID(), nullable=False),
    sa.Column('subject_id', sa.UUID(), nullable=False),
    sa.Column('decision_id', sa.UUID(), nullable=False),
    sa.Column('action', sa.String(length=128), nullable=False),
    sa.Column('anonymize_only', sa.Boolean(), nullable=False),
    sa.Column('erasure_log', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('correlation_id', sa.String(length=128), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('idempotency_key')
    )
    op.create_index(op.f('ix_crm_privacy_erasure_executions_decision_id'), 'crm_privacy_erasure_executions', ['decision_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_executions_gdpr_request_id'), 'crm_privacy_erasure_executions', ['gdpr_request_id'], unique=False)
    op.create_index(op.f('ix_crm_privacy_erasure_executions_tenant_id'), 'crm_privacy_erasure_executions', ['tenant_id'], unique=False)
    op.create_index('ix_privacy_erasure_exec_gate', 'crm_privacy_erasure_executions', ['tenant_id', 'gdpr_request_id', 'subject_id'], unique=False)
    op.create_table('crm_gdpr_request_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('request_id', sa.UUID(), nullable=False),
    sa.Column('action', sa.Enum('CREATED', 'STATUS_CHANGED', 'VERIFIED', 'DATA_EXPORTED', 'DATA_DELETED', 'REJECTED', 'CANCELLED', name='gdprrequesthistoryaction'), nullable=False),
    sa.Column('old_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'CANCELLED', name='gdprrequeststatus'), nullable=True),
    sa.Column('new_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'CANCELLED', name='gdprrequeststatus'), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('changed_by', sa.String(length=255), nullable=False),
    sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['request_id'], ['crm_gdpr_requests.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_gdpr_request_history_changed_at'), 'crm_gdpr_request_history', ['changed_at'], unique=False)
    op.create_index(op.f('ix_crm_gdpr_request_history_request_id'), 'crm_gdpr_request_history', ['request_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crm_gdpr_request_history_request_id'), table_name='crm_gdpr_request_history')
    op.drop_index(op.f('ix_crm_gdpr_request_history_changed_at'), table_name='crm_gdpr_request_history')
    op.drop_table('crm_gdpr_request_history')
    op.drop_index('ix_privacy_erasure_exec_gate', table_name='crm_privacy_erasure_executions')
    op.drop_index(op.f('ix_crm_privacy_erasure_executions_tenant_id'), table_name='crm_privacy_erasure_executions')
    op.drop_index(op.f('ix_crm_privacy_erasure_executions_gdpr_request_id'), table_name='crm_privacy_erasure_executions')
    op.drop_index(op.f('ix_crm_privacy_erasure_executions_decision_id'), table_name='crm_privacy_erasure_executions')
    op.drop_table('crm_privacy_erasure_executions')
    op.drop_index('ix_privacy_erasure_decision_tenant_req', table_name='crm_privacy_erasure_decisions')
    op.drop_index(op.f('ix_crm_privacy_erasure_decisions_tenant_id'), table_name='crm_privacy_erasure_decisions')
    op.drop_index(op.f('ix_crm_privacy_erasure_decisions_subject_id'), table_name='crm_privacy_erasure_decisions')
    op.drop_index(op.f('ix_crm_privacy_erasure_decisions_gdpr_request_id'), table_name='crm_privacy_erasure_decisions')
    op.drop_index(op.f('ix_crm_privacy_erasure_decisions_expires_at'), table_name='crm_privacy_erasure_decisions')
    op.drop_table('crm_privacy_erasure_decisions')
    op.drop_index('ix_privacy_erasure_audit_request_created', table_name='crm_privacy_erasure_audit')
    op.drop_index(op.f('ix_crm_privacy_erasure_audit_tenant_id'), table_name='crm_privacy_erasure_audit')
    op.drop_index(op.f('ix_crm_privacy_erasure_audit_gdpr_request_id'), table_name='crm_privacy_erasure_audit')
    op.drop_index(op.f('ix_crm_privacy_erasure_audit_decision_id'), table_name='crm_privacy_erasure_audit')
    op.drop_table('crm_privacy_erasure_audit')
    op.drop_index(op.f('ix_crm_gdpr_requests_verification_token'), table_name='crm_gdpr_requests')
    op.drop_index(op.f('ix_crm_gdpr_requests_tenant_id'), table_name='crm_gdpr_requests')
    op.drop_index(op.f('ix_crm_gdpr_requests_status'), table_name='crm_gdpr_requests')
    op.drop_index(op.f('ix_crm_gdpr_requests_request_type'), table_name='crm_gdpr_requests')
    op.drop_index(op.f('ix_crm_gdpr_requests_contact_id'), table_name='crm_gdpr_requests')
    op.drop_table('crm_gdpr_requests')
    sa.Enum(name='gdprrequesthistoryaction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gdprrequeststatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gdprrequesttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='verificationmethod').drop(op.get_bind(), checkfirst=True)
