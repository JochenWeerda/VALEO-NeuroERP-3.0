import { FinanzKreditor } from '../../core/entities/finanzKreditor.entity';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
import { ListResult } from '../../presentation/types/api-pagination';
export interface CreateFinanzKreditorDto {
    lieferanten_id?: string;
    kreditor_nr: string;
    zahlungsziel?: number;
    zahlungsart?: string;
    bankverbindung?: string;
    steuer_id?: string;
    steuernummer?: string;
    ist_aktiv?: boolean;
    notizen?: string;
    erstellt_von?: string;
}
export type UpdateFinanzKreditorDto = Partial<CreateFinanzKreditorDto>;
export declare class FinanzKreditorService {
    private readonly repository;
    constructor(repository: FinanzKreditorPostgresRepository);
    list(tenantId: string): Promise<FinanzKreditor[]>;
    listPaged(tenantId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<ListResult<FinanzKreditor>>;
    findById(id: string, tenantId: string): Promise<FinanzKreditor | null>;
    create(tenantId: string, payload: CreateFinanzKreditorDto): Promise<FinanzKreditor>;
    update(id: string, tenantId: string, payload: UpdateFinanzKreditorDto): Promise<FinanzKreditor>;
    remove(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzKreditor.service.d.ts.map