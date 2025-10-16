import { Anlieferavis } from '../entities/anlieferavis.entity'
import { AnlieferavisStatus } from '../entities/anlieferavis.entity'

export interface AnlieferavisRepository {
  save(avis: Anlieferavis): Promise<Anlieferavis>
  findById(id: string, tenantId: string): Promise<Anlieferavis | null>
  findByNummer(nummer: string, tenantId: string): Promise<Anlieferavis | null>
  findByBestellung(bestellungId: string, tenantId: string): Promise<Anlieferavis | null>
  findByTenant(tenantId: string, options?: {
    status?: AnlieferavisStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Anlieferavis[]>
  findUeberfaellige(tenantId: string): Promise<Anlieferavis[]>
  update(avis: Anlieferavis): Promise<Anlieferavis>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: AnlieferavisStatus): Promise<number>
}