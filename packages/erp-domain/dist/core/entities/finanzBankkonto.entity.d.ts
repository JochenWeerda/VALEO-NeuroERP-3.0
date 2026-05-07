/**
 * FinanzBankkonto domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
export interface FinanzBankkontoProps {
    id?: string;
    kontoname: string;
    bankname: string;
    iban?: string;
    bic?: string;
    kontonummer?: string;
    blz?: string;
    waehrung?: string;
    kontostand?: number;
    letzter_abgleich?: Date;
    ist_aktiv?: boolean;
    notizen?: string;
    erstellt_von?: string;
    erstellt_am?: Date;
    aktualisiert_am?: Date;
}
export declare class FinanzBankkonto {
    private readonly props;
    private constructor();
    static create(props: FinanzBankkontoProps): FinanzBankkonto;
    get id(): string | undefined;
    get kontoname(): string;
    get bankname(): string;
    get iban(): string | undefined;
    get bic(): string | undefined;
    get kontonummer(): string | undefined;
    get blz(): string | undefined;
    get waehrung(): string | undefined;
    get kontostand(): number | undefined;
    get letzterAbgleich(): Date | undefined;
    get istAktiv(): boolean | undefined;
    get notizen(): string | undefined;
    get erstelltVon(): string | undefined;
    get erstelltAm(): Date | undefined;
    get aktualisiertAm(): Date | undefined;
    toPrimitives(): FinanzBankkontoProps;
}
//# sourceMappingURL=finanzBankkonto.entity.d.ts.map