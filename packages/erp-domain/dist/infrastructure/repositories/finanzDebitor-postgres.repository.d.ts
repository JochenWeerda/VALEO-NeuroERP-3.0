import { Pool } from 'pg';
import { FinanzDebitor } from '../../core/entities/finanzDebitor.entity';
export declare class FinanzDebitorPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string, tenantId: string): Promise<FinanzDebitor | null>;
    findByDebitorNr(tenantId: string, debitorNr: string): Promise<FinanzDebitor | null>;
    count(tenantId: string): Promise<number>;
    listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzDebitor[]>;
    list(tenantId: string): Promise<FinanzDebitor[]>;
    save(entity: FinanzDebitor): Promise<FinanzDebitor>;
    update(entity: FinanzDebitor): Promise<FinanzDebitor>;
    delete(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzDebitor-postgres.repository.d.ts.map