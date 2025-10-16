import { inject, injectable } from 'inversify'
import { Rechnungseingang } from '../../core/entities/rechnungseingang.entity'
import { RechnungseingangRepository } from '../../core/repositories/rechnungseingang.repository'
import { RechnungseingangStatus } from '../../core/entities/rechnungseingang.entity'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'

export interface CreateRechnungseingangData {
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
}

export interface UpdateRechnungseingangData {
  bruttoBetrag?: number
  nettoBetrag?: number
  steuerBetrag?: number
  steuerSatz?: number
  skonto?: {
    prozent: number
    betrag: number
    frist?: string
  }
  zahlungsziel?: string
  positionen?: Array<{
    artikelId: string
    menge: number
    preis: number
    steuerSatz: number
    gesamt: number
  }>
  abweichungen?: Array<{
    typ: 'MENGE' | 'PREIS' | 'QUALITAET'
    beschreibung: string
    betrag?: number
  }>
  bemerkungen?: string
}

export class RechnungseingangService {
  constructor(
    private repository: RechnungseingangRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createRechnungseingang(data: CreateRechnungseingangData): Promise<Rechnungseingang> {
    // Validierung
    this.validateRechnungseingangData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNummer(data.rechnungsNummer, data.tenantId)
    if (existing) {
      throw new Error(`Rechnung mit Nummer ${data.rechnungsNummer} existiert bereits`)
    }

    // Rechnungseingang erstellen
    const rechnung = Rechnungseingang.create(data)

    // Speichern
    const savedRechnung = await this.repository.save(rechnung)

    // Audit-Log
    await this.auditService.log({
      actorId: 'system', // TODO: Aus Context holen
      entity: 'Rechnungseingang',
      entityId: savedRechnung.id,
      action: 'CREATE',
      after: savedRechnung,
      tenantId: data.tenantId
    })

    return savedRechnung
  }

  async getRechnungseingangById(id: string, tenantId: string): Promise<Rechnungseingang | null> {
    return this.repository.findById(id, tenantId)
  }

  async getRechnungseingaengeByTenant(tenantId: string, options?: {
    status?: RechnungseingangStatus
    lieferantId?: string
    bestellungId?: string
    wareneingangId?: string
    limit?: number
    offset?: number
  }): Promise<Rechnungseingang[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getRechnungseingaengeByBestellung(bestellungId: string, tenantId: string): Promise<Rechnungseingang[]> {
    return this.repository.findByBestellung(bestellungId, tenantId)
  }

  async getRechnungseingaengeByWareneingang(wareneingangId: string, tenantId: string): Promise<Rechnungseingang[]> {
    return this.repository.findByWareneingang(wareneingangId, tenantId)
  }

  async pruefenRechnungseingang(id: string, tenantId: string, actorId: string): Promise<Rechnungseingang> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    if (rechnung.status !== RechnungseingangStatus.ERFASST) {
      throw new Error('Nur erfasste Rechnungen können geprüft werden')
    }

    const gepruefteRechnung = rechnung.pruefen()
    const saved = await this.repository.update(gepruefteRechnung)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: rechnung,
      after: saved,
      tenantId
    })

    return saved
  }

  async freigebenRechnungseingang(id: string, tenantId: string, actorId: string): Promise<Rechnungseingang> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    if (rechnung.status !== RechnungseingangStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Rechnungen können freigegeben werden')
    }

    const freigegebeneRechnung = rechnung.freigeben()
    const saved = await this.repository.update(freigegebeneRechnung)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: rechnung,
      after: saved,
      tenantId
    })

    return saved
  }

  async verbuchenRechnungseingang(id: string, tenantId: string, actorId: string): Promise<Rechnungseingang> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    if (rechnung.status !== RechnungseingangStatus.FREIGEGEBEN) {
      throw new Error('Nur freigegebene Rechnungen können verbucht werden')
    }

    const verbuchteRechnung = rechnung.verbuchen()
    const saved = await this.repository.update(verbuchteRechnung)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: rechnung,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'Rechnungseingang',
      fromId: id,
      toEntity: 'Rechnungseingang',
      action: 'VERBUCHT',
      actorId,
      data: saved
    })

    return saved
  }

  async bezahlenRechnungseingang(id: string, tenantId: string, actorId: string): Promise<Rechnungseingang> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    if (rechnung.status !== RechnungseingangStatus.VERBUCHT) {
      throw new Error('Nur verbuchte Rechnungen können bezahlt werden')
    }

    const bezahlteRechnung = rechnung.bezahlen()
    const saved = await this.repository.update(bezahlteRechnung)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: rechnung,
      after: saved,
      tenantId
    })

    return saved
  }

  async updateRechnungseingang(id: string, tenantId: string, data: UpdateRechnungseingangData, actorId: string): Promise<Rechnungseingang> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    // TODO: Rechnungseingang mit neuen Daten aktualisieren
    // const updatedRechnung = rechnung.update(data)
    // const saved = await this.repository.update(updatedRechnung)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'UPDATE',
      before: rechnung,
      after: rechnung, // TODO: updatedRechnung
      tenantId
    })

    return rechnung // TODO: saved
  }

  async deleteRechnungseingang(id: string, tenantId: string, actorId: string): Promise<void> {
    const rechnung = await this.repository.findById(id, tenantId)
    if (!rechnung) {
      throw new Error('Rechnungseingang nicht gefunden')
    }

    if (rechnung.status !== RechnungseingangStatus.ERFASST) {
      throw new Error('Nur erfasste Rechnungen können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Rechnungseingang',
      entityId: id,
      action: 'DELETE',
      before: rechnung,
      tenantId
    })
  }

  async getUeberfaelligeRechnungseingaenge(tenantId: string): Promise<Rechnungseingang[]> {
    return this.repository.findUeberfaellige(tenantId)
  }

  async getRechnungseingaengeMitAbweichungen(tenantId: string): Promise<Rechnungseingang[]> {
    return this.repository.findMitAbweichungen(tenantId)
  }

  async getGesamtOffenerBetrag(tenantId: string): Promise<number> {
    return this.repository.getGesamtOffen(tenantId)
  }

  private validateRechnungseingangData(data: CreateRechnungseingangData): void {
    if (data.bruttoBetrag <= 0) {
      throw new Error('Bruttobetrag muss größer 0 sein')
    }

    if (data.nettoBetrag <= 0) {
      throw new Error('Nettobetrag muss größer 0 sein')
    }

    if (data.steuerSatz < 0) {
      throw new Error('Steuersatz darf nicht negativ sein')
    }

    if (!data.positionen.length) {
      throw new Error('Mindestens eine Position ist erforderlich')
    }

    // Validierung der Positionen
    for (const position of data.positionen) {
      if (position.menge <= 0 || position.preis <= 0) {
        throw new Error('Menge und Preis müssen größer 0 sein')
      }
    }

    // Validierung der Skonto-Daten
    if (data.skonto.prozent < 0 || data.skonto.betrag < 0) {
      throw new Error('Skonto-Prozent und -Betrag dürfen nicht negativ sein')
    }
  }
}