/**
 * FinanzKreditor domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
export interface FinanzKreditorProps {
    id?: string;
    lieferanten_id?: string;
    kreditor_nr: string;
    zahlungsziel?: number;
    zahlungsart?: string;
    bankverbindung?: string;
    steuernummer?: string;
    ust_id?: string;
    ist_aktiv?: boolean;
    notizen?: string;
    erstellt_von?: string;
    erstellt_am?: Date;
    aktualisiert_am?: Date;
}
export declare class FinanzKreditor {
    private readonly props;
    private constructor();
    static create(props: FinanzKreditorProps): FinanzKreditor;
    get id(): string | undefined;
    get lieferantenId(): string | undefined;
    get kreditorNr(): string;
    get zahlungsziel(): number | undefined;
    get zahlungsart(): string | undefined;
    get bankverbindung(): string | undefined;
    get steuernummer(): string | undefined;
    get ustId(): string | undefined;
    get istAktiv(): boolean | undefined;
    get notizen(): string | undefined;
    get erstelltVon(): string | undefined;
    get erstelltAm(): Date | undefined;
    get aktualisiertAm(): Date | undefined;
    toPrimitives(): FinanzKreditorProps;
}
//# sourceMappingURL=finanzKreditor.entity.d.ts.map