import { Auftragsbestaetigung } from '../entities/auftragsbestaetigung.entity'
import { AuftragsbestaetigungStatus } from '../entities/auftragsbestaetigung.entity'

export interface AuftragsbestaetigungRepository {
  save(ab: Auftragsbestaetigung): Promise<Auftragsbestaetigung>
  findById(id: string, tenantId: string): Promise<Auftragsbestaetigung | null>
  findByNummer(nummer: string, tenantId: string): Promise<Auftragsbestaetigung | null>
  findByBestellung(bestellungId: string, tenantId: string): Promise<Auftragsbestaetigung | null>
  findByTenant(tenantId: string, options?: {
    status?: AuftragsbestaetigungStatus
    bestellungId?: string
    limit?: number
    offset?: number
  }): Promise<Auftragsbestaetigung[]>
  findMitAbweichungen(tenantId: string): Promise<Auftragsbestaetigung[]>
  update(ab: Auftragsbestaetigung): Promise<Auftragsbestaetigung>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: AuftragsbestaetigungStatus): Promise<number>
}