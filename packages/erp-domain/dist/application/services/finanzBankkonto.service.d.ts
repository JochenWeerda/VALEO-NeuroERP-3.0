import { FinanzBankkonto } from '../../core/entities/finanzBankkonto.entity';
import { FinanzBankkontoPostgresRepository } from '../../infrastructure/repositories/finanzBankkonto-postgres.repository';
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
    list(): Promise<FinanzBankkonto[]>;
    findById(id: string): Promise<FinanzBankkonto | null>;
    create(payload: CreateFinanzBankkontoDto): Promise<FinanzBankkonto>;
    update(id: string, payload: UpdateFinanzBankkontoDto): Promise<FinanzBankkonto>;
    remove(id: string): Promise<void>;
}
//# sourceMappingURL=finanzBankkonto.service.d.ts.map