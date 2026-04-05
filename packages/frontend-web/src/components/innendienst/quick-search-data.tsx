import type { ReactNode } from 'react'
import {
  Clock,
  FileText,
  Package,
  Search,
  ShoppingCart,
  Users,
  type LucideIcon,
} from 'lucide-react'
import type { SearchResult } from '@/components/innendienst/QuickSearch'

const RECENT_SEARCHES_KEY = 'valeo-recent-searches'

type SearchResultDescriptor = Omit<SearchResult, 'id'> & {
  id: string
  match: (_query: string) => boolean
}

const SEARCH_FIXTURES: SearchResultDescriptor[] = [
  {
    id: 'c1',
    type: 'customer',
    title: 'Landwirtschaft Mueller GmbH',
    subtitle: 'Hauptstrasse 15, 12345 Neustadt',
    meta: 'Kunde seit 2019',
    url: '/verkauf/kunden-liste',
    match: (query) => query.includes('mueller') || query.includes('muller'),
  },
  {
    id: 'a1',
    type: 'article',
    title: 'Weizen Saatgut Premium Elite',
    subtitle: 'ART-001 | 25,50 EUR/kg',
    meta: 'Bestand: 2.500 kg',
    url: '/artikel/1',
    match: (query) => query.includes('weizen') || query.includes('duenger') || query.includes('dunger'),
  },
  {
    id: 'a2',
    type: 'article',
    title: 'NPK Duenger 15-15-15',
    subtitle: 'ART-002 | 180,00 EUR/t',
    meta: 'Bestand: 45 t',
    url: '/artikel/2',
    match: (query) => query.includes('weizen') || query.includes('duenger') || query.includes('dunger'),
  },
]

const TYPE_ICON_COMPONENTS: Record<SearchResult['type'], LucideIcon> = {
  customer: Users,
  order: ShoppingCart,
  article: Package,
  invoice: FileText,
  delivery: Package,
}

export const typeColors: Record<SearchResult['type'], string> = {
  customer: 'text-blue-600 bg-blue-100',
  order: 'text-emerald-600 bg-emerald-100',
  article: 'text-purple-600 bg-purple-100',
  invoice: 'text-amber-600 bg-amber-100',
  delivery: 'text-cyan-600 bg-cyan-100',
}

export const typeIcons: Record<SearchResult['type'], ReactNode> = Object.fromEntries(
  Object.entries(TYPE_ICON_COMPONENTS).map(([type, Icon]) => [type, <Icon className="h-4 w-4" key={type} />]),
) as Record<SearchResult['type'], ReactNode>

export async function searchAll(query: string): Promise<SearchResult[]> {
  if (!query || query.length < 2) {
    return []
  }

  await new Promise((resolve) => setTimeout(resolve, 300))

  const normalizedQuery = query.toLowerCase()
  const results = SEARCH_FIXTURES.filter((fixture) => fixture.match(normalizedQuery)).map(({ match: _match, ...result }) => result)

  if (/\d{4,}/.test(query)) {
    results.push({
      id: 'o1',
      type: 'order',
      title: `Auftrag #${query}`,
      subtitle: 'Landwirtschaft Mueller GmbH',
      meta: '15.01.2026',
      url: `/sales/auftraege-liste/${query}`,
    })
  }

  if (results.length === 0) {
    results.push(
      {
        id: 'c2',
        type: 'customer',
        title: `Suche nach "${query}" in Kunden...`,
        url: `/verkauf/kunden-liste?search=${encodeURIComponent(query)}`,
      },
      {
        id: 'a3',
        type: 'article',
        title: `Suche nach "${query}" in Artikeln...`,
        url: `/artikel?search=${encodeURIComponent(query)}`,
      },
    )
  }

  return results
}

export function loadRecentSearches(): SearchResult[] {
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    return stored ? (JSON.parse(stored) as SearchResult[]) : []
  } catch {
    return []
  }
}

export function storeRecentSearches(nextRecentSearches: SearchResult[]): void {
  try {
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(nextRecentSearches))
  } catch {
    // Ignore storage issues in fallback mode.
  }
}

export const recentSearchIcon = <Clock className="h-3 w-3" />
export const emptySearchIcon = <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
