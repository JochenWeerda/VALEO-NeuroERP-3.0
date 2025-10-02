/**
 * VALEO NeuroERP 3.0 - Finance Domain - Ledger Service
 *
 * Application Service for Ledger operations following Clean Architecture
 * Sprint 1 Implementation: Core ledger functionality
 */
import { AccountRepository, AccountingPeriodRepository, ClosePeriodCommand, CreateJournalCommand, Journal, JournalId, JournalRepository, PostJournalCommand, TenantId, TrialBalance } from '../../core/entities/ledger';
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
export declare class LedgerApplicationService implements LedgerService {
    private readonly dependencies;
    constructor(dependencies: LedgerServiceDependencies);
    /**
     * Create a new journal
     */
    createJournal(command: CreateJournalCommand): Promise<JournalId>;
    /**
     * Post a journal (make it permanent)
     */
    postJournal(command: PostJournalCommand): Promise<void>;
    /**
     * Get trial balance for period
     */
    getTrialBalance(tenantId: TenantId, period: string): Promise<TrialBalance>;
    /**
     * Close an accounting period
     */
    closePeriod(command: ClosePeriodCommand): Promise<void>;
    /**
     * Get journal by ID
     */
    getJournal(journalId: JournalId): Promise<Journal | null>;
    /**
     * List journals for tenant
     */
    listJournals(tenantId: TenantId, period?: string): Promise<Journal[]>;
    /**
     * Validate journal command
     */
    private validateJournalCommand;
}
export declare function createLedgerService(dependencies: LedgerServiceDependencies): LedgerApplicationService;
//# sourceMappingURL=ledger-service.d.ts.map