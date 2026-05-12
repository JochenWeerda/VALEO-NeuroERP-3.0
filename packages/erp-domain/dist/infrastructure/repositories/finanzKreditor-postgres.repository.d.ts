import { Pool } from 'pg';
import { FinanzKreditor } from '../../core/entities/finanzKreditor.entity';
export declare class FinanzKreditorPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string, tenantId: string): Promise<FinanzKreditor | null>;
    findByKreditorNr(tenantId: string, kreditorNr: string): Promise<FinanzKreditor | null>;
    count(tenantId: string): Promise<number>;
    listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzKreditor[]>;
    list(tenantId: string): Promise<FinanzKreditor[]>;
    save(entity: FinanzKreditor): Promise<FinanzKreditor>;
    update(entity: FinanzKreditor): Promise<FinanzKreditor>;
    delete(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzKreditor-postgres.repository.d.ts.map