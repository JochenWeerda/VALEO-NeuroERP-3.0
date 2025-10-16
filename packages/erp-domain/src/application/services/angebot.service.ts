import { inject, injectable } from 'inversify'
import { Angebot } from '../../core/entities/angebot.entity'
import { AngebotRepository } from '../../core/repositories/angebot.repository'
import { AngebotStatus } from '../../core/entities/angebot.entity'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'

export interface CreateAngebotData {
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
}

export interface UpdateAngebotData {
  artikel?: string
  menge?: number
  einheit?: string
  preis?: number
  waehrung?: string
  lieferzeit?: number
  gueltigBis?: Date
  mindestabnahme?: number
  zahlungsbedingungen?: string
  incoterms?: string
  bemerkungen?: string
}

export class AngebotService {
  constructor(
    private repository: AngebotRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createAngebot(data: CreateAngebotData): Promise<Angebot> {
    // Validierung
    this.validateAngebotData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNummer(data.angebotNummer, data.tenantId)
    if (existing) {
      throw new Error(`Angebot mit Nummer ${data.angebotNummer} existiert bereits`)
    }

    // Angebot erstellen
    const angebot = Angebot.create(data)

    // Speichern
    const savedAngebot = await this.repository.save(angebot)

    // Audit-Log
    await this.auditService.log({
      actorId: data.lieferantId, // TODO: Aus Context holen
      entity: 'Angebot',
      entityId: savedAngebot.id,
      action: 'CREATE',
      after: savedAngebot,
      tenantId: data.tenantId
    })

    return savedAngebot
  }

  async getAngebotById(id: string, tenantId: string): Promise<Angebot | null> {
    return this.repository.findById(id, tenantId)
  }

  async getAngeboteByTenant(tenantId: string, options?: {
    status?: AngebotStatus
    lieferantId?: string
    anfrageId?: string
    limit?: number
    offset?: number
  }): Promise<Angebot[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getAngeboteByAnfrage(anfrageId: string, tenantId: string): Promise<Angebot[]> {
    return this.repository.findByAnfrage(anfrageId, tenantId)
  }

  async pruefenAngebot(id: string, tenantId: string, actorId: string): Promise<Angebot> {
    const angebot = await this.repository.findById(id, tenantId)
    if (!angebot) {
      throw new Error('Angebot nicht gefunden')
    }

    if (angebot.status !== AngebotStatus.ERFASST) {
      throw new Error('Nur erfasste Angebote können geprüft werden')
    }

    const geprueftesAngebot = angebot.pruefen()
    const saved = await this.repository.update(geprueftesAngebot)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Angebot',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: angebot,
      after: saved,
      tenantId
    })

    return saved
  }

  async genehmigenAngebot(id: string, tenantId: string, actorId: string): Promise<Angebot> {
    const angebot = await this.repository.findById(id, tenantId)
    if (!angebot) {
      throw new Error('Angebot nicht gefunden')
    }

    if (angebot.status !== AngebotStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Angebote können genehmigt werden')
    }

    const genehmigtesAngebot = angebot.genehmigen()
    const saved = await this.repository.update(genehmigtesAngebot)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Angebot',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: angebot,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'Angebot',
      fromId: id,
      toEntity: 'Angebot',
      action: 'GENEHMIGT',
      actorId,
      data: saved
    })

    return saved
  }

  async ablehnenAngebot(id: string, tenantId: string, actorId: string): Promise<Angebot> {
    const angebot = await this.repository.findById(id, tenantId)
    if (!angebot) {
      throw new Error('Angebot nicht gefunden')
    }

    if (angebot.status === AngebotStatus.ABGELEHNT) {
      throw new Error('Angebot ist bereits abgelehnt')
    }

    const abgelehntesAngebot = angebot.ablehnen()
    const saved = await this.repository.update(abgelehntesAngebot)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Angebot',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: angebot,
      after: saved,
      tenantId
    })

    return saved
  }

  async updateAngebot(id: string, tenantId: string, data: UpdateAngebotData, actorId: string): Promise<Angebot> {
    const angebot = await this.repository.findById(id, tenantId)
    if (!angebot) {
      throw new Error('Angebot nicht gefunden')
    }

    // TODO: Angebot mit neuen Daten aktualisieren
    // const updatedAngebot = angebot.update(data)
    // const saved = await this.repository.update(updatedAngebot)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Angebot',
      entityId: id,
      action: 'UPDATE',
      before: angebot,
      after: angebot, // TODO: updatedAngebot
      tenantId
    })

    return angebot // TODO: saved
  }

  async deleteAngebot(id: string, tenantId: string, actorId: string): Promise<void> {
    const angebot = await this.repository.findById(id, tenantId)
    if (!angebot) {
      throw new Error('Angebot nicht gefunden')
    }

    if (angebot.status !== AngebotStatus.ERFASST) {
      throw new Error('Nur erfasste Angebote können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Angebot',
      entityId: id,
      action: 'DELETE',
      before: angebot,
      tenantId
    })
  }

  async getAbgelaufeneAngebote(tenantId: string): Promise<Angebot[]> {
    return this.repository.findAbgelaufene(tenantId)
  }

  private validateAngebotData(data: CreateAngebotData): void {
    if (data.menge <= 0) {
      throw new Error('Menge muss größer 0 sein')
    }

    if (data.preis <= 0) {
      throw new Error('Preis muss größer 0 sein')
    }

    if (data.lieferzeit < 0) {
      throw new Error('Lieferzeit darf nicht negativ sein')
    }

    if (data.gueltigBis <= new Date()) {
      throw new Error('Gültigkeitsdatum muss in der Zukunft liegen')
    }
  }
}