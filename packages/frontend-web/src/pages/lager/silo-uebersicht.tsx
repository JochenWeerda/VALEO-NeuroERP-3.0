/**
 * WM-AGRI-MAP-001 — Silo Bird-View: operatives Kapazitäts-Dashboard aller Silozellen.
 * Auto-Refresh alle 30 s. Kein Drag-Editor (→ lager/materialfluss-visualisierung).
 */

import { useMemo, useState } from 'react'

import { useNavigate } from '@/app/routing/typed-router'
import { PageToolbar } from '@/components/navigation/PageToolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { useWarehouses } from '@/lib/api/inventory'
import { agriStr, useAgriSiloCells } from '@/lib/api/agri-material-flow'
import { ArrowLeftRight, LayoutGrid, RefreshCw, Share2 } from 'lucide-react'

// ── Hilfsfunktionen ──────────────────────────────────────────────────────────

function toNum(v: unknown): number {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function fillPct(stock: number, cap: number): number {
  if (cap <= 0) return 0
  return Math.min(100, Math.round((stock / cap) * 100))
}

function qsColor(qs: string): string {
  if (qs === 'gesperrt') return 'bg-red-500'
  if (qs === 'in_pruefung') return 'bg-amber-400'
  return 'bg-emerald-500'
}

function qsLabel(qs: string): string {
  if (qs === 'gesperrt') return 'QS-gesperrt'
  if (qs === 'in_pruefung') return 'In Prüfung'
  return 'Freigegeben'
}

function fillBarColor(pct: number): string {
  if (pct >= 95) return 'bg-red-500'
  if (pct >= 80) return 'bg-amber-400'
  return 'bg-emerald-500'
}

// ── Einzel-Kachel ────────────────────────────────────────────────────────────

interface SiloCellCardProps {
  row: Record<string, unknown>
  onTransfer: (cellId: string, cellCode: string) => void
}

function SiloCellCard({ row, onTransfer }: SiloCellCardProps): JSX.Element {
  const id = agriStr(row, 'id')
  const code = agriStr(row, 'cell_code') || agriStr(row, 'name') || id
  const name = agriStr(row, 'name')
  const qs = agriStr(row, 'qs_status') || 'frei'
  const stock = toNum(row['current_stock_kg'])
  const cap = toNum(row['capacity_kg'])
  const pct = fillPct(stock, cap)
  const mat = agriStr(row, 'current_material_id')
  const lot = agriStr(row, 'current_lot_id')

  return (
    <Card className="flex flex-col gap-0 overflow-hidden min-h-[190px]">
      {/* Farbstreifen QS-Status */}
      <div className={`h-1.5 w-full ${qsColor(qs)}`} />
      <CardHeader className="pb-1 pt-3 px-3">
        <div className="flex items-start justify-between gap-1">
          <div className="min-w-0">
            <CardTitle className="text-sm font-semibold leading-tight truncate">{code}</CardTitle>
            {name && name !== code ? (
              <p className="text-[11px] text-muted-foreground truncate mt-0.5">{name}</p>
            ) : null}
          </div>
          <Badge
            variant="outline"
            className={`text-[10px] shrink-0 px-1.5 py-0 border-0 ${
              qs === 'gesperrt'
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                : qs === 'in_pruefung'
                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                  : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
            }`}
          >
            {qsLabel(qs)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="px-3 pb-3 flex flex-col gap-2 flex-1">
        {/* Füllstand */}
        <div>
          <div className="flex items-baseline justify-between mb-1">
            <span className="text-[11px] text-muted-foreground">Bestand</span>
            <span className="text-xs font-medium tabular-nums">
              {stock > 0 ? `${stock.toLocaleString('de-DE')} kg` : '—'}
              {cap > 0 ? (
                <span className="text-muted-foreground font-normal">
                  {' '}/ {cap.toLocaleString('de-DE')} kg
                </span>
              ) : null}
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${fillBarColor(pct)}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="text-right text-[10px] text-muted-foreground mt-0.5">{pct} %</div>
        </div>

        {/* Material / Lot */}
        {(mat || lot) && (
          <div className="text-[11px] text-muted-foreground space-y-0.5">
            {mat && (
              <div className="flex gap-1">
                <span className="shrink-0 font-medium text-foreground/70">Artikel:</span>
                <span className="truncate">{mat}</span>
              </div>
            )}
            {lot && (
              <div className="flex gap-1">
                <span className="shrink-0 font-medium text-foreground/70">Lot:</span>
                <span className="truncate font-mono">{lot}</span>
              </div>
            )}
          </div>
        )}

        {/* Transfer-Button */}
        <div className="mt-auto pt-1">
          <Button
            variant="outline"
            size="sm"
            className="w-full h-7 text-[11px] gap-1.5"
            disabled={qs === 'gesperrt'}
            onClick={() => onTransfer(id, code)}
          >
            <ArrowLeftRight className="h-3 w-3" />
            Transfer
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Zusammenfassung ───────────────────────────────────────────────────────────

interface SummaryBarProps {
  cells: Record<string, unknown>[]
}

function SummaryBar({ cells }: SummaryBarProps): JSX.Element {
  const totalCap = cells.reduce((s, r) => s + toNum(r['capacity_kg']), 0)
  const totalStock = cells.reduce((s, r) => s + toNum(r['current_stock_kg']), 0)
  const locked = cells.filter((r) => agriStr(r, 'qs_status') === 'gesperrt').length
  const pct = fillPct(totalStock, totalCap)

  return (
    <div className="flex flex-wrap gap-3">
      <div className="flex flex-col rounded-md border border-border bg-card px-4 py-2 min-w-[120px]">
        <span className="text-[11px] text-muted-foreground">Silozellen</span>
        <span className="text-xl font-semibold tabular-nums">{cells.length}</span>
      </div>
      <div className="flex flex-col rounded-md border border-border bg-card px-4 py-2 min-w-[160px]">
        <span className="text-[11px] text-muted-foreground">Gesamtbestand</span>
        <span className="text-xl font-semibold tabular-nums">
          {totalStock > 0 ? `${Math.round(totalStock / 1000).toLocaleString('de-DE')} t` : '—'}
        </span>
      </div>
      <div className="flex flex-col rounded-md border border-border bg-card px-4 py-2 min-w-[160px]">
        <span className="text-[11px] text-muted-foreground">Kapazität gesamt</span>
        <span className="text-xl font-semibold tabular-nums">
          {totalCap > 0 ? `${Math.round(totalCap / 1000).toLocaleString('de-DE')} t` : '—'}
        </span>
      </div>
      <div className="flex flex-col rounded-md border border-border bg-card px-4 py-2 min-w-[120px]">
        <span className="text-[11px] text-muted-foreground">Auslastung</span>
        <span className={`text-xl font-semibold tabular-nums ${pct >= 95 ? 'text-red-600' : pct >= 80 ? 'text-amber-600' : ''}`}>
          {totalCap > 0 ? `${pct} %` : '—'}
        </span>
      </div>
      {locked > 0 && (
        <div className="flex flex-col rounded-md border border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-800 px-4 py-2 min-w-[120px]">
          <span className="text-[11px] text-red-600 dark:text-red-400">QS-gesperrt</span>
          <span className="text-xl font-semibold text-red-600 dark:text-red-400 tabular-nums">{locked}</span>
        </div>
      )}
    </div>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function SiloUebersichtPage(): JSX.Element {
  const navigate = useNavigate()
  const warehousesQ = useWarehouses({ is_active: true })
  const items = warehousesQ.data?.items ?? []
  const [warehouseId, setWarehouseId] = useState('')
  const [qsFilter, setQsFilter] = useState<'alle' | 'frei' | 'in_pruefung' | 'gesperrt'>('alle')

  const cellsQ = useAgriSiloCells(warehouseId || undefined, {
    enabled: Boolean(warehouseId),
  })

  const cells = cellsQ.data ?? []

  const filtered = useMemo(() => {
    if (qsFilter === 'alle') return cells
    return cells.filter((r) => (agriStr(r, 'qs_status') || 'frei') === qsFilter)
  }, [cells, qsFilter])

  function handleTransfer(cellId: string, _cellCode: string): void {
    navigate('/lager/materialfluss', { state: { prefillFromCell: cellId } })
  }

  return (
    <>
      <PageToolbar
        title="Silo-Übersicht"
        subtitle="Bird-View: Kapazitäts- und QS-Status aller Silozellen. Auto-Refresh alle 30 s. (WM-AGRI-MAP-001)"
        mcpContext={{
          pageDomain: 'inventory',
          currentDocument: 'silo-uebersicht',
          availableActions: ['goto-materialfluss', 'goto-visualisierung'],
        }}
        primaryActions={[
          {
            id: 'goto-materialfluss',
            label: 'Materialfluss (Betrieb)',
            icon: <Share2 className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => navigate('/lager/materialfluss'),
            mcp: { intent: 'open-agri-material-operations' },
          },
          {
            id: 'goto-visualisierung',
            label: 'Layout-Editor',
            icon: <LayoutGrid className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => navigate('/lager/materialfluss-visualisierung'),
            mcp: { intent: 'open-agri-flow-visualisation' },
          },
        ]}
        rightSlot={
          <div className="flex items-center gap-3 flex-wrap justify-end">
            {cellsQ.isFetching && (
              <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" aria-label="Aktualisiere…" />
            )}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground whitespace-nowrap">Lager</span>
              <NativeSelect
                className="h-10 min-w-[200px] text-sm"
                value={warehouseId}
                onChange={(e) => setWarehouseId(e.target.value)}
              >
                <option value="">— wählen —</option>
                {items.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name ?? w.code ?? w.id}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground whitespace-nowrap">QS-Filter</span>
              <NativeSelect
                className="h-10 min-w-[140px] text-sm"
                value={qsFilter}
                onChange={(e) => setQsFilter(e.target.value as typeof qsFilter)}
              >
                <option value="alle">Alle</option>
                <option value="frei">Freigegeben</option>
                <option value="in_pruefung">In Prüfung</option>
                <option value="gesperrt">QS-gesperrt</option>
              </NativeSelect>
            </div>
          </div>
        }
      />

      <div className="container max-w-7xl py-6 space-y-6">
        {!warehouseId ? (
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <LayoutGrid className="h-12 w-12 mb-4 opacity-30" />
            <p className="text-sm">Bitte ein Lager auswählen, um die Silo-Übersicht zu laden.</p>
          </div>
        ) : cellsQ.isLoading ? (
          <div className="flex items-center justify-center py-20 text-muted-foreground text-sm">
            Lade Silozellen…
          </div>
        ) : cells.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <p className="text-sm">Keine Silozellen für dieses Lager gefunden.</p>
            <Button variant="link" className="mt-2 text-sm" onClick={() => navigate('/lager/materialfluss')}>
              Silozellen anlegen →
            </Button>
          </div>
        ) : (
          <>
            <SummaryBar cells={cells} />

            {filtered.length === 0 ? (
              <p className="text-sm text-muted-foreground py-8 text-center">
                Keine Zellen entsprechen dem gewählten QS-Filter.
              </p>
            ) : (
              <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                {filtered.map((row) => (
                  <SiloCellCard
                    key={agriStr(row, 'id')}
                    row={row}
                    onTransfer={handleTransfer}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </>
  )
}
