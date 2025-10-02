/**
 * FinanzKonto domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
export interface FinanzKontoProps {
    id?: string;
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
    erstellt_am?: Date;
    aktualisiert_am?: Date;
}
export declare class FinanzKonto {
    private readonly props;
    private constructor();
    static create(props: FinanzKontoProps): FinanzKonto;
    get id(): string | undefined;
    get kontonummer(): string;
    get kontobezeichnung(): string;
    get kontotyp(): string;
    get kontenklasse(): string | undefined;
    get kontengruppe(): string | undefined;
    get istAktiv(): boolean | undefined;
    get istSteuerpflichtig(): boolean | undefined;
    get steuersatz(): number | undefined;
    get beschreibung(): string | undefined;
    get erstelltVon(): string | undefined;
    get erstelltAm(): Date | undefined;
    get aktualisiertAm(): Date | undefined;
    toPrimitives(): FinanzKontoProps;
}
//# sourceMappingURL=finanzKonto.entity.d.ts.map