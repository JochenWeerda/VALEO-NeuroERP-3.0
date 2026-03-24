import { useMemo, useState } from 'react'
import {
  Bell,
  BookOpen,
  ChevronRight,
  Clock3,
  FileText,
  MoreHorizontal,
  Package,
  Receipt,
  Search,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
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
    id: 'requisition',
    label: 'Bedarf',
    status: 'ok',
    value: '3 Positionen',
    timestamp: '07:42',
    kpi: 'Bedarf genehmigt',
    insight: 'Anforderung vollstaendig mit Budgetbezug und Warengruppe.',
  },
  {
    id: 'approval',
    label: 'Freigabe',
    status: 'ok',
    value: '2 Stufen',
    timestamp: '07:49',
    kpi: '0 Eskalationen',
    insight: 'Freigabekette innerhalb der Policy abgeschlossen.',
  },
  {
    id: 'purchase-order',
    label: 'Bestellung',
    status: 'active',
    value: 'PO-2026-188',
    timestamp: 'Heute',
    kpi: 'Spend EUR 18.420',
    insight: 'Bestellung laeuft, Liefertermin und Incoterm werden aktiv ueberwacht.',
  },
  {
    id: 'goods-receipt',
    label: 'Wareneingang',
    status: 'warning',
    value: 'ETA +2 Tage',
    timestamp: 'Morgen',
    kpi: 'OTD 89%',
    insight: 'Lieferfenster kippt, Expressoption und Zweitquelle verfuegbar.',
  },
  {
    id: 'invoice',
    label: 'Rechnung',
    status: 'warning',
    value: '2-way Match',
    timestamp: 'T+1',
    kpi: '1 Abweichung',
    insight: 'Preisabweichung von 1,8% erwartet, Vorpruefung empfohlen.',
  },
  {
    id: 'payment',
    label: 'Zahlung',
    status: 'critical',
    value: 'Skonto offen',
    timestamp: 'T+10',
    kpi: 'Cash Impact EUR 370',
    insight: 'Skontofenster gefaehrdet, wenn Wareneingang weiter rutscht.',
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

export default function FlowSpineProcureToPayPage(): JSX.Element {
  const [selectedNodeId, setSelectedNodeId] = useState<string>('purchase-order')
  const selectedNode = useMemo(
    () => flowNodes.find((node) => node.id === selectedNodeId) ?? flowNodes[0],
    [selectedNodeId],
  )

  return (
    <PageSurface data-page-surface="flow-spine-procure-to-pay" className="bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.12),_transparent_30%),linear-gradient(180deg,#071120,#0b1326)]">
      <div className="flex min-h-full flex-col gap-6">
        <PageSection className="border-white/10 bg-slate-950/60 p-0 shadow-2xl shadow-indigo-950/20">
          <header className="flex h-16 items-center justify-between border-b border-white/5 px-5">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-200">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-semibold tracking-wide text-slate-100">Flow Spine UI</div>
                <div className="text-xs text-slate-400">Procure-to-Pay / Bestellung PO-2026-188</div>
              </div>
            </div>

            <div className="flex flex-1 items-center justify-center px-4">
              <div className="relative w-full max-w-xl">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <Input
                  aria-label="Globale Suche"
                  placeholder="Bestellung 2026-188, Lieferant TechLogistics oder Wareneingang suchen ..."
                  className="border-white/10 bg-white/5 pl-9 text-slate-100 placeholder:text-slate-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Badge variant="outline" className="border-indigo-400/30 bg-indigo-400/10 text-indigo-100">
                Fokus
              </Badge>
              <Button variant="ghost" size="icon" className="text-slate-300 hover:bg-white/5 hover:text-white">
                <Bell className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="text-slate-300 hover:bg-white/5 hover:text-white">
                <Settings className="h-4 w-4" />
              </Button>
              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-100">
                <UserCircle2 className="h-5 w-5 text-slate-300" />
                <span>Procurement Lead</span>
              </div>
            </div>
          </header>

          <div className="grid min-h-[720px] grid-cols-[240px_minmax(0,1fr)_320px]">
            <aside className="border-r border-white/5 bg-slate-950/40 p-4">
              <div className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Prozesse</p>
                <div className="space-y-2">
                  {[
                    { label: 'Order-to-Cash' },
                    { label: 'Procure-to-Pay', active: true },
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
                  <div className="rounded-2xl bg-white/5 px-3 py-3">PO-2026-188</div>
                  <div className="rounded-2xl bg-white/5 px-3 py-3">Lieferant TechLogistics</div>
                </div>
              </div>

              <div className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Letzte Vorgaenge</p>
                <div className="space-y-2 text-sm text-slate-400">
                  <div className="rounded-2xl border border-white/5 px-3 py-3">Lieferavis aktualisiert</div>
                  <div className="rounded-2xl border border-white/5 px-3 py-3">3-way-Match auffaellig</div>
                </div>
              </div>

              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Rollenwechsel</p>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Einkauf
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Kreditoren
                  </Button>
                </div>
              </div>
            </aside>

            <main className="overflow-hidden bg-[linear-gradient(180deg,rgba(15,23,42,0.45),rgba(15,23,42,0.15))] p-6">
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-white">Flow Spine - Procure-to-Pay</h1>
                  <p className="mt-1 max-w-2xl text-sm text-slate-400">
                    Beschaffungs- und Kreditorenfluss als steuerbarer Prozessraum mit Agentenhinweisen, Match-Pruefung und ETA-Fokus.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className="bg-emerald-500/15 text-emerald-200 hover:bg-emerald-500/15">Budget im Rahmen</Badge>
                  <Badge className="bg-amber-500/15 text-amber-100 hover:bg-amber-500/15">1 Lieferfenster kippt</Badge>
                </div>
              </div>

              <div className="relative rounded-[28px] border border-white/10 bg-white/[0.03] p-8 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
                <div className="pointer-events-none absolute left-12 right-12 top-1/2 h-1 -translate-y-1/2 rounded-full bg-white/5" />
                <div className="pointer-events-none absolute left-12 top-1/2 h-1 w-[52%] -translate-y-1/2 rounded-full bg-gradient-to-r from-emerald-400 via-indigo-400 to-amber-400 opacity-80" />

                <div className="relative grid grid-cols-6 gap-4">
                  {flowNodes.map((node) => {
                    const active = node.id === selectedNodeId
                    const Icon =
                      node.id === 'requisition'
                        ? BookOpen
                        : node.id === 'approval'
                          ? ShieldCheck
                          : node.id === 'purchase-order'
                            ? ShoppingCart
                            : node.id === 'goods-receipt'
                              ? Package
                              : node.id === 'invoice'
                                ? Receipt
                                : Wallet

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
                        <div className="flex items-center justify-between"><span>Spend</span><span>EUR 18.420</span></div>
                        <div className="flex items-center justify-between"><span>Lieferzeit</span><span>6,4 Tage</span></div>
                        <div className="flex items-center justify-between"><span>Match-Quote</span><span>96%</span></div>
                      </CardContent>
                    </Card>

                    <Card className="border-white/10 bg-white/[0.03]">
                      <CardHeader>
                        <CardTitle className="text-sm text-slate-200">Dokumente</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 text-sm text-slate-300">
                        <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> Bestellung PO-2026-188</div>
                        <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> Lieferavis XML</div>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">Upload</Button>
                      </CardContent>
                    </Card>

                    <Card className="border-white/10 bg-white/[0.03]">
                      <CardHeader>
                        <CardTitle className="text-sm text-slate-200">Aktionen</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Button className="w-full bg-indigo-500 text-white hover:bg-indigo-400">Lieferantenanfrage senden</Button>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">Wareneingang vorbereiten</Button>
                        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">3-way-Match pruefen</Button>
                      </CardContent>
                    </Card>

                    <Card className="border-amber-400/20 bg-amber-500/10">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-sm text-amber-50">
                          <Sparkles className="h-4 w-4" />
                          Agent
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 text-sm text-amber-50/90">
                        <p>Lieferverzug wahrscheinlich (72%). Expressversand oder Zweitlieferant empfohlen.</p>
                        <ul className="space-y-1 text-xs text-amber-100/80">
                          <li>- Shanghai-Abgang verspaetet</li>
                          <li>- Kritische Position fuer Servicefenster</li>
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
                      <CardTitle className="text-lg">P2P KPIs</CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-3">
                      {[
                        ['PO Cycle Time', '1,8 Tage'],
                        ['OTD', '89%'],
                        ['Open Matches', '2'],
                        ['Risk Score', '71/100'],
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
                      <CardTitle className="text-base">Beschaffungsrisiko</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                      <p>ETA-Abweichung bedroht Skonto- und Servicefenster.</p>
                      <div className="space-y-1 text-xs text-amber-50/80">
                        <div>- Hafenverzoegerung erkannt</div>
                        <div>- Vertragslieferant nur mit Aufpreis beschleunigbar</div>
                      </div>
                      <Button className="w-full bg-white text-slate-900 hover:bg-white/90">Expressoption anfragen</Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="actions" className="mt-4 space-y-3">
                  <Button className="w-full justify-between bg-indigo-500 text-white hover:bg-indigo-400">
                    Bestellung eskalieren <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Lieferfenster anpassen <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    Rechnungspruefung starten <ChevronRight className="h-4 w-4" />
                  </Button>
                </TabsContent>

                <TabsContent value="docs" className="mt-4 space-y-3">
                  {['Bestellung.pdf', 'SLA_TechLogistics.docx', 'Lieferavis.xml'].map((doc) => (
                    <div key={doc} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-200">
                      <span className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> {doc}</span>
                      <MoreHorizontal className="h-4 w-4 text-slate-500" />
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="kpis" className="mt-4 space-y-3">
                  {[
                    ['Liefertermintreue', '89%'],
                    ['Skonto', '2% offen'],
                    ['Cycle Time', '6,4 Tage'],
                    ['Spend Forecast', 'EUR 18.950'],
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
              <CardTitle className="text-base">Lieferanten-Heatmap</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-5 gap-2">
                {[44, 58, 63, 75, 91].map((v, idx) => (
                  <div
                    key={idx}
                    className="h-20 rounded-2xl bg-gradient-to-t from-indigo-500/15 to-indigo-400/45"
                    style={{ opacity: Math.min(1, v / 100) }}
                  />
                ))}
              </div>
              <p className="text-sm text-slate-400">Lieferanten- und ETA-Risiko je Warenstrom als Ausgangspunkt fuer spaetere 3D-Ansicht.</p>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/45 text-slate-100">
            <CardHeader>
              <CardTitle className="text-base">Agent Events</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-slate-300">
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>ETA-Warnung aktualisiert</span>
                <Clock3 className="h-4 w-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
                <span>Preisabweichung vorab erkannt</span>
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
                Lieferantensteuerung verfeinern <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                Match Engine anbinden <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full justify-between border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                Dispatch auf ETA-Events schalten <ChevronRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageSurface>
  )
}
