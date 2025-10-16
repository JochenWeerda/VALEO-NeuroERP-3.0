import { Request, Response } from 'express'
import { RechnungseingangService } from '../../application/services/rechnungseingang.service'
import { CreateRechnungseingangData } from '../../application/services/rechnungseingang.service'
import { RechnungseingangStatus } from '../../core/entities/rechnungseingang.entity'

export class RechnungseingangController {
  constructor(private rechnungseingangService: RechnungseingangService) {}

  async createRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

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

      const rechnung = await this.rechnungseingangService.createRechnungseingang(data)

      res.status(201).json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Erstellen des Rechnungseingangs:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

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
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getRechnungseingaenge(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        lieferantId: req.query.lieferantId as string,
        bestellungId: req.query.bestellungId as string,
        wareneingangId: req.query.wareneingangId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeByTenant(tenantId, options)

      res.json({
        success: true,
        data: rechnungen,
        total: rechnungen.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getRechnungseingaengeByBestellung(req: Request, res: Response): Promise<void> {
    try {
      const { bestellungId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeByBestellung(bestellungId as string, tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge zur Bestellung:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getRechnungseingaengeByWareneingang(req: Request, res: Response): Promise<void> {
    try {
      const { wareneingangId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeByWareneingang(wareneingangId as string, tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge zum Wareneingang:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async pruefenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rechnung = await this.rechnungseingangService.pruefenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Prüfen des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async freigebenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rechnung = await this.rechnungseingangService.freigebenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Freigeben des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async verbuchenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rechnung = await this.rechnungseingangService.verbuchenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Verbuchen des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async bezahlenRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rechnung = await this.rechnungseingangService.bezahlenRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Bezahlen des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rechnung = await this.rechnungseingangService.updateRechnungseingang(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: rechnung
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteRechnungseingang(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.rechnungseingangService.deleteRechnungseingang(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Rechnungseingang gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen des Rechnungseingangs:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getUeberfaelligeRechnungseingaenge(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const rechnungen = await this.rechnungseingangService.getUeberfaelligeRechnungseingaenge(tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden überfälliger Rechnungseingänge:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getRechnungseingaengeMitAbweichungen(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const rechnungen = await this.rechnungseingangService.getRechnungseingaengeMitAbweichungen(tenantId)

      res.json({
        success: true,
        data: rechnungen
      })
    } catch (error) {
      console.error('Fehler beim Laden der Rechnungseingänge mit Abweichungen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getGesamtOffenerBetrag(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const betrag = await this.rechnungseingangService.getGesamtOffenerBetrag(tenantId)

      res.json({
        success: true,
        data: { gesamtOffenerBetrag: betrag }
      })
    } catch (error) {
      console.error('Fehler beim Laden des Gesamtbetrags offener Rechnungen:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}
