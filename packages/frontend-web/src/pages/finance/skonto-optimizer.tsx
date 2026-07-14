import { useMemo, useRef, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentSuggestionBadge } from '@/components/agent/AgentSuggestionBadge'
import { AgentProcessPanel } from '@/components/agent'
import { AlertCircle, Euro, Search, Zap } from 'lucide-react'

type OpenItem = {
  id: string
  konto_name?: string | null
  rechnungsnr: string
  rechnungsdatum: string
  faelligkeit: string
  op_betrag: number
  offen: number
  waehrung?: string
  op_status: string
}

type OpenItemsResponse = {
  items: OpenItem[]
  summary: { count: number; op_summe: number; faellig: number; nicht_faellig: number }
}

type AgentSkontoResult = {
  zahlungsbetrag?: number
  valutatag?: string
  skonto_betrag?: number
  skonto_pct?: number
  empfehlung?: string
}

function daysUntil(dateStr: string): number {
  const diff = new Date(dateStr).getTime() - Date.now()
  return Math.ceil(diff / 86_400_000)
}

function skontoBetrag(item: OpenItem): number {
  // Rough estimate: 2% skonto if paid within 14 days
  const days = daysUntil(item.faelligkeit)
  if (days >= 0 && days <= 14) return Math.round(item.offen * 0.02 * 100) / 100
  return 0
}

export default function SkontoOptimizerPage(): JSX.Element {
  const navigate = useNavigate()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [agentSuggestion, setAgentSuggestion] = useState<AgentSkontoResult | null>(null)

  const { data, isLoading, refetch } = useQuery<OpenItemsResponse>({
    queryKey: ['finance', 'open-items', 'kreditoren', 'skonto'],
    queryFn: async () => {
      const res = await apiClient.get<OpenItemsResponse>('/api/v1/finance/open-items?typ=kreditoren&limit=200')
      return res.data
    },
  })

  const items = useMemo(() => {
    const raw = data?.items ?? []
    // Only items with active skonto window
    const eligible = raw.filter((i) => daysUntil(i.faelligkeit) >= 0 && daysUntil(i.faelligkeit) <= 14)
    if (!searchTerm.trim()) return eligible
    const term = searchTerm.trim().toLowerCase()
    return eligible.filter((i) =>
      [i.rechnungsnr, i.konto_name, i.faelligkeit]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(term)),
    )
  }, [data?.items, searchTerm])

  const totalSkonto = useMemo(
    () => items.reduce((sum, i) => sum + skontoBetrag(i), 0),
    [items],
  )

  const totalOffen = useMemo(() => items.reduce((sum, i) => sum + i.offen, 0), [items])

  const heuteAblaufend = items.filter((i) => daysUntil(i.faelligkeit) <= 3).length

  const shortcuts = buildCoreMaskShortcuts({
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => { void refetch() },
    onCancel: () => navigate('/finance/op-kreditoren'),
  })
  useKeyboardShortcuts(shortcuts)

  const agentParams = useMemo(
    () => ({ item_count: items.length, total_offen: totalOffen, heute_ablaufend: heuteAblaufend }),
    [items.length, totalOffen, heuteAblaufend],
  )

  const columns = [
    {
      key: 'konto_name' as const,
      label: 'Kreditor',
      render: (i: OpenItem) => (
        <div>
          <div className="font-medium">{i.konto_name ?? '-'}</div>
          <div className="font-mono text-xs text-muted-foreground">{i.rechnungsnr}</div>
        </div>
      ),
    },
    {
      key: 'faelligkeit' as const,
      label: 'Skonto bis',
      render: (i: OpenItem) => {
        const days = daysUntil(i.faelligkeit)
        return (
          <div className="flex items-center gap-2">
            <span>{new Date(i.faelligkeit).toLocaleDateString('de-DE')}</span>
            <Badge variant={days <= 3 ? 'destructive' : days <= 7 ? 'secondary' : 'outline'}>
              {days}d
            </Badge>
          </div>
        )
      },
    },
    {
      key: 'offen' as const,
      label: 'Offener Betrag (€)',
      render: (i: OpenItem) => (
        <span className="font-mono">{i.offen.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
      ),
    },
    {
      key: 'rechnungsnr' as const,
      label: 'Skonto (2%)',
      render: (i: OpenItem) => {
        const s = skontoBetrag(i)
        return s > 0 ? (
          <span className="font-mono font-semibold text-green-700">
            {s.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
          </span>
        ) : (
          <span className="text-muted-foreground">—</span>
        )
      },
    },
  ]

  if (isLoading) {
    return (
      <PageSurface data-page-surface="skonto-optimizer-loading" contentClassName="space-y-4">
        <Skeleton className="h-10 w-56" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </PageSurface>
    )
  }

  return (
    <PageSurface data-page-surface="skonto-optimizer" contentClassName="space-y-6">
      <PageSection description="KI-gestützte Skonto-Optimierung: offene Kreditorenposten mit aktiver Skontofrist und Agent-Empfehlung.">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold">Skonto-Optimierung</h1>
            <p className="text-muted-foreground">Kreditorenposten mit Skontopotenzial — Agent schlägt optimalen Zahlungsbetrag und Valutatag vor.</p>
          </div>
          <Button variant="outline" onClick={() => navigate('/finance/op-kreditoren')} className="min-h-touch gap-2 touch-manipulation">
            <Euro className="h-4 w-4" />
            OP Kreditoren
          </Button>
        </div>
      </PageSection>

      <AgentProcessPanel domain="finanzen" />

      <PageSection title="Skonto-Lage" description="Aktuelle Skontopotenziale aus offenen Kreditoren-Zahlungen.">
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Skonto-Posten</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Euro className="h-5 w-5 text-blue-600" />
                <span className="text-2xl font-bold">{items.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Skonto-Potenzial (€)</CardTitle></CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-success">
                {totalSkonto.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Heute/Morgen ablaufend</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {heuteAblaufend > 0 && <AlertCircle className="h-5 w-5 text-status-error" />}
                <span className={`text-2xl font-bold ${heuteAblaufend > 0 ? 'text-status-error' : ''}`}>
                  {heuteAblaufend}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Agent-Empfehlung" description="Der Skonto-Agent analysiert Fälligkeiten, Liquidität und empfiehlt optimalen Zahlungsplan.">
        <AgentSuggestionBadge<AgentSkontoResult>
          capabilityKey="skonto_optimizer"
          parameters={agentParams}
          label="Skonto-Optimierung starten"
          autoTrigger={false}
          onAccept={(suggestion) => setAgentSuggestion(suggestion)}
          renderSuggestion={(suggestion) => (
            <div className="space-y-1 text-sm">
              {suggestion.empfehlung && <p className="font-medium">{suggestion.empfehlung}</p>}
              {suggestion.zahlungsbetrag != null && (
                <p>Empfohlener Zahlungsbetrag: <span className="font-mono font-semibold">{suggestion.zahlungsbetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</span></p>
              )}
              {suggestion.valutatag && (
                <p>Valutatag: <span className="font-semibold">{new Date(suggestion.valutatag).toLocaleDateString('de-DE')}</span></p>
              )}
              {suggestion.skonto_betrag != null && (
                <p className="text-green-700">Skonto-Ersparnis: <span className="font-mono font-semibold">{suggestion.skonto_betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</span></p>
              )}
            </div>
          )}
        />

        {agentSuggestion && (
          <Card className="border-green-400 bg-green-50 mt-4">
            <CardContent className="pt-4">
              <div className="flex items-start gap-2">
                <Zap className="h-5 w-5 text-green-700 mt-0.5" />
                <div className="space-y-1 text-sm text-green-900">
                  <p className="font-semibold">Empfehlung übernommen</p>
                  {agentSuggestion.empfehlung && <p>{agentSuggestion.empfehlung}</p>}
                  {agentSuggestion.zahlungsbetrag != null && (
                    <p>Zahlungsbetrag: {agentSuggestion.zahlungsbetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</p>
                  )}
                  {agentSuggestion.valutatag && <p>Valutatag: {new Date(agentSuggestion.valutatag).toLocaleDateString('de-DE')}</p>}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </PageSection>

      <PageSection title="Skonto-Posten" description="Ctrl+F fokussiert die Suche, F5 aktualisiert, Escape zurück zu OP Kreditoren.">
        <div className="space-y-4">
          <div className="relative min-w-[18rem]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={searchInputRef}
              aria-label="Suche Skonto-Posten"
              placeholder="Kreditor, Rechnungsnr. oder Datum suchen"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="min-h-touch pl-10"
            />
          </div>
          <Card>
            <CardContent className="pt-6">
              <DataTable data={items} columns={columns} />
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <KeyboardShortcutBar shortcuts={shortcuts} />
    </PageSurface>
  )
}
