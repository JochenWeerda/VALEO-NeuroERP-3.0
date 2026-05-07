import { inject, injectable } from 'inversify'
import { Anfrage } from '../../core/entities/anfrage.entity'
import { AnfrageRepository } from '../../core/repositories/anfrage.repository'
import { AnfrageStatus, Prioritaet } from '../../core/entities/anfrage.entity'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'
import { clampLimit, clampOffset, ListResult } from '../../presentation/types/api-pagination'

import { AnfrageTyp } from '../../core/entities/anfrage.entity'

export interface CreateAnfrageData {
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
}

export interface UpdateAnfrageData {
  artikel?: string
  menge?: number
  einheit?: string
  prioritaet?: Prioritaet
  faelligkeit?: Date
  begruendung?: string
  kostenstelle?: string
  projekt?: string
  bemerkungen?: string
}

export class AnfrageService {
  constructor(
    private repository: AnfrageRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createAnfrage(data: CreateAnfrageData, auditActorId: string): Promise<Anfrage> {
    // Validierung
    this.validateAnfrageData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNummer(data.anfrageNummer, data.tenantId)
    if (existing) {
      throw new Error(`Anfrage mit Nummer ${data.anfrageNummer} existiert bereits`)
    }

    // Anfrage erstellen
    const anfrage = Anfrage.create(data)

    // Speichern
    const savedAnfrage = await this.repository.save(anfrage)

    // Audit-Log
    await this.auditService.log({
      actorId: auditActorId,
      entity: 'Anfrage',
      entityId: savedAnfrage.id,
      action: 'CREATE',
      after: savedAnfrage,
      tenantId: data.tenantId
    })

    return savedAnfrage
  }

  async getAnfrageById(id: string, tenantId: string): Promise<Anfrage | null> {
    return this.repository.findById(id, tenantId)
  }

  async getAnfragenByTenant(tenantId: string, options?: {
    status?: AnfrageStatus
    prioritaet?: Prioritaet
    anforderer?: string
    limit?: number
    offset?: number
  }): Promise<ListResult<Anfrage>> {
    const limit = clampLimit(options?.limit)
    const offset = clampOffset(options?.offset)
    const items = await this.repository.findByTenant(tenantId, {
      status: options?.status,
      prioritaet: options?.prioritaet,
      anforderer: options?.anforderer,
      limit,
      offset,
    })
    const total = await this.repository.countByTenant(tenantId, {
      status: options?.status,
      prioritaet: options?.prioritaet,
      anforderer: options?.anforderer,
    })
    return { items, total }
  }

  async freigebenAnfrage(id: string, tenantId: string, actorId: string): Promise<Anfrage> {
    const anfrage = await this.repository.findById(id, tenantId)
    if (!anfrage) {
      throw new Error('Anfrage nicht gefunden')
    }

    if (anfrage.status !== AnfrageStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können freigegeben werden')
    }

    const freigegebeneAnfrage = anfrage.freigeben()
    const saved = await this.repository.update(freigegebeneAnfrage)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anfrage',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: anfrage,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'Anfrage',
      fromId: id,
      toEntity: 'Anfrage',
      action: 'FREIGEGEBEN',
      actorId,
      data: saved
    })

    return saved
  }

  async updateAnfrage(id: string, tenantId: string, data: UpdateAnfrageData, actorId: string): Promise<Anfrage> {
    const anfrage = await this.repository.findById(id, tenantId)
    if (!anfrage) {
      throw new Error('Anfrage nicht gefunden')
    }

    if (anfrage.status !== AnfrageStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können aktualisiert werden')
    }

    const updatedAnfrage = new Anfrage(
      anfrage.id,
      anfrage.anfrageNummer,
      anfrage.typ,
      anfrage.anforderer,
      data.artikel ?? anfrage.artikel,
      data.menge ?? anfrage.menge,
      data.einheit ?? anfrage.einheit,
      data.prioritaet ?? anfrage.prioritaet,
      data.faelligkeit ?? anfrage.faelligkeit,
      anfrage.status,
      data.begruendung ?? anfrage.begruendung,
      anfrage.tenantId,
      data.kostenstelle !== undefined ? data.kostenstelle : anfrage.kostenstelle,
      data.projekt !== undefined ? data.projekt : anfrage.projekt,
      data.bemerkungen !== undefined ? data.bemerkungen : anfrage.bemerkungen,
      anfrage.version + 1,
      anfrage.createdAt,
      new Date(),
      anfrage.deletedAt
    )

    const saved = await this.repository.update(updatedAnfrage)

    await this.auditService.log({
      actorId,
      entity: 'Anfrage',
      entityId: id,
      action: 'UPDATE',
      before: anfrage,
      after: saved,
      tenantId
    })

    return saved
  }

  async deleteAnfrage(id: string, tenantId: string, actorId: string): Promise<void> {
    const anfrage = await this.repository.findById(id, tenantId)
    if (!anfrage) {
      throw new Error('Anfrage nicht gefunden')
    }

    if (anfrage.status !== AnfrageStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'Anfrage',
      entityId: id,
      action: 'DELETE',
      before: anfrage,
      tenantId
    })
  }

  async getUeberfaelligeAnfragen(tenantId: string): Promise<Anfrage[]> {
    return this.repository.findUeberfaellige(tenantId)
  }

  async getDringendeAnfragen(tenantId: string): Promise<Anfrage[]> {
    return this.repository.findDringende(tenantId)
  }

  private validateAnfrageData(data: CreateAnfrageData): void {
    if (data.menge <= 0) {
      throw new Error('Menge muss größer 0 sein')
    }

    if (data.faelligkeit <= new Date()) {
      throw new Error('Fälligkeit muss in der Zukunft liegen')
    }

    if (!data.begruendung.trim()) {
      throw new Error('Begründung ist erforderlich')
    }
  }
}