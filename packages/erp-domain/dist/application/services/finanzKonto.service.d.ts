/**
 * Application service for FinanzKonto generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
import { FinanzKonto } from '../../core/entities/finanzKonto.entity';
import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';
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
    list(): Promise<FinanzKonto[]>;
    findById(id: string): Promise<FinanzKonto | null>;
    create(payload: CreateFinanzKontoDto): Promise<FinanzKonto>;
    update(id: string, payload: UpdateFinanzKontoDto): Promise<FinanzKonto>;
    remove(id: string): Promise<void>;
}
//# sourceMappingURL=finanzKonto.service.d.ts.map