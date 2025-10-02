/**
 * VALEO NeuroERP 3.0 - Finance Domain - PostgreSQL Ledger Repository
 *
 * Infrastructure layer implementation for ledger data access
 * Following Repository pattern and Clean Architecture
 */
import { AccountId, AccountRepository, AccountingPeriod, AccountingPeriodRepository, Journal, JournalId, JournalRepository, PeriodId, TenantId } from '../../core/entities/ledger';
export interface PostgresConnection {
    query<T = any>(query: string, params?: any[]): Promise<{
        rows: T[];
        rowCount: number;
    }>;
    transaction<T>(callback: (client: any) => Promise<T>): Promise<T>;
}
export declare class PostgresJournalRepository implements JournalRepository {
    private readonly db;
    constructor(db: PostgresConnection);
    findById(id: JournalId): Promise<Journal | null>;
    findByPeriod(tenantId: TenantId, period: string): Promise<Journal[]>;
    findByTenant(tenantId: TenantId): Promise<Journal[]>;
    save(journal: Journal): Promise<void>;
    findUnbalancedJournals(tenantId: TenantId): Promise<Journal[]>;
    private findEntriesByJournalId;
}
export declare class PostgresAccountRepository implements AccountRepository {
    private readonly db;
    constructor(db: PostgresConnection);
    findById(id: AccountId): Promise<any | null>;
    findByAccountNumber(accountNumber: string): Promise<any | null>;
    findByType(type: string): Promise<any[]>;
    findChartOfAccounts(tenantId: TenantId): Promise<any[]>;
    save(account: any): Promise<void>;
    private mapRowToAccount;
}
export declare class PostgresAccountingPeriodRepository implements AccountingPeriodRepository {
    private readonly db;
    constructor(db: PostgresConnection);
    findById(id: PeriodId): Promise<AccountingPeriod | null>;
    findByPeriod(tenantId: TenantId, period: string): Promise<AccountingPeriod | null>;
    findOpenPeriods(tenantId: TenantId): Promise<AccountingPeriod[]>;
    save(period: AccountingPeriod): Promise<void>;
    private mapRowToPeriod;
}
export declare function createPostgresJournalRepository(db: PostgresConnection): JournalRepository;
export declare function createPostgresAccountRepository(db: PostgresConnection): AccountRepository;
export declare function createPostgresPeriodRepository(db: PostgresConnection): AccountingPeriodRepository;
//# sourceMappingURL=postgres-ledger-repository.d.ts.map