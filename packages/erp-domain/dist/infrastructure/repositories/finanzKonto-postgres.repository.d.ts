/**
 * FinanzKontoPostgresRepository implements persistence for the core account catalog.
 */
import { Pool } from 'pg';
import { FinanzKonto } from '../../core/entities/finanzKonto.entity';
export declare class FinanzKontoPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string, tenantId: string): Promise<FinanzKonto | null>;
    findByKontonummer(tenantId: string, kontonummer: string): Promise<FinanzKonto | null>;
    count(tenantId: string): Promise<number>;
    listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzKonto[]>;
    list(tenantId: string): Promise<FinanzKonto[]>;
    save(entity: FinanzKonto): Promise<FinanzKonto>;
    update(entity: FinanzKonto): Promise<FinanzKonto>;
    delete(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzKonto-postgres.repository.d.ts.map