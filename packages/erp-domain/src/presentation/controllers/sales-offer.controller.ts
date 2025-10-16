import { Request, Response } from 'express'
import { SalesOfferService } from '../../application/services/sales-offer.service'
import { CreateSalesOfferData } from '../../application/services/sales-offer.service'
import { SalesOfferStatus } from '../../core/entities/sales-offer.entity'

export class SalesOfferController {
  constructor(private salesOfferService: SalesOfferService) {}

  async createSalesOffer(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

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

      const salesOffer = await this.salesOfferService.createSalesOffer(data)

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
      const actorId = 'system' // TODO: Aus Auth-Middleware

      // TODO: CustomerInquiry laden und SalesOffer erstellen
      // Für jetzt einfach eine Fehlermeldung
      res.status(501).json({
        success: false,
        error: 'Funktion noch nicht implementiert - CustomerInquiry Service fehlt'
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

      const salesOffer = await this.salesOfferService.getSalesOfferById(id, tenantId)

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
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const salesOffers = await this.salesOfferService.getSalesOffersByTenant(tenantId, options)

      res.json({
        success: true,
        data: salesOffers,
        total: salesOffers.length // TODO: Pagination-Info
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

      const salesOffers = await this.salesOfferService.getSalesOffersByCustomerInquiry(inquiryId, tenantId)

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
      const actorId = req.user?.id || 'system'

      const salesOffer = await this.salesOfferService.sendSalesOffer(id, tenantId, actorId)

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
      const actorId = req.user?.id || 'system'

      const salesOffer = await this.salesOfferService.acceptSalesOffer(id, tenantId, actorId)

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
      const actorId = req.user?.id || 'system'

      const salesOffer = await this.salesOfferService.rejectSalesOffer(id, tenantId, actorId)

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
      const actorId = req.user?.id || 'system'

      const salesOffer = await this.salesOfferService.updateSalesOffer(id, tenantId, req.body, actorId)

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
      const actorId = req.user?.id || 'system'

      await this.salesOfferService.deleteSalesOffer(id, tenantId, actorId)

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