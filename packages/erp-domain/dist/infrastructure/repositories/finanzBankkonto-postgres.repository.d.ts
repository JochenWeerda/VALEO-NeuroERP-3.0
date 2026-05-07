import { Pool } from 'pg';
import { FinanzBankkonto } from '../../core/entities/finanzBankkonto.entity';
export declare class FinanzBankkontoPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string): Promise<FinanzBankkonto | null>;
    list(): Promise<FinanzBankkonto[]>;
    save(entity: FinanzBankkonto): Promise<FinanzBankkonto>;
    update(entity: FinanzBankkonto): Promise<FinanzBankkonto>;
    delete(id: string): Promise<void>;
}
//# sourceMappingURL=finanzBankkonto-postgres.repository.d.ts.map