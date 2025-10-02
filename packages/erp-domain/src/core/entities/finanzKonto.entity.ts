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

export class FinanzKonto {
  private constructor(private readonly props: FinanzKontoProps) {}

  public static create(props: FinanzKontoProps): FinanzKonto {
    return new FinanzKonto(props);
  }

  public get id(): string | undefined {
    return this.props.id;
  }

  public get kontonummer(): string {
    return this.props.kontonummer;
  }

  public get kontobezeichnung(): string {
    return this.props.kontobezeichnung;
  }

  public get kontotyp(): string {
    return this.props.kontotyp;
  }

  public get kontenklasse(): string | undefined {
    return this.props.kontenklasse;
  }

  public get kontengruppe(): string | undefined {
    return this.props.kontengruppe;
  }

  public get istAktiv(): boolean | undefined {
    return this.props.ist_aktiv;
  }

  public get istSteuerpflichtig(): boolean | undefined {
    return this.props.ist_steuerpflichtig;
  }

  public get steuersatz(): number | undefined {
    return this.props.steuersatz;
  }

  public get beschreibung(): string | undefined {
    return this.props.beschreibung;
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

  public toPrimitives(): FinanzKontoProps {
    return { ...this.props };
  }
}
