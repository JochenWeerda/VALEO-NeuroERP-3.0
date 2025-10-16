export enum AuftragsbestaetigungStatus {
  OFFEN = 'OFFEN',
  GEPRUEFT = 'GEPRUEFT',
  BESTAETIGT = 'BESTAETIGT'
}

export class Auftragsbestaetigung {
  constructor(
    public readonly id: string,
    public readonly bestaetigungsNummer: string,
    public readonly bestellungId: string,
    public readonly status: AuftragsbestaetigungStatus,
    public readonly bestaetigteTermine: Array<{
      positionId: string
      bestaetigterTermin: Date
      abweichung?: string
    }>,
    public readonly preisabweichungen: Array<{
      positionId: string
      urspruenglicherPreis: number
      neuerPreis: number
      begruendung?: string
    }>,
    public readonly tenantId: string,
    public readonly bemerkungen?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    bestaetigungsNummer: string
    bestellungId: string
    bestaetigteTermine: Array<{
      positionId: string
      bestaetigterTermin: Date
      abweichung?: string
    }>
    preisabweichungen: Array<{
      positionId: string
      urspruenglicherPreis: number
      neuerPreis: number
      begruendung?: string
    }>
    tenantId: string
    bemerkungen?: string
  }): Auftragsbestaetigung {
    return new Auftragsbestaetigung(
      '', // ID wird generiert
      data.bestaetigungsNummer,
      data.bestellungId,
      AuftragsbestaetigungStatus.OFFEN,
      data.bestaetigteTermine,
      data.preisabweichungen,
      data.tenantId,
      data.bemerkungen
    )
  }

  pruefen(): Auftragsbestaetigung {
    if (this.status !== AuftragsbestaetigungStatus.OFFEN) {
      throw new Error('Nur offene Bestätigungen können geprüft werden')
    }
    return new Auftragsbestaetigung(
      this.id,
      this.bestaetigungsNummer,
      this.bestellungId,
      AuftragsbestaetigungStatus.GEPRUEFT,
      this.bestaetigteTermine,
      this.preisabweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  bestaetigen(): Auftragsbestaetigung {
    if (this.status !== AuftragsbestaetigungStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Bestätigungen können bestätigt werden')
    }
    return new Auftragsbestaetigung(
      this.id,
      this.bestaetigungsNummer,
      this.bestellungId,
      AuftragsbestaetigungStatus.BESTAETIGT,
      this.bestaetigteTermine,
      this.preisabweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  hatTerminabweichungen(): boolean {
    return this.bestaetigteTermine.some(t => t.abweichung !== undefined)
  }

  hatPreisabweichungen(): boolean {
    return this.preisabweichungen.some(p => p.urspruenglicherPreis !== p.neuerPreis)
  }

  getGesamtPreisabweichung(): number {
    return this.preisabweichungen.reduce((sum, p) => sum + (p.neuerPreis - p.urspruenglicherPreis), 0)
  }

  getTerminAbweichungenCount(): number {
    return this.bestaetigteTermine.filter(t => t.abweichung !== undefined).length
  }
}