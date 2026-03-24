import { useMemo, useState } from 'react'
import {
  Bell,
  BookOpen,
  ChevronRight,
  Clock3,
  FileText,
  LayoutGrid,
  MoreHorizontal,
  Package,
  Receipt,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Truck,
  UserCircle2,
  Wallet,
} from 'lucide-react'
import { PageSurface, PageSection } from '@/components/patterns/PageSurface'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import { AgentProcessPanel } from '@/components/agent'

type NodeStatus = 'ok' | 'warning' | 'critical' | 'active'

type FlowNode = {
  id: string
  label: string
  status: NodeStatus
  value: string
  timestamp: string
  kpi: string
  insight: string
}

const flowNodes: FlowNode[] = [
  {
    id: 'order',
    label: 'Auftrag',
    status: 'ok',
    value: 'EUR 48.200',
    timestamp: '08:14',
    kpi: 'Deckungsbeitrag 18,4%',
    insight: 'Auftrag komplett, Bonitaet bestaetigt.',
  },
  {
    id: 'check',
    label: 'Pruefung',
    status: 'ok',
    value: '3 Checks',
    timestamp: '08:19',
    kpi: 'Freigabe in 2 Min.',
    insight: 'Kreditlimit und Lieferfenster sind gruen.',
  },
  {
    id: 'delivery',
    label: 'Lieferung',
    status: 'active',
    value: '2 Touren',
    timestamp: 'Heute',
    kpi: 'ETA +45 Min.',
    insight: 'Lieferverzug wahrscheinlich, Alternativroute empfohlen.',
  },
  {
    id: 'invoice',
    label: 'Rechnung',
    status: 'warning',
    value: '1 wartend',
    timestamp: 'Heute',
    kpi: 'SLA 81%',
    insight: 'Rechnungsfreigabe haengt an Lieferbestaetigung.',
  },
  {
    id: 'payment',
    label: 'Zahlung',
    status: 'warning',
    value: 'Skonto offen',
    timestamp: 'T+10',
    kpi: '2% Potenzial',
    insight: 'Fruehe Zahlung steigert Marge.',
  },
  {
    id: 'close',
    label: 'Abschluss',
    status: 'critical',
    value: '1 Risiko',
    timestamp: 'T+30',
    kpi: 'Marge gefaehrdet',
    insight: 'Korrekturbedarf moeglich, wenn Verzug eintritt.',
  },
]

function statusClasses(status: NodeStatus): string {
  switch (status) {
    case 'ok':
      return 'border-emerald-500/50 bg-emerald-500/12 text-emerald-200'
    case 'warning':
      return 'border-amber-500/50 bg-amber-500/12 text-amber-100'
    case 'critical':
      return 'border-rose-500/60 bg-rose-500/12 text-rose-100'
    case 'active':
      return 'border-indigo-400/70 bg-indigo-400/15 text-indigo-100 shadow-[0_0_40px_rgba(99,102,241,0.28)]'
  }
}

function statusBadge(status: NodeStatus): string {
  switch (status) {
    case 'ok':
      return 'OK'
    case 'warning':
      return 'RISIKO'
    case 'critical':
      return 'KRITISCH'
    case 'active':
      return 'AKTIV'
  }
}

export default function FlowSpineStudioPage(): JSX.Element {
  const [selectedNodeId, setSelectedNodeId] = useState<string>('delivery')
  const selectedNode = useMemo(
    () => flowNodes.find((node) => node.id === selectedNodeId) ?? flowNodes[0],
    [selectedNodeId],
  )

  return (
    <PageSurface data-page-surface="flow-spine-studio" className="bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.12),_transparent_30%),linear-gradient(180deg,#071120,#0b1326)]">
      <div className="flex min-h-full flex-col gap-6">
        <PageSection className="border-white/10 bg-slate-950/60 p-0 shadow-2xl shadow-indigo-950/20">
          <header className="flex h-16 items-center justify-between border-b border-white/5 px-5">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-200">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-semibold tracking-wide text-slate-100">Flow Spine UI</div>
                <div className="text-xs text-slate-400">Order-to-Cash / Auftrag O2C-4711</div>
              </div>
            </div>

            <div className="flex flex-1 items-center justify-center px-4">
              <div className="relative w-full max-w-xl">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <Input
                  aria-label="Globale Suche"
                  placeholder="Auftrag 4711, Rechnung RE-2026-004 oder Kunde suchen ..."
                  className="border-white/10 bg-white/5 pl-9 text-slate-100 placeholder:text-slate-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Badge variant="outline" className="border-indigo-400/30 bg-indigo-400/10 text-indigo-100">
                Flow
              </Badge>
              <Button variant="ghost" size="icon" className="text-slate-300 hover:bg-white/5 hover:text-white">
                <Bell className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="text-slate-300 hover:bg-white/5 hover:text-white">
                <Settings className="h-4 w-4" />
              </Button>
              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-100">
                <UserCircle2 className="h-5 w-5 text-slate-300" />
                <span>Operations Lead</span>
              </div>
            </div>
          </header>

          <div className="grid min-h-[720px] grid-cols-[240px_minmax(0,1fr)_320px]">
            <aside className="border-r border-white/5 bg-slate-950/40 p-4">
              <div className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Prozesse</p>
                <div className="space-y-2">
                  {[
                    { label: 'Order-to-Cash', active: true },
                    { label: 'Procure-to-Pay' },
                    { label: 'Inventory-to-Settlement' },
                  ].map((item) => (
                    <button
                      key={item.label}
                      className={cn(
                        'flex w-full items-center justify-between rounded-2xl px-3 py-3 text-left text-sm transition',
                        item.active
                          ? 'bg-indigo-500/12 text-indigo-100 ring-1 ring-indigo-400/20'
                          : 'bg-white/0 text-slate-300 hover:bg-white/5 hover:text-white',
                      )}
                    >
                      <span>{item.label}</span>
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Favoriten</p>
                <div className="space-y-2 text-sm text-slate-300">
                  <div className="rounded-2xl bg-white/5 px-3 py-3">Auftrag O2C-4711</div>
                  <div className="rounded-2xl bg-white/5 px-3 py-3">Rechnung RE-2026-004</div>
                </div>
              </div>

              <div className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Letzte Vorgaenge</p>
                <div className="space-y-2 text-sm text-slate-400">
                  <div className="rounded-2xl border border-white/5 px-3 py-3">Lieferung TOUR-88 aktualisiert</div>
                  <div className="rounded-2xl border border-white/5 px-3 py-3">Skonto-Empfehlung erkannt</div>
                </div>
              </div>

              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Rollenwechsel</p>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Sales Manager
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Finance Controller
                  </Button>
                </div>
              </div>
            </aside>

            <main className="overflow-hidden bg-[linear-gradient(180deg,rgba(15,23,42,0.45),rgba(15,23,42,0.15))] p-6">
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-white">Flow Spine - Order-to-Cash</h1>
                  <p className="mt-1 max-w-2xl text-sm text-slate-400">
                    Prozesszentrierter Arbeitsraum fuer Verstaendnis, Steuerung und agentische Assistenz statt Listen-Navigation.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className="bg-emerald-500/15 text-emerald-200 hover:bg-emerald-500/15">SLA stabil</Badge>
                  <Badge className="bg-amber-500/15 text-amber-100 hover:bg-amber-500/15">1 kritische Abweichung</Badge>
                </div>
              </div>

              <div className="relative rounded-[28px] border border-white/10 bg-white/[0.03] p-8 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
                <div className="pointer-events-none absolute left-12 right-12 top-1/2 h-1 -translate-y-1/2 rounded-full bg-white/5" />
                <div className="pointer-events-none absolute left-12 top-1/2 h-1 w-[58%] -translate-y-1/2 rounded-full bg-gradient-to-r from-emerald-400 via-indigo-400 to-amber-400 opacity-80" />

                <div className="relative grid grid-cols-6 gap-4">
                  {flowNodes.map((node) => {
                    const active = node.id === selectedNodeId
                    const Icon =
                      node.id === 'order'
                        ? Package
                        : node.id === 'check'
                          ? ShieldCheck
                          : node.id === 'delivery'
                            ? Truck
                            : node.id === 'invoice'
                              ? Receipt
                              : node.id === 'payment'
                                ? Wallet
                                : BookOpen

                    return (
                      <button
                        key={node.id}
                        onClick={() => setSelectedNodeId(node.id)}
                        className={cn(
                          'group flex flex-col items-center gap-3 rounded-3xl p-3 text-center transition duration-200',
                          active ? 'scale-[1.04]' : 'hover:-translate-y-1 hover:scale-[1.02]',
                        )}
                      >
                        <div
                          className={cn(
                            'flex h-16 w-16 items-center justify-center rounded-full border text-sm font-bold transition',
                            statusClasses(node.status),
                            active && 'h-20 w-20 shadow-[0_0_48px_rgba(99,102,241,0.25)]',
                          )}
                        >
                          <Icon className={cn('h-6 w-6', active && 'h-7 w-7')} />
                        </div>

                        <div className="space-y-1">
                          <div className="text-sm font-semibold text-slate-100">{node.label}</div>
                          <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-400">
                            {statusBadge(node.status)}
                          </div>
                          <div className="text-xs text-slate-500">{node.value}</div>
                          <div className="text-[11px] text-slate-400">{node.kpi}</div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="mt-6 grid gap-5 xl:grid-cols-[1fr_340px]">
                <Card className="border-white/10 bg-slate-950/45 text-slate-100">
                  <CardHeader className="flex flex-row items-start justify-between gap-4">
                    <div>
                      <CardTitle className="text-xl">Fokus-Modus: {selectedNode.label}</CardTitle>
                      <p className="mt-1 text-sm text-slate-400">{selectedNode.insight}</p>
                    </div>
                    <Badge className={cn('border px-2.5 py-1 text-xs', statusClasses(selectedNode.status))}>
                      {statusBadge(selectedNode.status)}
                    </Badge>
                  </CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <Card className="border-white/10 bg-white/[0.03]">
                      <CardHeader>
                        <CardTitle className="text-sm text-slate-200">KPIs</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2 text-sm text-slate-300">
                        <div className="flex items-center justify-between"><span>Marge</span><span>14,8%</span></div>
                        <div className="flex items-center justify-between"><span>Durchlaufzeit</span><span>3,2 Tage</span></div>
                        <div className="flex items-center justify-between"><span>SLA</span><span>81%</span></div>
                      </CardContent>
                    </Card>

                    <Card className="border-white/10 bg-white/[0.03]">
                      <CardHeader>
                        <CardTitle className="text-sm text-slate-200">Dokumente</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 text-sm text-slate-300">
                        <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> Lieferschein LS-884</div>
                        <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> Tourenfreigabe PDF</div>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">Upload</Button>
                      </CardContent>
                    </Card>

                    <Card className="border-white/10 bg-white/[0.03]">
                      <CardHeader>
                        <CardTitle className="text-sm text-slate-200">Aktionen</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Button className="w-full bg-indigo-500 text-white hover:bg-indigo-400">Lieferung starten</Button>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">Freigabe senden</Button>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">Rechnung erzeugen</Button>
                      </CardContent>
                    </Card>

                    <Card className="border-rose-400/20 bg-rose-500/10">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-sm text-rose-100">
                          <Sparkles className="h-4 w-4" />
                          Agent
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 text-sm text-rose-50/90">
                        <p>Lieferverzug wahrscheinlich (78%). Alternativlieferant oder Umlagerung empfohlen.</p>
                        <ul className="space-y-1 text-xs text-rose-100/80">
                          <li>- Lieferant A verspaetet</li>
                          <li>- Lagerbestand kritisch</li>
                        </ul>
                        <div className="grid grid-cols-3 gap-2">
                          <Button size="sm" className="bg-white text-slate-900 hover:bg-white/90">Uebernehmen</Button>
                          <Button size="sm" variant="outline" className="border-white/20 bg-white/5 text-white hover:bg-white/10">Anpassen</Button>
                          <Button size="sm" variant="ghost" className="text-white hover:bg-white/10">Ignorieren</Button>
                        </div>
                      </CardContent>
                    </Card>
                  </CardContent>
                </Card>

                <div className="space-y-4">
                  <AgentProcessPanel domain="workflow" className="max-w-none" />

                  <Card className="border-white/10 bg-slate-950/45 text-slate-100">
                    <CardHeader>
                      <CardTitle className="text-lg">Flow KPIs</CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-3">
                      {[
                        ['Durchlaufzeit', '4,1 Tage'],
                        ['On-Time Delivery', '92%'],
                        ['Open Approvals', '3'],
                        ['Risk Score', '68/100'],
                      ].map(([label, value]) => (
                        <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</div>
                          <div className="mt-2 text-xl font-bold text-white">{value}</div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </div>
            </main>

            <aside className="border-l border-white/5 bg-slate-950/40 p-5">
              <Tabs defaultValue="agent" className="flex h-full flex-col">
                <TabsList className="grid w-full grid-cols-4 bg-white/5">
                  <TabsTrigger value="agent">Agent</TabsTrigger>
                  <TabsTrigger value="actions">Aktionen</TabsTrigger>
                  <TabsTrigger value="docs">Docs</TabsTrigger>
                  <TabsTrigger value="kpis">KPIs</TabsTrigger>
                </TabsList>

                <TabsContent value="agent" className="mt-4 flex-1 space-y-4">
                  <Card className="border-amber-400/20 bg-amber-500/10 text-amber-50">
                    <CardHeader>
                      <CardTitle className="text-base">Risiko erkannt</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                      <p>Lieferverzug wahrscheinlich (78%).</p>
                      <div className="space-y-1 text-xs text-amber-50/80">
                        <div>- Lieferant A verspaetet</div>
                        <div>- Lagerbestand kritisch</div>
                      </div>
                      <Button className="w-full bg-white text-slate-900 hover:bg-white/90">Alternativlieferant aktivieren</Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="actions" className="mt-4 space-y-3">
                  <Button className="w-full justify-between bg-indigo-500 text-white hover:bg-indigo-400">
                    Lieferung starten <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Freigabe senden <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Rechnung erzeugen <ChevronRight className="h-4 w-4" />
                  </Button>
                </TabsContent>

                <TabsContent value="docs" className="mt-4 space-y-3">
                  {['Auftrag.pdf', 'Lieferschein.pdf', 'Rechnung.xml'].map((doc) => (
                    <div key={doc} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-200">
                      <span className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> {doc}</span>
                      <MoreHorizontal className="h-4 w-4 text-slate-500" />
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="kpis" className="mt-4 space-y-3">
                  {[
                    ['Marge', '14,8%'],
                    ['SLA', '81%'],
                    ['Cycle Time', '3,2 Tage'],
                    ['Cash Forecast', 'EUR 41.700'],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                      <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</div>
                      <div className="mt-2 text-lg font-semibold text-white">{value}</div>
                    </div>
                  ))}
                </TabsContent>
              </Tabs>
            </aside>
          </div>
        </PageSection>

        <div className="grid gap-4 lg:grid-cols-3">
          <Card className="border-white/10 bg-slate-950/45 text-slate-100">
            <CardHeader>
              <CardTitle className="text-base">Operative Heatmap</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-5 gap-2">
                {[35, 52, 64, 78, 93].map((v, idx) => (
                  <div
                    key={idx}
                    className="h-20 rounded-2xl bg-gradient-to-t from-indigo-500/15 to-indigo-400/45"
                    style={{ opacity: Math.min(1, v / 100) }}
                  />
                ))}
              </div>
              <p className="text-sm text-slate-400">Fake-3D Heatmap als Ausgangspunkt fuer spaetere React-Three-Fiber-Ansicht.</p>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/45 text-slate-100">
            <CardHeader>
              <CardTitle className="text-base">Agent Events</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-slate-300">
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>Delay Prediction aktualisiert</span>
                <Clock3 className="h-4 w-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>Skonto-Potenzial erkannt</span>
                <Clock3 className="h-4 w-4 text-slate-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/45 text-slate-100">
            <CardHeader>
              <CardTitle className="text-base">Naechste Schritte</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-between bg-emerald-500 text-slate-950 hover:bg-emerald-400">
                Figma-fertige Variante ableiten <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                Live-Daten anbinden <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                R3F-Spine ausbauen <ChevronRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageSurface>
  )
}
