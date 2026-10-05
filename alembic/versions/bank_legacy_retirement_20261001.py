"""Remove the competing bank model and its development-only legacy records.

Revision ID: bank_legacy_retirement_20261001
Revises: steuernachweis_mandant_20261001

Explicit user authorization 2026-10-01: development phase, all legacy data may
be removed. No archive or compatibility adapter. domain_erp is canonical.
Never re-import or re-match old rows: original currency/source/audit are absent.
No CASCADE: unknown external dependencies must abort the whole migration.
"""
from alembic import op

revision = 'bank_legacy_retirement_20261001'
down_revision = 'steuernachweis_mandant_20261001'
branch_labels = None
depends_on = None

UPGRADE_SQL = (
    """DO $$ BEGIN
        IF to_regclass('domain_erp.bank_statements') IS NULL
           OR to_regclass('domain_erp.bank_statement_lines') IS NULL THEN
            RAISE EXCEPTION 'Canonical bank model is required before legacy retirement';
        END IF;
        IF to_regclass('domain_finance.bank_statements') IS NULL
           OR to_regclass('domain_finance.bank_statement_lines') IS NULL THEN
            RAISE EXCEPTION 'Both legacy bank source tables are required';
        END IF;
    END $$""",
    'LOCK TABLE domain_finance.bank_statements, domain_finance.bank_statement_lines IN ACCESS EXCLUSIVE MODE',
    'DROP TABLE domain_finance.bank_statement_lines',
    'DROP TABLE domain_finance.bank_statements',
)


def upgrade():
    for statement in UPGRADE_SQL:
        op.execute(statement)


def downgrade():
    raise RuntimeError('Development bank legacy retirement is irreversible; restore an explicit backup instead')
