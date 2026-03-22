/**
 * Process Mining Analytics — Gap 018
 * Top-Prozesse, Bottlenecks, SLA-Drilldown
 */

import { useState, useRef } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import { AlertTriangle, BarChart3, CheckCircle, Clock, TrendingUp, XCircle } from 'lucide-react'
import {
  useProcessMiningTopProcesses,
  useProcessMiningBottlenecks,
  useProcessMiningDrilldown,
  type ProcessSummary,
  type ProcessBottleneck,
} from '@/lib/api/process-mining'

function severityBadge(s: ProcessBottleneck['severity']) {
  return (
    <Badge variant={s === 'hoch' ? 'destructive' : s === 'mittel' ? 'secondary' : 'outline'}>
      {s === 'hoch' ? 'Hoch' : s === 'mittel' ? 'Mittel' : 'Niedrig'}
    </Badge>
  )
}

export default function ProcessMiningAnalyticsPage(): JSX.Element {
  const [selectedProcess, setSelectedProcess] = useState<string | null>(null)
  const searchRef = useRef<HTMLInputElement | null>(null)

  const topQuery = useProcessMiningTopProcesses(10)
  const bottleneckQuery = useProcessMiningBottlenecks()
  const drilldownQuery = useProcessMiningDrilldown(selectedProcess ?? '')

  const processes = topQuery.data ?? []
  const bottlenecks = bottleneckQuery.data ?? []

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => {
      void topQuery.refetch()
      void bottleneckQuery.refetch()
    },
    onSearch: () => searchRef.current?.focus(),
  })
  useKeyboardShortcuts(shortcuts)

  const processColumns = [
    {
      key: 'process_name' as const,
      label: 'Prozess',
      render: (p: ProcessSummary) => (
        <button
          onClick={() => setSelectedProcess(p.projection_key)}
          className="font-medium text-blue-600 hover:underline text-left"
        >
          {p.process_name}
        </button>
      ),
    },
    {
      key: 'total_executions' as const,
      label: 'Ausführungen',
      render: (p: ProcessSummary) => <span className="font-mono">{p.total_executions.toLocaleString('de-DE')}</span>,
    },
    {
      key: 'avg_duration_sec' as const,
      label: 'Ø Dauer',
      render: (p: ProcessSummary) => (
        <span className="font-mono">{p.avg_duration_sec.toFixed(1)}s</span>
      ),
    },
    {
      key: 'p95_duration_sec' as const,
      label: 'P95 Dauer',
      render: (p: ProcessSummary) => (
        <span className={`font-mono ${p.p95_duration_sec > p.avg_duration_sec * 3 ? 'text-red-600 font-semibold' : ''}`}>
          {p.p95_duration_sec.toFixed(1)}s
        </span>
      ),
    },
    {
      key: 'error_rate_pct' as const,
      label: 'Fehlerrate',
      render: (p: ProcessSummary) => (
        <div className="flex items-center gap-1">
          {p.error_rate_pct > 5 ? <XCircle className="h-4 w-4 text-red-500" /> : <CheckCircle className="h-4 w-4 text-green-500" />}
          <span className={p.error_rate_pct > 5 ? 'text-red-600 font-semibold' : ''}>{p.error_rate_pct.toFixed(1)}%</span>
        </div>
      ),
    },
    {
      key: 'last_seen' as const,
      label: 'Zuletzt',
      render: (p: ProcessSummary) => new Date(p.last_seen).toLocaleDateString('de-DE'),
    },
  ]

  const bottleneckColumns = [
    {
      key: 'process_name' as const,
      label: 'Prozess',
      render: (b: ProcessBottleneck) => <span className="font-medium">{b.process_name}</span>,
    },
    {
      key: 'bottleneck_type' as const,
      label: 'Typ',
      render: (b: ProcessBottleneck) => (
        <Badge variant="outline">
          {b.bottleneck_type === 'duration' ? 'Laufzeit' : b.bottleneck_type === 'error_rate' ? 'Fehlerrate' : 'Warteschlange'}
        </Badge>
      ),
    },
    { key: 'severity' as const, label: 'Schwere', render: (b: ProcessBottleneck) => severityBadge(b.severity) },
    {
      key: 'current_value' as const,
      label: 'Aktuell / Schwelle',
      render: (b: ProcessBottleneck) => (
        <span className="font-mono text-sm text-red-600">
          {b.current_value.toFixed(1)} / {b.threshold_value.toFixed(1)}
        </span>
      ),
    },
    {
      key: 'affected_executions' as const,
      label: 'Betroffene Ausf.',
      render: (b: ProcessBottleneck) => <span className="font-mono">{b.affected_executions}</span>,
    },
    { key: 'recommendation' as const, label: 'Empfehlung' },
  ]

  const hochBottlenecks = bottlenecks.filter((b) => b.severity === 'hoch').length
  const drilldown = drilldownQuery.data

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Prozess-Analyse</h1>
        <p className="text-muted-foreground">Process Mining — Top-Prozesse, Bottlenecks & SLA-Drilldown</p>
      </div>

      <AgentProcessPanel domain="workflow" />

      {hochBottlenecks > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{hochBottlenecks} kritische(r) Engpass/Engpässe — sofortiger Handlungsbedarf!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Prozesse gesamt</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{processes.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Ausführungen gesamt</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{processes.reduce((s, p) => s + p.total_executions, 0).toLocaleString('de-DE')}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Engpässe</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{bottlenecks.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kritische Engpässe</CardTitle></CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{hochBottlenecks}</span>
          </CardContent>
        </Card>
      </div>

      {/* Drilldown-Panel */}
      {selectedProcess && drilldown && (
        <Card className="border-blue-300 bg-blue-50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{drilldown.process_name} — Drilldown</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setSelectedProcess(null)}>✕ Schließen</Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-6 text-sm">
              <div>
                <span className="text-muted-foreground">SLA-Ziel: </span>
                <span className="font-mono font-semibold">{drilldown.sla_target_sec}s</span>
              </div>
              <div>
                <span className="text-muted-foreground">SLA-Einhaltung: </span>
                <span className={`font-mono font-semibold ${drilldown.sla_compliance_pct < 95 ? 'text-red-600' : 'text-green-600'}`}>
                  {drilldown.sla_compliance_pct.toFixed(1)}%
                </span>
              </div>
            </div>
            <div className="space-y-1">
              {drilldown.steps.map((step) => (
                <div key={step.step_name} className={`flex items-center justify-between rounded p-2 text-sm ${step.is_bottleneck ? 'bg-red-100 border border-red-300' : 'bg-white border'}`}>
                  <div className="flex items-center gap-2">
                    {step.is_bottleneck && <AlertTriangle className="h-4 w-4 text-red-600" />}
                    <span className={step.is_bottleneck ? 'font-semibold text-red-800' : ''}>{step.step_name}</span>
                  </div>
                  <div className="flex gap-4 text-muted-foreground font-mono text-xs">
                    <span>{step.avg_duration_sec.toFixed(1)}s</span>
                    {step.error_count > 0 && <span className="text-red-600">{step.error_count} Fehler</span>}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Top-Prozesse</CardTitle></CardHeader>
        <CardContent>
          <DataTable data={processes} columns={processColumns} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Engpässe</CardTitle></CardHeader>
        <CardContent>
          <DataTable data={bottlenecks} columns={bottleneckColumns} />
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
