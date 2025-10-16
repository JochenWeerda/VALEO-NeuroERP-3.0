import { Request, Response } from 'express'
import { AnfrageService } from '../../application/services/anfrage.service'
import { CreateAnfrageData } from '../../application/services/anfrage.service'
import { AnfrageTyp, Prioritaet } from '../../core/entities/anfrage.entity'

export class AnfrageController {
  constructor(private anfrageService: AnfrageService) {}

  async createAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

      const data: CreateAnfrageData = {
        anfrageNummer: req.body.anfrageNummer,
        typ: req.body.typ as AnfrageTyp,
        anforderer: req.body.anforderer,
        artikel: req.body.artikel,
        menge: req.body.menge,
        einheit: req.body.einheit,
        prioritaet: req.body.prioritaet as Prioritaet,
        faelligkeit: new Date(req.body.faelligkeit),
        begruendung: req.body.begruendung,
        tenantId,
        kostenstelle: req.body.kostenstelle,
        projekt: req.body.projekt,
        bemerkungen: req.body.bemerkungen
      }

      const anfrage = await this.anfrageService.createAnfrage(data)

      res.status(201).json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Anfrage:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const anfrage = await this.anfrageService.getAnfrageById(id as string, tenantId)

      if (!anfrage) {
        res.status(404).json({
          success: false,
          error: 'Anfrage nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Laden der Anfrage:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        prioritaet: req.query.prioritaet as any,
        anforderer: req.query.anforderer as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const anfragen = await this.anfrageService.getAnfragenByTenant(tenantId, options)

      res.json({
        success: true,
        data: anfragen,
        total: anfragen.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Anfragen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async freigebenAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const anfrage = await this.anfrageService.freigebenAnfrage(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Freigeben der Anfrage:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const anfrage = await this.anfrageService.updateAnfrage(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Anfrage:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.anfrageService.deleteAnfrage(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Anfrage gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Anfrage:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getUeberfaelligeAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const anfragen = await this.anfrageService.getUeberfaelligeAnfragen(tenantId)

      res.json({
        success: true,
        data: anfragen
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Anfragen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getDringendeAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const anfragen = await this.anfrageService.getDringendeAnfragen(tenantId)

      res.json({
        success: true,
        data: anfragen
      })
    } catch (error) {
      console.error('Fehler beim Laden dringender Anfragen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}
