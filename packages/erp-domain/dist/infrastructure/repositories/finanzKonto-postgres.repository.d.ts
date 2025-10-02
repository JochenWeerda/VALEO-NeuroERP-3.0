/**
 * FinanzKontoPostgresRepository implements persistence for the core account catalog.
 */
import { Pool } from 'pg';
import { FinanzKonto } from '../../core/entities/finanzKonto.entity';
export declare class FinanzKontoPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string): Promise<FinanzKonto | null>;
    findByKontonummer(kontonummer: string): Promise<FinanzKonto | null>;
    list(): Promise<FinanzKonto[]>;
    save(entity: FinanzKonto): Promise<FinanzKonto>;
    update(entity: FinanzKonto): Promise<FinanzKonto>;
    delete(id: string): Promise<void>;
}
//# sourceMappingURL=finanzKonto-postgres.repository.d.ts.map