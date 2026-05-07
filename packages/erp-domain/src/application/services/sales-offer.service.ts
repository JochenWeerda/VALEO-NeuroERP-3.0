import { inject, injectable } from 'inversify'
import { SalesOffer, SalesOfferStatus } from '../../core/entities/sales-offer.entity'
import { CustomerInquiry, CustomerInquiryStatus } from '../../core/entities/customer-inquiry.entity'
import { SalesOfferRepository } from '../../core/repositories/sales-offer.repository'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'
import { clampLimit, clampOffset, ListResult } from '../../presentation/types/api-pagination'

export interface CreateSalesOfferData {
  offerNumber: string
  customerInquiryId: string
  customerId: string
  subject: string
  description: string
  totalAmount: number
  currency: string
  validUntil: Date
  tenantId: string
  contactPerson?: string
  deliveryDate?: Date
  paymentTerms?: string
  notes?: string
}

export interface UpdateSalesOfferData {
  subject?: string
  description?: string
  totalAmount?: number
  validUntil?: Date
  contactPerson?: string
  deliveryDate?: Date
  paymentTerms?: string
  notes?: string
}

export class SalesOfferService {
  constructor(
    private repository: SalesOfferRepository,
    private auditService: AuditService,
    private workflowService: WorkflowService
  ) {}

  async createSalesOffer(data: CreateSalesOfferData, auditActorId: string): Promise<SalesOffer> {
    // Validierung
    this.validateSalesOfferData(data)

    // Prüfen ob Nummer bereits existiert
    const existing = await this.repository.findByNumber(data.offerNumber, data.tenantId)
    if (existing) {
      throw new Error(`SalesOffer mit Nummer ${data.offerNumber} existiert bereits`)
    }

    // SalesOffer erstellen
    const salesOffer = SalesOffer.create(data)

    // Speichern
    const savedSalesOffer = await this.repository.save(salesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId: auditActorId,
      entity: 'SalesOffer',
      entityId: savedSalesOffer.id,
      action: 'CREATE',
      after: savedSalesOffer,
      tenantId: data.tenantId
    })

    return savedSalesOffer
  }

  async createSalesOfferFromInquiry(
    customerInquiry: CustomerInquiry,
    data: {
      offerNumber: string
      totalAmount: number
      validUntil: Date
      deliveryDate?: Date
      paymentTerms?: string
      notes?: string
    },
    actorId: string
  ): Promise<SalesOffer> {
    // Prüfen ob CustomerInquiry bereits ein Angebot hat
    const existingOffers = await this.repository.findByCustomerInquiryId(customerInquiry.id, customerInquiry.tenantId)
    if (existingOffers.length > 0) {
      throw new Error('CustomerInquiry hat bereits ein SalesOffer')
    }

    let ci = customerInquiry
    if (ci.status === CustomerInquiryStatus.EINGEGANGEN) {
      ci = ci.bearbeiten(ci.assignedTo)
    }
    if (ci.status !== CustomerInquiryStatus.BEARBEITET) {
      throw new Error('CustomerInquiry muss vor Angebotserstellung im Status BEARBEITET sein (oder EINGEGANGEN für automatische Überführung)')
    }

    const salesOffer = SalesOffer.createFromCustomerInquiry(ci, data)

    const savedSalesOffer = await this.repository.save(salesOffer)

    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: savedSalesOffer.id,
      action: 'CREATE_FROM_INQUIRY',
      after: savedSalesOffer,
      tenantId: ci.tenantId
    })

    const afterInquiry = ci.angebotErstellen()

    await this.auditService.log({
      actorId,
      entity: 'CustomerInquiry',
      entityId: afterInquiry.id,
      action: 'ANGEBOT_ERSTELLT',
      before: ci,
      after: afterInquiry,
      tenantId: ci.tenantId
    })

    return savedSalesOffer
  }

  async getSalesOfferById(id: string, tenantId: string): Promise<SalesOffer | null> {
    return this.repository.findById(id, tenantId)
  }

  async getSalesOffersByTenant(tenantId: string, options?: {
    status?: SalesOfferStatus
    customerId?: string
    limit?: number
    offset?: number
  }): Promise<ListResult<SalesOffer>> {
    const limit = clampLimit(options?.limit)
    const offset = clampOffset(options?.offset)
    const items = await this.repository.findByTenant(tenantId, {
      status: options?.status,
      customerId: options?.customerId,
      limit,
      offset,
    })
    const total = await this.repository.countByTenant(tenantId, {
      status: options?.status,
      customerId: options?.customerId,
    })
    return { items, total }
  }

  async getSalesOffersByCustomerInquiry(customerInquiryId: string, tenantId: string): Promise<SalesOffer[]> {
    return this.repository.findByCustomerInquiryId(customerInquiryId, tenantId)
  }

  async sendSalesOffer(id: string, tenantId: string, actorId: string): Promise<SalesOffer> {
    const salesOffer = await this.repository.findById(id, tenantId)
    if (!salesOffer) {
      throw new Error('SalesOffer nicht gefunden')
    }

    if (salesOffer.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können versendet werden')
    }

    const sentSalesOffer = salesOffer.versenden()
    const saved = await this.repository.update(sentSalesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: salesOffer,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'SalesOffer',
      fromId: id,
      toEntity: 'SalesOffer',
      action: 'VERSENDET',
      actorId,
      data: saved
    })

    return saved
  }

  async acceptSalesOffer(id: string, tenantId: string, actorId: string): Promise<SalesOffer> {
    const salesOffer = await this.repository.findById(id, tenantId)
    if (!salesOffer) {
      throw new Error('SalesOffer nicht gefunden')
    }

    if (!salesOffer.kannAngenommenWerden()) {
      throw new Error('SalesOffer kann nicht angenommen werden')
    }

    const acceptedSalesOffer = salesOffer.annehmen()
    const saved = await this.repository.update(acceptedSalesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: salesOffer,
      after: saved,
      tenantId
    })

    // Workflow-Trigger
    await this.workflowService.executeTransition({
      fromEntity: 'SalesOffer',
      fromId: id,
      toEntity: 'SalesOffer',
      action: 'ANGENOMMEN',
      actorId,
      data: saved
    })

    return saved
  }

  async rejectSalesOffer(id: string, tenantId: string, actorId: string): Promise<SalesOffer> {
    const salesOffer = await this.repository.findById(id, tenantId)
    if (!salesOffer) {
      throw new Error('SalesOffer nicht gefunden')
    }

    if (salesOffer.status === SalesOfferStatus.ANGENOMMEN || salesOffer.status === SalesOfferStatus.ABGELAUFEN) {
      throw new Error('SalesOffer kann nicht mehr abgelehnt werden')
    }

    const rejectedSalesOffer = salesOffer.ablehnen()
    const saved = await this.repository.update(rejectedSalesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'STATUS_CHANGE',
      before: salesOffer,
      after: saved,
      tenantId
    })

    return saved
  }

  async updateSalesOffer(id: string, tenantId: string, data: UpdateSalesOfferData, actorId: string): Promise<SalesOffer> {
    const salesOffer = await this.repository.findById(id, tenantId)
    if (!salesOffer) {
      throw new Error('SalesOffer nicht gefunden')
    }

    if (salesOffer.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können aktualisiert werden')
    }

    const updatedSalesOffer = new SalesOffer(
      salesOffer.id,
      salesOffer.offerNumber,
      salesOffer.customerInquiryId,
      salesOffer.customerId,
      data.subject ?? salesOffer.subject,
      data.description ?? salesOffer.description,
      data.totalAmount ?? salesOffer.totalAmount,
      salesOffer.currency,
      data.validUntil ?? salesOffer.validUntil,
      salesOffer.status,
      salesOffer.tenantId,
      data.contactPerson !== undefined ? data.contactPerson : salesOffer.contactPerson,
      data.deliveryDate !== undefined ? data.deliveryDate : salesOffer.deliveryDate,
      data.paymentTerms !== undefined ? data.paymentTerms : salesOffer.paymentTerms,
      data.notes !== undefined ? data.notes : salesOffer.notes,
      salesOffer.version + 1,
      salesOffer.createdAt,
      new Date(),
      salesOffer.deletedAt
    )

    const saved = await this.repository.update(updatedSalesOffer)

    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'UPDATE',
      before: salesOffer,
      after: saved,
      tenantId
    })

    return saved
  }

  async deleteSalesOffer(id: string, tenantId: string, actorId: string): Promise<void> {
    const salesOffer = await this.repository.findById(id, tenantId)
    if (!salesOffer) {
      throw new Error('SalesOffer nicht gefunden')
    }

    if (salesOffer.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können gelöscht werden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'DELETE',
      before: salesOffer,
      tenantId
    })
  }

  async getExpiredSalesOffers(tenantId: string): Promise<SalesOffer[]> {
    return this.repository.findExpired(tenantId)
  }

  async getValidSalesOffers(tenantId: string): Promise<SalesOffer[]> {
    return this.repository.findValid(tenantId)
  }

  private validateSalesOfferData(data: CreateSalesOfferData): void {
    if (data.totalAmount <= 0) {
      throw new Error('Gesamtbetrag muss größer 0 sein')
    }

    if (data.validUntil <= new Date()) {
      throw new Error('Gültigkeitsdatum muss in der Zukunft liegen')
    }

    if (!data.subject.trim()) {
      throw new Error('Betreff ist erforderlich')
    }

    if (!data.description.trim()) {
      throw new Error('Beschreibung ist erforderlich')
    }
  }
}