import { FinanzBankkonto } from '../../core/entities/finanzBankkonto.entity';
import { FinanzBankkontoPostgresRepository } from '../../infrastructure/repositories/finanzBankkonto-postgres.repository';
import { ListResult } from '../../presentation/types/api-pagination';
export interface CreateFinanzBankkontoDto {
    kontoname: string;
    bankname: string;
    iban?: string;
    bic?: string;
    kontonummer?: string;
    blz?: string;
    waehrung?: string;
    kontostand?: number;
    letzter_abgleich?: string | Date;
    ist_aktiv?: boolean;
    notizen?: string;
    erstellt_von?: string;
}
export type UpdateFinanzBankkontoDto = Partial<CreateFinanzBankkontoDto>;
export declare class FinanzBankkontoService {
    private readonly repository;
    constructor(repository: FinanzBankkontoPostgresRepository);
    list(tenantId: string): Promise<FinanzBankkonto[]>;
    listPaged(tenantId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<ListResult<FinanzBankkonto>>;
    findById(id: string, tenantId: string): Promise<FinanzBankkonto | null>;
    create(tenantId: string, payload: CreateFinanzBankkontoDto): Promise<FinanzBankkonto>;
    update(id: string, tenantId: string, payload: UpdateFinanzBankkontoDto): Promise<FinanzBankkonto>;
    remove(id: string, tenantId: string): Promise<void>;
}
//# sourceMappingURL=finanzBankkonto.service.d.ts.map