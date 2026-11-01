import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDomainIdentity } from '../intake/domain-data'
import type { Waage } from '@/lib/api/betrieb'

export type ScaleApiRow = {
  id: string; standort: string; typ: string; max_kapazitaet: number
  letzte_eichung?: string | null; naechste_eichung?: string | null; status: string
}
export function mapScale(row: ScaleApiRow): Waage {
  return { id: row.id, standort: row.standort, typ: row.typ, maxKapazitaet: row.max_kapazitaet,
    letzteEichung: row.letzte_eichung ?? '', naechsteEichung: row.naechste_eichung ?? '', status: row.status as Waage['status'] }
}
export function useDomainScales() {
  const { tenantId, actor } = useDomainIdentity()
  return useQuery({ queryKey: ['studio-scales', tenantId, actor], enabled: Boolean(tenantId && actor), queryFn: async () => {
    const response = await apiClient.get<ScaleApiRow[]>('/api/v1/waage/waagen?limit=1000')
    if (!Array.isArray(response.data)) throw new Error('Ungültige Waagenliste')
    return response.data.map(mapScale)
  } })
}
