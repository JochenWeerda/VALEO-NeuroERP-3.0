import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';
import { FinanzBuchungPostgresRepository } from '../../infrastructure/repositories/finanzBuchung-postgres.repository';
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
    list(): Promise<FinanzBuchung[]>;
    findById(id: string): Promise<FinanzBuchung | null>;
    create(payload: CreateFinanzBuchungDto): Promise<FinanzBuchung>;
    update(id: string, payload: UpdateFinanzBuchungDto): Promise<FinanzBuchung>;
    remove(id: string): Promise<void>;
}
//# sourceMappingURL=finanzBuchung.service.d.ts.map