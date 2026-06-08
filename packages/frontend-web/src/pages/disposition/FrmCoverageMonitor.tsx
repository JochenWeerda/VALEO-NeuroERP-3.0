import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { Download, RefreshCw, ClipboardList } from 'lucide-react'
import { getCoverageMonitor, requestOverride, type CoverageItem } from '@/lib/api/positions'

function getDefaultPeriodFrom(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

function getDefaultPeriodTo(): string {
  const d = new Date()
  d.setMonth(d.getMonth() + 5)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

function cellBgClass(severity: string): string {
  if (severity === 'RED') return 'bg-red-100 dark:bg-red-900/30'
  if (severity === 'YELLOW') return 'bg-yellow-100 dark:bg-yellow-900/30'
  return ''
}

export default function FrmCoverageMonitor(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [branchId, setBranchId] = useState<string | undefined>(undefined)
  const [asOfDate, setAsOfDate] = useState<string>(() => new Date().toISOString().slice(0, 10))
  const [periodFrom, setPeriodFrom] = useState(getDefaultPeriodFrom)
  const [periodTo, setPeriodTo] = useState(getDefaultPeriodTo)
  const [severityFilter, setSeverityFilter] = useState<string>('RED,YELLOW')
  const [withoutOverrideOnly, setWithoutOverrideOnly] = useState(false)
  const [skip, setSkip] = useState(0)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [massActionLoading, setMassActionLoading] = useState(false)
  const limit = 50

  const params = useMemo(
    () => ({
      branch_id: branchId,
      as_of_date: asOfDate,
      period_mode: 'M',
      period_from: periodFrom,
      period_to: periodTo,
      severity_filter: severityFilter || undefined,
      without_override_only: withoutOverrideOnly,
      skip,
      limit,
    }),
    [branchId, asOfDate, periodFrom, periodTo, severityFilter, withoutOverrideOnly, skip],
  )

  const { data: coverageRes, isLoading, refetch } = useQuery({
    queryKey: ['positions', 'coverage-monitor', params],
    queryFn: () => getCoverageMonitor(params),
  })
  const data = coverageRes

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetch() },
    onCancel: () => navigate('/disposition'),
  })
  useKeyboardShortcuts(shortcuts)

  const handleExport = () => {
    if (!data?.items?.length) return
    const headers = ['Artikel', 'Periode', 'EK offen', 'VK offen', 'Netto', 'Toleranz', 'Schweregrad', 'Override-Status']
    const rows = data.items.map((i: CoverageItem) => [
      i.article_id,
      i.period_key,
      i.qty_buy_open,
      i.qty_sell_open,
      i.qty_net,
      i.qty_tolerance ?? '',
      i.severity,
      i.override_status ?? '',
    ])
    const csv = [`\ufeff${  headers.join(';')}`, ...rows.map((r: (string | number)[]) => r.join(';'))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `coverage-monitor-${asOfDate}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const itemKey = (i: CoverageItem) => `${i.article_id}|${i.period_key}`

  const toggleSelect = (i: CoverageItem) => {
    const key = itemKey(i)
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  const selectAll = () => {
    if (!data?.items?.length) return
    if (selected.size >= data.items.length) setSelected(new Set())
    else setSelected(new Set(data.items.map((i: CoverageItem) => itemKey(i))))
  }

  const handleMassFreigabe = async () => {
    const toRequest = data?.items?.filter((i: CoverageItem) => selected.has(itemKey(i))) ?? []
    if (!toRequest.length) return
    setMassActionLoading(true)
    try {
      for (const i of toRequest) {
        await requestOverride({
          branch_id: branchId ?? undefined,
          article_id: i.article_id,
          period_key: i.period_key,
          reason: `Massen-Freigabe: ${i.article_id} / ${i.period_key}`,
        })
      }
      setSelected(new Set())
      await queryClient.invalidateQueries({ queryKey: ['positions', 'coverage-monitor'] })
    } finally {
      setMassActionLoading(false)
    }
  }

  const handleMassAufgabe = () => {
    if (selected.size === 0) return
    const items = data?.items?.filter((i: CoverageItem) => selected.has(itemKey(i))) ?? []
    const itemsParam = items.map((i: CoverageItem) => `${i.article_id}|${i.period_key}`).join(',')
    navigate(`/workflows/trigger?source=position-coverage&count=${selected.size}&items=${encodeURIComponent(itemsParam)}`)
  }

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Coverage Monitor (kritische Lücken)</h1>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Aktualisieren
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 md:grid-cols-6">
          <div>
            <Label>Stichtag</Label>
            <Input type="date" value={asOfDate} onChange={(e) => setAsOfDate(e.target.value)} />
          </div>
          <div>
            <Label>Periode von</Label>
            <Input value={periodFrom} onChange={(e) => setPeriodFrom(e.target.value)} />
          </div>
          <div>
            <Label>Periode bis</Label>
            <Input value={periodTo} onChange={(e) => setPeriodTo(e.target.value)} />
          </div>
          <div>
            <Label>Schweregrad</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="RED">Nur Rot</option>
              <option value="RED,YELLOW">Rot + Gelb</option>
              <option value="YELLOW">Nur Gelb</option>
            </select>
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={withoutOverrideOnly}
                onChange={(e) => setWithoutOverrideOnly(e.target.checked)}
                className="rounded border-input"
              />
              <span className="text-sm">Nur ohne Override</span>
            </label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-base">Kritische Positionen</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={selected.size === 0 || massActionLoading}
              onClick={handleMassFreigabe}
            >
              Freigabe anfordern ({selected.size})
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={selected.size === 0}
              onClick={handleMassAufgabe}
            >
              <ClipboardList className="mr-2 h-4 w-4" />
              Aufgabe erstellen
            </Button>
            <Button variant="outline" size="sm" onClick={handleExport} disabled={!data?.items?.length}>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Lade…</p>}
          {data && (
            <>
              <p className="text-sm text-muted-foreground mb-2">
                Gesamt: {data.total} Einträge
                {selected.size > 0 && ` · ${selected.size} ausgewählt`}
              </p>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">
                      <input
                        type="checkbox"
                        checked={data.items.length > 0 && selected.size >= data.items.length}
                        onChange={selectAll}
                        className="rounded border-input"
                      />
                    </TableHead>
                    <TableHead>Artikel</TableHead>
                    <TableHead>Periode</TableHead>
                    <TableHead className="text-right">EK offen</TableHead>
                    <TableHead className="text-right">VK offen</TableHead>
                    <TableHead className="text-right">Netto</TableHead>
                    <TableHead className="text-right">Toleranz</TableHead>
                    <TableHead>Schweregrad</TableHead>
                    <TableHead>Verantwortlicher</TableHead>
                    <TableHead>Override-Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((item, idx) => (
                    <TableRow
                      key={`${item.article_id}-${item.period_key}-${idx}`}
                      className={selected.has(itemKey(item)) ? 'bg-muted/50' : ''}
                    >
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selected.has(itemKey(item))}
                          onChange={() => toggleSelect(item)}
                          className="rounded border-input"
                        />
                      </TableCell>
                      <TableCell>{item.article_id}</TableCell>
                      <TableCell>{item.period_key}</TableCell>
                      <TableCell className="text-right">{item.qty_buy_open.toLocaleString('de-DE')}</TableCell>
                      <TableCell className="text-right">{item.qty_sell_open.toLocaleString('de-DE')}</TableCell>
                      <TableCell className="text-right">{item.qty_net.toLocaleString('de-DE')}</TableCell>
                      <TableCell className="text-right">
                        {item.qty_tolerance != null ? item.qty_tolerance.toLocaleString('de-DE') : '-'}
                      </TableCell>
                      <TableCell>
                        <span className={`${cellBgClass(item.severity)  } px-2 py-0.5 rounded`}>
                          {item.severity}
                        </span>
                      </TableCell>
                      <TableCell>{item.responsible ?? '-'}</TableCell>
                      <TableCell>{item.override_status ?? '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex gap-2 mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={skip === 0}
                  onClick={() => setSkip((s) => Math.max(0, s - limit))}
                >
                  Zurück
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={skip + limit >= data.total}
                  onClick={() => setSkip((s) => s + limit)}
                >
                  Weiter
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
