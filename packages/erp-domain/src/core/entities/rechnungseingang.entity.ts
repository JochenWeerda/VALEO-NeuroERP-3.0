export enum RechnungseingangStatus {
  ERFASST = 'ERFASST',
  GEPRUEFT = 'GEPRUEFT',
  FREIGEGEBEN = 'FREIGEGEBEN',
  VERBUCHT = 'VERBUCHT',
  BEZAHLT = 'BEZAHLT'
}

export class Rechnungseingang {
  constructor(
    public readonly id: string,
    public readonly rechnungsNummer: string,
    public readonly lieferantId: string,
    public readonly bestellungId: string | null,
    public readonly wareneingangId: string | null,
    public readonly rechnungsDatum: Date,
    public readonly status: RechnungseingangStatus,
    public readonly bruttoBetrag: number,
    public readonly nettoBetrag: number,
    public readonly steuerBetrag: number,
    public readonly steuerSatz: number,
    public readonly skonto: {
      prozent: number
      betrag: number
      frist?: string
    },
    public readonly zahlungsziel: string,
    public readonly positionen: Array<{
      artikelId: string
      menge: number
      preis: number
      steuerSatz: number
      gesamt: number
    }>,
    public readonly abweichungen: Array<{
      typ: 'MENGE' | 'PREIS' | 'QUALITAET'
      beschreibung: string
      betrag?: number
    }>,
    public readonly tenantId: string,
    public readonly bemerkungen?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    rechnungsNummer: string
    lieferantId: string
    bestellungId?: string
    wareneingangId?: string
    rechnungsDatum: Date
    bruttoBetrag: number
    nettoBetrag: number
    steuerBetrag: number
    steuerSatz: number
    skonto: {
      prozent: number
      betrag: number
      frist?: string
    }
    zahlungsziel: string
    positionen: Array<{
      artikelId: string
      menge: number
      preis: number
      steuerSatz: number
      gesamt: number
    }>
    abweichungen: Array<{
      typ: 'MENGE' | 'PREIS' | 'QUALITAET'
      beschreibung: string
      betrag?: number
    }>
    tenantId: string
    bemerkungen?: string
  }): Rechnungseingang {
    return new Rechnungseingang(
      '', // ID wird generiert
      data.rechnungsNummer,
      data.lieferantId,
      data.bestellungId || null,
      data.wareneingangId || null,
      data.rechnungsDatum,
      RechnungseingangStatus.ERFASST,
      data.bruttoBetrag,
      data.nettoBetrag,
      data.steuerBetrag,
      data.steuerSatz,
      data.skonto,
      data.zahlungsziel,
      data.positionen,
      data.abweichungen,
      data.tenantId,
      data.bemerkungen
    )
  }

  pruefen(): Rechnungseingang {
    if (this.status !== RechnungseingangStatus.ERFASST) {
      throw new Error('Nur erfasste Rechnungen können geprüft werden')
    }
    return new Rechnungseingang(
      this.id,
      this.rechnungsNummer,
      this.lieferantId,
      this.bestellungId,
      this.wareneingangId,
      this.rechnungsDatum,
      RechnungseingangStatus.GEPRUEFT,
      this.bruttoBetrag,
      this.nettoBetrag,
      this.steuerBetrag,
      this.steuerSatz,
      this.skonto,
      this.zahlungsziel,
      this.positionen,
      this.abweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  freigeben(): Rechnungseingang {
    if (this.status !== RechnungseingangStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Rechnungen können freigegeben werden')
    }
    return new Rechnungseingang(
      this.id,
      this.rechnungsNummer,
      this.lieferantId,
      this.bestellungId,
      this.wareneingangId,
      this.rechnungsDatum,
      RechnungseingangStatus.FREIGEGEBEN,
      this.bruttoBetrag,
      this.nettoBetrag,
      this.steuerBetrag,
      this.steuerSatz,
      this.skonto,
      this.zahlungsziel,
      this.positionen,
      this.abweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  verbuchen(): Rechnungseingang {
    if (this.status !== RechnungseingangStatus.FREIGEGEBEN) {
      throw new Error('Nur freigegebene Rechnungen können verbucht werden')
    }
    return new Rechnungseingang(
      this.id,
      this.rechnungsNummer,
      this.lieferantId,
      this.bestellungId,
      this.wareneingangId,
      this.rechnungsDatum,
      RechnungseingangStatus.VERBUCHT,
      this.bruttoBetrag,
      this.nettoBetrag,
      this.steuerBetrag,
      this.steuerSatz,
      this.skonto,
      this.zahlungsziel,
      this.positionen,
      this.abweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  bezahlen(): Rechnungseingang {
    if (this.status !== RechnungseingangStatus.VERBUCHT) {
      throw new Error('Nur verbuchte Rechnungen können bezahlt werden')
    }
    return new Rechnungseingang(
      this.id,
      this.rechnungsNummer,
      this.lieferantId,
      this.bestellungId,
      this.wareneingangId,
      this.rechnungsDatum,
      RechnungseingangStatus.BEZAHLT,
      this.bruttoBetrag,
      this.nettoBetrag,
      this.steuerBetrag,
      this.steuerSatz,
      this.skonto,
      this.zahlungsziel,
      this.positionen,
      this.abweichungen,
      this.tenantId,
      this.bemerkungen,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  hatAbweichungen(): boolean {
    return this.abweichungen.length > 0
  }

  getGesamtAbweichungsbetrag(): number {
    return this.abweichungen.reduce((sum, abw) => sum + (abw.betrag || 0), 0)
  }

  istUeberfaellig(): boolean {
    // Vereinfachte Logik - in Realität komplexer mit Zahlungsziel-Berechnung
    const zahlungszielStr = this.zahlungsziel || '30 Tage'
    const tage = parseInt(zahlungszielStr.split(' ')[0] || '30') || 30
    const faelligkeitsDatum = new Date(this.rechnungsDatum)
    faelligkeitsDatum.setDate(faelligkeitsDatum.getDate() + tage)
    return new Date() > faelligkeitsDatum
  }

  getSkontoBetrag(): number {
    return this.nettoBetrag * (this.skonto.prozent / 100)
  }

  getZahlungsbetrag(): number {
    return this.bruttoBetrag - this.getSkontoBetrag()
  }
}