import { Request, Response } from 'express'
import { RechnungseingangService } from '../../application/services/rechnungseingang.service'
import { CreateRechnungseingangData } from '../../application/services/rechnungseingang.service'
import { RechnungseingangStatus } from '../../core/entities/rechnungseingang.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError, respondDomainMutationError } from '../utils/request-context'

export class RechnungseingangController {
  constructor(private rechnungseingangService: RechnungseingangService) {}

  async createRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const auditActorId = resolveActorId(req)

      const data: CreateRechnungseingangData = {
        rechnungsNummer: req.body.rechnungsNummer,
        lieferantId: req.body.lieferantId,
        bestellungId: req.body.bestellungId,
        wareneingangId: req.body.wareneingangId,
        rechnungsDatum: new Date(req.body.rechnungsDatum),
        bruttoBetrag: req.body.bruttoBetrag,
        nettoBetrag: req.body.nettoBetrag,
        steuerBetrag: req.body.steuerBetrag,
        steuerSatz: req.body.steuerSatz,
        skonto: req.body.skonto,
        zahlungsziel: req.body.zahlungsziel,
        positionen: req.body.positionen,
        abweichungen: req.body.abweichungen || [],
        tenantId,
        bemerkungen: req.body.bemerkungen
      }

      const rechnung = await this.rechnungseingangService.createRechnungseingang(data, auditActorId)

      res.status(201).json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des Rechnungseingangs:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

      const rechnung = await this.rechnungseingangService.getRechnungseingangById(id as string, tenantId)

      if (!rechnung) {
        res.status(404).json({
          success: false,
          error: 'Rechnungseingang nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Laden des Rechnungseingangs:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getRechnungseingaenge(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        status: req.query.status as any,
        lieferantId: req.query.lieferantId as string,
        bestellungId: req.query.bestellungId as string,
        wareneingangId: req.query.wareneingangId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.rechnungseingangService.getRechnungseingaengeByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getRechnungseingaengeByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = resolveTenantId(req)

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeByBestellung(bestellungId as string, tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge zur Bestellung:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getRechnungseingaengeByWareneingang(req: Request, res: Response): Promise<void> {
    try {
      const { wareneingangId } = req.params
      const tenantId = resolveTenantId(req)

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeByWareneingang(wareneingangId as string, tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge zum Wareneingang:', error)
      respondControllerError(res, error, 500)
    }
  }

  async pruefenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rechnung = await this.rechnungseingangService.pruefenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Prüfen des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async freigebenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rechnung = await this.rechnungseingangService.freigebenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Freigeben des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async verbuchenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rechnung = await this.rechnungseingangService.verbuchenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Verbuchen des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async bezahlenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rechnung = await this.rechnungseingangService.bezahlenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Bezahlen des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async updateRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rechnung = await this.rechnungseingangService.updateRechnungseingang(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deleteRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      await this.rechnungseingangService.deleteRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Rechnungseingang gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des Rechnungseingangs:', error)
      respondDomainMutationError(res, error)
    }
  }

  async getUeberfaelligeRechnungseingaenge(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const rechnungen = await this.rechnungseingangService.getUeberfaelligeRechnungseingaenge(tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Rechnungseingänge:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getRechnungseingaengeMitAbweichungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeMitAbweichungen(tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge mit Abweichungen:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getGesamtOffenerBetrag(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const betrag = await this.rechnungseingangService.getGesamtOffenerBetrag(tenantId)

      res.json({
        success: true,
        data: { gesamtOffenerBetrag: betrag }
      })
    } catch (error) {
      console.error('Fehler beim Laden des Gesamtbetrags offener Rechnungen:', error)
      respondControllerError(res, error, 500)
    }
  }
}
