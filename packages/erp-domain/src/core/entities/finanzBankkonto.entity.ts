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

export class FinanzBankkonto {
  private constructor(private readonly props: FinanzBankkontoProps) {}

  public static create(props: FinanzBankkontoProps): FinanzBankkonto {
    return new FinanzBankkonto(props);
  }

  public get id(): string | undefined {
    return this.props.id;
  }

  public get kontoname(): string {
    return this.props.kontoname;
  }

  public get bankname(): string {
    return this.props.bankname;
  }

  public get iban(): string | undefined {
    return this.props.iban;
  }

  public get bic(): string | undefined {
    return this.props.bic;
  }

  public get kontonummer(): string | undefined {
    return this.props.kontonummer;
  }

  public get blz(): string | undefined {
    return this.props.blz;
  }

  public get waehrung(): string | undefined {
    return this.props.waehrung;
  }

  public get kontostand(): number | undefined {
    return this.props.kontostand;
  }

  public get letzterAbgleich(): Date | undefined {
    return this.props.letzter_abgleich;
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

  public toPrimitives(): FinanzBankkontoProps {
    return { ...this.props };
  }
}
