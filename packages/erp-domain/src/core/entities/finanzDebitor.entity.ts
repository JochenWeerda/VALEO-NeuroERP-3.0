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

export class FinanzDebitor {
  private constructor(private readonly props: FinanzDebitorProps) {}

  public static create(props: FinanzDebitorProps): FinanzDebitor {
    return new FinanzDebitor(props);
  }

  public get id(): string | undefined {
    return this.props.id;
  }

  public get kundenId(): string | undefined {
    return this.props.kunden_id;
  }

  public get debitorNr(): string {
    return this.props.debitor_nr;
  }

  public get kreditlimit(): number | undefined {
    return this.props.kreditlimit;
  }

  public get zahlungsziel(): number | undefined {
    return this.props.zahlungsziel;
  }

  public get zahlungsart(): string | undefined {
    return this.props.zahlungsart;
  }

  public get bankverbindung(): string | undefined {
    return this.props.bankverbindung;
  }

  public get steuernummer(): string | undefined {
    return this.props.steuernummer;
  }

  public get ustId(): string | undefined {
    return this.props.ust_id;
  }

  public get istAktiv(): boolean | undefined {
    return this.props.ist_aktiv;
  }

  public get notizen(): string | undefined {
    return this.props.notizen;
  }

  public get erstelltVon(): string | undefined {
    return this.props.erstellt_von;
  }

  public get erstelltAm(): Date | undefined {
    return this.props.erstellt_am;
  }

  public get aktualisiertAm(): Date | undefined {
    return this.props.aktualisiert_am;
  }

  public toPrimitives(): FinanzDebitorProps {
    return { ...this.props };
  }
}
