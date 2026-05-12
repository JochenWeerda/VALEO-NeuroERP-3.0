/**
 * FinanzBuchungPostgresRepository generated for FinanzBuchung using CRM migration toolkit.
 * Handles persistence with PostgreSQL using pg.Pool.
 */
import { Pool } from 'pg';
import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';
export declare class FinanzBuchungPostgresRepository {
    private readonly pool;
    constructor(pool: Pool);
    private mapRow;
    private static readonly LIST_SELECT;
    findById(id: string, tenantId: string): Promise<FinanzBuchung | null>;
    findByBuchungsnummer(tenantId: string, buchungsnummer: string): Promise<FinanzBuchung | null>;
    count(tenantId: string): Promise<number>;
    listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzBuchung[]>;
    list(tenantId: string): Promise<FinanzBuchung[]>;
    save(entity: FinanzBuchung): Promise<void>;
    update(entity: FinanzBuchung): Promise<void>;
    delete(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzBuchung-postgres.repository.d.ts.map