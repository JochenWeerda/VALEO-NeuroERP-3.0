import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';
import { FinanzBuchungPostgresRepository } from '../../infrastructure/repositories/finanzBuchung-postgres.repository';
import { ListResult } from '../../presentation/types/api-pagination';
export interface CreateFinanzBuchungDto {
    buchungsnummer?: string;
    buchungsdatum: string | Date;
    belegdatum: string | Date;
    belegnummer?: string;
    buchungstext: string;
    sollkonto?: string;
    habenkonto?: string;
    betrag: number;
    waehrung?: string;
    steuerbetrag?: number;
    steuersatz?: number;
    buchungsart?: string;
    referenz_typ?: string;
    referenz_id?: string;
    ist_storniert?: boolean;
    storno_buchung_id?: string;
    erstellt_von?: string;
}
export type UpdateFinanzBuchungDto = Partial<CreateFinanzBuchungDto>;
export declare class FinanzBuchungService {
    private readonly repository;
    constructor(repository: FinanzBuchungPostgresRepository);
    list(tenantId: string): Promise<FinanzBuchung[]>;
    listPaged(tenantId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<ListResult<FinanzBuchung>>;
    findById(id: string, tenantId: string): Promise<FinanzBuchung | null>;
    create(tenantId: string, payload: CreateFinanzBuchungDto): Promise<FinanzBuchung>;
    update(id: string, tenantId: string, payload: UpdateFinanzBuchungDto): Promise<FinanzBuchung>;
    remove(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzBuchung.service.d.ts.map