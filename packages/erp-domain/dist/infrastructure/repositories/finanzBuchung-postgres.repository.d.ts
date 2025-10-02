/**
 * FinanzBuchungPostgresRepository generated for FinanzBuchung using CRM migration toolkit.
 * Handles persistence with PostgreSQL using pg.Pool.
 * Start simple: find -> save -> update -> delete -> list. Extend for joins later.
 */
import { Pool } from 'pg';
import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';
export declare class FinanzBuchungPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    findById(id: string): Promise<FinanzBuchung | null>;
    list(): Promise<FinanzBuchung[]>;
    save(entity: FinanzBuchung): Promise<void>;
    update(entity: FinanzBuchung): Promise<void>;
    delete(id: string): Promise<void>;
}
//# sourceMappingURL=finanzBuchung-postgres.repository.d.ts.map