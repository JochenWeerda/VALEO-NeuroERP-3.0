import { Request, Response } from 'express'
import { AnfrageService } from '../../application/services/anfrage.service'
import { CreateAnfrageData } from '../../application/services/anfrage.service'
import { AnfrageTyp, Prioritaet } from '../../core/entities/anfrage.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import {
  resolveActorId,
  resolveTenantId,
  respondControllerError,
  respondDomainMutationError,
} from '../utils/request-context'

export class AnfrageController {
  constructor(private anfrageService: AnfrageService) {}

  async createAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const auditActorId = resolveActorId(req)

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

      const anfrage = await this.anfrageService.createAnfrage(data, auditActorId)

      res.status(201).json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Anfrage:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

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
      respondControllerError(res, error, 500)
    }
  }

  async getAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        status: req.query.status as any,
        prioritaet: req.query.prioritaet as any,
        anforderer: req.query.anforderer as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.anfrageService.getAnfragenByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Anfragen:', error)
      respondControllerError(res, error, 500)
    }
  }

  async freigebenAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const anfrage = await this.anfrageService.freigebenAnfrage(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Freigeben der Anfrage:', error)
      respondDomainMutationError(res, error)
    }
  }

  async updateAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const anfrage = await this.anfrageService.updateAnfrage(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: anfrage
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Anfrage:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deleteAnfrage(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      await this.anfrageService.deleteAnfrage(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Anfrage gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Anfrage:', error)
      respondDomainMutationError(res, error)
    }
  }

  async getUeberfaelligeAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const anfragen = await this.anfrageService.getUeberfaelligeAnfragen(tenantId)

      res.json({
        success: true,
        data: anfragen
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Anfragen:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getDringendeAnfragen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const anfragen = await this.anfrageService.getDringendeAnfragen(tenantId)

      res.json({
        success: true,
        data: anfragen
      })
    } catch (error) {
      console.error('Fehler beim Laden dringender Anfragen:', error)
      respondControllerError(res, error, 500)
    }
  }
}
