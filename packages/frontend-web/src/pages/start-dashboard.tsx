import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  DollarSign,
  Package,
  Pin,
  PinOff,
  Search,
  ShoppingCart,
  Users,
} from 'lucide-react'
import {
  ACTION_SHORTCUTS,
  NAV_SECTIONS,
  type NavItem,
} from '@/app/navigation/manifest'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useFeature } from '@/hooks/useFeature'
import { usePinnedTiles } from '@/hooks/usePinnedTiles'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/axios'

type StarterTile = {
  id: string
  label: string
  description: string
  path: string
  icon: NavItem['icon']
  keywords: string[]
  sectionId: string
}

const SEARCH_KEYS = ['label', 'description'] as const
const MAX_CHILD_LINKS = 7
const NUM_DE = new Intl.NumberFormat('de-DE')

interface KpiTile {
  key: string
  label: string
  path: string
  format: (v: number) => string
  icon: JSX.Element
}

const KPI_TILES: KpiTile[] = [
  { key: 'revenue', label: 'Umsatz', path: '/dashboard/sales', format: (v) => `\u20AC ${NUM_DE.format(v)}`, icon: <DollarSign className="h-4 w-4" /> },
  { key: 'orders', label: 'Auftraege', path: '/sales/order', format: (v) => NUM_DE.format(v), icon: <ShoppingCart className="h-4 w-4" /> },
  { key: 'customers', label: 'Kunden', path: '/verkauf/kunden-liste', format: (v) => NUM_DE.format(v), icon: <Users className="h-4 w-4" /> },
  { key: 'inventory', label: 'Lagerauslastung', path: '/lager/bestandsuebersicht', format: (v) => `${v}%`, icon: <Package className="h-4 w-4" /> },
]

function toStarterTile(section: NavItem): StarterTile | null {
  const resolvedPath = section.path ?? findFirstRoutableChildPath(section)
  if (!resolvedPath) {
    return null
  }

  const keywords = (section.keywords ?? []).map((entry) => entry.toLowerCase())
  return {
    id: section.id,
    label: section.label,
    description: `${section.mcp.businessDomain.toUpperCase()} - ${section.mcp.scope}`,
    path: resolvedPath,
    icon: section.icon,
    keywords,
    sectionId: section.id,
  }
}

function findFirstRoutableChildPath(item: NavItem): string | null {
  if (item.path && !item.path.includes(':')) {
    return item.path
  }
  if (!item.children || item.children.length === 0) {
    return null
  }
  for (const child of item.children) {
    const found = findFirstRoutableChildPath(child)
    if (found) {
      return found
    }
  }
  return null
}

function getSectionShortcuts(section: NavItem): Array<NavItem & { path: string }> {
  if (!section.children) {
    return []
  }

  return section.children
    .filter((child): child is NavItem & { path: string } => {
      if (!child.path || child.path.includes(':')) {
        return false
      }
      return true
    })
    .slice(0, MAX_CHILD_LINKS)
}

function flattenStarterTiles(sections: NavItem[]): StarterTile[] {
  return sections.reduce<StarterTile[]>((accumulator, section) => {
    const tile = toStarterTile(section)
    if (tile) {
      accumulator.push(tile)
    }
    return accumulator
  }, [])
}

export default function StartDashboardPage(): JSX.Element {
  const agrarEnabled = useFeature('agrar')
  const [query, setQuery] = useState<string>('')
  const { isPinned, pinnedTileIds, togglePin } = usePinnedTiles()

  const sections = useMemo(
    () => NAV_SECTIONS.filter((section) => (section.featureKey === 'agrar' ? agrarEnabled : true)),
    [agrarEnabled],
  )

  const allTiles = useMemo(() => flattenStarterTiles(sections), [sections])
  const normalizedQuery = query.trim().toLowerCase()

  const filteredTiles = useMemo(() => {
    if (!normalizedQuery) {
      return allTiles
    }

    return allTiles.filter((tile) => {
      const keywordMatch = tile.keywords.some((keyword) => keyword.includes(normalizedQuery))
      const textMatch = SEARCH_KEYS.some((key) => tile[key].toLowerCase().includes(normalizedQuery))
      return keywordMatch || textMatch
    })
  }, [allTiles, normalizedQuery])

  const pinnedTiles = useMemo(
    () => allTiles.filter((tile) => pinnedTileIds.includes(tile.id)),
    [allTiles, pinnedTileIds],
  )

  const { data: kpis, isPending: kpiLoading } = useQuery({
    queryKey: queryKeys.analytics.kpis,
    queryFn: async () => {
      const res = await apiClient.get<Record<string, number>>('/api/v1/analytics/kpis')
      return res.data
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  return (
    <div className="space-y-6">
      {/* KPI-Streifen */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {KPI_TILES.map((tile) => {
          const value = kpis?.[tile.key]
          return (
            <Link key={tile.key} to={tile.path} className="hover:shadow-md transition-shadow rounded-lg">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">{tile.label}</span>
                    <span className="text-muted-foreground">{tile.icon}</span>
                  </div>
                  <div className="mt-2">
                    {kpiLoading ? (
                      <Skeleton className="h-8 w-24" />
                    ) : (
                      <div className="text-2xl font-bold">
                        {value !== undefined ? tile.format(value) : '-'}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </section>

      <section className="rounded-2xl border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">App Starter</h1>
            <p className="text-sm text-muted-foreground">
              Einstieg in alle VALEO ERP Bereiche mit aktueller Modul-Verdrahtung.
            </p>
          </div>
          <div className="relative w-full max-w-xl">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="pl-9"
              placeholder="Module durchsuchen..."
              aria-label="Module durchsuchen"
            />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="secondary">{allTiles.length} Bereiche</Badge>
          <Badge variant="outline">{ACTION_SHORTCUTS.length} Schnellaktionen</Badge>
          <Badge variant="outline">{pinnedTiles.length} Favoriten</Badge>
        </div>
      </section>

      <section className="rounded-2xl border bg-card p-4 shadow-sm">
        <h2 className="text-lg font-semibold">Schnellaktionen</h2>
        <p className="mb-3 text-sm text-muted-foreground">
          Haeufige Startaktionen fuer Tagesgeschaeft und neue Belege.
        </p>
        <div className="flex flex-wrap gap-2">
          {ACTION_SHORTCUTS.map((action) => (
            <Button key={action.id} asChild variant="outline" size="sm">
              <Link to={action.path}>{action.label}</Link>
            </Button>
          ))}
        </div>
      </section>

      {pinnedTiles.length > 0 ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Pin className="h-4 w-4 text-amber-600" />
            <h2 className="text-lg font-semibold">Favoriten</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {pinnedTiles.map((tile) => {
              const Icon = tile.icon
              return (
                <Card key={`pinned-${tile.id}`} className="border-amber-200 bg-amber-50/40">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg border bg-background p-2">
                          <Icon className="h-4 w-4" />
                        </span>
                        <div>
                          <CardTitle className="text-base">{tile.label}</CardTitle>
                          <CardDescription>{tile.description}</CardDescription>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => togglePin(tile.id)}
                        aria-label={`${tile.label} entpinnen`}
                      >
                        <PinOff className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Button asChild size="sm">
                      <Link to={tile.path}>Oeffnen</Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filteredTiles.map((tile) => {
          const section = sections.find((entry) => entry.id === tile.sectionId)
          const shortcuts = section ? getSectionShortcuts(section) : []
          const Icon = tile.icon

          return (
            <Card key={tile.id} className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="rounded-lg border bg-muted/40 p-2">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div>
                      <CardTitle className="text-base">
                        <Link to={tile.path} className="hover:underline">{tile.label}</Link>
                      </CardTitle>
                      <CardDescription>{tile.description}</CardDescription>
                    </div>
                  </div>
                  <Button
                    variant={isPinned(tile.id) ? 'secondary' : 'ghost'}
                    size="icon"
                    onClick={() => togglePin(tile.id)}
                    aria-label={isPinned(tile.id) ? `${tile.label} entpinnen` : `${tile.label} pinnen`}
                  >
                    <Pin className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {shortcuts.map((shortcut) => (
                    <Button key={shortcut.id} asChild variant="outline" size="sm">
                      <Link to={shortcut.path}>{shortcut.label}</Link>
                    </Button>
                  ))}
                </div>
                <Button asChild size="sm">
                  <Link to={tile.path}>Bereich oeffnen</Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </section>
    </div>
  )
}
