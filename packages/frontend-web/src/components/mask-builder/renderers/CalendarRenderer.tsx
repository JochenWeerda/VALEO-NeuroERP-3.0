import { memo, useMemo, useState } from 'react'
import { CalendarDays, ChevronRight, Download, RefreshCw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api-client'
import { useNavigate } from '@/app/routing/typed-router'
import type { RenderCalendarPlan } from '../render-plan/types'

type CalendarItem = {
  id: string
  layer: string
  item_type: string
  title: string
  starts_at: string
  ends_at?: string | null
  all_day: boolean
  status: string
  object_route?: string | null
  object_screen_id?: string | null
  payload?: Record<string, unknown>
}

const LAYER_TONE: Record<string, string> = {
  finanzen: 'border-l-emerald-600',
  fristen: 'border-l-amber-500',
  crm: 'border-l-sky-600',
  logistik: 'border-l-indigo-600',
  personal: 'border-l-rose-600',
  saison: 'border-l-lime-600',
}

function startOfToday(): Date {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

function isoDate(date: Date): string {
  return date.toISOString()
}

function addDays(date: Date, days: number): Date {
  const copy = new Date(date)
  copy.setDate(copy.getDate() + days)
  return copy
}

function formatDate(value: string): string {
  const date = new Date(value)
  return new Intl.DateTimeFormat('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(date)
}

export const CalendarRenderer = memo(function CalendarRenderer({
  calendar,
  initialItems,
}: {
  calendar?: RenderCalendarPlan
  /** Test hook; production fetches from calendar.endpoint. */
  initialItems?: CalendarItem[]
}): JSX.Element | null {
  const navigate = useNavigate()
  const [activeLayers, setActiveLayers] = useState<Set<string>>(
    () => new Set(calendar?.layers.filter((layer) => layer.defaultVisible).map((layer) => layer.key) ?? []),
  )
  const [view, setView] = useState(calendar?.defaultView ?? 'agenda')
  const today = useMemo(() => startOfToday(), [])
  const to = useMemo(() => addDays(today, 30), [today])
  const queryLayers = [...activeLayers].join(',')
  const endpoint = calendar?.endpoint

  const query = useQuery({
    queryKey: ['planung-kalender', endpoint, isoDate(today), isoDate(to), queryLayers],
    enabled: Boolean(endpoint) && !initialItems,
    queryFn: async () => {
      if (!endpoint) return []
      const params = new URLSearchParams({ from: isoDate(today), to: isoDate(to) })
      if (queryLayers) params.set('layers', queryLayers)
      const response = await apiClient.get<CalendarItem[]>(`${endpoint}?${String(params)}`)
      return response.data
    },
    staleTime: 60_000,
  })

  if (!calendar) return null

  const items = initialItems ?? query.data ?? []
  const visibleItems = items
    .filter((item) => activeLayers.has(item.layer))
    .sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const deadlineUntil = addDays(today, calendar.deadlineBandDays)
  const deadlines = visibleItems.filter((item) => {
    const starts = new Date(item.starts_at)
    return starts >= today && starts < deadlineUntil && item.item_type === 'frist'
  })

  return (
    <section data-testid="calendar-renderer" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <CalendarDays className="h-4 w-4 shrink-0 text-muted-foreground" />
          <h2 className="text-sm font-semibold">Planungskalender</h2>
        </div>
        <div className="flex items-center gap-1">
          {(['month', 'week', 'agenda'] as const).map((key) => (
            <Button
              key={key}
              type="button"
              size="sm"
              variant={view === key ? 'default' : 'outline'}
              onClick={() => setView(key)}
              data-testid={`calendar-view-${key}`}
            >
              {key === 'month' ? 'Monat' : key === 'week' ? 'Woche' : 'Agenda'}
            </Button>
          ))}
          {calendar.reprojectEndpoint && (
            <Button type="button" size="icon" variant="outline" aria-label="Kalender neu projizieren" data-testid="calendar-reproject">
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
          {calendar.icsTokenEndpoint && (
            <Button type="button" size="icon" variant="outline" aria-label="ICS Feed" data-testid="calendar-ics">
              <Download className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2" aria-label="Kalender-Layer">
        {calendar.layers.map((layer) => {
          const active = activeLayers.has(layer.key)
          return (
            <button
              key={layer.key}
              type="button"
              className={`rounded-md border px-2.5 py-1 text-xs font-medium ${active ? 'bg-primary text-primary-foreground' : 'bg-background text-muted-foreground'}`}
              aria-pressed={active}
              data-testid={`calendar-layer-${layer.key}`}
              onClick={() => {
                setActiveLayers((prev) => {
                  const next = new Set(prev)
                  if (next.has(layer.key)) next.delete(layer.key)
                  else next.add(layer.key)
                  return next
                })
              }}
            >
              {layer.label}
            </button>
          )
        })}
      </div>

      <div className="rounded-md border bg-muted/30 p-3" data-testid="calendar-deadline-band">
        <div className="mb-2 text-xs font-medium text-muted-foreground">Fristenband naechste {calendar.deadlineBandDays} Tage</div>
        {deadlines.length === 0 ? (
          <div className="text-sm text-muted-foreground">Keine Fristen im sichtbaren Zeitraum.</div>
        ) : (
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
            {deadlines.map((item) => (
              <button
                key={item.id}
                type="button"
                data-testid={`calendar-deadline-${item.id}`}
                className={`rounded-md border border-l-4 ${LAYER_TONE[item.layer] ?? 'border-l-border'} bg-card px-3 py-2 text-left text-sm hover:bg-accent`}
                onClick={() => item.object_route && navigate(item.object_route)}
              >
                <span className="block font-medium">{item.title}</span>
                <span className="text-xs text-muted-foreground">{formatDate(item.starts_at)}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-2" data-view={view} data-testid="calendar-agenda">
        {query.isLoading && <div className="text-sm text-muted-foreground">Kalender wird geladen...</div>}
        {!query.isLoading && visibleItems.length === 0 && <div className="text-sm text-muted-foreground">Keine Kalendereintraege im Zeitraum.</div>}
        {visibleItems.map((item) => (
          <button
            key={item.id}
            type="button"
            data-testid={`calendar-item-${item.id}`}
            className={`flex items-center justify-between gap-3 rounded-md border border-l-4 ${LAYER_TONE[item.layer] ?? 'border-l-border'} bg-card px-3 py-2 text-left hover:bg-accent`}
            onClick={() => item.object_route && navigate(item.object_route)}
            disabled={!item.object_route}
          >
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">{item.title}</span>
              <span className="text-xs text-muted-foreground">{formatDate(item.starts_at)} · {item.layer} · {item.status}</span>
            </span>
            {item.object_route && <ChevronRight className="h-4 w-4 shrink-0 opacity-60" />}
          </button>
        ))}
      </div>
    </section>
  )
})
