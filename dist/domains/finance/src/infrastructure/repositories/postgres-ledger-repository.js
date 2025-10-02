"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - PostgreSQL Ledger Repository
 *
 * Infrastructure layer implementation for ledger data access
 * Following Repository pattern and Clean Architecture
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PostgresAccountingPeriodRepository = exports.PostgresAccountRepository = exports.PostgresJournalRepository = void 0;
exports.createPostgresJournalRepository = createPostgresJournalRepository;
exports.createPostgresAccountRepository = createPostgresAccountRepository;
exports.createPostgresPeriodRepository = createPostgresPeriodRepository;
const ledger_1 = require("../../core/entities/ledger");
// ===== REPOSITORY IMPLEMENTATIONS =====
class PostgresJournalRepository {
    db;
    constructor(db) {
        this.db = db;
    }
    async findById(id) {
        const query = `
      SELECT id, tenant_id, period, journal_number, description, status,
             total_debit, total_credit, source_type, source_reference,
             posted_at, posted_by, metadata, created_at, updated_at
      FROM finance_journals
      WHERE id = $1
    `;
        const result = await this.db.query(query, [id]);
        if (result.rows.length === 0) {
            return null;
        }
        const row = result.rows[0];
        const entries = await this.findEntriesByJournalId(id);
        return new ledger_1.JournalEntity(row.id, row.tenant_id, row.period, row.journal_number, row.description, entries, {
            type: row.source_type,
            reference: row.source_reference
        }, row.status, row.posted_at, row.posted_by, row.metadata, row.created_at, row.updated_at);
    }
    async findByPeriod(tenantId, period) {
        const query = `
      SELECT id, tenant_id, period, journal_number, description, status,
             total_debit, total_credit, source_type, source_reference,
             posted_at, posted_by, metadata, created_at, updated_at
      FROM finance_journals
      WHERE tenant_id = $1 AND period = $2
      ORDER BY created_at DESC
    `;
        const result = await this.db.query(query, [tenantId, period]);
        const journals = [];
        for (const row of result.rows) {
            const entries = await this.findEntriesByJournalId(row.id);
            journals.push(new ledger_1.JournalEntity(row.id, row.tenant_id, row.period, row.journal_number, row.description, entries, {
                type: row.source_type,
                reference: row.source_reference
            }, row.status, row.posted_at, row.posted_by, row.metadata, row.created_at, row.updated_at));
        }
        return journals;
    }
    async findByTenant(tenantId) {
        const query = `
      SELECT id, tenant_id, period, journal_number, description, status,
             total_debit, total_credit, source_type, source_reference,
             posted_at, posted_by, metadata, created_at, updated_at
      FROM finance_journals
      WHERE tenant_id = $1
      ORDER BY created_at DESC
    `;
        const result = await this.db.query(query, [tenantId]);
        const journals = [];
        for (const row of result.rows) {
            const entries = await this.findEntriesByJournalId(row.id);
            journals.push(new ledger_1.JournalEntity(row.id, row.tenant_id, row.period, row.journal_number, row.description, entries, {
                type: row.source_type,
                reference: row.source_reference
            }, row.status, row.posted_at, row.posted_by, row.metadata, row.created_at, row.updated_at));
        }
        return journals;
    }
    async save(journal) {
        await this.db.transaction(async (client) => {
            // Save or update journal header
            const journalQuery = journal.id ? `
        UPDATE finance_journals SET
          period = $2, journal_number = $3, description = $4, status = $5,
          total_debit = $6, total_credit = $7, source_type = $8, source_reference = $9,
          posted_at = $10, posted_by = $11, metadata = $12, updated_at = NOW()
        WHERE id = $1
      ` : `
        INSERT INTO finance_journals (
          id, tenant_id, period, journal_number, description, status,
          total_debit, total_credit, source_type, source_reference,
          posted_at, posted_by, metadata, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
      `;
            const journalParams = journal.id ? [
                journal.id, journal.period, journal.journalNumber, journal.description,
                journal.status, journal.totalDebit, journal.totalCredit,
                journal.source.type, journal.source.reference,
                journal.postedAt, journal.postedBy, journal.metadata
            ] : [
                journal.id, journal.tenantId, journal.period, journal.journalNumber,
                journal.description, journal.status, journal.totalDebit, journal.totalCredit,
                journal.source.type, journal.source.reference,
                journal.postedAt, journal.postedBy, journal.metadata, journal.createdAt
            ];
            await client.query(journalQuery, journalParams);
            // Delete existing entries if updating
            if (journal.id) {
                await client.query('DELETE FROM finance_journal_entries WHERE journal_id = $1', [journal.id]);
            }
            // Insert new entries
            for (const entry of journal.entries) {
                const entryQuery = `
          INSERT INTO finance_journal_entries (
            id, journal_id, account_id, debit, credit, description,
            cost_center, tax_code, metadata, created_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        `;
                await client.query(entryQuery, [
                    entry.id, entry.journalId, entry.accountId, entry.debit, entry.credit,
                    entry.description, entry.costCenter, entry.taxCode, entry.metadata, entry.createdAt
                ]);
            }
        });
    }
    async findUnbalancedJournals(tenantId) {
        const query = `
      SELECT id, tenant_id, period, journal_number, description, status,
             total_debit, total_credit, source_type, source_reference,
             posted_at, posted_by, metadata, created_at, updated_at
      FROM finance_journals
      WHERE tenant_id = $1 AND status = 'DRAFT'
        AND ABS(total_debit - total_credit) > 0.01
      ORDER BY created_at DESC
    `;
        const result = await this.db.query(query, [tenantId]);
        const journals = [];
        for (const row of result.rows) {
            const entries = await this.findEntriesByJournalId(row.id);
            journals.push(new ledger_1.JournalEntity(row.id, row.tenant_id, row.period, row.journal_number, row.description, entries, {
                type: row.source_type,
                reference: row.source_reference
            }, row.status, row.posted_at, row.posted_by, row.metadata, row.created_at, row.updated_at));
        }
        return journals;
    }
    async findEntriesByJournalId(journalId) {
        const query = `
      SELECT id, journal_id, account_id, debit, credit, description,
             cost_center, tax_code, metadata, created_at
      FROM finance_journal_entries
      WHERE journal_id = $1
      ORDER BY created_at
    `;
        const result = await this.db.query(query, [journalId]);
        return result.rows.map((row) => ({
            id: row.id,
            journalId: row.journal_id,
            accountId: row.account_id,
            debit: parseFloat(row.debit),
            credit: parseFloat(row.credit),
            description: row.description,
            costCenter: row.cost_center,
            taxCode: row.tax_code,
            metadata: row.metadata,
            createdAt: row.created_at
        }));
    }
}
exports.PostgresJournalRepository = PostgresJournalRepository;
class PostgresAccountRepository {
    db;
    constructor(db) {
        this.db = db;
    }
    async findById(id) {
        const query = `
      SELECT id, tenant_id, account_number, name, type, category, is_active,
             parent_account_id, tax_code, metadata, created_at, updated_at
      FROM finance_accounts
      WHERE id = $1
    `;
        const result = await this.db.query(query, [id]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToAccount(result.rows[0]);
    }
    async findByAccountNumber(accountNumber) {
        const query = `
      SELECT id, tenant_id, account_number, name, type, category, is_active,
             parent_account_id, tax_code, metadata, created_at, updated_at
      FROM finance_accounts
      WHERE account_number = $1 AND is_active = true
    `;
        const result = await this.db.query(query, [accountNumber]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToAccount(result.rows[0]);
    }
    async findByType(type) {
        const query = `
      SELECT id, tenant_id, account_number, name, type, category, is_active,
             parent_account_id, tax_code, metadata, created_at, updated_at
      FROM finance_accounts
      WHERE type = $1 AND is_active = true
      ORDER BY account_number
    `;
        const result = await this.db.query(query, [type]);
        return result.rows.map(row => this.mapRowToAccount(row));
    }
    async findChartOfAccounts(tenantId) {
        const query = `
      SELECT id, tenant_id, account_number, name, type, category, is_active,
             parent_account_id, tax_code, metadata, created_at, updated_at
      FROM finance_accounts
      WHERE tenant_id = $1 AND is_active = true
      ORDER BY type, account_number
    `;
        const result = await this.db.query(query, [tenantId]);
        return result.rows.map(row => this.mapRowToAccount(row));
    }
    async save(account) {
        const query = account.id ? `
      UPDATE finance_accounts SET
        account_number = $2, name = $3, type = $4, category = $5, is_active = $6,
        parent_account_id = $7, tax_code = $8, metadata = $9, updated_at = NOW()
      WHERE id = $1
    ` : `
      INSERT INTO finance_accounts (
        id, tenant_id, account_number, name, type, category, is_active,
        parent_account_id, tax_code, metadata, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    `;
        const params = account.id ? [
            account.id, account.accountNumber, account.name, account.type,
            account.category, account.isActive, account.parentAccountId,
            account.taxCode, account.metadata
        ] : [
            account.id, account.tenantId, account.accountNumber, account.name,
            account.type, account.category, account.isActive, account.parentAccountId,
            account.taxCode, account.metadata, account.createdAt
        ];
        await this.db.query(query, params);
    }
    mapRowToAccount(row) {
        return {
            id: row.id,
            tenantId: row.tenant_id,
            accountNumber: row.account_number,
            name: row.name,
            type: row.type,
            category: row.category,
            isActive: row.is_active,
            parentAccountId: row.parent_account_id,
            taxCode: row.tax_code,
            metadata: row.metadata,
            createdAt: row.created_at,
            updatedAt: row.updated_at
        };
    }
}
exports.PostgresAccountRepository = PostgresAccountRepository;
class PostgresAccountingPeriodRepository {
    db;
    constructor(db) {
        this.db = db;
    }
    async findById(id) {
        const query = `
      SELECT id, tenant_id, period, status, start_date, end_date,
             closed_at, closed_by, metadata, created_at
      FROM finance_accounting_periods
      WHERE id = $1
    `;
        const result = await this.db.query(query, [id]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToPeriod(result.rows[0]);
    }
    async findByPeriod(tenantId, period) {
        const query = `
      SELECT id, tenant_id, period, status, start_date, end_date,
             closed_at, closed_by, metadata, created_at
      FROM finance_accounting_periods
      WHERE tenant_id = $1 AND period = $2
    `;
        const result = await this.db.query(query, [tenantId, period]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToPeriod(result.rows[0]);
    }
    async findOpenPeriods(tenantId) {
        const query = `
      SELECT id, tenant_id, period, status, start_date, end_date,
             closed_at, closed_by, metadata, created_at
      FROM finance_accounting_periods
      WHERE tenant_id = $1 AND status = 'OPEN'
      ORDER BY period DESC
    `;
        const result = await this.db.query(query, [tenantId]);
        return result.rows.map(row => this.mapRowToPeriod(row));
    }
    async save(period) {
        const query = period.id ? `
      UPDATE finance_accounting_periods SET
        period = $2, status = $3, start_date = $4, end_date = $5,
        closed_at = $6, closed_by = $7, metadata = $8
      WHERE id = $1
    ` : `
      INSERT INTO finance_accounting_periods (
        id, tenant_id, period, status, start_date, end_date, metadata, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `;
        const params = period.id ? [
            period.id, period.period, period.status, period.startDate, period.endDate,
            period.closedAt, period.closedBy, period.metadata
        ] : [
            period.id, period.tenantId, period.period, period.status,
            period.startDate, period.endDate, period.metadata, period.createdAt
        ];
        await this.db.query(query, params);
    }
    mapRowToPeriod(row) {
        return new ledger_1.AccountingPeriodEntity(row.id, row.tenant_id, row.period, row.status, new Date(row.start_date), new Date(row.end_date), row.closed_at ? new Date(row.closed_at) : undefined, row.closed_by, row.metadata, row.created_at);
    }
}
exports.PostgresAccountingPeriodRepository = PostgresAccountingPeriodRepository;
// ===== FACTORY FUNCTIONS =====
function createPostgresJournalRepository(db) {
    return new PostgresJournalRepository(db);
}
function createPostgresAccountRepository(db) {
    return new PostgresAccountRepository(db);
}
function createPostgresPeriodRepository(db) {
    return new PostgresAccountingPeriodRepository(db);
}
