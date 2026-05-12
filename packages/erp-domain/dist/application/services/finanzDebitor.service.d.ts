import { FinanzDebitor } from '../../core/entities/finanzDebitor.entity';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';
import { ListResult } from '../../presentation/types/api-pagination';
export interface CreateFinanzDebitorDto {
    kunden_id?: string;
    debitor_nr: string;
    kreditlimit?: number;
    zahlungsziel?: number;
    zahlungsart?: string;
    bankverbindung?: string;
    steuernummer?: string;
    ust_id?: string;
    ist_aktiv?: boolean;
    notizen?: string;
    erstellt_von?: string;
}
export type UpdateFinanzDebitorDto = Partial<CreateFinanzDebitorDto>;
export declare class FinanzDebitorService {
    private readonly repository;
    constructor(repository: FinanzDebitorPostgresRepository);
    list(tenantId: string): Promise<FinanzDebitor[]>;
    listPaged(tenantId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<ListResult<FinanzDebitor>>;
    findById(id: string, tenantId: string): Promise<FinanzDebitor | null>;
    create(tenantId: string, payload: CreateFinanzDebitorDto): Promise<FinanzDebitor>;
    update(id: string, tenantId: string, payload: UpdateFinanzDebitorDto): Promise<FinanzDebitor>;
    remove(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzDebitor.service.d.ts.map