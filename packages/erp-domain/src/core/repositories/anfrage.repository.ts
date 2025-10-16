import { Anfrage } from '../entities/anfrage.entity'
import { AnfrageStatus, Prioritaet } from '../entities/anfrage.entity'

export interface AnfrageRepository {
  save(anfrage: Anfrage): Promise<Anfrage>
  findById(id: string, tenantId: string): Promise<Anfrage | null>
  findByNummer(nummer: string, tenantId: string): Promise<Anfrage | null>
  findByTenant(tenantId: string, options?: {
    status?: AnfrageStatus
    prioritaet?: Prioritaet
    anforderer?: string
    limit?: number
    offset?: number
  }): Promise<Anfrage[]>
  findUeberfaellige(tenantId: string): Promise<Anfrage[]>
  findDringende(tenantId: string): Promise<Anfrage[]>
  update(anfrage: Anfrage): Promise<Anfrage>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: AnfrageStatus): Promise<number>
}