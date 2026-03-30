import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'

export type KontraktLookupResult = {
  contract_id: string
  contract_no: string
  line_id: string
  position_no: number
  article_id: string
  bezeichnung: string
  unit_price: number | null
  discount_pct: number | null
  qty_contract: number
  qty_remaining: number | null
  rest_quantity: number
  allow_overdelivery: boolean
  status: string
}

type UseKontraktLookupReturn = {
  resolveKontrakt: (contractNo: string, articleId?: string) => Promise<KontraktLookupResult | null>
  isResolving: boolean
}

export function useKontraktLookup(): UseKontraktLookupReturn {
  const [isResolving, setIsResolving] = useState(false)

  const resolveKontrakt = useCallback(
    async (contractNo: string, articleId?: string): Promise<KontraktLookupResult | null> => {
      if (!contractNo.trim()) return null
      setIsResolving(true)
      try {
        const res = await apiClient.post<{
          items: Array<{
            contract_id: string
            line_id: string
            contract_no: string
            position_no: number
            article_id: string
            bezeichnung: string
            valid_from?: string | null
            valid_to?: string | null
            name: string
          }>
        }>('/api/v1/kontrakte/lookup/verkauf', {
          query: contractNo,
          only_open: true,
          limit: 20,
        })

        const items = res.items ?? []
        if (items.length === 0) return null

        const exactMatch = items.find((i) => i.contract_no === contractNo)
        const match = exactMatch ?? items[0]

        const detail = await apiClient.get<{
          contract_id: string
          contract_no: string
          status: string
          rest_quantity: number
          allow_overdelivery: boolean
          lines: Array<{
            line_id: string
            position_no: number
            article_id: string
            description1?: string | null
            qty_contract: number
            qty_remaining?: number | null
            unit_price?: number | null
            discount_pct?: number | null
          }>
        }>(`/api/v1/kontrakte/${match.contract_id}`)

        let line = detail.lines.find((l) => l.line_id === match.line_id)
        if (articleId && !line) {
          line = detail.lines.find((l) => l.article_id === articleId)
        }
        if (!line) line = detail.lines[0]
        if (!line) return null

        return {
          contract_id: detail.contract_id,
          contract_no: detail.contract_no,
          line_id: line.line_id,
          position_no: line.position_no,
          article_id: line.article_id,
          bezeichnung: line.description1 ?? match.bezeichnung,
          unit_price: line.unit_price ?? null,
          discount_pct: line.discount_pct ?? null,
          qty_contract: line.qty_contract,
          qty_remaining: line.qty_remaining ?? null,
          rest_quantity: detail.rest_quantity,
          allow_overdelivery: detail.allow_overdelivery,
          status: detail.status,
        }
      } catch {
        return null
      } finally {
        setIsResolving(false)
      }
    },
    [],
  )

  return { resolveKontrakt, isResolving }
}
