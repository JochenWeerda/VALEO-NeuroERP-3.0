import { Request, Response } from 'express'
import { AnlieferavisService } from '../../application/services/anlieferavis.service'
import { CreateAnlieferavisData } from '../../application/services/anlieferavis.service'
import { AnlieferavisStatus } from '../../core/entities/anlieferavis.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError, respondDomainMutationError } from '../utils/request-context'

export class AnlieferavisController {
  constructor(private anlieferavisService: AnlieferavisService) {}

  async createAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const auditActorId = resolveActorId(req)

      const data: CreateAnlieferavisData = {
        avisNummer: req.body.avisNummer,
        bestellungId: req.body.bestellungId,
        geplantesAnlieferDatum: new Date(req.body.geplantesAnlieferDatum),
        fahrzeug: req.body.fahrzeug,
        positionen: req.body.positionen,
        tenantId,
        bemerkungen: req.body.bemerkungen
      }

      const avis = await this.anlieferavisService.createAnlieferavis(data, auditActorId)

      res.status(201).json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des Anlieferavis:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

      const avis = await this.anlieferavisService.getAnlieferavisById(id as string, tenantId)

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
      respondControllerError(res, error, 500)
    }
  }

  async getAnlieferavise(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        status: req.query.status as any,
        bestellungId: req.query.bestellungId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.anlieferavisService.getAnlieferaviseByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Anlieferavise:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAnlieferavisByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = resolveTenantId(req)

      const avis = await this.anlieferavisService.getAnlieferavisByBestellung(bestellungId as string, tenantId)

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
      respondControllerError(res, error, 500)
    }
  }

  async bestaetigenAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const avis = await this.anlieferavisService.bestaetigenAnlieferavis(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Bestätigen des Anlieferavis:', error)
      respondDomainMutationError(res, error)
    }
  }

  async stornierenAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const avis = await this.anlieferavisService.stornierenAnlieferavis(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Stornieren des Anlieferavis:', error)
      respondDomainMutationError(res, error)
    }
  }

  async updateAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const avis = await this.anlieferavisService.updateAnlieferavis(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: avis
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Anlieferavis:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deleteAnlieferavis(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      await this.anlieferavisService.deleteAnlieferavis(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Anlieferavis gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des Anlieferavis:', error)
      respondDomainMutationError(res, error)
    }
  }

  async getUeberfaelligeAnlieferavise(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const avise = await this.anlieferavisService.getUeberfaelligeAnlieferavise(tenantId)

      res.json({
        success: true,
        data: avise
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Anlieferavise:', error)
      respondControllerError(res, error, 500)
    }
  }
}
