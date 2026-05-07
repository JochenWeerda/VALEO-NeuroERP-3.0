/**
 * FinanzDebitor domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
export interface FinanzDebitorProps {
    id?: string;
    kunden_id?: string;
    debitor_nr: string;
    kreditlimit?: number;
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
export declare class FinanzDebitor {
    private readonly props;
    private constructor();
    static create(props: FinanzDebitorProps): FinanzDebitor;
    get id(): string | undefined;
    get kundenId(): string | undefined;
    get debitorNr(): string;
    get kreditlimit(): number | undefined;
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
    toPrimitives(): FinanzDebitorProps;
}
//# sourceMappingURL=finanzDebitor.entity.d.ts.map