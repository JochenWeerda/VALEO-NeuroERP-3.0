export enum AnlieferavisStatus {
  GESENDET = 'GESENDET',
  BESTAETIGT = 'BESTAETIGT',
  STORNIERT = 'STORNIERT'
}

export class Anlieferavis {
  constructor(
    public readonly id: string,
    public readonly avisNummer: string,
    public readonly bestellungId: string,
    public readonly status: AnlieferavisStatus,
    public readonly geplantesAnlieferDatum: Date,
    public readonly fahrzeug: {
      kennzeichen: string
      fahrer: string
      telefon?: string
    },
    public readonly positionen: Array<{
      positionId: string
      menge: number
      chargenNummer?: string
      verpackung?: string
    }>,
    public readonly tenantId: string,
    public readonly bemerkungen?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    avisNummer: string
    bestellungId: string
    geplantesAnlieferDatum: Date
    fahrzeug: {
      kennzeichen: string
      fahrer: string
      telefon?: string
    }
    positionen: Array<{
      positionId: string
      menge: number
      chargenNummer?: string
      verpackung?: string
    }>
    tenantId: string
    bemerkungen?: string
  }): Anlieferavis {
    return new Anlieferavis(
      '', // ID wird generiert
      data.avisNummer,
      data.bestellungId,
      AnlieferavisStatus.GESENDET,
      data.geplantesAnlieferDatum,
      data.fahrzeug,
      data.positionen,
      data.tenantId,
      data.bemerkungen
    )
  }

  bestaetigen(): Anlieferavis {
    if (this.status !== AnlieferavisStatus.GESENDET) {
      throw new Error('Nur gesendete Avise können bestätigt werden')
    }
    return new Anlieferavis(
      this.id,
      this.avisNummer,
      this.bestellungId,
      AnlieferavisStatus.BESTAETIGT,
      this.geplantesAnlieferDatum,
      this.fahrzeug,
      this.positionen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  stornieren(): Anlieferavis {
    if (this.status === AnlieferavisStatus.STORNIERT) {
      throw new Error('Avis ist bereits storniert')
    }
    return new Anlieferavis(
      this.id,
      this.avisNummer,
      this.bestellungId,
      AnlieferavisStatus.STORNIERT,
      this.geplantesAnlieferDatum,
      this.fahrzeug,
      this.positionen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  istUeberfaellig(): boolean {
    return new Date() > this.geplantesAnlieferDatum
  }

  getTageBisAnlieferung(): number {
    const diffTime = this.geplantesAnlieferDatum.getTime() - new Date().getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  getGesamtMenge(): number {
    return this.positionen.reduce((sum, pos) => sum + pos.menge, 0)
  }

  hatChargenInformationen(): boolean {
    return this.positionen.some(pos => pos.chargenNummer !== undefined)
  }
}