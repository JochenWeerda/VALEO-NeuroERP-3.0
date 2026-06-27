"""FINANCE-HR-EINKAUF-REPAIR-001: Finance + HR + Einkauf Batch-Repair Wave 12.

Tabellen aus Parallel-Alembic-Branches idempotent in der Hauptkette anlegen:

  domain_erp   — ap_approval_rules, ap_approval_requests, ap_approvals,
                 matching_rules, bank_matches, booking_templates,
                 closing_checklist_templates, closing_checklists,
                 tax_keys, vat_returns, offene_posten, open_items,
                 business_partners, collaterals, debitors, debtors,
                 pos_transactions, pos_transaction_lines,
                 delivery_notes (erp-schema), cash_movements,
                 serial_numbers, gift_cards,
                 bank_statements, bank_statement_lines
                 + ADD COLUMN IF NOT EXISTS auf journal_entries und
                   journal_entry_lines

  domain_einkauf — rfq_requests, rfq_quotes

  domain_hr      — shifts

  domain_shared  — zahlungsformulare, zinsgruppen, leergutarten

Revision ID: finance_hr_einkauf_repair_20260626
Revises: finance_agrar_sales_repair_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "finance_hr_einkauf_repair_20260626"
down_revision = "finance_agrar_sales_repair_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    for schema in ("domain_erp", "domain_einkauf", "domain_hr", "domain_shared"):
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    # ════════════════════════════════════════════════════════════════════════
    # domain_erp — AP-Freigabe + Matching + Buchungsvorlagen + Checklisten
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approval_rules (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            min_amount      NUMERIC(15,2),
            max_amount      NUMERIC(15,2),
            required_roles  JSONB           NOT NULL DEFAULT '[]'::jsonb,
            priority        INTEGER         NOT NULL DEFAULT 0,
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ap_approval_rules_tenant
            ON domain_erp.ap_approval_rules (tenant_id, active)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approval_requests (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            rule_id         VARCHAR(64),
            invoice_id      VARCHAR(64),
            amount          NUMERIC(15,2)   NOT NULL DEFAULT 0,
            status          VARCHAR(32)     NOT NULL DEFAULT 'pending',
            requested_by    VARCHAR(128),
            requested_at    TIMESTAMPTZ     DEFAULT NOW(),
            deadline        TIMESTAMPTZ,
            notes           TEXT,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ap_approval_requests_tenant_status
            ON domain_erp.ap_approval_requests (tenant_id, status)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.ap_approvals (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            request_id      VARCHAR(64)     NOT NULL,
            approver_id     VARCHAR(128)    NOT NULL,
            approver_name   VARCHAR(255),
            decision        VARCHAR(16)     NOT NULL,
            decided_at      TIMESTAMPTZ     DEFAULT NOW(),
            comment         TEXT,
            created_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ap_approvals_request
            ON domain_erp.ap_approvals (request_id)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.matching_rules (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            rule_type       VARCHAR(32)     NOT NULL DEFAULT 'exact',
            field_mapping   JSONB           NOT NULL DEFAULT '{}'::jsonb,
            tolerance_pct   NUMERIC(7,4)    NOT NULL DEFAULT 0,
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_matches (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64)     NOT NULL,
            bank_line_id        VARCHAR(64)     NOT NULL,
            op_id               VARCHAR(64),
            invoice_id          VARCHAR(64),
            match_score         NUMERIC(5,4)    NOT NULL DEFAULT 0,
            match_type          VARCHAR(32)     NOT NULL DEFAULT 'manual',
            matched_by          VARCHAR(128),
            matched_at          TIMESTAMPTZ     DEFAULT NOW(),
            amount_diff         NUMERIC(15,2)   NOT NULL DEFAULT 0,
            status              VARCHAR(32)     NOT NULL DEFAULT 'matched',
            created_at          TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    for ddl in [
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS bank_line_id VARCHAR(64)",
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS invoice_id VARCHAR(64)",
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS match_score NUMERIC(5,4) DEFAULT 0",
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS matched_by VARCHAR(128)",
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS amount_diff NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE domain_erp.bank_matches ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'matched'",
    ]:
        conn.execute(text(ddl))
    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp'
                  AND table_name = 'bank_matches'
                  AND column_name = 'statement_line_id'
            ) THEN
                UPDATE domain_erp.bank_matches
                SET bank_line_id = statement_line_id
                WHERE bank_line_id IS NULL AND statement_line_id IS NOT NULL;
            END IF;
        END
        $$
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_bank_matches_bank_line
            ON domain_erp.bank_matches (bank_line_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_bank_matches_tenant_status
            ON domain_erp.bank_matches (tenant_id, status)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.booking_templates (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            description     TEXT,
            template_lines  JSONB           NOT NULL DEFAULT '[]'::jsonb,
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.closing_checklist_templates (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            period_type     VARCHAR(16)     NOT NULL DEFAULT 'monthly',
            items           JSONB           NOT NULL DEFAULT '[]'::jsonb,
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.closing_checklists (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            template_id     VARCHAR(64),
            period_start    DATE            NOT NULL,
            period_end      DATE            NOT NULL,
            status          VARCHAR(32)     NOT NULL DEFAULT 'open',
            completed_by    VARCHAR(128),
            completed_at    TIMESTAMPTZ,
            items           JSONB           NOT NULL DEFAULT '[]'::jsonb,
            notes           TEXT,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    for ddl in [
        "ALTER TABLE domain_erp.closing_checklists ADD COLUMN IF NOT EXISTS period_start DATE",
        "ALTER TABLE domain_erp.closing_checklists ADD COLUMN IF NOT EXISTS period_end DATE",
        "ALTER TABLE domain_erp.closing_checklists ADD COLUMN IF NOT EXISTS completed_by VARCHAR(128)",
        "ALTER TABLE domain_erp.closing_checklists ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ",
        "ALTER TABLE domain_erp.closing_checklists ADD COLUMN IF NOT EXISTS notes TEXT",
    ]:
        conn.execute(text(ddl))
    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp'
                  AND table_name = 'closing_checklists'
                  AND column_name = 'period'
            ) THEN
                UPDATE domain_erp.closing_checklists
                SET period_start = COALESCE(
                        period_start,
                        TO_DATE(period || '-01', 'YYYY-MM-DD')
                    ),
                    period_end = COALESCE(
                        period_end,
                        (TO_DATE(period || '-01', 'YYYY-MM-DD') + INTERVAL '1 month' - INTERVAL '1 day')::date
                    )
                WHERE period IS NOT NULL AND period_start IS NULL;
            END IF;
        END
        $$
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_closing_checklists_tenant_period
            ON domain_erp.closing_checklists (tenant_id, period_start, status)
    """))

    # ── Steuer/USt ────────────────────────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.tax_keys (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            key_code        VARCHAR(20)     NOT NULL,
            description     VARCHAR(255)    NOT NULL,
            tax_rate        NUMERIC(7,4)    NOT NULL DEFAULT 0,
            tax_type        VARCHAR(32)     NOT NULL DEFAULT 'USt',
            account_code    VARCHAR(20),
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_tax_keys_tenant_code UNIQUE (tenant_id, key_code)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.vat_returns (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            period_year     INTEGER         NOT NULL,
            period_month    INTEGER         NOT NULL,
            status          VARCHAR(32)     NOT NULL DEFAULT 'draft',
            submitted_at    TIMESTAMPTZ,
            submitted_by    VARCHAR(128),
            data            JSONB           NOT NULL DEFAULT '{}'::jsonb,
            notes           TEXT,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_vat_returns_tenant_period UNIQUE (tenant_id, period_year, period_month)
        )
    """))

    # ── Offene Posten ─────────────────────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.offene_posten (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            partner_id      VARCHAR(64),
            partner_type    VARCHAR(16)     NOT NULL DEFAULT 'debitor',
            document_type   VARCHAR(32)     NOT NULL,
            document_number VARCHAR(100)    NOT NULL,
            document_date   DATE            NOT NULL,
            due_date        DATE,
            currency        VARCHAR(3)      NOT NULL DEFAULT 'EUR',
            gross_amount    NUMERIC(15,2)   NOT NULL DEFAULT 0,
            open_amount     NUMERIC(15,2)   NOT NULL DEFAULT 0,
            discount_date   DATE,
            discount_amount NUMERIC(15,2)   NOT NULL DEFAULT 0,
            status          VARCHAR(32)     NOT NULL DEFAULT 'open',
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    for ddl in [
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS partner_id VARCHAR(64)",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS partner_type VARCHAR(16) DEFAULT 'debitor'",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS document_type VARCHAR(32) DEFAULT 'invoice'",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS document_number VARCHAR(100)",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS document_date DATE",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS due_date DATE",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'EUR'",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS gross_amount NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS open_amount NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS discount_date DATE",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS discount_amount NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE domain_erp.offene_posten ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'open'",
    ]:
        conn.execute(text(ddl))
    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'op_status'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET status = COALESCE(status, op_status, 'open')
                    WHERE status IS NULL
                $sql$;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'kunde_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET partner_id = COALESCE(partner_id, kunde_id)
                    WHERE partner_id IS NULL
                $sql$;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'debtor_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET partner_id = COALESCE(partner_id, debtor_id)
                    WHERE partner_id IS NULL
                $sql$;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'rechnungsnr'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET document_number = COALESCE(document_number, rechnungsnr)
                    WHERE document_number IS NULL
                $sql$;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'faelligkeit'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET due_date = COALESCE(due_date, faelligkeit)
                    WHERE due_date IS NULL
                $sql$;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'offene_posten'
                  AND column_name = 'offen'
            ) THEN
                EXECUTE $sql$
                    UPDATE domain_erp.offene_posten
                    SET open_amount = COALESCE(open_amount, offen)
                    WHERE open_amount IS NULL
                $sql$;
            END IF;
        END
        $$
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_offene_posten_tenant_status
            ON domain_erp.offene_posten (tenant_id, status, due_date)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_offene_posten_partner
            ON domain_erp.offene_posten (partner_id, partner_type)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.open_items (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            offener_posten_id VARCHAR(64),
            allocation_date DATE,
            allocated_amount NUMERIC(15,2)  NOT NULL DEFAULT 0,
            payment_reference VARCHAR(255),
            cleared_by      VARCHAR(128),
            created_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    # ── Business Partners / Kreditoren / Debitoren ────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.business_partners (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            partner_number  VARCHAR(50)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            partner_type    VARCHAR(32)     NOT NULL DEFAULT 'both',
            vat_id          VARCHAR(30),
            tax_number      VARCHAR(30),
            iban            VARCHAR(34),
            bic             VARCHAR(11),
            payment_terms   INTEGER         NOT NULL DEFAULT 30,
            credit_limit    NUMERIC(15,2),
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_business_partners_tenant_number UNIQUE (tenant_id, partner_number)
        )
    """))
    for ddl in [
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS partner_number VARCHAR(50)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS name VARCHAR(255)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS partner_type VARCHAR(32) DEFAULT 'both'",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS vat_id VARCHAR(30)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS tax_number VARCHAR(30)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS iban VARCHAR(34)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS bic VARCHAR(11)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS payment_terms INTEGER DEFAULT 30",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(15,2)",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()",
        "ALTER TABLE domain_erp.business_partners ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()",
    ]:
        conn.execute(text(ddl))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_business_partners_tenant_active
            ON domain_erp.business_partners (tenant_id, active)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.collaterals (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            partner_id      VARCHAR(64),
            collateral_type VARCHAR(32)     NOT NULL DEFAULT 'guarantee',
            description     VARCHAR(255),
            amount          NUMERIC(15,2)   NOT NULL DEFAULT 0,
            valid_from      DATE,
            valid_to        DATE,
            status          VARCHAR(32)     NOT NULL DEFAULT 'active',
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.debitors (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            debitor_number  VARCHAR(50)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            credit_limit    NUMERIC(15,2),
            payment_terms   INTEGER         NOT NULL DEFAULT 30,
            dunning_level   INTEGER         NOT NULL DEFAULT 0,
            is_blocked      BOOLEAN         NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_debitors_tenant_number UNIQUE (tenant_id, debitor_number)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.debtors (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            debtor_number   VARCHAR(50)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            outstanding     NUMERIC(15,2)   NOT NULL DEFAULT 0,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    # ── POS ───────────────────────────────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.pos_transactions (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            pos_terminal_id VARCHAR(64),
            transaction_date TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
            total_amount    NUMERIC(15,2)   NOT NULL DEFAULT 0,
            payment_method  VARCHAR(32)     NOT NULL DEFAULT 'cash',
            status          VARCHAR(32)     NOT NULL DEFAULT 'completed',
            operator_id     VARCHAR(128),
            customer_id     VARCHAR(64),
            receipt_number  VARCHAR(100),
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text(
        "ALTER TABLE domain_erp.pos_transactions "
        "ADD COLUMN IF NOT EXISTS transaction_date TIMESTAMPTZ DEFAULT NOW()"
    ))
    conn.execute(text("""
        UPDATE domain_erp.pos_transactions
        SET transaction_date = COALESCE(transaction_date, created_at, NOW())
        WHERE transaction_date IS NULL
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_pos_transactions_tenant_date
            ON domain_erp.pos_transactions (tenant_id, transaction_date)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.pos_transaction_lines (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            transaction_id  VARCHAR(64)     NOT NULL,
            article_number  VARCHAR(80),
            description     VARCHAR(255),
            quantity        NUMERIC(12,3)   NOT NULL DEFAULT 1,
            unit_price      NUMERIC(12,4)   NOT NULL DEFAULT 0,
            line_total      NUMERIC(14,2)   NOT NULL DEFAULT 0,
            tax_rate        NUMERIC(7,4)    NOT NULL DEFAULT 0,
            created_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_pos_transaction_lines_transaction
            ON domain_erp.pos_transaction_lines (transaction_id)
    """))

    # ── Delivery Notes (erp schema) + Cash + Serial + Gift ───────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.delivery_notes (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            note_number     VARCHAR(100)    NOT NULL,
            delivery_date   DATE            NOT NULL,
            status          VARCHAR(32)     NOT NULL DEFAULT 'draft',
            total_net       NUMERIC(14,2),
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_erp_delivery_notes_tenant_number UNIQUE (tenant_id, note_number)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.cash_movements (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            pos_terminal_id VARCHAR(64),
            movement_type   VARCHAR(32)     NOT NULL DEFAULT 'in',
            amount          NUMERIC(15,2)   NOT NULL DEFAULT 0,
            currency        VARCHAR(3)      NOT NULL DEFAULT 'EUR',
            reason          VARCHAR(255),
            operator_id     VARCHAR(128),
            created_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_cash_movements_tenant_date
            ON domain_erp.cash_movements (tenant_id, created_at)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.serial_numbers (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            article_number  VARCHAR(80)     NOT NULL,
            serial_number   VARCHAR(100)    NOT NULL,
            status          VARCHAR(32)     NOT NULL DEFAULT 'available',
            batch_id        VARCHAR(64),
            sold_to         VARCHAR(64),
            sold_at         TIMESTAMPTZ,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_serial_numbers_tenant_article_serial
                UNIQUE (tenant_id, article_number, serial_number)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.gift_cards (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            card_number     VARCHAR(100)    NOT NULL,
            initial_value   NUMERIC(12,2)   NOT NULL DEFAULT 0,
            current_balance NUMERIC(12,2)   NOT NULL DEFAULT 0,
            issued_at       TIMESTAMPTZ     DEFAULT NOW(),
            expires_at      TIMESTAMPTZ,
            status          VARCHAR(32)     NOT NULL DEFAULT 'active',
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW(),
            CONSTRAINT uq_gift_cards_tenant_number UNIQUE (tenant_id, card_number)
        )
    """))

    # ── Bank Statements + Lines ───────────────────────────────────────────────

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_statements (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR         NOT NULL,
            bank_account_id VARCHAR         NOT NULL,
            account_iban    VARCHAR(100),
            statement_date  DATE            NOT NULL,
            opening_balance NUMERIC(15,2)   NOT NULL DEFAULT 0,
            closing_balance NUMERIC(15,2)   NOT NULL DEFAULT 0,
            format          VARCHAR(20),
            total_lines     INTEGER         NOT NULL DEFAULT 0,
            imported_lines  INTEGER         NOT NULL DEFAULT 0,
            status          VARCHAR(50)     DEFAULT 'imported',
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_bank_statements_tenant_date
            ON domain_erp.bank_statements (tenant_id, statement_date)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_statement_lines (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR         NOT NULL,
            statement_id    VARCHAR         NOT NULL,
            line_number     INTEGER         NOT NULL,
            booking_date    DATE            NOT NULL,
            value_date      DATE            NOT NULL,
            amount          NUMERIC(15,2)   NOT NULL,
            currency        VARCHAR(3)      DEFAULT 'EUR',
            reference       VARCHAR(255),
            remittance_info TEXT,
            creditor_name   VARCHAR(255),
            creditor_iban   VARCHAR(50),
            debtor_name     VARCHAR(255),
            debtor_iban     VARCHAR(50),
            status          VARCHAR(50)     DEFAULT 'UNMATCHED',
            matched_op_id   VARCHAR(255),
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_bank_statement_lines_statement
            ON domain_erp.bank_statement_lines (statement_id, line_number)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_bank_statement_lines_tenant_status
            ON domain_erp.bank_statement_lines (tenant_id, status)
    """))

    # ── ADD COLUMN IF NOT EXISTS auf journal_entries ──────────────────────────

    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'domain_erp' AND table_name = 'journal_entries'
            ) THEN
                ALTER TABLE domain_erp.journal_entries
                    ADD COLUMN IF NOT EXISTS period  VARCHAR(7),
                    ADD COLUMN IF NOT EXISTS source_user VARCHAR(128);
            END IF;
        END
        $$
    """))

    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'domain_erp' AND table_name = 'journal_entry_lines'
            ) THEN
                ALTER TABLE domain_erp.journal_entry_lines
                    ADD COLUMN IF NOT EXISTS debit_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS credit_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS tax_code       VARCHAR(20),
                    ADD COLUMN IF NOT EXISTS profit_center  VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS reference      VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS updated_at     TIMESTAMPTZ   DEFAULT NOW(),
                    ADD COLUMN IF NOT EXISTS tenant_id      VARCHAR(64);
            END IF;
        END
        $$
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_einkauf — RFQ (Angebotsanfragen)
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_einkauf"))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_requests (
            id              BIGSERIAL       PRIMARY KEY,
            article_id      TEXT            NOT NULL,
            quantity        NUMERIC(18,4)   NOT NULL,
            needed_by_date  DATE,
            notes           TEXT,
            status          TEXT            NOT NULL DEFAULT 'OFFEN',
            tenant_id       VARCHAR(36)     NOT NULL,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_rfq_requests_tenant
            ON domain_einkauf.rfq_requests (tenant_id, status)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_quotes (
            id              BIGSERIAL       PRIMARY KEY,
            rfq_id          BIGINT          NOT NULL
                REFERENCES domain_einkauf.rfq_requests(id) ON DELETE CASCADE,
            supplier_id     TEXT            NOT NULL,
            unit_price      NUMERIC(18,4)   NOT NULL,
            delivery_days   INTEGER,
            notes           TEXT,
            status          TEXT            NOT NULL DEFAULT 'OFFEN',
            received_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            tenant_id       VARCHAR(36)     NOT NULL
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_rfq_quotes_rfq
            ON domain_einkauf.rfq_quotes (rfq_id)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_hr — Schichten (Shifts)
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_hr.shifts (
            id                          VARCHAR         PRIMARY KEY,
            tenant_id                   VARCHAR         NOT NULL,
            shift_date                  DATE            NOT NULL,
            name                        TEXT            NOT NULL,
            location_code               TEXT            NOT NULL DEFAULT 'main',
            required_role               TEXT            NOT NULL DEFAULT 'employee',
            required_qualifications     JSONB           NOT NULL DEFAULT '[]'::jsonb,
            required_headcount          INTEGER         NOT NULL DEFAULT 1,
            starts_at                   TIME            NOT NULL,
            ends_at                     TIME            NOT NULL,
            assigned_employee_refs      JSONB           NOT NULL DEFAULT '[]'::jsonb,
            status                      TEXT            NOT NULL DEFAULT 'planned',
            conflicts                   JSONB           NOT NULL DEFAULT '[]'::jsonb,
            notes                       TEXT,
            created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            created_by                  TEXT,
            updated_by                  TEXT,
            CONSTRAINT shifts_required_headcount_ck CHECK (required_headcount > 0),
            CONSTRAINT shifts_status_ck CHECK (
                status IN ('planned','warning','blocked','cancelled')
            )
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_shifts_tenant_date
            ON domain_hr.shifts (tenant_id, shift_date)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_shared — Zahlungsformulare, Zinsgruppen, Leergutarten
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.zahlungsformulare (
            id                  TEXT        PRIMARY KEY,
            tenant_id           TEXT        NOT NULL,
            formular_nr         TEXT        NOT NULL,
            bezeichnung         TEXT        NOT NULL,
            formularklasse      TEXT        NOT NULL DEFAULT 'ausgang',
            bank_blz            TEXT,
            bank_iban           TEXT,
            formulareinrichtung TEXT,
            aktiv               BOOLEAN     NOT NULL DEFAULT TRUE,
            created_at          TIMESTAMP   NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_zahlungsformulare_tenant_nr UNIQUE (tenant_id, formular_nr)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.zinsgruppen (
            id                          TEXT        PRIMARY KEY,
            tenant_id                   TEXT        NOT NULL,
            gruppe_nr                   TEXT        NOT NULL,
            bezeichnung                 TEXT        NOT NULL,
            zinssatz                    NUMERIC(7,4) NOT NULL,
            zinsmethode                 TEXT        NOT NULL DEFAULT 'act_360',
            schwellwert_tage            INTEGER     NOT NULL DEFAULT 0,
            konto_zinsen                TEXT,
            konto_zinsabschlagsteuer    TEXT,
            aktiv                       BOOLEAN     NOT NULL DEFAULT TRUE,
            created_at                  TIMESTAMP   NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_zinsgruppen_tenant_nr UNIQUE (tenant_id, gruppe_nr)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.leergutarten (
            id              TEXT        PRIMARY KEY,
            tenant_id       TEXT        NOT NULL,
            art_nr          TEXT        NOT NULL,
            bezeichnung     TEXT        NOT NULL,
            leergut_typ     TEXT        NOT NULL DEFAULT 'palette',
            pfandwert       NUMERIC(10,2),
            konto_leergut   TEXT,
            aktiv           BOOLEAN     NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_leergutarten_tenant_nr UNIQUE (tenant_id, art_nr)
        )
    """))


def downgrade() -> None:
    pass
