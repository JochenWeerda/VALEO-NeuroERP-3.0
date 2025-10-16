export enum AnfrageTyp {
  BANF = 'BANF', // Bedarfsanforderung
  ANF = 'ANF'    // Anfrage
}

export enum AnfrageStatus {
  ENTWURF = 'ENTWURF',
  FREIGEGEBEN = 'FREIGEGEBEN',
  ANGEBOTSPHASE = 'ANGEBOTSPHASE'
}

export enum Prioritaet {
  NIEDRIG = 'niedrig',
  NORMAL = 'normal',
  HOCH = 'hoch',
  DRINGEND = 'dringend'
}

export class Anfrage {
  constructor(
    public readonly id: string,
    public readonly anfrageNummer: string,
    public readonly typ: AnfrageTyp,
    public readonly anforderer: string,
    public readonly artikel: string,
    public readonly menge: number,
    public readonly einheit: string,
    public readonly prioritaet: Prioritaet,
    public readonly faelligkeit: Date,
    public readonly status: AnfrageStatus,
    public readonly begruendung: string,
    public readonly tenantId: string,
    public readonly kostenstelle?: string,
    public readonly projekt?: string,
    public readonly bemerkungen?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    anfrageNummer: string
    typ: AnfrageTyp
    anforderer: string
    artikel: string
    menge: number
    einheit: string
    prioritaet: Prioritaet
    faelligkeit: Date
    begruendung: string
    tenantId: string
    kostenstelle?: string
    projekt?: string
    bemerkungen?: string
  }): Anfrage {
    return new Anfrage(
      '', // ID wird generiert
      data.anfrageNummer,
      data.typ,
      data.anforderer,
      data.artikel,
      data.menge,
      data.einheit,
      data.prioritaet,
      data.faelligkeit,
      AnfrageStatus.ENTWURF,
      data.begruendung,
      data.tenantId,
      data.kostenstelle,
      data.projekt,
      data.bemerkungen
    )
  }

  freigeben(): Anfrage {
    if (this.status !== AnfrageStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können freigegeben werden')
    }
    return new Anfrage(
      this.id,
      this.anfrageNummer,
      this.typ,
      this.anforderer,
      this.artikel,
      this.menge,
      this.einheit,
      this.prioritaet,
      this.faelligkeit,
      AnfrageStatus.FREIGEGEBEN,
      this.begruendung,
      this.tenantId,
      this.kostenstelle,
      this.projekt,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  inAngebotsphase(): Anfrage {
    if (this.status !== AnfrageStatus.FREIGEGEBEN) {
      throw new Error('Nur freigegebene Anfragen können in Angebotsphase wechseln')
    }
    return new Anfrage(
      this.id,
      this.anfrageNummer,
      this.typ,
      this.anforderer,
      this.artikel,
      this.menge,
      this.einheit,
      this.prioritaet,
      this.faelligkeit,
      AnfrageStatus.ANGEBOTSPHASE,
      this.begruendung,
      this.tenantId,
      this.kostenstelle,
      this.projekt,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  istUeberfaellig(): boolean {
    return new Date() > this.faelligkeit
  }

  istDringend(): boolean {
    return this.prioritaet === Prioritaet.DRINGEND
  }

  getTageBisFaelligkeit(): number {
    const diffTime = this.faelligkeit.getTime() - new Date().getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }
}