/**
 * VALEO NeuroERP 3.0 - Finance Domain - Ledger Service
 *
 * Application Service for Ledger operations following Clean Architecture
 * Sprint 1 Implementation: Core ledger functionality
 */

import {
  AccountId,
  AccountRepository,
  AccountingPeriodEntity,
  AccountingPeriodRepository,
  ClosePeriodCommand,
  CreateJournalCommand,
  Journal,
  JournalCreatedEvent,
  JournalEntity,
  JournalId,
  JournalPostedEvent,
  JournalRepository,
  PeriodClosedEvent,
  PostJournalCommand,
  TenantId,
  TrialBalance,
  TrialBalanceEntry
} from '../../core/entities/ledger';

// ===== SERVICE INTERFACES =====

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

export interface LedgerService {
  createJournal(command: CreateJournalCommand): Promise<JournalId>;
  postJournal(command: PostJournalCommand): Promise<void>;
  getTrialBalance(tenantId: TenantId, period: string): Promise<TrialBalance>;
  closePeriod(command: ClosePeriodCommand): Promise<void>;
  getJournal(journalId: JournalId): Promise<Journal | null>;
  listJournals(tenantId: TenantId, period?: string): Promise<Journal[]>;
}

export interface LedgerServiceDependencies {
  journalRepository: JournalRepository;
  accountRepository: AccountRepository;
  periodRepository: AccountingPeriodRepository;
  eventPublisher: EventPublisher;
}

// ===== APPLICATION SERVICE =====

export class LedgerApplicationService implements LedgerService {
  constructor(
    private readonly dependencies: LedgerServiceDependencies
  ) {}

  /**
   * Create a new journal
   */
  async createJournal(command: CreateJournalCommand): Promise<JournalId> {
    // Business validation
    await this.validateJournalCommand(command);

    // Create journal entity
    const journal = JournalEntity.create(command);

    // Save to repository
    await this.dependencies.journalRepository.save(journal);

    // Publish domain event
    const event = new JournalCreatedEvent(journal);
    await this.dependencies.eventPublisher.publish(event);

    return journal.id;
  }

  /**
   * Post a journal (make it permanent)
   */
  async postJournal(command: PostJournalCommand): Promise<void> {
    // Get journal
    const journal = await this.dependencies.journalRepository.findById(command.journalId);
    if (!journal) {
      throw new Error(`Journal ${command.journalId} not found`);
    }

    if (journal.status !== 'DRAFT') {
      throw new Error('Only draft journals can be posted');
    }

    // Validate period is open
    const period = await this.dependencies.periodRepository.findByPeriod(
      journal.tenantId,
      journal.period
    );

    if (!period) {
      throw new Error(`Period ${journal.period} not found for tenant ${journal.tenantId}`);
    }

    if (period.status !== 'OPEN') {
      throw new Error(`Period ${journal.period} is not open`);
    }

    // Post the journal
    const postedJournal = (journal as JournalEntity).post(command.postedBy);

    // Save updated journal
    await this.dependencies.journalRepository.save(postedJournal);

    // Publish event
    const event = new JournalPostedEvent(
      postedJournal.id,
      postedJournal.tenantId,
      postedJournal.period,
      postedJournal.entries,
      postedJournal.totalDebit,
      postedJournal.totalCredit,
      postedJournal.source,
      command.postedBy
    );

    await this.dependencies.eventPublisher.publish(event);
  }

  /**
   * Get trial balance for period
   */
  async getTrialBalance(tenantId: TenantId, period: string): Promise<TrialBalance> {
    // Get all journals for period
    const journals = await this.dependencies.journalRepository.findByPeriod(tenantId, period);

    // Filter only posted journals
    const postedJournals = journals.filter(j => j.status === 'POSTED');

    // Calculate trial balance
    const entries = new Map<AccountId, { debit: number; credit: number }>();

    for (const journal of postedJournals) {
      for (const entry of journal.entries) {
        const current = entries.get(entry.accountId) || { debit: 0, credit: 0 };
        entries.set(entry.accountId, {
          debit: current.debit + entry.debit,
          credit: current.credit + entry.credit
        });
      }
    }

    // Get account details
    const trialBalanceEntries: TrialBalanceEntry[] = [];

    for (const [accountId, amounts] of entries.entries()) {
      const account = await this.dependencies.accountRepository.findById(accountId);
      if (account) {
        trialBalanceEntries.push({
          accountId,
          accountNumber: account.accountNumber,
          accountName: account.name,
          debit: amounts.debit,
          credit: amounts.credit,
          balance: amounts.debit - amounts.credit
        });
      }
    }

    // Calculate totals
    const totalDebit = trialBalanceEntries.reduce((sum, entry) => sum + entry.debit, 0);
    const totalCredit = trialBalanceEntries.reduce((sum, entry) => sum + entry.credit, 0);

    return {
      period,
      tenantId,
      entries: trialBalanceEntries,
      totalDebit,
      totalCredit,
      isBalanced: Math.abs(totalDebit - totalCredit) < 0.01,
      generatedAt: new Date()
    };
  }

  /**
   * Close an accounting period
   */
  async closePeriod(command: ClosePeriodCommand): Promise<void> {
    // Get period
    let period = await this.dependencies.periodRepository.findByPeriod(
      command.tenantId,
      command.period
    );

    if (!period) {
      // Create period if it doesn't exist
      period = AccountingPeriodEntity.create(command.tenantId, command.period);
    }

    if (period.status !== 'OPEN') {
      throw new Error(`Period ${command.period} is not open`);
    }

    // Get trial balance to ensure it's balanced
    const trialBalance = await this.getTrialBalance(command.tenantId, command.period);

    if (!trialBalance.isBalanced) {
      throw new Error(`Period ${command.period} is not balanced. Cannot close unbalanced period.`);
    }

    // Close the period
    const closedPeriod = (period as AccountingPeriodEntity).close(command.closedBy);

    // Save period
    await this.dependencies.periodRepository.save(closedPeriod);

    // Get journals for the period to count them
    const journals = await this.dependencies.journalRepository.findByPeriod(
      command.tenantId,
      command.period
    );

    // Publish event
    const event = new PeriodClosedEvent(
      closedPeriod.id,
      closedPeriod.tenantId,
      closedPeriod.period,
      command.closedBy,
      journals.length,
      trialBalance.totalDebit,
      trialBalance.totalCredit
    );

    await this.dependencies.eventPublisher.publish(event);
  }

  /**
   * Get journal by ID
   */
  async getJournal(journalId: JournalId): Promise<Journal | null> {
    return await this.dependencies.journalRepository.findById(journalId);
  }

  /**
   * List journals for tenant
   */
  async listJournals(tenantId: TenantId, period?: string): Promise<Journal[]> {
    if (period) {
      return await this.dependencies.journalRepository.findByPeriod(tenantId, period);
    }
    return await this.dependencies.journalRepository.findByTenant(tenantId);
  }

  /**
   * Validate journal command
   */
  private async validateJournalCommand(command: CreateJournalCommand): Promise<void> {
    // Check if period exists and is open
    const period = await this.dependencies.periodRepository.findByPeriod(
      command.tenantId,
      command.period
    );

    if (!period) {
      throw new Error(`Period ${command.period} not found for tenant ${command.tenantId}`);
    }

    if (period.status !== 'OPEN') {
      throw new Error(`Period ${command.period} is not open for posting`);
    }

    // Validate entries
    if (command.entries.length === 0) {
      throw new Error('Journal must have at least one entry');
    }

    // Check if entries balance
    const totalDebit = command.entries.reduce((sum, entry) => sum + entry.debit, 0);
    const totalCredit = command.entries.reduce((sum, entry) => sum + entry.credit, 0);

    if (Math.abs(totalDebit - totalCredit) > 0.01) {
      throw new Error('Journal entries must balance (debits must equal credits)');
    }

    // Validate accounts exist
    for (const entry of command.entries) {
      const account = await this.dependencies.accountRepository.findById(entry.accountId);
      if (!account) {
        throw new Error(`Account ${entry.accountId} not found`);
      }
      if (!account.isActive) {
        throw new Error(`Account ${entry.accountId} is not active`);
      }
    }
  }
}

// ===== FACTORY FUNCTION =====

export function createLedgerService(
  dependencies: LedgerServiceDependencies
): LedgerApplicationService {
  return new LedgerApplicationService(dependencies);
}