import { Request, Response } from 'express'
import { SalesOfferService } from '../../application/services/sales-offer.service'
import { CreateSalesOfferData } from '../../application/services/sales-offer.service'
import { SalesOfferStatus } from '../../core/entities/sales-offer.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId } from '../utils/request-context'
import { CustomerInquiry } from '../../core/entities/customer-inquiry.entity'

export class SalesOfferController {
  constructor(private salesOfferService: SalesOfferService) {}

  async createSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const auditActorId = resolveActorId(req)

      const data: CreateSalesOfferData = {
        offerNumber: req.body.offerNumber,
        customerInquiryId: req.body.customerInquiryId,
        customerId: req.body.customerId,
        subject: req.body.subject,
        description: req.body.description,
        totalAmount: req.body.totalAmount,
        currency: req.body.currency,
        validUntil: new Date(req.body.validUntil),
        tenantId,
        contactPerson: req.body.contactPerson,
        deliveryDate: req.body.deliveryDate ? new Date(req.body.deliveryDate) : undefined,
        paymentTerms: req.body.paymentTerms,
        notes: req.body.notes
      }

      const salesOffer = await this.salesOfferService.createSalesOffer(data, auditActorId)

      res.status(201).json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des SalesOffers:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async createSalesOfferFromInquiry(req: Request, res: Response): Promise<void> {
    try {
      const { inquiryId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      const snap = req.body?.inquirySnapshot as Record<string, unknown> | undefined
      let inquiry: CustomerInquiry
      if (snap && typeof snap === 'object') {
        inquiry = CustomerInquiry.fromPayload({
          ...snap,
          id: snap.id ?? inquiryId,
          tenantId: snap.tenantId ?? snap.tenant_id ?? tenantId
        })
      } else {
        inquiry = CustomerInquiry.fromPayload({
          id: inquiryId,
          tenantId,
          inquiryNumber: req.body?.inquiryNumber ?? `INQ-${inquiryId}`,
          customerId: req.body?.customerId ?? '',
          type: req.body?.inquiryType ?? 'STANDARD',
          subject: req.body?.subject ?? '',
          description: req.body?.description ?? '',
          priority: req.body?.priority ?? 'normal',
          currency: req.body?.currency ?? 'EUR',
          status: 'BEARBEITET'
        })
      }

      const offer = await this.salesOfferService.createSalesOfferFromInquiry(
        inquiry,
        {
          offerNumber: req.body.offerNumber,
          totalAmount: Number(req.body.totalAmount),
          validUntil: new Date(req.body.validUntil),
          deliveryDate: req.body.deliveryDate ? new Date(req.body.deliveryDate) : undefined,
          paymentTerms: req.body.paymentTerms,
          notes: req.body.notes
        },
        actorId
      )

      res.status(201).json({
        success: true,
        data: offer
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des SalesOffers aus CustomerInquiry:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const salesOffer = await this.salesOfferService.getSalesOfferById(id as string, tenantId)

      if (!salesOffer) {
        res.status(404).json({
          success: false,
          error: 'SalesOffer nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Laden des SalesOffers:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getSalesOffers(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as SalesOfferStatus,
        customerId: req.query.customerId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.salesOfferService.getSalesOffersByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der SalesOffers:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getSalesOffersByCustomerInquiry(req: Request, res: Response): Promise<void> {
    try {
      const { inquiryId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const salesOffers = await this.salesOfferService.getSalesOffersByCustomerInquiry(inquiryId as string, tenantId)

      res.json({
        success: true,
        data: salesOffers
      })
    } catch (error) {
      console.error('Fehler beim Laden der SalesOffers für CustomerInquiry:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async sendSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      const salesOffer = await this.salesOfferService.sendSalesOffer(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Versenden des SalesOffers:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async acceptSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      const salesOffer = await this.salesOfferService.acceptSalesOffer(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Annehmen des SalesOffers:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async rejectSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      const salesOffer = await this.salesOfferService.rejectSalesOffer(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Ablehnen des SalesOffers:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      const salesOffer = await this.salesOfferService.updateSalesOffer(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: salesOffer
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des SalesOffers:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = resolveActorId(req)

      await this.salesOfferService.deleteSalesOffer(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'SalesOffer gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des SalesOffers:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getExpiredSalesOffers(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const salesOffers = await this.salesOfferService.getExpiredSalesOffers(tenantId)

      res.json({
        success: true,
        data: salesOffers
      })
    } catch (error) {
      console.error('Fehler beim Laden abgelaufener SalesOffers:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getValidSalesOffers(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const salesOffers = await this.salesOfferService.getValidSalesOffers(tenantId)

      res.json({
        success: true,
        data: salesOffers
      })
    } catch (error) {
      console.error('Fehler beim Laden gültiger SalesOffers:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}
