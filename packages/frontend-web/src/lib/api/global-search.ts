import { apiClient } from '../api-client'

export interface GlobalSearchResult {
  id: string
  type: 'customer' | 'article' | 'order' | 'invoice' | 'partner' | 'contract'
  label: string
  sublabel?: string
  path: string
}

export interface GlobalSearchResponse {
  results: GlobalSearchResult[]
  total: number
}

export async function globalSearch(query: string): Promise<GlobalSearchResponse> {
  if (!query || query.trim().length < 2) {
    return { results: [], total: 0 }
  }
  const response = await apiClient.get<GlobalSearchResponse>('/api/v1/search', {
    params: { q: query.trim(), limit: 12 },
  })
  return response.data
}

export type QuickAction = {
  id: string
  label: string
  path: string
  keywords: string[]
}

export const QUICK_ACTIONS: QuickAction[] = [
  { id: 'new-order', label: 'Neuer Auftrag', path: '/verkauf/auftraege/neu', keywords: ['auftrag', 'neu', 'anlegen', 'erstellen', 'verkauf'] },
  { id: 'new-purchase-order', label: 'Neue Bestellung', path: '/einkauf/bestellungen/neu', keywords: ['bestellung', 'einkauf', 'neu', 'anlegen'] },
  { id: 'new-wareneingang', label: 'Wareneingang buchen', path: '/lager/wareneingang', keywords: ['wareneingang', 'einbuchen', 'lager', 'annahme'] },
  { id: 'new-invoice', label: 'Neue Rechnung', path: '/finance/rechnungen/neu', keywords: ['rechnung', 'faktura', 'neu', 'anlegen'] },
  { id: 'new-customer', label: 'Neuen Kunden anlegen', path: '/crm/kunden/neu', keywords: ['kunde', 'neu', 'anlegen', 'crm'] },
  { id: 'new-contract', label: 'Neuen Kontrakt anlegen', path: '/agrar/kontrakte/neu', keywords: ['kontrakt', 'agrar', 'neu', 'anlegen'] },
]
