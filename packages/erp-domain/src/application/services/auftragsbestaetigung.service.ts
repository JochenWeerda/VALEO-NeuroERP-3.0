import { inject, injectable } from 'inversify'
import { Auftragsbestaetigung } from '../../core/entities/auftragsbestaetigung.entity'
import { AuftragsbestaetigungRepository } from '../../core/repositories/auftragsbestaetigung.repository'
import { AuftragsbestaetigungStatus } from '../../core/entities/auftragsbestaetigung.entity'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'

export interface CreateAuftragsbestaetigungData {
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
}

export interface UpdateAuftragsbestaetigungData {
  bestaetigteTermine?: Array<{
    positionId: string
    bestaetigterTermin: Date
    abweichung?: string
  }>
  preisabweichungen?: Array<{
    positionId: string
    urspruenglicherPreis: number
    neuerPreis: number
    begruendung?: string
  }>
  bemerkungen?: string
}

export class AuftragsbestaetigungService {
  constructor(
    private repository: AuftragsbestaetigungRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createAuftragsbestaetigung(data: CreateAuftragsbestaetigungData): Promise<Auftragsbestaetigung> {
    // Validierung
    this.validateAuftragsbestaetigungData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNummer(data.bestaetigungsNummer, data.tenantId)
    if (existing) {
      throw new Error(`Auftragsbestätigung mit Nummer ${data.bestaetigungsNummer} existiert bereits`)
    }

    // Prüfen ob bereits eine Bestätigung für diese Bestellung existiert
    const existingForBestellung = await this.repository.findByBestellung(data.bestellungId, data.tenantId)
    if (existingForBestellung) {
      throw new Error(`Für diese Bestellung existiert bereits eine Auftragsbestätigung`)
    }

    // Auftragsbestätigung erstellen
    const ab = Auftragsbestaetigung.create(data)

    // Speichern
    const savedAb = await this.repository.save(ab)

    // Audit-Log
    await this.auditService.log({
      actorId: 'system', // TODO: Aus Context holen
      entity: 'Auftragsbestaetigung',
      entityId: savedAb.id,
      action: 'CREATE',
      after: savedAb,
      tenantId: data.tenantId
    })

    return savedAb
  }

  async getAuftragsbestaetigungById(id: string, tenantId: string): Promise<Auftragsbestaetigung | null> {
    return this.repository.findById(id, tenantId)
  }

  async getAuftragsbestaetigungenByTenant(tenantId: string, options?: {
    status?: AuftragsbestaetigungStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Auftragsbestaetigung[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getAuftragsbestaetigungByBestellung(bestellungId: string, tenantId: string): Promise<Auftragsbestaetigung | null> {
    return this.repository.findByBestellung(bestellungId, tenantId)
  }

  async pruefenAuftragsbestaetigung(id: string, tenantId: string, actorId: string): Promise<Auftragsbestaetigung> {
    const ab = await this.repository.findById(id, tenantId)
    if (!ab) {
      throw new Error('Auftragsbestätigung nicht gefunden')
    }

    if (ab.status !== AuftragsbestaetigungStatus.OFFEN) {
      throw new Error('Nur offene Auftragsbestätigungen können geprüft werden')
    }

    const gepruefteAb = ab.pruefen()
    const saved = await this.repository.update(gepruefteAb)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Auftragsbestaetigung',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: ab,
      after: saved,
      tenantId
    })

    return saved
  }

  async bestaetigenAuftragsbestaetigung(id: string, tenantId: string, actorId: string): Promise<Auftragsbestaetigung> {
    const ab = await this.repository.findById(id, tenantId)
    if (!ab) {
      throw new Error('Auftragsbestätigung nicht gefunden')
    }

    if (ab.status !== AuftragsbestaetigungStatus.GEPRUEFT) {
      throw new Error('Nur geprüfte Auftragsbestätigungen können bestätigt werden')
    }

    const bestaetigteAb = ab.bestaetigen()
    const saved = await this.repository.update(bestaetigteAb)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Auftragsbestaetigung',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: ab,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'Auftragsbestaetigung',
      fromId: id,
      toEntity: 'Auftragsbestaetigung',
      action: 'BESTAETIGT',
      actorId,
      data: saved
    })

    return saved
  }

  async updateAuftragsbestaetigung(id: string, tenantId: string, data: UpdateAuftragsbestaetigungData, actorId: string): Promise<Auftragsbestaetigung> {
    const ab = await this.repository.findById(id, tenantId)
    if (!ab) {
      throw new Error('Auftragsbestätigung nicht gefunden')
    }

    // TODO: Auftragsbestätigung mit neuen Daten aktualisieren
    // const updatedAb = ab.update(data)
    // const saved = await this.repository.update(updatedAb)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Auftragsbestaetigung',
      entityId: id,
      action: 'UPDATE',
      before: ab,
      after: ab, // TODO: updatedAb
      tenantId
    })

    return ab // TODO: saved
  }

  async deleteAuftragsbestaetigung(id: string, tenantId: string, actorId: string): Promise<void> {
    const ab = await this.repository.findById(id, tenantId)
    if (!ab) {
      throw new Error('Auftragsbestätigung nicht gefunden')
    }

    if (ab.status !== AuftragsbestaetigungStatus.OFFEN) {
      throw new Error('Nur offene Auftragsbestätigungen können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Auftragsbestaetigung',
      entityId: id,
      action: 'DELETE',
      before: ab,
      tenantId
    })
  }

  async getAuftragsbestaetigungenMitAbweichungen(tenantId: string): Promise<Auftragsbestaetigung[]> {
    return this.repository.findMitAbweichungen(tenantId)
  }

  private validateAuftragsbestaetigungData(data: CreateAuftragsbestaetigungData): void {
    if (!data.bestaetigteTermine.length) {
      throw new Error('Mindestens ein bestätigter Termin ist erforderlich')
    }

    if (!data.preisabweichungen.length) {
      throw new Error('Mindestens eine Preisabweichung ist erforderlich')
    }

    // Validierung der Termine
    for (const termin of data.bestaetigteTermine) {
      if (termin.bestaetigterTermin <= new Date()) {
        throw new Error('Bestätigte Termine müssen in der Zukunft liegen')
      }
    }

    // Validierung der Preisabweichungen
    for (const abweichung of data.preisabweichungen) {
      if (abweichung.urspruenglicherPreis <= 0 || abweichung.neuerPreis <= 0) {
        throw new Error('Preise müssen größer 0 sein')
      }
    }
  }
}