import { Rechnungseingang } from '../entities/rechnungseingang.entity'
import { RechnungseingangStatus } from '../entities/rechnungseingang.entity'

export interface RechnungseingangRepository {
  save(rechnung: Rechnungseingang): Promise<Rechnungseingang>
  findById(id: string, tenantId: string): Promise<Rechnungseingang | null>
  findByNummer(nummer: string, tenantId: string): Promise<Rechnungseingang | null>
  findByBestellung(bestellungId: string, tenantId: string): Promise<Rechnungseingang[]>
  findByWareneingang(wareneingangId: string, tenantId: string): Promise<Rechnungseingang[]>
  findByTenant(tenantId: string, options?: {
    status?: RechnungseingangStatus
    lieferantId?: string
    bestellungId?: string
    wareneingangId?: string
    limit?: number
    offset?: number
  }): Promise<Rechnungseingang[]>
  findUeberfaellige(tenantId: string): Promise<Rechnungseingang[]>
  findMitAbweichungen(tenantId: string): Promise<Rechnungseingang[]>
  update(rechnung: Rechnungseingang): Promise<Rechnungseingang>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: RechnungseingangStatus): Promise<number>
  getGesamtOffen(tenantId: string): Promise<number>
}