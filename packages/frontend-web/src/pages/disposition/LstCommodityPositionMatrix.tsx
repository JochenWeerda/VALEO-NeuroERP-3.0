import { useState, useMemo, useCallback, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from '@/app/routing/react-router-compat'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { RefreshCw, Settings, Download, AlertTriangle } from 'lucide-react'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import {
  getMatrix,
  getKpi,
  refreshSnapshot,
  getCoverageMonitor,
  getCellDrilldown,
  type MatrixParams,
  type MatrixResponse,
  type KpiResponse,
  type ArticleRow,
  type PeriodCell,
} from '@/lib/api/positions'
import { DlgPositionDetails } from './DlgPositionDetails'

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
  return 'bg-green-50 dark:bg-green-900/20'
}

export default function LstCommodityPositionMatrix(): JSX.Element {
  const navigate = useNavigate()
  const [branchId, setBranchId] = useState<string | undefined>(undefined)
  const [asOfDate, setAsOfDate] = useState<string>(() => new Date().toISOString().slice(0, 10))
  const [periodMode, setPeriodMode] = useState<string>('M')
  const [periodFrom, setPeriodFrom] = useState(getDefaultPeriodFrom)
  const [periodTo, setPeriodTo] = useState(getDefaultPeriodTo)
  const [articleIds, setArticleIds] = useState<string>('')
  const [viewMode, setViewMode] = useState<NonNullable<MatrixParams['view_mode']>>('physisch')
  const [drilldown, setDrilldown] = useState<{ articleId: string; periodKey: string } | null>(null)
  const [contextCell, setContextCell] = useState<{ articleId: string; periodKey: string; x: number; y: number } | null>(null)
  const articleFilterRef = useRef<HTMLInputElement | null>(null)

  const matrixParams = useMemo(
    (): MatrixParams => ({
      branch_id: branchId || undefined,
      as_of_date: asOfDate,
      period_mode: periodMode,
      period_from: periodFrom,
      period_to: periodTo,
      article_ids: articleIds.trim() || undefined,
      use_cache: false,
      view_mode: viewMode,
    }),
    [branchId, asOfDate, periodMode, periodFrom, periodTo, articleIds, viewMode],
  )

  const matrixQuery = useQuery({
    queryKey: ['positions', 'matrix', matrixParams],
    queryFn: () => getMatrix(matrixParams),
  })

  const kpiQuery = useQuery({
    queryKey: ['positions', 'kpi', { ...matrixParams, use_cache: undefined }],
    queryFn: () =>
      getKpi({
        branch_id: matrixParams.branch_id,
        as_of_date: matrixParams.as_of_date,
        period_mode: matrixParams.period_mode,
        period_from: matrixParams.period_from,
        period_to: matrixParams.period_to,
        article_ids: matrixParams.article_ids,
        view_mode: matrixParams.view_mode,
      }),
  })

  const coverageParams = useMemo(
    () => ({
      branch_id: matrixParams.branch_id,
      as_of_date: matrixParams.as_of_date,
      period_mode: matrixParams.period_mode,
      period_from: matrixParams.period_from,
      period_to: matrixParams.period_to,
      severity_filter: 'RED,YELLOW',
      view_mode: matrixParams.view_mode,
      skip: 0,
      limit: 100,
    }),
    [matrixParams],
  )

  const coverageQuery = useQuery({
    queryKey: ['positions', 'coverage', coverageParams],
    queryFn: () => getCoverageMonitor(coverageParams),
  })

  const matrix = matrixQuery.data
  const kpi = kpiQuery.data
  const coverage = coverageQuery.data

  const handleExportMatrix = useCallback(() => {
    if (!matrix) return
    const headers = ['Artikel-Nr.', 'Bezeichnung', 'Einheit', 'Summe EK offen', 'Summe VK offen', 'Summe Netto', ...matrix.period_keys]
    const rows = matrix.rows.map((row: ArticleRow) => [
      row.article_id,
      row.article_name,
      row.unit,
      row.sum_buy_open,
      row.sum_sell_open,
      row.sum_net,
      ...row.cells.map((c: PeriodCell) => c.qty_net),
    ])
    const csv = [headers.join(';'), ...rows.map((r: (string | number)[]) => r.join(';'))].join('\n')
    const blob = new Blob([`\ufeff${  csv}`], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `position-matrix-${asOfDate}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }, [matrix, asOfDate])

  useEffect(() => {
    const close = () => setContextCell(null)
    document.addEventListener('click', close)
    return () => document.removeEventListener('click', close)
  }, [])

  const handleContextMenu = useCallback(
    (e: React.MouseEvent, articleId: string, periodKey: string) => {
      e.preventDefault()
      setContextCell({ articleId, periodKey, x: e.clientX, y: e.clientY })
    },
    [],
  )

  const handleFreigabeFromContext = useCallback(() => {
    if (!contextCell) return
    setDrilldown({ articleId: contextCell.articleId, periodKey: contextCell.periodKey })
    setContextCell(null)
  }, [contextCell])

  const handleCreateTaskFromContext = useCallback(() => {
    if (!contextCell) return
    navigate(
      `/workflows/supervisor?source=position-matrix&articleId=${encodeURIComponent(contextCell.articleId)}&periodKey=${encodeURIComponent(contextCell.periodKey)}`,
    )
    setContextCell(null)
  }, [contextCell, navigate])

  const handleExportDetail = useCallback(async () => {
    if (!contextCell) return
    try {
      const drill = await getCellDrilldown(contextCell.articleId, contextCell.periodKey, {
        branch_id: branchId ?? undefined,
        as_of_date: asOfDate,
        period_mode: periodMode,
        view_mode: viewMode,
      })
      const rows: string[][] = [
        ['Artikel', drill.article_id],
        ['Periode', drill.period_key],
        ['EK offen', String(drill.qty_buy_open)],
        ['VK offen', String(drill.qty_sell_open)],
        ['Netto', String(drill.qty_net)],
        ['Status', drill.severity],
        [],
        ['Kontrakt', 'Typ', 'Menge Rest', 'Anteil %'],
        ...drill.top_causers.map((t) => [t.contract_no, t.contract_type, String(t.qty_rest), String(t.share_pct ?? '')]),
      ]
      const csv = rows.map((r) => r.join(';')).join('\n')
      const blob = new Blob([`\ufeff${  csv}`], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `position-detail-${drill.article_id}-${drill.period_key}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setContextCell(null)
    }
  }, [contextCell, branchId, asOfDate, periodMode, viewMode])

  const handleRefresh = async () => {
    await refreshSnapshot({
      branch_id: matrixParams.branch_id,
      as_of_date: matrixParams.as_of_date,
      period_mode: matrixParams.period_mode,
      period_from: matrixParams.period_from,
      period_to: matrixParams.period_to,
      article_ids: matrixParams.article_ids,
      view_mode: matrixParams.view_mode,
    })
    matrixQuery.refetch()
    kpiQuery.refetch()
  }

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void handleRefresh() },
    onSearch: () => articleFilterRef.current?.focus(),
  })
  useKeyboardShortcuts(shortcuts)

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Commodity Position Matrix</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportMatrix} disabled={!matrix?.rows?.length}>
            <Download className="mr-1 h-4 w-4" />
            Export
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to="/disposition/regeln">
              <Settings className="mr-1 h-4 w-4" />
              Regeln
            </Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to="/disposition/coverage-monitor">
              <AlertTriangle className="mr-1 h-4 w-4" />
              Coverage Monitor
            </Link>
          </Button>
        </div>
      </div>

      <AgentProcessPanel domain="einkauf" />

      {/* Filter */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Kontext</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 md:grid-cols-6">
          <div>
            <Label>Niederlassung</Label>
            <Input
              value={branchId ?? ''}
              onChange={(e) => setBranchId(e.target.value || undefined)}
              placeholder="optional (z.B. NL-1)"
            />
          </div>
          <div>
            <Label>Stichtag</Label>
            <Input
              type="date"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
            />
          </div>
          <div>
            <Label>Betrachtung</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as NonNullable<MatrixParams['view_mode']>)}
            >
              <option value="physisch">Physisch</option>
              <option value="physisch_disponiert">Physisch + disponiert</option>
              <option value="inkl_archiv">inkl. Archiv</option>
            </select>
          </div>
          <div>
            <Label>Periodenmodus</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={periodMode}
              onChange={(e) => setPeriodMode(e.target.value)}
            >
              <option value="W">Woche</option>
              <option value="M">Monat</option>
              <option value="Q">Quartal</option>
            </select>
          </div>
          <div>
            <Label>Periode von</Label>
            <Input
              value={periodFrom}
              onChange={(e) => setPeriodFrom(e.target.value)}
              placeholder="YYYY-MM"
            />
          </div>
          <div>
            <Label>Periode bis</Label>
            <Input
              value={periodTo}
              onChange={(e) => setPeriodTo(e.target.value)}
              placeholder="YYYY-MM"
            />
          </div>
          <div className="md:col-span-2">
            <Label>Artikel (kommagetrennt)</Label>
            <Input
              ref={articleFilterRef}
              value={articleIds}
              onChange={(e) => setArticleIds(e.target.value)}
              placeholder="optional (z.B. Raps, Sojaschrot)"
            />
          </div>
        </CardContent>
      </Card>

      {/* KPI */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Short-Zellen</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{kpi?.short_cell_count ?? '-'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Größte Lücke (t)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{kpi?.max_short_qty ?? '-'}</p>
            {kpi?.max_short_article_id && (
              <p className="text-xs text-muted-foreground">
                {kpi.max_short_article_id} / {kpi.max_short_period_key}
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aus Deckung</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{kpi?.expiring_coverage_count ?? '-'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Button onClick={() => handleRefresh()} disabled={matrixQuery.isFetching}>
              <RefreshCw className={`mr-2 h-4 w-4 ${matrixQuery.isFetching ? 'animate-spin' : ''}`} />
              Neu berechnen
            </Button>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="matrix">
        <TabsList>
          <TabsTrigger value="matrix">Periodenmatrix</TabsTrigger>
          <TabsTrigger value="coverage">Coverage Monitor</TabsTrigger>
        </TabsList>
        <TabsContent value="matrix" className="mt-4">
          {matrixQuery.isLoading && <p className="text-muted-foreground">Lade Matrix…</p>}
          {matrixQuery.error && (
            <p className="text-destructive">Fehler: {String(matrixQuery.error)}</p>
          )}
          {matrix && (
            <TooltipProvider>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Artikel-Nr.</TableHead>
                      <TableHead>Bezeichnung</TableHead>
                      <TableHead>Einheit</TableHead>
                      <TableHead className="text-right">Summe EK offen</TableHead>
                      <TableHead className="text-right">Summe VK offen</TableHead>
                      <TableHead className="text-right">Summe Netto</TableHead>
                      {matrix.period_keys.map((pk) => (
                        <TableHead key={pk} className="text-right min-w-[80px]">
                          {pk}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {matrix.rows.map((row: ArticleRow) => (
                      <TableRow key={row.article_id}>
                        <TableCell className="font-medium">{row.article_id}</TableCell>
                        <TableCell>{row.article_name}</TableCell>
                        <TableCell>{row.unit}</TableCell>
                        <TableCell className="text-right">{row.sum_buy_open.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{row.sum_sell_open.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{row.sum_net.toLocaleString('de-DE')}</TableCell>
                        {row.cells.map((cell: PeriodCell) => (
                          <TableCell
                            key={cell.period_key}
                            className={`text-right cursor-pointer ${cellBgClass(cell.severity)}`}
                            onClick={() =>
                              setDrilldown({ articleId: row.article_id, periodKey: cell.period_key })
                            }
                            onContextMenu={(e) => handleContextMenu(e, row.article_id, cell.period_key)}
                          >
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <span>
                                  {cell.qty_net.toLocaleString('de-DE')}
                                </span>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Einkauf offen: {cell.qty_buy_open.toLocaleString('de-DE')} t</p>
                                <p>Verkauf offen: {cell.qty_sell_open.toLocaleString('de-DE')} t</p>
                                <p>Netto: {cell.qty_net.toLocaleString('de-DE')} t</p>
                                <p>Toleranz: {cell.qty_tolerance != null ? cell.qty_tolerance.toLocaleString('de-DE') : '-'}</p>
                                <p>Status: {cell.severity}</p>
                              </TooltipContent>
                            </Tooltip>
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TooltipProvider>
          )}
        </TabsContent>
        <TabsContent value="coverage" className="mt-4">
          {coverageQuery.isLoading && <p className="text-muted-foreground">Lade…</p>}
          {coverage && (
            <div className="overflow-x-auto rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Artikel</TableHead>
                    <TableHead>Periode</TableHead>
                    <TableHead className="text-right">EK offen</TableHead>
                    <TableHead className="text-right">VK offen</TableHead>
                    <TableHead className="text-right">Netto</TableHead>
                    <TableHead>Schweregrad</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {coverage.items.map((item, idx) => (
                    <TableRow key={`${item.article_id}-${item.period_key}-${idx}`}>
                      <TableCell>{item.article_id}</TableCell>
                      <TableCell>{item.period_key}</TableCell>
                      <TableCell className="text-right">{item.qty_buy_open.toLocaleString('de-DE')}</TableCell>
                      <TableCell className="text-right">{item.qty_sell_open.toLocaleString('de-DE')}</TableCell>
                      <TableCell className="text-right">{item.qty_net.toLocaleString('de-DE')}</TableCell>
                      <TableCell>
                        <span className={`${cellBgClass(item.severity)  } px-2 py-0.5 rounded`}>{item.severity}</span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {contextCell && (
        <div
          className="fixed z-50 min-w-[180px] rounded-md border bg-popover py-1 shadow-md"
          style={{ left: contextCell.x, top: contextCell.y }}
          role="menu"
        >
          <button
            type="button"
            className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
            onClick={(e) => { e.stopPropagation(); handleFreigabeFromContext(); }}
          >
            Freigabe anfordern
          </button>
          <button
            type="button"
            className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
            onClick={(e) => { e.stopPropagation(); handleCreateTaskFromContext(); }}
          >
            Als Aufgabe
          </button>
          <button
            type="button"
            className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
            onClick={(e) => { e.stopPropagation(); void handleExportDetail(); }}
          >
            Export Detail
          </button>
        </div>
      )}

      {drilldown && (
        <DlgPositionDetails
          articleId={drilldown.articleId}
          periodKey={drilldown.periodKey}
          branchId={branchId}
          asOfDate={asOfDate}
          periodMode={periodMode}
          viewMode={viewMode}
          open={true}
          onOpenChange={(open) => !open && setDrilldown(null)}
        />
      )}
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
