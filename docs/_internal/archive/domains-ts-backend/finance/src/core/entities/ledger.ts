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

// ===== BRANDED TYPES =====
export type JournalId = string;
export type AccountId = string;
export type EntryId = string;
export type PeriodId = string;
export type TenantId = string;

// ===== CORE ENTITIES =====

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
  readonly period: string; // YYYY-MM format
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
  readonly period: string; // YYYY-MM format
  readonly status: 'OPEN' | 'CLOSED' | 'ADJUSTING';
  readonly startDate: Date;
  readonly endDate: Date;
  readonly closedAt?: Date;
  readonly closedBy?: string;
  readonly metadata: Record<string, any>;
  readonly createdAt: Date;
}

// ===== COMMANDS =====

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

// ===== DOMAIN EVENTS =====

export class JournalCreatedEvent implements DomainEvent {
  readonly type = 'finance.journal.created';
  readonly occurredAt: Date;
  readonly aggregateId: JournalId;

  constructor(
    public readonly journal: Journal
  ) {
    this.occurredAt = new Date();
    this.aggregateId = journal.id;
  }
}

export class JournalPostedEvent implements DomainEvent {
  readonly type = 'finance.journal.posted';
  readonly occurredAt: Date;
  readonly aggregateId: JournalId;

  constructor(
    public readonly journalId: JournalId,
    public readonly tenantId: TenantId,
    public readonly period: string,
    public readonly entries: JournalEntry[],
    public readonly totalDebit: number,
    public readonly totalCredit: number,
    public readonly source: Journal['source'],
    public readonly postedBy: string,
    public readonly explain?: string
  ) {
    this.occurredAt = new Date();
    this.aggregateId = journalId;
  }
}

export class PeriodClosedEvent implements DomainEvent {
  readonly type = 'finance.period.closed';
  readonly occurredAt: Date;
  readonly aggregateId: PeriodId;

  constructor(
    public readonly periodId: PeriodId,
    public readonly tenantId: TenantId,
    public readonly period: string,
    public readonly closedBy: string,
    public readonly journalCount: number,
    public readonly totalDebit: number,
    public readonly totalCredit: number
  ) {
    this.occurredAt = new Date();
    this.aggregateId = periodId;
  }
}

// ===== VALUE OBJECTS =====

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

// ===== BUSINESS LOGIC =====

/**
 * Journal Entity with business logic
 */
export class JournalEntity implements Journal {
  public readonly id: JournalId;
  public readonly tenantId: TenantId;
  public readonly period: string;
  public readonly journalNumber: string;
  public readonly description: string;
  public readonly status: 'DRAFT' | 'POSTED' | 'CLOSED';
  public readonly entries: JournalEntry[];
  public readonly totalDebit: number;
  public readonly totalCredit: number;
  public readonly source: Journal['source'];
  public readonly postedAt?: Date;
  public readonly postedBy?: string;
  public readonly metadata: Record<string, any>;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  constructor(
    id: JournalId,
    tenantId: TenantId,
    period: string,
    journalNumber: string,
    description: string,
    entries: JournalEntry[],
    source: Journal['source'],
    status: Journal['status'] = 'DRAFT',
    postedAt?: Date,
    postedBy?: string,
    metadata: Record<string, any> = {},
    createdAt?: Date,
    updatedAt?: Date
  ) {
    this.id = id;
    this.tenantId = tenantId;
    this.period = period;
    this.journalNumber = journalNumber;
    this.description = description;
    this.entries = entries;
    this.source = source;
    this.status = status;
    if (postedAt !== undefined) this.postedAt = postedAt;
    if (postedBy !== undefined) this.postedBy = postedBy;
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
  static create(command: CreateJournalCommand): JournalEntity {
    const id = crypto.randomUUID() as JournalId;
    const journalNumber = `JNL-${command.period}-${Date.now().toString(36).toUpperCase()}`;

    // Create journal entries
    const entries: JournalEntry[] = command.entries.map((entry, index) => ({
      id: crypto.randomUUID() as EntryId,
      journalId: id,
      createdAt: new Date(),
      ...entry
    }));

    return new JournalEntity(
      id,
      command.tenantId,
      command.period,
      journalNumber,
      command.description,
      entries,
      command.source,
      'DRAFT',
      undefined,
      undefined,
      command.metadata
    );
  }

  /**
   * Post the journal (business operation)
   */
  post(postedBy: string): JournalEntity {
    if (this.status !== 'DRAFT') {
      throw new Error('Only draft journals can be posted');
    }

    if (!this.isBalanced()) {
      throw new Error('Journal must be balanced before posting');
    }

    return new JournalEntity(
      this.id,
      this.tenantId,
      this.period,
      this.journalNumber,
      this.description,
      this.entries,
      this.source,
      'POSTED',
      new Date(),
      postedBy,
      this.metadata,
      this.createdAt,
      new Date()
    );
  }

  /**
   * Check if journal is balanced (debits = credits)
   */
  isBalanced(): boolean {
    return Math.abs(this.totalDebit - this.totalCredit) < 0.01; // Allow for rounding
  }

  /**
   * Get trial balance impact
   */
  getTrialBalanceImpact(): TrialBalanceEntry[] {
    const impact = new Map<AccountId, { debit: number; credit: number }>();

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
      accountName: '',   // Would be populated from Account lookup
      debit: amounts.debit,
      credit: amounts.credit,
      balance: amounts.debit - amounts.credit
    }));
  }

  /**
   * Validate journal business rules
   */
  private validateJournal(): void {
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

/**
 * Accounting Period Entity
 */
export class AccountingPeriodEntity implements AccountingPeriod {
  public readonly id: PeriodId;
  public readonly tenantId: TenantId;
  public readonly period: string;
  public readonly status: 'OPEN' | 'CLOSED' | 'ADJUSTING';
  public readonly startDate: Date;
  public readonly endDate: Date;
  public readonly closedAt?: Date;
  public readonly closedBy?: string;
  public readonly metadata: Record<string, any>;
  public readonly createdAt: Date;

  constructor(
    id: PeriodId,
    tenantId: TenantId,
    period: string,
    status: AccountingPeriod['status'],
    startDate: Date,
    endDate: Date,
    closedAt?: Date,
    closedBy?: string,
    metadata: Record<string, any> = {},
    createdAt?: Date
  ) {
    this.id = id;
    this.tenantId = tenantId;
    this.period = period;
    this.status = status;
    this.startDate = startDate;
    this.endDate = endDate;
    if (closedAt !== undefined) this.closedAt = closedAt;
    if (closedBy !== undefined) this.closedBy = closedBy;
    this.metadata = metadata;
    this.createdAt = createdAt ?? new Date();

    this.validatePeriod();
  }

  /**
   * Create period from period string
   */
  static create(tenantId: TenantId, period: string): AccountingPeriodEntity {
    const [year, month] = period.split('-').map(Number);

    if (!year || !month || month < 1 || month > 12) {
      throw new Error('Invalid period format. Expected YYYY-MM');
    }

    const startDate = new Date(year, month - 1, 1);
    const endDate = new Date(year, month, 0); // Last day of month

    const id = crypto.randomUUID() as PeriodId;

    return new AccountingPeriodEntity(
      id,
      tenantId,
      period,
      'OPEN',
      startDate,
      endDate
    );
  }

  /**
   * Close the period
   */
  close(closedBy: string): AccountingPeriodEntity {
    if (this.status !== 'OPEN') {
      throw new Error('Only open periods can be closed');
    }

    return new AccountingPeriodEntity(
      this.id,
      this.tenantId,
      this.period,
      'CLOSED',
      this.startDate,
      this.endDate,
      new Date(),
      closedBy,
      this.metadata,
      this.createdAt
    );
  }

  /**
   * Check if date falls within period
   */
  containsDate(date: Date): boolean {
    return date >= this.startDate && date <= this.endDate;
  }

  /**
   * Validate period business rules
   */
  private validatePeriod(): void {
    if (this.startDate >= this.endDate) {
      throw new Error('Period start date must be before end date');
    }

    if (this.status === 'CLOSED' && (!this.closedAt || !this.closedBy)) {
      throw new Error('Closed period must have closedAt and closedBy');
    }
  }
}

// ===== REPOSITORY INTERFACES =====

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

// ===== SERVICE INTERFACES =====

export interface LedgerService {
  createJournal(command: CreateJournalCommand): Promise<JournalId>;
  postJournal(command: PostJournalCommand): Promise<void>;
  getTrialBalance(tenantId: TenantId, period: string): Promise<TrialBalance>;
  closePeriod(command: ClosePeriodCommand): Promise<void>;
  getJournal(journalId: JournalId): Promise<Journal | null>;
  listJournals(tenantId: TenantId, period?: string): Promise<Journal[]>;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Generate next journal number for period
 */
export function generateJournalNumber(period: string): string {
  const timestamp = Date.now().toString(36).toUpperCase();
  return `JNL-${period}-${timestamp}`;
}

/**
 * Validate journal balance
 */
export function validateJournalBalance(entries: JournalEntry[]): boolean {
  const totalDebit = entries.reduce((sum, entry) => sum + entry.debit, 0);
  const totalCredit = entries.reduce((sum, entry) => sum + entry.credit, 0);
  return Math.abs(totalDebit - totalCredit) < 0.01;
}

/**
 * Calculate period from date
 */
export function getPeriodFromDate(date: Date): string {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  return `${year}-${month}`;
}