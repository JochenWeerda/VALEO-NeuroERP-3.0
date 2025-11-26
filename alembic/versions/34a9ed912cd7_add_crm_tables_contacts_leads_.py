"""Add CRM tables - contacts, leads, activities, betriebsprofile

Revision ID: 34a9ed912cd7
Revises: 519e0d90cd66
Create Date: 2025-10-16 22:16:57.884256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34a9ed912cd7'
down_revision: Union[str, None] = '519e0d90cd66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CRM Contacts
    op.create_table(
        'crm_contacts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('company', sa.String(255), nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('phone', sa.String(50)),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('address_street', sa.String(255)),
        sa.Column('address_zip', sa.String(10)),
        sa.Column('address_city', sa.String(100)),
        sa.Column('address_country', sa.String(100)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True)
    )
    
    # CRM Leads
    op.create_table(
        'crm_leads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company', sa.String(255), nullable=False, index=True),
        sa.Column('contact_person', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('source', sa.String(100)),
        sa.Column('potential', sa.Numeric(12, 2), default=0),
        sa.Column('priority', sa.String(20)),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('assigned_to', sa.String(100)),
        sa.Column('expected_close_date', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True)
    )
    
    # CRM Activities
    op.create_table(
        'crm_activities',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('contact_id', sa.String(36), sa.ForeignKey('crm_contacts.id'), index=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('subject', sa.String(255)),
        sa.Column('notes', sa.Text),
        sa.Column('status', sa.String(20)),
        sa.Column('created_by', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True)
    )
    
    # CRM Betriebsprofile
    op.create_table(
        'crm_betriebsprofile',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('betriebsform', sa.String(100)),
        sa.Column('flaeche_ha', sa.Numeric(10, 2)),
        sa.Column('tierbestand', sa.Integer),
        sa.Column('contact_id', sa.String(36), sa.ForeignKey('crm_contacts.id')),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True)
    )


def downgrade() -> None:
    op.drop_table('crm_betriebsprofile')
    op.drop_table('crm_activities')
    op.drop_table('crm_leads')
    op.drop_table('crm_contacts')
