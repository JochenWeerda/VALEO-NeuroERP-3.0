"""Add VAT codes tables with audit trail

Adds:
- vat_codes: Configurable tax codes for Germany/EU
- vat_codes_audit: Full audit trail for changes
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_vat_codes_20260220'
down_revision = 'add_nutrient_compositions_20260219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vat_codes table
    op.create_table(
        'vat_codes',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_long', sa.String(500), nullable=True),
        sa.Column('category', sa.Enum('DE_INLAND', 'DE_AGR_PAUSCHAL', 'DE_FORST', 'EU_IGL', 'EU_ERWERB', 'EU_OSS', 'EXPORT', 'EXEMPT', name='vatcodecategory'), nullable=False),
        sa.Column('rate', sa.Float, nullable=False),
        sa.Column('skr03_account', sa.String(10), nullable=True),
        sa.Column('skr04_account', sa.String(10), nullable=True),
        sa.Column('valid_from', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('valid_to', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('legal_basis', sa.String(200), nullable=True),
        sa.Column('legal_note', sa.Text, nullable=True),
        sa.Column('is_standard', sa.Boolean, default=False),
        sa.Column('is_reduced', sa.Boolean, default=False),
        sa.Column('is_zero', sa.Boolean, default=False),
        sa.Column('is_reverse_charge', sa.Boolean, default=False),
        sa.Column('is_agricultural', sa.Boolean, default=False),
        sa.Column('paragraph_24', sa.Boolean, default=False),
        sa.Column('tenant_id', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.String(100), nullable=True),
    )
    
    # Create audit table
    op.create_table(
        'vat_codes_audit',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('vat_code_id', sa.String(50), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=True),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('changed_by', sa.String(100), nullable=False),
        sa.Column('changed_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('legal_reference', sa.String(200), nullable=True),
        sa.Column('tenant_id', sa.String(50), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_vat_codes_category', 'vat_codes', ['category'])
    op.create_index('ix_vat_codes_tenant', 'vat_codes', ['tenant_id'])
    op.create_index('ix_vat_codes_is_active', 'vat_codes', ['is_active'])
    op.create_index('ix_vat_codes_audit_vat_code', 'vat_codes_audit', ['vat_code_id'])
    op.create_index('ix_vat_codes_audit_changed_at', 'vat_codes_audit', ['changed_at'])
    
    # Seed default VAT codes
    op.execute("""
        INSERT INTO vat_codes (id, name, name_long, category, rate, skr03_account, skr04_account, legal_basis, is_standard, is_reduced, is_zero, is_reverse_charge, is_agricultural, paragraph_24, is_active, tenant_id, created_by)
        VALUES 
        ('DE_19', 'USt 19%', 'Umsatzsteuer 19% Regelsteuersatz', 'DE_INLAND', 19.0, '1776', '1776', '§ 12 Abs. 1 UStG', true, false, false, false, false, false, true, NULL, 'system'),
        ('DE_7', 'USt 7%', 'Umsatzsteuer 7% ermäßigter Steuersatz', 'DE_INLAND', 7.0, '1771', '1771', '§ 12 Abs. 2 UStG Anlage 2', false, true, false, false, false, false, true, NULL, 'system'),
        ('DE_AGR_24_78', 'Durchschnittssatz 7,8%', 'Landwirtschaftlicher Durchschnittssatz §24 UStG', 'DE_AGR_PAUSCHAL', 7.8, '1773', '1773', '§ 24 Nr. 1 UStG', false, false, false, false, true, true, true, NULL, 'system'),
        ('DE_FORST_24_55', 'Forstwirtschaft 5,5%', 'Forstwirtschaftlicher Durchschnittssatz §24 Nr. 2 UStG', 'DE_FORST', 5.5, '1774', '1774', '§ 24 Nr. 2 UStG', false, false, false, false, true, true, true, NULL, 'system'),
        ('DE_AGR_24_19', '§24 Lieferungen 19%', 'Bestimmte Lieferungen nach §24 UStG', 'DE_AGR_PAUSCHAL', 19.0, '1776', '1776', '§ 24 Nr. 3 UStG', false, false, false, false, true, true, true, NULL, 'system'),
        ('DE_0', '0% USt', 'Steuerfreie Lieferung (0%)', 'EXEMPT', 0.0, NULL, NULL, '§ 4 UStG', false, false, true, false, false, false, true, NULL, 'system'),
        ('EU_IGL_0', 'IG Lieferung 0%', 'Innergemeinschaftliche Lieferung §6a UStG', 'EU_IGL', 0.0, NULL, NULL, '§ 6a UStG', false, false, true, false, false, false, true, NULL, 'system'),
        ('EU_ACQ_19', 'IG Erwerb 19%', 'Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge)', 'EU_ERWERB', 19.0, '1776', '1776', '§ 1a UStG', false, false, false, true, false, false, true, NULL, 'system'),
        ('EU_ACQ_7', 'IG Erwerb 7%', 'Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge) 7%', 'EU_ERWERB', 7.0, '1771', '1771', '§ 1a UStG', false, false, false, true, false, false, true, NULL, 'system'),
        ('EXPORT_0', 'Export 0%', 'Ausfuhrlieferung §4 Nr. 1a UStG', 'EXPORT', 0.0, NULL, NULL, '§ 4 Nr. 1a UStG', false, false, true, false, false, false, true, NULL, 'system')
    """.replace('§', '§').replace('§', '§'))


def downgrade() -> None:
    op.drop_table('vat_codes_audit')
    op.drop_table('vat_codes')
    op.execute("DROP TYPE vatcodecategory")
