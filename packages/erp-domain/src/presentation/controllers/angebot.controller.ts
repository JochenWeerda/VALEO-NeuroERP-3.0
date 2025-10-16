import { Request, Response } from 'express'
import { AngebotService } from '../../application/services/angebot.service'
import { CreateAngebotData } from '../../application/services/angebot.service'
import { AngebotStatus } from '../../core/entities/angebot.entity'

export class AngebotController {
  constructor(private angebotService: AngebotService) {}

  async createAngebot(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

      const data: CreateAngebotData = {
        angebotNummer: req.body.angebotNummer,
        anfrageId: req.body.anfrageId,
        lieferantId: req.body.lieferantId,
        artikel: req.body.artikel,
        menge: req.body.menge,
        einheit: req.body.einheit,
        preis: req.body.preis,
        waehrung: req.body.waehrung || 'EUR',
        lieferzeit: req.body.lieferzeit,
        gueltigBis: new Date(req.body.gueltigBis),
        tenantId,
        mindestabnahme: req.body.mindestabnahme,
        zahlungsbedingungen: req.body.zahlungsbedingungen,
        incoterms: req.body.incoterms,
        bemerkungen: req.body.bemerkungen
      }

      const angebot = await this.angebotService.createAngebot(data)

      res.status(201).json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des Angebots:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const angebot = await this.angebotService.getAngebotById(id, tenantId)

      if (!angebot) {
        res.status(404).json({
          success: false,
          error: 'Angebot nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Laden des Angebots:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAngebote(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        lieferantId: req.query.lieferantId as string,
        anfrageId: req.query.anfrageId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const angebote = await this.angebotService.getAngeboteByTenant(tenantId, options)

      res.json({
        success: true,
        data: angebote,
        total: angebote.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Angebote:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAngeboteByAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { anfrageId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const angebote = await this.angebotService.getAngeboteByAnfrage(anfrageId, tenantId)

      res.json({
        success: true,
        data: angebote
      })
    } catch (error) {
      console.error('Fehler beim Laden der Angebote zur Anfrage:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async pruefenAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const angebot = await this.angebotService.pruefenAngebot(id, tenantId, actorId)

      res.json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Prüfen des Angebots:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async genehmigenAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const angebot = await this.angebotService.genehmigenAngebot(id, tenantId, actorId)

      res.json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Genehmigen des Angebots:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async ablehnenAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const angebot = await this.angebotService.ablehnenAngebot(id, tenantId, actorId)

      res.json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Ablehnen des Angebots:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const angebot = await this.angebotService.updateAngebot(id, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: angebot
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Angebots:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteAngebot(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.angebotService.deleteAngebot(id, tenantId, actorId)

      res.json({
        success: true,
        message: 'Angebot gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des Angebots:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAbgelaufeneAngebote(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const angebote = await this.angebotService.getAbgelaufeneAngebote(tenantId)

      res.json({
        success: true,
        data: angebote
      })
    } catch (error) {
      console.error('Fehler beim Laden abgelaufener Angebote:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}