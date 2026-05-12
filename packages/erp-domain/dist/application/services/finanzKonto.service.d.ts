/**

 * Application service for FinanzKonto generated via CRM toolkit.

 * Encapsulates use-cases and translates primitives to domain entities.

 */
import { FinanzKonto } from '../../core/entities/finanzKonto.entity';
import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';
import { ListResult } from '../../presentation/types/api-pagination';
export interface CreateFinanzKontoDto {
    kontonummer: string;
    kontobezeichnung: string;
    kontotyp: string;
    kontenklasse?: string;
    kontengruppe?: string;
    ist_aktiv?: boolean;
    ist_steuerpflichtig?: boolean;
    steuersatz?: number;
    beschreibung?: string;
    erstellt_von?: string;
}
export type UpdateFinanzKontoDto = Partial<CreateFinanzKontoDto>;
export declare class FinanzKontoService {
    private readonly repository;
    constructor(repository: FinanzKontoPostgresRepository);
    list(tenantId: string): Promise<FinanzKonto[]>;
    listPaged(tenantId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<ListResult<FinanzKonto>>;
    findById(id: string, tenantId: string): Promise<FinanzKonto | null>;
    create(tenantId: string, payload: CreateFinanzKontoDto): Promise<FinanzKonto>;
    update(id: string, tenantId: string, payload: UpdateFinanzKontoDto): Promise<FinanzKonto>;
    remove(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzKonto.service.d.ts.map