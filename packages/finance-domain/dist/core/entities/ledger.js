"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - Ledger Core Entities
 *
 * Core ledger entities following Domain-Driven Design principles
 * with branded types and comprehensive business logic
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AccountingPeriodEntity = exports.JournalEntity = exports.PeriodClosedEvent = exports.JournalPostedEvent = exports.JournalCreatedEvent = void 0;
exports.generateJournalNumber = generateJournalNumber;
exports.validateJournalBalance = validateJournalBalance;
exports.getPeriodFromDate = getPeriodFromDate;
// ===== DOMAIN EVENTS =====
class JournalCreatedEvent {
    constructor(journal) {
        this.journal = journal;
        this.type = 'finance.journal.created';
        this.occurredAt = new Date();
        this.aggregateId = journal.id;
    }
}
exports.JournalCreatedEvent = JournalCreatedEvent;
class JournalPostedEvent {
    constructor(journalId, tenantId, period, entries, totalDebit, totalCredit, source, postedBy, explain) {
        this.journalId = journalId;
        this.tenantId = tenantId;
        this.period = period;
        this.entries = entries;
        this.totalDebit = totalDebit;
        this.totalCredit = totalCredit;
        this.source = source;
        this.postedBy = postedBy;
        this.explain = explain;
        this.type = 'finance.journal.posted';
        this.occurredAt = new Date();
        this.aggregateId = journalId;
    }
}
exports.JournalPostedEvent = JournalPostedEvent;
class PeriodClosedEvent {
    constructor(periodId, tenantId, period, closedBy, journalCount, totalDebit, totalCredit) {
        this.periodId = periodId;
        this.tenantId = tenantId;
        this.period = period;
        this.closedBy = closedBy;
        this.journalCount = journalCount;
        this.totalDebit = totalDebit;
        this.totalCredit = totalCredit;
        this.type = 'finance.period.closed';
        this.occurredAt = new Date();
        this.aggregateId = periodId;
    }
}
exports.PeriodClosedEvent = PeriodClosedEvent;
// ===== BUSINESS LOGIC =====
/**
 * Journal Entity with business logic
 */
class JournalEntity {
    constructor(id, tenantId, period, journalNumber, description, entries, source, status = 'DRAFT', postedAt, postedBy, metadata = {}, createdAt, updatedAt) {
        this.id = id;
        this.tenantId = tenantId;
        this.period = period;
        this.journalNumber = journalNumber;
        this.description = description;
        this.entries = entries;
        this.source = source;
        this.status = status;
        if (postedAt !== undefined)
            this.postedAt = postedAt;
        if (postedBy !== undefined)
            this.postedBy = postedBy;
        this.metadata = metadata;
        this.createdAt = createdAt ?? new Date();
        this.updatedAt = updatedAt ?? new Date();
        // Calculate totals
        this.totalDebit = entries.reduce((sum, entry) => sum + entry.debit, 0);
        this.totalCredit = entries.reduce((sum, entry) => sum + entry.credit, 0);
        // Validate business rules
        this.validateJournal();
    }
    /**
     * Create a new journal from command
     */
    static create(command) {
        const id = crypto.randomUUID();
        const journalNumber = `JNL-${command.period}-${Date.now().toString(36).toUpperCase()}`;
        // Create journal entries
        const entries = command.entries.map((entry, index) => ({
            id: crypto.randomUUID(),
            journalId: id,
            createdAt: new Date(),
            ...entry
        }));
        return new JournalEntity(id, command.tenantId, command.period, journalNumber, command.description, entries, command.source, 'DRAFT', undefined, undefined, command.metadata);
    }
    /**
     * Post the journal (business operation)
     */
    post(postedBy) {
        if (this.status !== 'DRAFT') {
            throw new Error('Only draft journals can be posted');
        }
        if (!this.isBalanced()) {
            throw new Error('Journal must be balanced before posting');
        }
        return new JournalEntity(this.id, this.tenantId, this.period, this.journalNumber, this.description, this.entries, this.source, 'POSTED', new Date(), postedBy, this.metadata, this.createdAt, new Date());
    }
    /**
     * Check if journal is balanced (debits = credits)
     */
    isBalanced() {
        return Math.abs(this.totalDebit - this.totalCredit) < 0.01; // Allow for rounding
    }
    /**
     * Get trial balance impact
     */
    getTrialBalanceImpact() {
        const impact = new Map();
        for (const entry of this.entries) {
            const current = impact.get(entry.accountId) || { debit: 0, credit: 0 };
            impact.set(entry.accountId, {
                debit: current.debit + entry.debit,
                credit: current.credit + entry.credit
            });
        }
        return Array.from(impact.entries()).map(([accountId, amounts]) => ({
            accountId,
            accountNumber: '', // Would be populated from Account lookup
            accountName: '', // Would be populated from Account lookup
            debit: amounts.debit,
            credit: amounts.credit,
            balance: amounts.debit - amounts.credit
        }));
    }
    /**
     * Validate journal business rules
     */
    validateJournal() {
        if (this.entries.length === 0) {
            throw new Error('Journal must have at least one entry');
        }
        if (this.entries.length === 1) {
            throw new Error('Journal must have at least two entries for double-entry bookkeeping');
        }
        // Check for at least one debit and one credit
        const hasDebit = this.entries.some(entry => entry.debit > 0);
        const hasCredit = this.entries.some(entry => entry.credit > 0);
        if (!hasDebit || !hasCredit) {
            throw new Error('Journal must have both debit and credit entries');
        }
    }
}
exports.JournalEntity = JournalEntity;
/**
 * Accounting Period Entity
 */
class AccountingPeriodEntity {
    constructor(id, tenantId, period, status, startDate, endDate, closedAt, closedBy, metadata = {}, createdAt) {
        this.id = id;
        this.tenantId = tenantId;
        this.period = period;
        this.status = status;
        this.startDate = startDate;
        this.endDate = endDate;
        if (closedAt !== undefined)
            this.closedAt = closedAt;
        if (closedBy !== undefined)
            this.closedBy = closedBy;
        this.metadata = metadata;
        this.createdAt = createdAt ?? new Date();
        this.validatePeriod();
    }
    /**
     * Create period from period string
     */
    static create(tenantId, period) {
        const [year, month] = period.split('-').map(Number);
        if (!year || !month || month < 1 || month > 12) {
            throw new Error('Invalid period format. Expected YYYY-MM');
        }
        const startDate = new Date(year, month - 1, 1);
        const endDate = new Date(year, month, 0); // Last day of month
        const id = crypto.randomUUID();
        return new AccountingPeriodEntity(id, tenantId, period, 'OPEN', startDate, endDate);
    }
    /**
     * Close the period
     */
    close(closedBy) {
        if (this.status !== 'OPEN') {
            throw new Error('Only open periods can be closed');
        }
        return new AccountingPeriodEntity(this.id, this.tenantId, this.period, 'CLOSED', this.startDate, this.endDate, new Date(), closedBy, this.metadata, this.createdAt);
    }
    /**
     * Check if date falls within period
     */
    containsDate(date) {
        return date >= this.startDate && date <= this.endDate;
    }
    /**
     * Validate period business rules
     */
    validatePeriod() {
        if (this.startDate >= this.endDate) {
            throw new Error('Period start date must be before end date');
        }
        if (this.status === 'CLOSED' && (!this.closedAt || !this.closedBy)) {
            throw new Error('Closed period must have closedAt and closedBy');
        }
    }
}
exports.AccountingPeriodEntity = AccountingPeriodEntity;
// ===== UTILITY FUNCTIONS =====
/**
 * Generate next journal number for period
 */
function generateJournalNumber(period) {
    const timestamp = Date.now().toString(36).toUpperCase();
    return `JNL-${period}-${timestamp}`;
}
/**
 * Validate journal balance
 */
function validateJournalBalance(entries) {
    const totalDebit = entries.reduce((sum, entry) => sum + entry.debit, 0);
    const totalCredit = entries.reduce((sum, entry) => sum + entry.credit, 0);
    return Math.abs(totalDebit - totalCredit) < 0.01;
}
/**
 * Calculate period from date
 */
function getPeriodFromDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    return `${year}-${month}`;
}
//# sourceMappingURL=ledger.js.map