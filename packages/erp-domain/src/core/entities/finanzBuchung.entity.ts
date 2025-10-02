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

export class FinanzBuchung {
  private constructor(private readonly props: FinanzBuchungProps) {}

  public static create(props: FinanzBuchungProps): FinanzBuchung {
    return new FinanzBuchung(props);
  }

  public get id(): string | undefined {
    return this.props.id;
  }

  public get buchungsnummer(): string {
    return this.props.buchungsnummer;
  }

  public get buchungsdatum(): Date {
    return this.props.buchungsdatum;
  }

  public get belegdatum(): Date {
    return this.props.belegdatum;
  }

  public get belegnummer(): string | undefined {
    return this.props.belegnummer;
  }

  public get buchungstext(): string {
    return this.props.buchungstext;
  }

  public get sollkonto(): string | undefined {
    return this.props.sollkonto;
  }

  public get habenkonto(): string | undefined {
    return this.props.habenkonto;
  }

  public get betrag(): number {
    return this.props.betrag;
  }

  public get waehrung(): string | undefined {
    return this.props.waehrung;
  }

  public get steuerbetrag(): number | undefined {
    return this.props.steuerbetrag;
  }

  public get steuersatz(): number | undefined {
    return this.props.steuersatz;
  }

  public get buchungsart(): string | undefined {
    return this.props.buchungsart;
  }

  public get referenzTyp(): string | undefined {
    return this.props.referenz_typ;
  }

  public get referenzId(): string | undefined {
    return this.props.referenz_id;
  }

  public get istStorniert(): boolean | undefined {
    return this.props.ist_storniert;
  }

  public get stornoBuchungId(): string | undefined {
    return this.props.storno_buchung_id;
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

  public toPrimitives(): FinanzBuchungProps {
    return { ...this.props };
  }
}
