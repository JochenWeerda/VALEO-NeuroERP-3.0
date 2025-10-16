import { inject, injectable } from 'inversify'
import { Anlieferavis } from '../../core/entities/anlieferavis.entity'
import { AnlieferavisRepository } from '../../core/repositories/anlieferavis.repository'
import { AnlieferavisStatus } from '../../core/entities/anlieferavis.entity'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'

export interface CreateAnlieferavisData {
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
}

export interface UpdateAnlieferavisData {
  geplantesAnlieferDatum?: Date
  fahrzeug?: {
    kennzeichen: string
    fahrer: string
    telefon?: string
  }
  positionen?: Array<{
    positionId: string
    menge: number
    chargenNummer?: string
    verpackung?: string
  }>
  bemerkungen?: string
}

export class AnlieferavisService {
  constructor(
    private repository: AnlieferavisRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createAnlieferavis(data: CreateAnlieferavisData): Promise<Anlieferavis> {
    // Validierung
    this.validateAnlieferavisData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNummer(data.avisNummer, data.tenantId)
    if (existing) {
      throw new Error(`Anlieferavis mit Nummer ${data.avisNummer} existiert bereits`)
    }

    // Prüfen ob bereits ein Avis für diese Bestellung existiert
    const existingForBestellung = await this.repository.findByBestellung(data.bestellungId, data.tenantId)
    if (existingForBestellung && existingForBestellung.status !== AnlieferavisStatus.STORNIERT) {
      throw new Error(`Für diese Bestellung existiert bereits ein aktiver Anlieferavis`)
    }

    // Anlieferavis erstellen
    const avis = Anlieferavis.create(data)

    // Speichern
    const savedAvis = await this.repository.save(avis)

    // Audit-Log
    await this.auditService.log({
      actorId: 'system', // TODO: Aus Context holen
      entity: 'Anlieferavis',
      entityId: savedAvis.id,
      action: 'CREATE',
      after: savedAvis,
      tenantId: data.tenantId
    })

    return savedAvis
  }

  async getAnlieferavisById(id: string, tenantId: string): Promise<Anlieferavis | null> {
    return this.repository.findById(id, tenantId)
  }

  async getAnlieferaviseByTenant(tenantId: string, options?: {
    status?: AnlieferavisStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Anlieferavis[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getAnlieferavisByBestellung(bestellungId: string, tenantId: string): Promise<Anlieferavis | null> {
    return this.repository.findByBestellung(bestellungId, tenantId)
  }

  async bestaetigenAnlieferavis(id: string, tenantId: string, actorId: string): Promise<Anlieferavis> {
    const avis = await this.repository.findById(id, tenantId)
    if (!avis) {
      throw new Error('Anlieferavis nicht gefunden')
    }

    if (avis.status !== AnlieferavisStatus.GESENDET) {
      throw new Error('Nur gesendete Avise können bestätigt werden')
    }

    const bestaetigterAvis = avis.bestaetigen()
    const saved = await this.repository.update(bestaetigterAvis)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anlieferavis',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: avis,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'Anlieferavis',
      fromId: id,
      toEntity: 'Anlieferavis',
      action: 'BESTAETIGT',
      actorId,
      data: saved
    })

    return saved
  }

  async stornierenAnlieferavis(id: string, tenantId: string, actorId: string): Promise<Anlieferavis> {
    const avis = await this.repository.findById(id, tenantId)
    if (!avis) {
      throw new Error('Anlieferavis nicht gefunden')
    }

    if (avis.status === AnlieferavisStatus.STORNIERT) {
      throw new Error('Anlieferavis ist bereits storniert')
    }

    const stornierterAvis = avis.stornieren()
    const saved = await this.repository.update(stornierterAvis)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anlieferavis',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: avis,
      after: saved,
      tenantId
    })

    return saved
  }

  async updateAnlieferavis(id: string, tenantId: string, data: UpdateAnlieferavisData, actorId: string): Promise<Anlieferavis> {
    const avis = await this.repository.findById(id, tenantId)
    if (!avis) {
      throw new Error('Anlieferavis nicht gefunden')
    }

    // TODO: Anlieferavis mit neuen Daten aktualisieren
    // const updatedAvis = avis.update(data)
    // const saved = await this.repository.update(updatedAvis)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anlieferavis',
      entityId: id,
      action: 'UPDATE',
      before: avis,
      after: avis, // TODO: updatedAvis
      tenantId
    })

    return avis // TODO: saved
  }

  async deleteAnlieferavis(id: string, tenantId: string, actorId: string): Promise<void> {
    const avis = await this.repository.findById(id, tenantId)
    if (!avis) {
      throw new Error('Anlieferavis nicht gefunden')
    }

    if (avis.status !== AnlieferavisStatus.GESENDET) {
      throw new Error('Nur gesendete Avise können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anlieferavis',
      entityId: id,
      action: 'DELETE',
      before: avis,
      tenantId
    })
  }

  async getUeberfaelligeAnlieferavise(tenantId: string): Promise<Anlieferavis[]> {
    return this.repository.findUeberfaellige(tenantId)
  }

  private validateAnlieferavisData(data: CreateAnlieferavisData): void {
    if (!data.positionen.length) {
      throw new Error('Mindestens eine Position ist erforderlich')
    }

    if (data.geplantesAnlieferDatum <= new Date()) {
      throw new Error('Geplantes Anlieferdatum muss in der Zukunft liegen')
    }

    // Validierung der Positionen
    for (const position of data.positionen) {
      if (position.menge <= 0) {
        throw new Error('Menge muss größer 0 sein')
      }
    }

    // Validierung des Fahrzeugs
    if (!data.fahrzeug.kennzeichen.trim()) {
      throw new Error('Fahrzeug-Kennzeichen ist erforderlich')
    }

    if (!data.fahrzeug.fahrer.trim()) {
      throw new Error('Fahrer-Name ist erforderlich')
    }
  }
}