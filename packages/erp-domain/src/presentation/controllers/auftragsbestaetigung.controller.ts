import { Request, Response } from 'express'
import { AuftragsbestaetigungService } from '../../application/services/auftragsbestaetigung.service'
import { CreateAuftragsbestaetigungData } from '../../application/services/auftragsbestaetigung.service'
import { AuftragsbestaetigungStatus } from '../../core/entities/auftragsbestaetigung.entity'

export class AuftragsbestaetigungController {
  constructor(private auftragsbestaetigungService: AuftragsbestaetigungService) {}

  async createAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

      const data: CreateAuftragsbestaetigungData = {
        bestaetigungsNummer: req.body.bestaetigungsNummer,
        bestellungId: req.body.bestellungId,
        bestaetigteTermine: req.body.bestaetigteTermine,
        preisabweichungen: req.body.preisabweichungen,
        tenantId,
        bemerkungen: req.body.bemerkungen
      }

      const ab = await this.auftragsbestaetigungService.createAuftragsbestaetigung(data)

      res.status(201).json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Auftragsbestätigung:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const ab = await this.auftragsbestaetigungService.getAuftragsbestaetigungById(id as string, tenantId)

      if (!ab) {
        res.status(404).json({
          success: false,
          error: 'Auftragsbestätigung nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigung:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuftragsbestaetigungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        bestellungId: req.query.bestellungId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const abs = await this.auftragsbestaetigungService.getAuftragsbestaetigungenByTenant(tenantId, options)

      res.json({
        success: true,
        data: abs,
        total: abs.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigungen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuftragsbestaetigungByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const ab = await this.auftragsbestaetigungService.getAuftragsbestaetigungByBestellung(bestellungId as string, tenantId)

      if (!ab) {
        res.status(404).json({
          success: false,
          error: 'Auftragsbestätigung für diese Bestellung nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigung zur Bestellung:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async pruefenAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const ab = await this.auftragsbestaetigungService.pruefenAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Prüfen der Auftragsbestätigung:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async bestaetigenAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const ab = await this.auftragsbestaetigungService.bestaetigenAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Bestätigen der Auftragsbestätigung:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const ab = await this.auftragsbestaetigungService.updateAuftragsbestaetigung(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Auftragsbestätigung:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.auftragsbestaetigungService.deleteAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Auftragsbestätigung gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Auftragsbestätigung:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAuftragsbestaetigungenMitAbweichungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const abs = await this.auftragsbestaetigungService.getAuftragsbestaetigungenMitAbweichungen(tenantId)

      res.json({
        success: true,
        data: abs
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigungen mit Abweichungen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}
