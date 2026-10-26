"""Basis des CRM Consent-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen: sie wichen von den Modellen ab (IDs
varchar statt uuid, Enum-Spalten als varchar, abweichende Tabellen). Indizes, die nur die
Altkette kannte, sind in die Modelle uebernommen. Eigene Versionstabelle siehe env.py.

Revision ID: crm_consent_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_consent_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_consent_consents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('contact_id', sa.UUID(), nullable=False),
    sa.Column('channel', sa.Enum('EMAIL', 'SMS', 'PHONE', 'POSTAL', name='consentchannel'), nullable=False),
    sa.Column('consent_type', sa.Enum('MARKETING', 'SERVICE', 'REQUIRED', name='consenttype'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'GRANTED', 'DENIED', 'REVOKED', name='consentstatus'), nullable=False),
    sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('denied_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('double_opt_in_token', sa.UUID(), nullable=True),
    sa.Column('double_opt_in_confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('source', sa.Enum('WEB_FORM', 'API', 'IMPORT', 'MANUAL', name='consentsource'), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_consent_consents_channel'), 'crm_consent_consents', ['channel'], unique=False)
    op.create_index(op.f('ix_crm_consent_consents_contact_id'), 'crm_consent_consents', ['contact_id'], unique=False)
    op.create_index(op.f('ix_crm_consent_consents_double_opt_in_token'), 'crm_consent_consents', ['double_opt_in_token'], unique=True)
    op.create_index(op.f('ix_crm_consent_consents_status'), 'crm_consent_consents', ['status'], unique=False)
    op.create_index(op.f('ix_crm_consent_consents_tenant_id'), 'crm_consent_consents', ['tenant_id'], unique=False)
    op.create_table('crm_consent_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('consent_id', sa.UUID(), nullable=False),
    sa.Column('action', sa.Enum('GRANTED', 'DENIED', 'REVOKED', 'UPDATED', name='consenthistoryaction'), nullable=False),
    sa.Column('old_status', sa.Enum('PENDING', 'GRANTED', 'DENIED', 'REVOKED', name='consentstatus'), nullable=True),
    sa.Column('new_status', sa.Enum('PENDING', 'GRANTED', 'DENIED', 'REVOKED', name='consentstatus'), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('changed_by', sa.String(length=255), nullable=False),
    sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['consent_id'], ['crm_consent_consents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_consent_history_changed_at'), 'crm_consent_history', ['changed_at'], unique=False)
    op.create_index(op.f('ix_crm_consent_history_consent_id'), 'crm_consent_history', ['consent_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crm_consent_history_consent_id'), table_name='crm_consent_history')
    op.drop_index(op.f('ix_crm_consent_history_changed_at'), table_name='crm_consent_history')
    op.drop_table('crm_consent_history')
    op.drop_index(op.f('ix_crm_consent_consents_tenant_id'), table_name='crm_consent_consents')
    op.drop_index(op.f('ix_crm_consent_consents_status'), table_name='crm_consent_consents')
    op.drop_index(op.f('ix_crm_consent_consents_double_opt_in_token'), table_name='crm_consent_consents')
    op.drop_index(op.f('ix_crm_consent_consents_contact_id'), table_name='crm_consent_consents')
    op.drop_index(op.f('ix_crm_consent_consents_channel'), table_name='crm_consent_consents')
    op.drop_table('crm_consent_consents')
    sa.Enum(name='consentchannel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='consenthistoryaction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='consentsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='consentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='consenttype').drop(op.get_bind(), checkfirst=True)
