import { FinanzDebitor } from '../../core/entities/finanzDebitor.entity';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';
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
    list(): Promise<FinanzDebitor[]>;
    findById(id: string): Promise<FinanzDebitor | null>;
    create(payload: CreateFinanzDebitorDto): Promise<FinanzDebitor>;
    update(id: string, payload: UpdateFinanzDebitorDto): Promise<FinanzDebitor>;
    remove(id: string): Promise<void>;
}
//# sourceMappingURL=finanzDebitor.service.d.ts.map