"""Join the independently delivered HR and tax-account migration branches."""
revision = "merge_hr_tax_20261019"
down_revision = ("hr_employee_files_20261019", "tax_account_category_20261019")
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
