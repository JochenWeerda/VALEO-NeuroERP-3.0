import { Angebot } from '../entities/angebot.entity'
import { AngebotStatus } from '../entities/angebot.entity'

export interface AngebotRepository {
  save(angebot: Angebot): Promise<Angebot>
  findById(id: string, tenantId: string): Promise<Angebot | null>
  findByNummer(nummer: string, tenantId: string): Promise<Angebot | null>
  findByTenant(tenantId: string, options?: {
    status?: AngebotStatus
    lieferantId?: string
    anfrageId?: string
    limit?: number
    offset?: number
  }): Promise<Angebot[]>
  findAbgelaufene(tenantId: string): Promise<Angebot[]>
  findByAnfrage(anfrageId: string, tenantId: string): Promise<Angebot[]>
  update(angebot: Angebot): Promise<Angebot>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: AngebotStatus): Promise<number>
}