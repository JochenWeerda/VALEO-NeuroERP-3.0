"""add missing domain_erp finance tables and compatibility columns

Revision ID: d1e2f3a4b5c6
Revises: c6d7e8f9a0b1
Create Date: 2026-03-04 16:55:00
"""

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "d1e2f3a4b5c6"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


def _create_table(sql: str) -> None:
    op.execute(text(sql))


def _create_index(sql: str) -> None:
    op.execute(text(sql))


def _add_column_if_missing(table: str, col: str, definition: str) -> None:
    op.execute(
        text(
            f"""
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema='domain_erp' AND table_name='{table}' AND column_name='{col}'
              ) THEN
                ALTER TABLE domain_erp.{table} ADD COLUMN {col} {definition};
              END IF;
            END
            $$;
            """
        )
    )


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approval_rules (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            conditions JSONB,
            required_approvals INTEGER NOT NULL DEFAULT 1,
            approval_roles JSONB,
            priority INTEGER NOT NULL DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approval_requests (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            invoice_id VARCHAR(64) NOT NULL,
            requested_by VARCHAR(128),
            required_approvals INTEGER NOT NULL DEFAULT 1,
            applicable_rule JSONB,
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            comment TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approvals (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            request_id VARCHAR(64) NOT NULL,
            approved_by VARCHAR(128) NOT NULL,
            action VARCHAR(16) NOT NULL,
            comment TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.matching_rules (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            rule_name VARCHAR(100) NOT NULL,
            priority INTEGER NOT NULL DEFAULT 0,
            match_type VARCHAR(32) NOT NULL,
            conditions JSONB,
            confidence_threshold NUMERIC(5,4) NOT NULL DEFAULT 0.8,
            auto_apply BOOLEAN NOT NULL DEFAULT TRUE,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.bank_matches (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            statement_line_id VARCHAR(64) NOT NULL,
            op_id VARCHAR(64),
            confidence NUMERIC(5,4) NOT NULL DEFAULT 1.0,
            match_type VARCHAR(32),
            auto_matched BOOLEAN NOT NULL DEFAULT FALSE,
            matched_at TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.booking_templates (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'GENERAL',
            trigger_type VARCHAR(32) DEFAULT 'MANUAL',
            trigger_config JSONB,
            lines JSONB,
            default_amount NUMERIC(15,2),
            currency VARCHAR(3) DEFAULT 'EUR',
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_rules (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            level INTEGER NOT NULL,
            days_overdue_min INTEGER NOT NULL DEFAULT 0,
            days_overdue_max INTEGER,
            fee_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            fee_percentage NUMERIC(7,4) NOT NULL DEFAULT 0,
            interest_rate NUMERIC(7,4) NOT NULL DEFAULT 0,
            payment_deadline_days INTEGER NOT NULL DEFAULT 14,
            block_customer BOOLEAN NOT NULL DEFAULT FALSE,
            escalate_to_collection BOOLEAN NOT NULL DEFAULT FALSE,
            description_template TEXT,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_notices (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            op_id VARCHAR(64),
            debtor_id VARCHAR(64),
            dunning_level INTEGER NOT NULL DEFAULT 1,
            dunning_date DATE NOT NULL,
            due_date DATE,
            open_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            dunning_fee NUMERIC(15,2) NOT NULL DEFAULT 0,
            interest NUMERIC(15,2) NOT NULL DEFAULT 0,
            total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            payment_deadline DATE,
            status VARCHAR(32) NOT NULL DEFAULT 'created',
            sent_date DATE,
            payment_date DATE,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_runs (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            run_number VARCHAR(50) NOT NULL,
            execution_date DATE NOT NULL,
            initiator_name VARCHAR(255) NOT NULL,
            initiator_iban VARCHAR(34) NOT NULL,
            initiator_bic VARCHAR(11),
            total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            payment_count INTEGER NOT NULL DEFAULT 0,
            status VARCHAR(32) NOT NULL DEFAULT 'draft',
            approved_at TIMESTAMPTZ,
            approved_by VARCHAR(128),
            executed_at TIMESTAMPTZ,
            sepa_file_id VARCHAR(128),
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_run_items (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            payment_run_id VARCHAR(64) NOT NULL,
            creditor_id VARCHAR(64),
            creditor_name VARCHAR(255),
            iban VARCHAR(34),
            bic VARCHAR(11),
            amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            purpose TEXT,
            op_id VARCHAR(64),
            invoice_number VARCHAR(100),
            discount_used BOOLEAN NOT NULL DEFAULT FALSE,
            discount_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            end_to_end_id VARCHAR(64),
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_returns (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            payment_run_id VARCHAR(64) NOT NULL,
            payment_item_id VARCHAR(64) NOT NULL,
            return_reason VARCHAR(100),
            return_date DATE,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.closing_checklist_templates (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            template_name VARCHAR(100) NOT NULL,
            description TEXT,
            closing_type VARCHAR(32) NOT NULL,
            items JSONB,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.closing_checklists (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            period VARCHAR(7) NOT NULL,
            closing_type VARCHAR(32) NOT NULL,
            template_id VARCHAR(64),
            status VARCHAR(32) NOT NULL DEFAULT 'draft',
            progress_percentage NUMERIC(7,2) NOT NULL DEFAULT 0,
            total_items INTEGER NOT NULL DEFAULT 0,
            completed_items INTEGER NOT NULL DEFAULT 0,
            required_items INTEGER NOT NULL DEFAULT 0,
            completed_required_items INTEGER NOT NULL DEFAULT 0,
            items JSONB,
            completed_at TIMESTAMPTZ,
            completed_by VARCHAR(128),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.tax_keys (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            code VARCHAR(2) NOT NULL,
            bezeichnung VARCHAR(100) NOT NULL,
            steuersatz NUMERIC(7,4) NOT NULL DEFAULT 0,
            ustva_position VARCHAR(10),
            ustva_bezeichnung VARCHAR(200),
            intracom BOOLEAN NOT NULL DEFAULT FALSE,
            export BOOLEAN NOT NULL DEFAULT FALSE,
            reverse_charge BOOLEAN NOT NULL DEFAULT FALSE,
            gueltig_von DATE NOT NULL,
            gueltig_bis DATE,
            notizen TEXT,
            debit_account VARCHAR(20),
            credit_account VARCHAR(20),
            country VARCHAR(2) NOT NULL DEFAULT 'DE',
            region VARCHAR(50),
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.vat_returns (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            period VARCHAR(7) NOT NULL,
            return_type VARCHAR(32) NOT NULL DEFAULT 'monthly',
            taxpayer_name VARCHAR(255),
            tax_id VARCHAR(64),
            vat_id VARCHAR(64),
            total_sales_net NUMERIC(15,2) NOT NULL DEFAULT 0,
            total_input_tax NUMERIC(15,2) NOT NULL DEFAULT 0,
            total_output_tax NUMERIC(15,2) NOT NULL DEFAULT 0,
            vat_payable NUMERIC(15,2) NOT NULL DEFAULT 0,
            positions JSONB,
            status VARCHAR(32) NOT NULL DEFAULT 'draft',
            calculated_at TIMESTAMPTZ,
            validated_at TIMESTAMPTZ,
            submitted_at TIMESTAMPTZ,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.exchange_rates (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC(18,8) NOT NULL,
            valid_from DATE NOT NULL,
            valid_to DATE,
            source VARCHAR(64),
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.offene_posten (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            rechnungsnr VARCHAR(100),
            datum DATE,
            rechnungsdatum DATE,
            booking_date DATE,
            faelligkeit DATE,
            due_date DATE,
            konto_typ VARCHAR(32),
            kunde_id VARCHAR(64),
            kunde_name VARCHAR(255),
            lieferant_id VARCHAR(64),
            lieferant_name VARCHAR(255),
            debtor_id VARCHAR(64),
            creditor_id VARCHAR(64),
            waehrung VARCHAR(3) DEFAULT 'EUR',
            betrag NUMERIC(15,2) DEFAULT 0,
            open_amount NUMERIC(15,2) DEFAULT 0,
            offen NUMERIC(15,2) DEFAULT 0,
            op_status VARCHAR(32),
            op_text TEXT,
            dunning_level INTEGER DEFAULT 0,
            zahlbar BOOLEAN DEFAULT TRUE,
            skonto_prozent NUMERIC(7,4),
            skonto_bis DATE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.open_items (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            typ VARCHAR(32),
            partner_name VARCHAR(255),
            beleg_nummer VARCHAR(100),
            faellig_am DATE,
            offen NUMERIC(15,2) DEFAULT 0,
            waehrung VARCHAR(3) DEFAULT 'EUR',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.business_partners (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            partner_name VARCHAR(255),
            credit_limit NUMERIC(15,2),
            used_credit NUMERIC(15,2),
            currency VARCHAR(3) DEFAULT 'EUR',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.collaterals (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            collateral_type VARCHAR(64),
            description TEXT,
            value NUMERIC(15,2),
            currency VARCHAR(3) DEFAULT 'EUR',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.debitors (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            customer_id VARCHAR(64),
            debitor_number VARCHAR(50),
            name VARCHAR(255),
            address JSONB,
            payment_terms VARCHAR(100),
            credit_limit NUMERIC(15,2) DEFAULT 0,
            current_balance NUMERIC(15,2) DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.debtors (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            name VARCHAR(255),
            blocked BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.pos_transactions (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            source VARCHAR(32),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.pos_transaction_lines (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            transaction_id VARCHAR(64),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.delivery_notes (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            source VARCHAR(32),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.cash_movements (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.serial_numbers (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    _create_table(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.gift_cards (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    _add_column_if_missing("journal_entries", "period", "VARCHAR(7)")
    _add_column_if_missing("journal_entries", "source_user", "VARCHAR(128)")

    _add_column_if_missing("journal_entry_lines", "tenant_id", "VARCHAR(64)")
    _add_column_if_missing("journal_entry_lines", "debit_amount", "NUMERIC(15,2) DEFAULT 0")
    _add_column_if_missing("journal_entry_lines", "credit_amount", "NUMERIC(15,2) DEFAULT 0")
    _add_column_if_missing("journal_entry_lines", "tax_code", "VARCHAR(20)")
    _add_column_if_missing("journal_entry_lines", "profit_center", "VARCHAR(100)")
    _add_column_if_missing("journal_entry_lines", "reference", "VARCHAR(255)")
    _add_column_if_missing("journal_entry_lines", "updated_at", "TIMESTAMPTZ DEFAULT NOW()")

    op.execute(text("UPDATE domain_erp.journal_entry_lines SET debit_amount = COALESCE(debit,0) WHERE debit_amount IS NULL"))
    op.execute(text("UPDATE domain_erp.journal_entry_lines SET credit_amount = COALESCE(credit,0) WHERE credit_amount IS NULL"))
    op.execute(text("UPDATE domain_erp.journal_entries SET period = TO_CHAR(entry_date, 'YYYY-MM') WHERE period IS NULL AND entry_date IS NOT NULL"))

    for tbl in [
        "ap_approval_rules","ap_approval_requests","ap_approvals","matching_rules","bank_matches",
        "booking_templates","dunning_rules","dunning_notices","payment_runs","payment_run_items",
        "payment_returns","closing_checklist_templates","closing_checklists","tax_keys","vat_returns",
        "exchange_rates","offene_posten","open_items","business_partners","collaterals","debitors",
        "debtors","pos_transactions","pos_transaction_lines","delivery_notes","cash_movements",
        "serial_numbers","gift_cards"
    ]:
        _create_index(f"CREATE INDEX IF NOT EXISTS ix_{tbl}_tenant_id ON domain_erp.{tbl} (tenant_id)")

    _create_index("CREATE UNIQUE INDEX IF NOT EXISTS uq_tax_keys_tenant_code ON domain_erp.tax_keys (tenant_id, code)")
    _create_index("CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_runs_tenant_run_number ON domain_erp.payment_runs (tenant_id, run_number)")


def downgrade() -> None:
    # Recovery migration: keep downgrade non-destructive for safety.
    pass
