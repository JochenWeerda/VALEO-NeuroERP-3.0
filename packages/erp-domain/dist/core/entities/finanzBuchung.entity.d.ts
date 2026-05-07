/**
 * FinanzBuchung domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
export interface FinanzBuchungProps {
    id?: string;
    buchungsnummer: string;
    buchungsdatum: Date;
    belegdatum: Date;
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
    erstellt_am?: Date;
    aktualisiert_am?: Date;
}
export declare class FinanzBuchung {
    private readonly props;
    private constructor();
    static create(props: FinanzBuchungProps): FinanzBuchung;
    get id(): string | undefined;
    get buchungsnummer(): string;
    get buchungsdatum(): Date;
    get belegdatum(): Date;
    get belegnummer(): string | undefined;
    get buchungstext(): string;
    get sollkonto(): string | undefined;
    get habenkonto(): string | undefined;
    get betrag(): number;
    get waehrung(): string | undefined;
    get steuerbetrag(): number | undefined;
    get steuersatz(): number | undefined;
    get buchungsart(): string | undefined;
    get referenzTyp(): string | undefined;
    get referenzId(): string | undefined;
    get istStorniert(): boolean | undefined;
    get stornoBuchungId(): string | undefined;
    get erstelltVon(): string | undefined;
    get erstelltAm(): Date | undefined;
    get aktualisiertAm(): Date | undefined;
    toPrimitives(): FinanzBuchungProps;
}
//# sourceMappingURL=finanzBuchung.entity.d.ts.map