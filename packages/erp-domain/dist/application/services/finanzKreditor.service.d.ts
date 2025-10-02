import { FinanzKreditor } from '../../core/entities/finanzKreditor.entity';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
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
    list(): Promise<FinanzKreditor[]>;
    findById(id: string): Promise<FinanzKreditor | null>;
    create(payload: CreateFinanzKreditorDto): Promise<FinanzKreditor>;
    update(id: string, payload: UpdateFinanzKreditorDto): Promise<FinanzKreditor>;
    remove(id: string): Promise<void>;
}
//# sourceMappingURL=finanzKreditor.service.d.ts.map