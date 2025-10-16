import { inject, injectable } from 'inversify'
import { SalesOffer, SalesOfferStatus } from '../../core/entities/sales-offer.entity'
import { CustomerInquiry } from '../../core/entities/customer-inquiry.entity'
import { SalesOfferRepository } from '../../core/repositories/sales-offer.repository'
import { AuditService } from './audit.service'
import { WorkflowService } from './workflow.service'

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

  async createSalesOffer(data: CreateSalesOfferData): Promise<SalesOffer> {
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
      actorId: 'system', // TODO: Aus Context holen
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

    // SalesOffer aus CustomerInquiry erstellen
    const salesOffer = SalesOffer.createFromCustomerInquiry(customerInquiry, data)

    // Speichern
    const savedSalesOffer = await this.repository.save(salesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: savedSalesOffer.id,
      action: 'CREATE_FROM_INQUIRY',
      after: savedSalesOffer,
      tenantId: customerInquiry.tenantId
    })

    // CustomerInquiry Status aktualisieren
    const updatedInquiry = customerInquiry.angebotErstellen()
    // TODO: CustomerInquiry Repository aktualisieren

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
  }): Promise<SalesOffer[]> {
    return this.repository.findByTenant(tenantId, options)
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

    // TODO: SalesOffer mit neuen Daten aktualisieren
    // const updatedSalesOffer = salesOffer.update(data)
    // const saved = await this.repository.update(updatedSalesOffer)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'SalesOffer',
      entityId: id,
      action: 'UPDATE',
      before: salesOffer,
      after: salesOffer, // TODO: updatedSalesOffer
      tenantId
    })

    return salesOffer // TODO: saved
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