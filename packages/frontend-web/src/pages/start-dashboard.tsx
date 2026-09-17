import { useMemo, useState } from 'react'
import { Link } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import {
  DollarSign,
  Pin,
  PinOff,
  Search,
  ShoppingCart,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { getSectionPresentation } from '@/app/navigation/dashboard-catalog'
import {
  canonicalizeLaunchpadSpaceId,
  flattenLaunchpadTiles,
  launchpadTileSurface,
  matchesLaunchpadCatalogQuery,
  resolveLaunchpadSpaces,
} from '@/app/navigation/launchpad-spaces'
import { useNavSections } from '@/app/navigation/nav-runtime'
import { LaunchpadBoard } from '@/components/navigation/LaunchpadBoard'
import { useWorkspaceRedirect } from '@/hooks/useWorkspaceRedirect'
import type { NavItem } from '@/app/navigation/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useFeature } from '@/hooks/useFeature'
import { usePinnedTiles } from '@/hooks/usePinnedTiles'
import { useTranslation } from 'react-i18next'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/api-client'

type StarterTile = {
  id: string
  label: string
  description: string
  path: string
  icon: NavItem['icon']
  badgeIcon: LucideIcon
  badgeLabel: string
  landingLabel: string
  keywords: string[]
  sectionId: string
}

const SEARCH_KEYS = ['label', 'description'] as const
const NUM_DE = new Intl.NumberFormat('de-DE')
const LEITSTAND_PATH = '/workflow/leitstand'
const LETZTE_DOKUMENTE_PATH = '/workspace/letzte-dokumente'
const SPACE_STORAGE_KEY = 'valeo-launchpad-space'
const PAGE_STORAGE_KEY = 'valeo-launchpad-page'

function readStoredSpace(): string | undefined {
  try {
    return canonicalizeLaunchpadSpaceId(sessionStorage.getItem(SPACE_STORAGE_KEY) ?? undefined)
  } catch {
    return undefined
  }
}

function writeStoredSpace(spaceId: string): void {
  try {
    sessionStorage.setItem(SPACE_STORAGE_KEY, spaceId)
  } catch {
    // Best-effort: private mode may block sessionStorage.
  }
}

function readStoredPages(): Record<string, string> {
  try {
    const raw = sessionStorage.getItem(PAGE_STORAGE_KEY)
    if (!raw) {
      return {}
    }
    const parsed: unknown = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') {
      return {}
    }
    return Object.fromEntries(
      Object.entries(parsed as Record<string, unknown>).filter(
        (entry): entry is [string, string] => typeof entry[1] === 'string',
      ),
    )
  } catch {
    return {}
  }
}

function writeStoredPages(pages: Record<string, string>): void {
  try {
    sessionStorage.setItem(PAGE_STORAGE_KEY, JSON.stringify(pages))
  } catch {
    // Best-effort: private mode may block sessionStorage.
  }
}

interface KpiTile {
  key: string
  label: string
  path: string
  format: (v: number) => string
  icon: JSX.Element
  accentClass: string
}

const HOME_PRIMARY_ACTIONS = [
  { id: 'home-kunde', label: '+ Kunde', path: '/verkauf/kunden-stamm' },
  { id: 'home-angebot', label: '+ Angebot', path: '/sales/angebote' },
  { id: 'home-auftrag', label: '+ Auftrag', path: '/sales/order' },
  { id: 'home-aktivitaet', label: '+ Aktivität', path: '/crm/aktivitaeten' },
] as const

const EMPTY_START_KPIS: Record<string, number> = {}

const KPI_TILES: KpiTile[] = [
  {
    key: 'revenue',
    label: 'Umsatz',
    path: '/dashboard/sales',
    format: (v) => `\u20AC ${NUM_DE.format(v)}`,
    icon: <DollarSign className="h-4 w-4" />,
    accentClass: 'text-[hsl(var(--accent))]',
  },
  {
    key: 'orders',
    label: 'Auftraege',
    path: '/sales/order',
    format: (v) => NUM_DE.format(v),
    icon: <ShoppingCart className="h-4 w-4" />,
    accentClass: 'text-primary',
  },
  {
    key: 'customers',
    label: 'Kunden',
    path: '/verkauf/kunden-liste',
    format: (v) => NUM_DE.format(v),
    icon: <Users className="h-4 w-4" />,
    accentClass: 'text-primary',
  },
]

function toStarterTile(section: NavItem, lang?: string): StarterTile | null {
  const presentation = getSectionPresentation(section, lang)
  const path = presentation.landingPath
  if (!path) {
    return null
  }

  const keywords = (section.keywords ?? []).map((entry) => entry.toLowerCase())
  return {
    id: section.id,
    label: section.label,
    description: presentation.description,
    path,
    icon: section.icon,
    badgeIcon: presentation.domain.icon,
    badgeLabel: presentation.domain.label,
    landingLabel: presentation.landingLabel,
    keywords: [...keywords, presentation.domain.label.toLowerCase(), presentation.landingLabel.toLowerCase()],
    sectionId: section.id,
  }
}

function flattenStarterTiles(sections: NavItem[], lang?: string): StarterTile[] {
  return sections.reduce<StarterTile[]>((accumulator, section) => {
    const tile = toStarterTile(section, lang)
    if (tile) {
      accumulator.push(tile)
    }
    return accumulator
  }, [])
}

export default function StartDashboardPage(): JSX.Element {
  const { i18n } = useTranslation()
  // UIX-061: rollenbasierter Redirect auf cockpit-Workspace (flag-geschuetzt).
  useWorkspaceRedirect()
  const agrarEnabled = useFeature('agrar')
  const navSections = useNavSections()
  const [query, setQuery] = useState<string>('')
  const { pinnedTileIds, togglePin } = usePinnedTiles()

  const sections = useMemo(
    () => navSections.filter((section) => (section.featureKey === 'agrar' ? agrarEnabled : true)),
    [agrarEnabled, navSections],
  )

  const activeLang = i18n.resolvedLanguage ?? i18n.language ?? 'de'
  const allTiles = useMemo(() => flattenStarterTiles(sections, activeLang), [activeLang, sections])
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

  const launchpadSpaces = useMemo(
    () => resolveLaunchpadSpaces(sections, activeLang),
    [activeLang, sections],
  )
  const launchpadTiles = useMemo(() => flattenLaunchpadTiles(launchpadSpaces), [launchpadSpaces])
  const defaultSpaceId = launchpadSpaces[0]?.id ?? 'handel'
  const [spaceId, setSpaceId] = useState<string>(() => readStoredSpace() ?? defaultSpaceId)
  const [pageBySpace, setPageBySpace] = useState<Record<string, string>>(() => readStoredPages())
  const activeSpaceId = launchpadSpaces.some((space) => space.id === spaceId) ? spaceId : defaultSpaceId

  const searchHits = useMemo(() => {
    if (!normalizedQuery) {
      return []
    }
    return launchpadTiles.filter((tile) => {
      return matchesLaunchpadCatalogQuery(tile, normalizedQuery) || tile.pageLabel.toLowerCase().includes(normalizedQuery)
    })
  }, [launchpadTiles, normalizedQuery])

  const { data: kpis, isPending: kpiLoading } = useQuery({
    queryKey: queryKeys.analytics.kpis,
    queryFn: async () => {
      const res = await apiClient.get<Record<string, number>>('/api/v1/analytics/kpis')
      return res.data ?? {}
    },
    initialData: EMPTY_START_KPIS,
    initialDataUpdatedAt: 0, // initialData sofort als veraltet behandeln -> Fetch beim Mount
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  return (
    <div className="min-h-full space-y-10 px-0 py-4">
      <section className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-1">
          <p className="text-2xs tracking-wide uppercase text-muted-foreground">Start · Arbeitsplatz</p>
          <h1 className="text-2xl font-semibold tracking-normal text-foreground">Start</h1>
          <p className="text-sm text-muted-foreground">
            Wo bin ich, was kann ich tun, was ist wichtig. Der Prozessstand läuft am Beleg mit.
          </p>
        </div>
        <div className="relative w-full max-w-xl">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="pl-9"
            placeholder="Belege und Apps suchen..."
            aria-label="Belege und Apps suchen"
          />
        </div>
      </section>

      {normalizedQuery ? (
        <section className="space-y-3" aria-label="Suchtreffer">
          <h2 className="text-lg font-semibold text-foreground">Treffer</h2>
          {searchHits.length === 0 && filteredTiles.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Belege oder Apps gefunden.</p>
          ) : (
            <div className="flex flex-wrap gap-3">
              {searchHits.map((tile) => (
                <LaunchpadTile
                  key={`${tile.spaceId}-${tile.pageId}-${tile.id}`}
                  label={tile.label}
                  path={tile.path}
                  caption={tile.pageLabel}
                  colorKey={tile.id}
                />
              ))}
            </div>
          )}
        </section>
      ) : (
        <LaunchpadBoard
          catalogSpaces={launchpadSpaces}
          spaceId={activeSpaceId}
          onSpaceIdChange={(next) => {
            setSpaceId(next)
            writeStoredSpace(next)
          }}
          pageBySpace={pageBySpace}
          onPageBySpaceChange={(nextPages) => {
            setPageBySpace(nextPages)
            writeStoredPages(nextPages)
          }}
        />
      )}

      {pinnedTiles.length > 0 ? (
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Pin className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <h2 className="text-lg font-semibold">Favoriten</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {pinnedTiles.map((tile) => {
              const Icon = tile.icon
              const BadgeIcon = tile.badgeIcon
              return (
                <Card key={`pinned-${tile.id}`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg border border-border bg-background p-2">
                          <Icon className="h-4 w-4" />
                        </span>
                        <div>
                          <CardTitle className="text-base">
                            <Link to={tile.path} className="hover:underline">{tile.label}</Link>
                          </CardTitle>
                          <CardDescription>{tile.description}</CardDescription>
                          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                            <Badge variant="outline" className="inline-flex items-center gap-1">
                              <BadgeIcon className="h-3 w-3" />
                              {tile.badgeLabel}
                            </Badge>
                            <span>Startet mit: {tile.landingLabel}</span>
                          </div>
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

      <section className="flex flex-wrap items-center gap-2">
        <span className="text-2xs tracking-wide uppercase text-muted-foreground">Schnellaktionen</span>
        {HOME_PRIMARY_ACTIONS.map((action) => (
          <Button key={action.id} asChild variant="outline">
            <Link to={action.path}>{action.label}</Link>
          </Button>
        ))}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button type="button" variant="ghost" aria-label="Weitere Schnellaktionen">
              Mehr
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" side="top" className="z-[200] border bg-popover text-popover-foreground shadow-xl">
            {ACTION_SHORTCUTS.filter((action) => action.id !== 'action-kunden-schnellauswahl').map((action) => (
              <DropdownMenuItem key={action.id} asChild>
                <Link to={action.path}>{action.label}</Link>
              </DropdownMenuItem>
            ))}
            <DropdownMenuItem asChild>
              <Link to={LETZTE_DOKUMENTE_PATH}>Letzte Dokumente</Link>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      <section className="space-y-3" aria-label="Kennzahlen">
        <div className="grid gap-4 sm:grid-cols-3">
        {KPI_TILES.map((tile) => {
          const value = kpis?.[tile.key]
          return (
            <Link
              key={tile.key}
              to={tile.path}
              aria-label={`${tile.label} zur Auswertung`}
              className="group min-h-11 rounded-(--radius) border border-l-4 border-border border-l-[hsl(var(--accent))] bg-card px-4 py-4 shadow-sm transition-all hover:border-primary/40 hover:shadow-md focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">{tile.label}</span>
                <span className={tile.accentClass}>{tile.icon}</span>
              </div>
              <div className="mt-2">
                {kpiLoading ? (
                  <Skeleton className="h-7 w-20" />
                ) : (
                  <div className="text-xl font-bold tracking-normal tabular-nums text-foreground">
                    {value !== undefined ? tile.format(value) : '-'}
                  </div>
                )}
              </div>
              <p className="mt-2 text-xs font-medium text-primary group-hover:underline">Zur Auswertung</p>
            </Link>
          )
        })}
        </div>
        <p className="text-2xs text-muted-foreground">
          Zeitraum, Trend und Abweichung sind nicht ermittelt. Es werden keine Schätzwerte angezeigt.
        </p>
      </section>

      <p className="text-xs text-muted-foreground">
        Ausnahmen und übergreifende Koordination bleiben im{' '}
        <Link to={LEITSTAND_PATH} className="underline underline-offset-2 hover:text-foreground">
          Leitstand
        </Link>
        . Prozessräume sind kein Einstieg für das Tagesgeschäft.
      </p>
    </div>
  )
}

function LaunchpadTile({
  label,
  path,
  caption,
  colorKey,
}: {
  label: string
  path: string
  caption?: string
  colorKey: string
}): JSX.Element {
  const surface = launchpadTileSurface(colorKey)
  return (
    <Link
      to={path}
      aria-label={label}
      className="flex min-h-32 w-full max-w-52 shrink-0 flex-col justify-between rounded-(--radius) border border-l-4 p-3 shadow-sm transition-shadow hover:shadow-md focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring"
      style={surface}
    >
      {caption ? (
        <span className="text-2xs tracking-wide uppercase text-muted-foreground">{caption}</span>
      ) : (
        <span aria-hidden="true" />
      )}
      <span className="text-sm font-semibold leading-snug text-foreground">{label}</span>
    </Link>
  )
}
