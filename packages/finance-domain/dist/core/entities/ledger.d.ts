/**
 * VALEO NeuroERP 3.0 - Finance Domain - Ledger Core Entities
 *
 * Core ledger entities following Domain-Driven Design principles
 * with branded types and comprehensive business logic
 */
export interface DomainEvent {
    type: string;
    occurredAt: Date;
    aggregateId: string;
    payload?: unknown;
    metadata?: Record<string, unknown>;
}
export type JournalId = string;
export type AccountId = string;
export type EntryId = string;
export type PeriodId = string;
export type TenantId = string;
/**
 * Chart of Accounts Entry
 * Represents a single account in the chart of accounts
 */
export interface Account {
    readonly id: AccountId;
    readonly tenantId: TenantId;
    readonly accountNumber: string;
    readonly name: string;
    readonly type: 'ASSET' | 'LIABILITY' | 'EQUITY' | 'REVENUE' | 'EXPENSE';
    readonly category: string;
    readonly isActive: boolean;
    readonly parentAccountId?: AccountId;
    readonly taxCode?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
/**
 * Journal Entry
 * Represents a single debit/credit entry in a journal
 */
export interface JournalEntry {
    readonly id: EntryId;
    readonly journalId: JournalId;
    readonly accountId: AccountId;
    readonly debit: number;
    readonly credit: number;
    readonly description: string;
    readonly costCenter?: string;
    readonly taxCode?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
}
/**
 * Journal
 * Represents a complete journal with multiple entries
 */
export interface Journal {
    readonly id: JournalId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly journalNumber: string;
    readonly description: string;
    readonly status: 'DRAFT' | 'POSTED' | 'CLOSED';
    readonly entries: JournalEntry[];
    readonly totalDebit: number;
    readonly totalCredit: number;
    readonly source: {
        type: 'AP' | 'AR' | 'BANK' | 'MANUAL' | 'AI';
        reference: string;
    };
    readonly postedAt?: Date;
    readonly postedBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
/**
 * Accounting Period
 * Represents a financial period (month, quarter, year)
 */
export interface AccountingPeriod {
    readonly id: PeriodId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly status: 'OPEN' | 'CLOSED' | 'ADJUSTING';
    readonly startDate: Date;
    readonly endDate: Date;
    readonly closedAt?: Date;
    readonly closedBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
}
export interface CreateJournalCommand {
    tenantId: TenantId;
    period: string;
    description: string;
    entries: Omit<JournalEntry, 'id' | 'journalId' | 'createdAt'>[];
    source: {
        type: 'AP' | 'AR' | 'BANK' | 'MANUAL' | 'AI';
        reference: string;
    };
    metadata?: Record<string, any>;
}
export interface PostJournalCommand {
    journalId: JournalId;
    postedBy: string;
}
export interface ClosePeriodCommand {
    tenantId: TenantId;
    period: string;
    closedBy: string;
}
export declare class JournalCreatedEvent implements DomainEvent {
    readonly journal: Journal;
    readonly type = "finance.journal.created";
    readonly occurredAt: Date;
    readonly aggregateId: JournalId;
    constructor(journal: Journal);
}
export declare class JournalPostedEvent implements DomainEvent {
    readonly journalId: JournalId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly entries: JournalEntry[];
    readonly totalDebit: number;
    readonly totalCredit: number;
    readonly source: Journal['source'];
    readonly postedBy: string;
    readonly explain?: string;
    readonly type = "finance.journal.posted";
    readonly occurredAt: Date;
    readonly aggregateId: JournalId;
    constructor(journalId: JournalId, tenantId: TenantId, period: string, entries: JournalEntry[], totalDebit: number, totalCredit: number, source: Journal['source'], postedBy: string, explain?: string);
}
export declare class PeriodClosedEvent implements DomainEvent {
    readonly periodId: PeriodId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly closedBy: string;
    readonly journalCount: number;
    readonly totalDebit: number;
    readonly totalCredit: number;
    readonly type = "finance.period.closed";
    readonly occurredAt: Date;
    readonly aggregateId: PeriodId;
    constructor(periodId: PeriodId, tenantId: TenantId, period: string, closedBy: string, journalCount: number, totalDebit: number, totalCredit: number);
}
export interface TrialBalanceEntry {
    accountId: AccountId;
    accountNumber: string;
    accountName: string;
    debit: number;
    credit: number;
    balance: number;
}
export interface TrialBalance {
    period: string;
    tenantId: TenantId;
    entries: TrialBalanceEntry[];
    totalDebit: number;
    totalCredit: number;
    isBalanced: boolean;
    generatedAt: Date;
}
/**
 * Journal Entity with business logic
 */
export declare class JournalEntity implements Journal {
    readonly id: JournalId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly journalNumber: string;
    readonly description: string;
    readonly status: 'DRAFT' | 'POSTED' | 'CLOSED';
    readonly entries: JournalEntry[];
    readonly totalDebit: number;
    readonly totalCredit: number;
    readonly source: Journal['source'];
    readonly postedAt?: Date;
    readonly postedBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(id: JournalId, tenantId: TenantId, period: string, journalNumber: string, description: string, entries: JournalEntry[], source: Journal['source'], status?: Journal['status'], postedAt?: Date, postedBy?: string, metadata?: Record<string, any>, createdAt?: Date, updatedAt?: Date);
    /**
     * Create a new journal from command
     */
    static create(command: CreateJournalCommand): JournalEntity;
    /**
     * Post the journal (business operation)
     */
    post(postedBy: string): JournalEntity;
    /**
     * Check if journal is balanced (debits = credits)
     */
    isBalanced(): boolean;
    /**
     * Get trial balance impact
     */
    getTrialBalanceImpact(): TrialBalanceEntry[];
    /**
     * Validate journal business rules
     */
    private validateJournal;
}
/**
 * Accounting Period Entity
 */
export declare class AccountingPeriodEntity implements AccountingPeriod {
    readonly id: PeriodId;
    readonly tenantId: TenantId;
    readonly period: string;
    readonly status: 'OPEN' | 'CLOSED' | 'ADJUSTING';
    readonly startDate: Date;
    readonly endDate: Date;
    readonly closedAt?: Date;
    readonly closedBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    constructor(id: PeriodId, tenantId: TenantId, period: string, status: AccountingPeriod['status'], startDate: Date, endDate: Date, closedAt?: Date, closedBy?: string, metadata?: Record<string, any>, createdAt?: Date);
    /**
     * Create period from period string
     */
    static create(tenantId: TenantId, period: string): AccountingPeriodEntity;
    /**
     * Close the period
     */
    close(closedBy: string): AccountingPeriodEntity;
    /**
     * Check if date falls within period
     */
    containsDate(date: Date): boolean;
    /**
     * Validate period business rules
     */
    private validatePeriod;
}
export interface JournalRepository {
    findById(id: JournalId): Promise<Journal | null>;
    findByPeriod(tenantId: TenantId, period: string): Promise<Journal[]>;
    findByTenant(tenantId: TenantId): Promise<Journal[]>;
    save(journal: Journal): Promise<void>;
    findUnbalancedJournals(tenantId: TenantId): Promise<Journal[]>;
}
export interface AccountRepository {
    findById(id: AccountId): Promise<Account | null>;
    findByAccountNumber(accountNumber: string): Promise<Account | null>;
    findByType(type: Account['type']): Promise<Account[]>;
    findChartOfAccounts(tenantId: TenantId): Promise<Account[]>;
    save(account: Account): Promise<void>;
}
export interface AccountingPeriodRepository {
    findById(id: PeriodId): Promise<AccountingPeriod | null>;
    findByPeriod(tenantId: TenantId, period: string): Promise<AccountingPeriod | null>;
    findOpenPeriods(tenantId: TenantId): Promise<AccountingPeriod[]>;
    save(period: AccountingPeriod): Promise<void>;
}
export interface LedgerService {
    createJournal(command: CreateJournalCommand): Promise<JournalId>;
    postJournal(command: PostJournalCommand): Promise<void>;
    getTrialBalance(tenantId: TenantId, period: string): Promise<TrialBalance>;
    closePeriod(command: ClosePeriodCommand): Promise<void>;
    getJournal(journalId: JournalId): Promise<Journal | null>;
    listJournals(tenantId: TenantId, period?: string): Promise<Journal[]>;
}
/**
 * Generate next journal number for period
 */
export declare function generateJournalNumber(period: string): string;
/**
 * Validate journal balance
 */
export declare function validateJournalBalance(entries: JournalEntry[]): boolean;
/**
 * Calculate period from date
 */
export declare function getPeriodFromDate(date: Date): string;
//# sourceMappingURL=ledger.d.ts.map