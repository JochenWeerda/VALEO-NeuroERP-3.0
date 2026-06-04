import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Käufergruppen-Klassifikation: Katalog + Bestätigen/Überschreiben durch den Vertrieb.
 * Die Einordnung ist erklärbar (Begründung) und korrigierbar (mit Audit-Log).
 */

export type KaeufergruppeKatalogItem = {
  group: string
  label: string
  ziel_anteil_min: number
  ziel_anteil_max: number
  abschluss_faktor: number
  grenzaufwand: number
  ansatz: string
}

export function useKaeufergruppenKatalog() {
  return useQuery({
    queryKey: ['kaeufergruppe-katalog'],
    queryFn: async () => {
      const res = await apiClient.get<KaeufergruppeKatalogItem[]>('/api/v1/crm/kaeufergruppe/katalog')
      return Array.isArray(res.data) ? res.data : []
    },
    staleTime: 600_000,
  })
}

export function useSetKaeufergruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { kunden_nr: string; group: string; bediener?: string; kommentar?: string }) => {
      const { kunden_nr, ...body } = input
      const res = await apiClient.post(`/api/v1/crm/kaeufergruppe/${encodeURIComponent(kunden_nr)}/setzen`, { ...body, source: 'manual' })
      return res.data
    },
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: ['bedarfsdeckung', vars.kunden_nr] })
      void qc.invalidateQueries({ queryKey: ['bedarfsdeckung-pipeline'] })
    },
  })
}
