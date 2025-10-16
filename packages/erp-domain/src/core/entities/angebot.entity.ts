export enum AngebotStatus {
  ERFASST = 'ERFASST',
  GEPRUEFT = 'GEPRUEFT',
  GENEHMIGT = 'GENEHMIGT',
  ABGELEHNT = 'ABGELEHNT'
}

export class Angebot {
  constructor(
    public readonly id: string,
    public readonly angebotNummer: string,
    public readonly anfrageId: string | null,
    public readonly lieferantId: string,
    public readonly artikel: string,
    public readonly menge: number,
    public readonly einheit: string,
    public readonly preis: number,
    public readonly waehrung: string,
    public readonly lieferzeit: number, // in Tagen
    public readonly gueltigBis: Date,
    public readonly status: AngebotStatus,
    public readonly tenantId: string,
    public readonly mindestabnahme?: number,
    public readonly zahlungsbedingungen?: string,
    public readonly incoterms?: string,
    public readonly bemerkungen?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    angebotNummer: string
    anfrageId?: string
    lieferantId: string
    artikel: string
    menge: number
    einheit: string
    preis: number
    waehrung: string
    lieferzeit: number
    gueltigBis: Date
    tenantId: string
    mindestabnahme?: number
    zahlungsbedingungen?: string
    incoterms?: string
    bemerkungen?: string
  }): Angebot {
    return new Angebot(
      '', // ID wird generiert
      data.angebotNummer,
      data.anfrageId || null,
      data.lieferantId,
      data.artikel,
      data.menge,
      data.einheit,
      data.preis,
      data.waehrung,
      data.lieferzeit,
      data.gueltigBis,
      AngebotStatus.ERFASST,
      data.tenantId,
      data.mindestabnahme,
      data.zahlungsbedingungen,
      data.incoterms,
      data.bemerkungen
    )
  }

  pruefen(): Angebot {
    if (this.status !== AngebotStatus.ERFASST) {
      throw new Error('Nur erfasste Angebote können geprüft werden')
    }
    return new Angebot(
      this.id,
      this.angebotNummer,
      this.anfrageId,
      this.lieferantId,
      this.artikel,
      this.menge,
      this.einheit,
      this.preis,
      this.waehrung,
      this.lieferzeit,
      this.gueltigBis,
      AngebotStatus.GEPRUEFT,
      this.tenantId,
      this.mindestabnahme,
      this.zahlungsbedingungen,
      this.incoterms,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  genehmigen(): Angebot {
    if (this.status !== AngebotStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Angebote können genehmigt werden')
    }
    return new Angebot(
      this.id,
      this.angebotNummer,
      this.anfrageId,
      this.lieferantId,
      this.artikel,
      this.menge,
      this.einheit,
      this.preis,
      this.waehrung,
      this.lieferzeit,
      this.gueltigBis,
      AngebotStatus.GENEHMIGT,
      this.tenantId,
      this.mindestabnahme,
      this.zahlungsbedingungen,
      this.incoterms,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  ablehnen(): Angebot {
    if (this.status === AngebotStatus.ABGELEHNT) {
      throw new Error('Angebot ist bereits abgelehnt')
    }
    return new Angebot(
      this.id,
      this.angebotNummer,
      this.anfrageId,
      this.lieferantId,
      this.artikel,
      this.menge,
      this.einheit,
      this.preis,
      this.waehrung,
      this.lieferzeit,
      this.gueltigBis,
      AngebotStatus.ABGELEHNT,
      this.tenantId,
      this.mindestabnahme,
      this.zahlungsbedingungen,
      this.incoterms,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  istAbgelaufen(): boolean {
    return new Date() > this.gueltigBis
  }

  getTageBisAblauf(): number {
    const diffTime = this.gueltigBis.getTime() - new Date().getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  getGesamtPreis(): number {
    return this.menge * this.preis
  }

  hatAnfrage(): boolean {
    return this.anfrageId !== null
  }
}