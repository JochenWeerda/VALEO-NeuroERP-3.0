import { Request, Response } from 'express'
import { AnlieferavisService } from '../../application/services/anlieferavis.service'
import { CreateAnlieferavisData } from '../../application/services/anlieferavis.service'
import { AnlieferavisStatus } from '../../core/entities/anlieferavis.entity'

export class AnlieferavisController {
  constructor(private anlieferavisService: AnlieferavisService) {}

  async createAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

      const data: CreateAnlieferavisData = {
        avisNummer: req.body.avisNummer,
        bestellungId: req.body.bestellungId,
        geplantesAnlieferDatum: new Date(req.body.geplantesAnlieferDatum),
        fahrzeug: req.body.fahrzeug,
        positionen: req.body.positionen,
        tenantId,
        bemerkungen: req.body.bemerkungen
      }

      const avis = await this.anlieferavisService.createAnlieferavis(data)

      res.status(201).json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des Anlieferavis:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const avis = await this.anlieferavisService.getAnlieferavisById(id, tenantId)

      if (!avis) {
        res.status(404).json({
          success: false,
          error: 'Anlieferavis nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Laden des Anlieferavis:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAnlieferavise(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        bestellungId: req.query.bestellungId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const avise = await this.anlieferavisService.getAnlieferaviseByTenant(tenantId, options)

      res.json({
        success: true,
        data: avise,
        total: avise.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Anlieferavise:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAnlieferavisByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const avis = await this.anlieferavisService.getAnlieferavisByBestellung(bestellungId, tenantId)

      if (!avis) {
        res.status(404).json({
          success: false,
          error: 'Anlieferavis für diese Bestellung nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Laden des Anlieferavis zur Bestellung:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async bestaetigenAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const avis = await this.anlieferavisService.bestaetigenAnlieferavis(id, tenantId, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Bestätigen des Anlieferavis:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async stornierenAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const avis = await this.anlieferavisService.stornierenAnlieferavis(id, tenantId, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Stornieren des Anlieferavis:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const avis = await this.anlieferavisService.updateAnlieferavis(id, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Anlieferavis:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.anlieferavisService.deleteAnlieferavis(id, tenantId, actorId)

      res.json({
        success: true,
        message: 'Anlieferavis gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des Anlieferavis:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getUeberfaelligeAnlieferavise(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const avise = await this.anlieferavisService.getUeberfaelligeAnlieferavise(tenantId)

      res.json({
        success: true,
        data: avise
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Anlieferavise:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}