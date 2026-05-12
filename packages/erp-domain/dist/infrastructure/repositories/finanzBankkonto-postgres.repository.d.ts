import { Pool } from 'pg';
import { FinanzBankkonto } from '../../core/entities/finanzBankkonto.entity';
export declare class FinanzBankkontoPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string, tenantId: string): Promise<FinanzBankkonto | null>;
    count(tenantId: string): Promise<number>;
    listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzBankkonto[]>;
    list(tenantId: string): Promise<FinanzBankkonto[]>;
    save(entity: FinanzBankkonto): Promise<FinanzBankkonto>;
    update(entity: FinanzBankkonto): Promise<FinanzBankkonto>;
    delete(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzBankkonto-postgres.repository.d.ts.map