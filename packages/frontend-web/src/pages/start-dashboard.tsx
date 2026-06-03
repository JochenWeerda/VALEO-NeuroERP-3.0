import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowRight,
  DollarSign,
  Package,
  Pin,
  PinOff,
  Search,
  ShoppingCart,
  Users,
  Zap,
  type LucideIcon,
} from 'lucide-react'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { getDomainPresentation, getSectionPresentation } from '@/app/navigation/dashboard-catalog'
import { useNavSections } from '@/app/navigation/nav-runtime'
import type { NavItem } from '@/app/navigation/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useFeature } from '@/hooks/useFeature'
import { usePinnedTiles } from '@/hooks/usePinnedTiles'
import { useTranslation } from 'react-i18next'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/api-client'
import { fetchFlowSpineCatalog, getFlowSpineFetchErrorMessage, type FlowSpineCatalog } from '@/lib/api/flow-spines'

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
const MAX_CHILD_LINKS = 7
const NUM_DE = new Intl.NumberFormat('de-DE')

interface KpiTile {
  key: string
  label: string
  path: string
  format: (v: number) => string
  icon: JSX.Element
  accentClass: string
}

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
    path: '/crm/kunden-schnellauswahl',
    format: (v) => NUM_DE.format(v),
    icon: <Users className="h-4 w-4" />,
    accentClass: 'text-primary',
  },
  {
    key: 'inventory',
    label: 'Lagerauslastung',
    path: '/lager/bestandsuebersicht',
    format: (v) => `${v}%`,
    icon: <Package className="h-4 w-4" />,
    accentClass: 'text-[hsl(var(--accent))]',
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

function flattenStarterTiles(sections: NavItem[], lang?: string): StarterTile[] {
  return sections.reduce<StarterTile[]>((accumulator, section) => {
    const tile = toStarterTile(section, lang)
    if (tile) {
      accumulator.push(tile)
    }
    return accumulator
  }, [])
}

const DOMAIN_COLOR: Record<string, string> = {
  'order-to-cash': 'from-indigo-500/20 to-indigo-600/5 border-indigo-500/30',
  'procure-to-pay': 'from-amber-500/20 to-amber-600/5 border-amber-500/30',
  'inventory-to-settlement': 'from-sky-500/20 to-sky-600/5 border-sky-500/30',
  'harvest-to-settlement': 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/30',
  'contract-to-settlement': 'from-violet-500/20 to-violet-600/5 border-violet-500/30',
  'complaint-to-resolution': 'from-rose-500/20 to-rose-600/5 border-rose-500/30',
  'service-to-customer': 'from-cyan-500/20 to-cyan-600/5 border-cyan-500/30',
  'finance-to-close': 'from-green-500/20 to-green-600/5 border-green-500/30',
  'compliance-to-report': 'from-teal-500/20 to-teal-600/5 border-teal-500/30',
}

export default function StartDashboardPage(): JSX.Element {
  const { i18n } = useTranslation()
  const agrarEnabled = useFeature('agrar')
  const navSections = useNavSections()
  const navigate = useNavigate()
  const [query, setQuery] = useState<string>('')
  const { isPinned, pinnedTileIds, togglePin } = usePinnedTiles()

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

  const {
    data: flowCatalog,
    isPending: flowCatalogPending,
    isError: flowCatalogError,
    error: flowCatalogErr,
  } = useQuery<FlowSpineCatalog>({
    queryKey: ['flow-spine', 'catalog', activeLang],
    queryFn: fetchFlowSpineCatalog,
    staleTime: 120_000,
    retry: false,
  })

  return (
    <div className="min-h-full space-y-8 px-0 py-2">
      {/* KPI-Streifen */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {KPI_TILES.map((tile) => {
          const value = kpis?.[tile.key]
          return (
            <Link
              key={tile.key}
              to={tile.path}
              className="group rounded-[var(--radius)] border border-l-4 border-border border-l-[hsl(var(--accent))] bg-card shadow-sm transition-all hover:border-primary/40 hover:shadow-md"
            >
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">{tile.label}</span>
                  <span className={tile.accentClass}>{tile.icon}</span>
                </div>
                <div className="mt-3">
                  {kpiLoading ? (
                    <Skeleton className="h-8 w-24" />
                  ) : (
                    <div className="text-2xl font-bold tracking-normal tabular-nums text-foreground">
                      {value !== undefined ? tile.format(value) : '-'}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          )
        })}
      </section>

      {/* Flow Spine E2E-Prozesse */}
      <section className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-primary/10">
            <Zap className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold leading-none text-foreground">Flow Spine Prozesse</h2>
            <p className="mt-0.5 text-xs text-muted-foreground">End-to-End Prozesskontrolle mit KI-Copilot</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {flowCatalogPending && !flowCatalog
            ? Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-20 w-full rounded-2xl" />)
            : null}
          {flowCatalogError ? (
            <div className="sm:col-span-2 xl:col-span-3 rounded-2xl border border-destructive/25 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              Flow-Spine-Katalog konnte nicht geladen werden: {getFlowSpineFetchErrorMessage(flowCatalogErr)}. Lokal FastAPI starten und Vite{' '}
              <code className="rounded bg-muted px-1 text-xs">/api/v1</code> auf Port 8000 proxien.
            </div>
          ) : null}
          {!flowCatalogPending &&
          !flowCatalogError &&
          flowCatalog &&
          (!flowCatalog.processes?.length ? (
            <div className="sm:col-span-2 xl:col-span-3 text-sm text-muted-foreground">
              Keine Flow-Spine-Prozesse im Katalog-Antwort (leeres <code className="rounded bg-muted px-1 text-xs">processes</code>-Array).
            </div>
          ) : (
            flowCatalog.processes.map((proc) => {
                const gradient = DOMAIN_COLOR[proc.key] ?? 'from-slate-500/20 to-slate-600/5 border-slate-500/30'
                const domain = getDomainPresentation(proc.domain, activeLang)
                const DomainIcon = domain.icon
                return (
                  <button
                    key={proc.key}
                    type="button"
                    onClick={() => navigate(proc.route_path)}
                    className={`group flex flex-col items-start gap-1 rounded-2xl border bg-gradient-to-br p-4 text-left shadow-sm transition-all hover:shadow-md dark:hover:brightness-110 ${gradient}`}
                  >
                    <div className="flex w-full items-center justify-between">
                      <span className="text-sm font-semibold">{proc.label}</span>
                      <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </div>
                    <span className="text-xs text-muted-foreground line-clamp-2">{proc.summary}</span>
                    <Badge
                      variant="outline"
                      className="mt-2 inline-flex items-center gap-1 rounded-full border-white/20 bg-white/10 px-2.5 py-1 text-[10px] font-medium tracking-[0.12em] text-foreground/90"
                    >
                      <DomainIcon className="h-3 w-3" />
                      {domain.label}
                    </Badge>
                  </button>
                )
              })
          ))}
        </div>
      </section>

      {/* Header + Suche */}
      <section className="rounded-[var(--radius)] border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-normal text-foreground">App Starter</h1>
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

      {/* Schnellaktionen */}
      <section className="rounded-[var(--radius)] border border-border bg-card p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-foreground">Schnellaktionen</h2>
        <p className="mb-3 text-sm text-muted-foreground">
          Haeufige Startaktionen fuer Tagesgeschaeft und neue Belege.
        </p>
        <div className="flex flex-wrap gap-2">
          {ACTION_SHORTCUTS.map((action) => (
            <Button
              key={action.id}
              asChild
              variant="outline"
              size="sm"
              className="dark:border-white/10 dark:bg-slate-900/50 dark:hover:border-indigo-400/40 dark:hover:bg-slate-800/60"
            >
              <Link to={action.path}>{action.label}</Link>
            </Button>
          ))}
        </div>
      </section>

      {/* Favoriten */}
      {pinnedTiles.length > 0 ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Pin className="h-4 w-4 text-amber-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold">Favoriten</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {pinnedTiles.map((tile) => {
              const Icon = tile.icon
              const BadgeIcon = tile.badgeIcon
              return (
                <Card
                  key={`pinned-${tile.id}`}
                  className="border-amber-200 bg-amber-50/40 dark:border-amber-500/25 dark:bg-amber-500/5"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg border border-border bg-background p-2 dark:border-white/10 dark:bg-slate-900/60">
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
                        className="dark:hover:bg-white/5"
                      >
                        <PinOff className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Button
                      asChild
                      size="sm"
                      className="dark:bg-indigo-600/80 dark:text-white dark:hover:bg-indigo-600"
                    >
                      <Link to={tile.path}>Oeffnen</Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>
      ) : null}

      {/* Alle Module */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filteredTiles.map((tile) => {
          const section = sections.find((entry) => entry.id === tile.sectionId)
          const shortcuts = section ? getSectionShortcuts(section) : []
          const Icon = tile.icon
          const BadgeIcon = tile.badgeIcon

          return (
            <div
              key={tile.id}
              className="flex h-full flex-col rounded-2xl border border-border bg-card shadow-sm dark:border-white/10 dark:bg-slate-950/60"
            >
              <div className="p-4 pb-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="rounded-lg border border-border bg-muted/40 p-2 dark:border-white/10 dark:bg-slate-800/60">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div>
                      <div className="text-base font-semibold leading-tight">
                        <Link to={tile.path} className="hover:underline hover:text-indigo-500 dark:hover:text-indigo-400">
                          {tile.label}
                        </Link>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">{tile.description}</div>
                      <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                        <Badge variant="outline" className="inline-flex items-center gap-1">
                          <BadgeIcon className="h-3 w-3" />
                          {tile.badgeLabel}
                        </Badge>
                        <span>Öffnet: {tile.landingLabel}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant={isPinned(tile.id) ? 'secondary' : 'ghost'}
                    size="icon"
                    onClick={() => togglePin(tile.id)}
                    aria-label={isPinned(tile.id) ? `${tile.label} entpinnen` : `${tile.label} pinnen`}
                    className="shrink-0 dark:hover:bg-white/5"
                  >
                    <Pin className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="flex flex-1 flex-col gap-3 px-4 pb-4">
                {shortcuts.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {shortcuts.map((shortcut) => (
                      <Button
                        key={shortcut.id}
                        asChild
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs dark:border-white/10 dark:bg-slate-900/40 dark:hover:border-indigo-400/30 dark:hover:bg-slate-800/50"
                      >
                        <Link to={shortcut.path}>{shortcut.label}</Link>
                      </Button>
                    ))}
                  </div>
                )}
                <Button
                  asChild
                  size="sm"
                  className="mt-auto self-start dark:bg-indigo-600/70 dark:text-white dark:hover:bg-indigo-600"
                >
                  <Link to={tile.path}>Bereich oeffnen</Link>
                </Button>
              </div>
            </div>
          )
        })}
      </section>
    </div>
  )
}
