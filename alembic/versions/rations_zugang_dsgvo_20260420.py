"""rations_zugang DSGVO access control table

Revision ID: rations_zugang_dsgvo_20260420
Revises:
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'rations_zugang_dsgvo_20260420'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.create_table(
        'rations_zugang',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('empfaenger_email', sa.String(255), nullable=False),
        sa.Column('empfaenger_name', sa.String(255), nullable=True),
        sa.Column('zugang_typ', sa.String(50), nullable=False, server_default='portal_user'),
        sa.Column('share_token', sa.String(64), nullable=True, unique=True),
        sa.Column('gueltig_ab', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('gueltig_bis', sa.DateTime(timezone=True), nullable=True),
        sa.Column('darf_lesen', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('darf_rationen_anlegen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('darf_grundfutter_anlegen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('darf_zugang_verwalten', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('gesperrt_am', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gesperrt_durch', sa.String(255), nullable=True),
        sa.Column('sperrgrund', sa.Text(), nullable=True),
        sa.Column('erstellt_von_email', sa.String(255), nullable=False),
        sa.Column('erstellt_von_name', sa.String(255), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_shared',
    )
    op.create_index('ix_rz_tenant', 'rations_zugang', ['tenant_id'], schema='domain_shared')
    op.create_index('ix_rz_token', 'rations_zugang', ['share_token'], schema='domain_shared')
    op.create_index('ix_rz_email', 'rations_zugang', ['empfaenger_email'], schema='domain_shared')


def downgrade() -> None:
    op.drop_index('ix_rz_email', 'rations_zugang', schema='domain_shared')
    op.drop_index('ix_rz_token', 'rations_zugang', schema='domain_shared')
    op.drop_index('ix_rz_tenant', 'rations_zugang', schema='domain_shared')
    op.drop_table('rations_zugang', schema='domain_shared')
