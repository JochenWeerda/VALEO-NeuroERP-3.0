import { Request, Response } from 'express'
import { AuftragsbestaetigungService } from '../../application/services/auftragsbestaetigung.service'
import { CreateAuftragsbestaetigungData } from '../../application/services/auftragsbestaetigung.service'
import { AuftragsbestaetigungStatus } from '../../core/entities/auftragsbestaetigung.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError, respondDomainMutationError } from '../utils/request-context'

export class AuftragsbestaetigungController {
  constructor(private auftragsbestaetigungService: AuftragsbestaetigungService) {}

  async createAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const auditActorId = resolveActorId(req)

      const data: CreateAuftragsbestaetigungData = {
        bestaetigungsNummer: req.body.bestaetigungsNummer,
        bestellungId: req.body.bestellungId,
        bestaetigteTermine: req.body.bestaetigteTermine,
        preisabweichungen: req.body.preisabweichungen,
        tenantId,
        bemerkungen: req.body.bemerkungen
      }

      const ab = await this.auftragsbestaetigungService.createAuftragsbestaetigung(data, auditActorId)

      res.status(201).json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Auftragsbestätigung:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

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
      respondControllerError(res, error, 500)
    }
  }

  async getAuftragsbestaetigungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        status: req.query.status as any,
        bestellungId: req.query.bestellungId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.auftragsbestaetigungService.getAuftragsbestaetigungenByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigungen:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAuftragsbestaetigungByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = resolveTenantId(req)

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
      respondControllerError(res, error, 500)
    }
  }

  async pruefenAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const ab = await this.auftragsbestaetigungService.pruefenAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Prüfen der Auftragsbestätigung:', error)
      respondDomainMutationError(res, error)
    }
  }

  async bestaetigenAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const ab = await this.auftragsbestaetigungService.bestaetigenAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Bestätigen der Auftragsbestätigung:', error)
      respondDomainMutationError(res, error)
    }
  }

  async updateAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const ab = await this.auftragsbestaetigungService.updateAuftragsbestaetigung(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: ab
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Auftragsbestätigung:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deleteAuftragsbestaetigung(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      await this.auftragsbestaetigungService.deleteAuftragsbestaetigung(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Auftragsbestätigung gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Auftragsbestätigung:', error)
      respondDomainMutationError(res, error)
    }
  }

  async getAuftragsbestaetigungenMitAbweichungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const abs = await this.auftragsbestaetigungService.getAuftragsbestaetigungenMitAbweichungen(tenantId)

      res.json({
        success: true,
        data: abs
      })
    } catch (error) {
      console.error('Fehler beim Laden der Auftragsbestätigungen mit Abweichungen:', error)
      respondControllerError(res, error, 500)
    }
  }
}
