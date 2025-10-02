import { Pool } from 'pg';
import { FinanzKreditor } from '../../core/entities/finanzKreditor.entity';
export declare class FinanzKreditorPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string): Promise<FinanzKreditor | null>;
    findByKreditorNr(kreditorNr: string): Promise<FinanzKreditor | null>;
    list(): Promise<FinanzKreditor[]>;
    save(entity: FinanzKreditor): Promise<FinanzKreditor>;
    update(entity: FinanzKreditor): Promise<FinanzKreditor>;
    delete(id: string): Promise<void>;
}
//# sourceMappingURL=finanzKreditor-postgres.repository.d.ts.map