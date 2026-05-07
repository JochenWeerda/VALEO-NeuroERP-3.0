import { Pool } from 'pg';
import { FinanzDebitor } from '../../core/entities/finanzDebitor.entity';
export declare class FinanzDebitorPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string): Promise<FinanzDebitor | null>;
    findByDebitorNr(debitorNr: string): Promise<FinanzDebitor | null>;
    list(): Promise<FinanzDebitor[]>;
    save(entity: FinanzDebitor): Promise<FinanzDebitor>;
    update(entity: FinanzDebitor): Promise<FinanzDebitor>;
    delete(id: string): Promise<void>;
}
//# sourceMappingURL=finanzDebitor-postgres.repository.d.ts.map