/**
 * WM-AGRI-MOBILE-004 — Mobile Silo-Operateur-UI: touch-optimiert fuer Waage/Hallenterminal.
 * Kompakte Aktionskacheln: Lot-Link, Transfer, QS-Status, Spuelcharge.
 */

import { useState } from 'react'

import { PageToolbar } from '@/components/navigation/PageToolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useWarehouses } from '@/lib/api/inventory'
import {
  agriStr,
  useAgriSiloCells,
  useBookAgriMaterialTransfer,
} from '@/lib/api/agri-material-flow'
import { ArrowLeftRight, CheckCircle2, Droplets, Link2, RefreshCw, Warehouse } from 'lucide-react'

// ── Hilfsfunktionen ──────────────────────────────────────────────────────────

function toNum(v: unknown): number {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function fillPct(stock: number, cap: number): number {
  if (cap <= 0) return 0
  return Math.min(100, Math.round((stock / cap) * 100))
}

// ── Aktion: Lot-Link (Auto-Buchung) ──────────────────────────────────────────

function AutoLotLinkPanel({ warehouseId }: { warehouseId: string }): JSX.Element {
  const { toast } = useToast()
  const [lotId, setLotId] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  async function handleBook() {
    if (!lotId.trim() || busy) return
    setBusy(true)
    try {
      const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/material-flow/lot-link/auto-book', {
        lot_id: lotId.trim(),
        warehouse_id: warehouseId,
        booked_by: 'mobil',
      })
      setResult(data as Record<string, unknown>)
      const r = data as Record<string, unknown>
      if (r['ok']) {
        toast({ title: 'Lot-Link gebucht', description: `Zelle: ${String(r['cell_id'] ?? '—')}` })
      } else {
        toast({ title: 'Kein Auto-Link', description: String(r['reason'] ?? ''), variant: 'destructive' })
      }
    } catch (err) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Link2 className="h-5 w-5 text-primary" />
          Auto Lot-Link
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={lotId}
          onChange={(e) => setLotId(e.target.value)}
          placeholder="Lot-ID oder Lot-Nummer"
          className="h-12 text-base"
          onKeyDown={(e) => e.key === 'Enter' && void handleBook()}
        />
        <Button className="w-full h-12 text-base gap-2" disabled={!lotId.trim() || busy} onClick={handleBook}>
          {busy ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Link2 className="h-4 w-4" />}
          {busy ? 'Buche...' : 'Automatisch buchen'}
        </Button>
        {result && (
          <div className={`rounded-md border px-3 py-2 text-sm ${result['ok'] ? 'border-emerald-300 bg-emerald-50 dark:bg-emerald-900/20' : 'border-red-300 bg-red-50 dark:bg-red-900/20'}`}>
            {result['ok'] ? (
              <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>Gebucht in Zelle <strong>{String(result['cell_id'] ?? '—')}</strong>, {Number(result['quantity_kg'] ?? 0).toLocaleString('de-DE')} kg</span>
              </div>
            ) : (
              <span className="text-red-700 dark:text-red-400">{String(result['reason'] ?? 'Kein Ergebnis')}</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ── Aktion: Schnelltransfer ───────────────────────────────────────────────────

function QuickTransferPanel({ warehouseId, cells }: { warehouseId: string; cells: Record<string, unknown>[] }): JSX.Element {
  const { toast } = useToast()
  const transfer = useBookAgriMaterialTransfer()
  const [fromCell, setFromCell] = useState('')
  const [toCell, setToCell] = useState('')
  const [qty, setQty] = useState('')
  const [articleId, setArticleId] = useState('')

  const fromData = cells.find((c) => agriStr(c, 'id') === fromCell)
  const maxQty = fromData ? toNum(fromData['current_stock_kg']) : 0

  async function handleTransfer() {
    if (!fromCell || !toCell || !qty || !articleId || transfer.isPending) return
    try {
      await transfer.mutateAsync({
        warehouse_id: warehouseId,
        from_cell_id: fromCell,
        to_cell_id: toCell,
        quantity_kg: Number(qty.replace(',', '.')),
        article_id: articleId,
        booked_by: 'mobil',
      })
      toast({ title: 'Transfer gebucht' })
      setQty('')
    } catch (err) {
      toast({ title: 'Transfer fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <ArrowLeftRight className="h-5 w-5 text-primary" />
          Schnelltransfer
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Von</label>
            <NativeSelect value={fromCell} onChange={(e) => setFromCell(e.target.value)} className="h-12 text-base w-full">
              <option value="">-- Zelle --</option>
              {cells.map((c) => (
                <option key={agriStr(c, 'id')} value={agriStr(c, 'id')}>
                  {agriStr(c, 'cell_code')} ({toNum(c['current_stock_kg']).toLocaleString('de-DE')} kg)
                </option>
              ))}
            </NativeSelect>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Nach</label>
            <NativeSelect value={toCell} onChange={(e) => setToCell(e.target.value)} className="h-12 text-base w-full">
              <option value="">-- Zelle --</option>
              {cells.map((c) => (
                <option key={agriStr(c, 'id')} value={agriStr(c, 'id')}>
                  {agriStr(c, 'cell_code')}
                </option>
              ))}
            </NativeSelect>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">
              Menge (kg){maxQty > 0 && <span className="text-muted-foreground"> max {maxQty.toLocaleString('de-DE')}</span>}
            </label>
            <Input
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              placeholder="kg"
              className="h-12 text-base"
              type="number"
              min={1}
              max={maxQty || undefined}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Artikel-ID</label>
            <Input
              value={articleId}
              onChange={(e) => setArticleId(e.target.value)}
              placeholder="Artikel"
              className="h-12 text-base"
            />
          </div>
        </div>
        <Button
          className="w-full h-12 text-base gap-2"
          disabled={!fromCell || !toCell || !qty || !articleId || fromCell === toCell || transfer.isPending}
          onClick={handleTransfer}
        >
          {transfer.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <ArrowLeftRight className="h-4 w-4" />}
          {transfer.isPending ? 'Buche...' : 'Transfer buchen'}
        </Button>
      </CardContent>
    </Card>
  )
}

// ── Aktion: Spuelcharge ───────────────────────────────────────────────────────

function FlushChargePanel({ warehouseId, cells }: { warehouseId: string; cells: Record<string, unknown>[] }): JSX.Element {
  const { toast } = useToast()
  const [fromCell, setFromCell] = useState('')
  const [toCell, setToCell] = useState('')
  const [flushMat, setFlushMat] = useState('')
  const [flushQty, setFlushQty] = useState('500')
  const [busy, setBusy] = useState(false)

  async function handleFlush() {
    if (!fromCell || !toCell || !flushMat || busy) return
    setBusy(true)
    try {
      await apiClient.post('/api/v1/lager/wms/agri/material-flow/flush-charge', {
        warehouse_id: warehouseId,
        from_cell_id: fromCell,
        to_cell_id: toCell,
        flush_material_id: flushMat,
        flush_quantity_kg: Number(flushQty.replace(',', '.')),
        booked_by: 'mobil',
      })
      toast({ title: 'Spuelcharge gebucht' })
      setFromCell('')
      setToCell('')
    } catch (err) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Droplets className="h-5 w-5 text-blue-500" />
          Spuelcharge
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Von</label>
            <NativeSelect value={fromCell} onChange={(e) => setFromCell(e.target.value)} className="h-12 text-base w-full">
              <option value="">-- Zelle --</option>
              {cells.map((c) => <option key={agriStr(c, 'id')} value={agriStr(c, 'id')}>{agriStr(c, 'cell_code')}</option>)}
            </NativeSelect>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Nach</label>
            <NativeSelect value={toCell} onChange={(e) => setToCell(e.target.value)} className="h-12 text-base w-full">
              <option value="">-- Zelle --</option>
              {cells.map((c) => <option key={agriStr(c, 'id')} value={agriStr(c, 'id')}>{agriStr(c, 'cell_code')}</option>)}
            </NativeSelect>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Spuel-Material</label>
            <Input value={flushMat} onChange={(e) => setFlushMat(e.target.value)} placeholder="Artikel-ID" className="h-12 text-base" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-muted-foreground">Menge (kg)</label>
            <Input value={flushQty} onChange={(e) => setFlushQty(e.target.value)} placeholder="kg" className="h-12 text-base" type="number" />
          </div>
        </div>
        <Button
          className="w-full h-12 text-base gap-2"
          variant="outline"
          disabled={!fromCell || !toCell || !flushMat || fromCell === toCell || busy}
          onClick={handleFlush}
        >
          {busy ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Droplets className="h-4 w-4" />}
          {busy ? 'Buche...' : 'Spuelcharge starten'}
        </Button>
      </CardContent>
    </Card>
  )
}

// ── Zellen-Schnuebersicht ─────────────────────────────────────────────────────

function CellQuickView({ cells }: { cells: Record<string, unknown>[] }): JSX.Element {
  if (cells.length === 0) return <></>
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-muted-foreground font-normal">Silozellen-Status</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-border">
          {cells.slice(0, 12).map((c) => {
            const stock = toNum(c['current_stock_kg'])
            const cap = toNum(c['capacity_kg'])
            const pct = fillPct(stock, cap)
            const qs = agriStr(c, 'qs_status') || 'frei'
            return (
              <div key={agriStr(c, 'id')} className="flex items-center gap-3 px-4 py-2.5">
                <div className={`h-2.5 w-2.5 rounded-full shrink-0 ${qs === 'gesperrt' ? 'bg-red-500' : qs === 'in_pruefung' ? 'bg-amber-400' : 'bg-emerald-500'}`} />
                <span className="font-mono text-sm font-medium w-20 shrink-0">{agriStr(c, 'cell_code')}</span>
                <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                  <div className={`h-full rounded-full ${pct >= 95 ? 'bg-red-500' : pct >= 80 ? 'bg-amber-400' : 'bg-emerald-500'}`} style={{ width: `${pct}%` }} />
                </div>
                <span className="text-xs text-muted-foreground tabular-nums w-12 text-right">{pct}%</span>
                {qs === 'gesperrt' && <Badge variant="destructive" className="text-[10px] h-5 px-1">QS</Badge>}
              </div>
            )
          })}
          {cells.length > 12 && (
            <div className="px-4 py-2 text-xs text-muted-foreground text-center">+ {cells.length - 12} weitere</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function SiloMobilPage(): JSX.Element {
  const warehousesQ = useWarehouses({ is_active: true })
  const items = warehousesQ.data?.items ?? []
  const [warehouseId, setWarehouseId] = useState(items[0]?.id ?? '')

  const cellsQ = useAgriSiloCells(warehouseId || undefined, {
    enabled: Boolean(warehouseId),
    refetchInterval: 20_000,
  })
  const cells = cellsQ.data ?? []

  return (
    <>
      <PageToolbar
        title="Silo-Terminal"
        subtitle="Mobil-UI fuer Waage und Hallenterminal (WM-AGRI-MOBILE-004)"
        mcpContext={{ pageDomain: 'inventory', currentDocument: 'silo-mobil', availableActions: [] }}
        rightSlot={
          <div className="flex items-center gap-2">
            {cellsQ.isFetching && <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />}
            <Warehouse className="h-4 w-4 text-muted-foreground shrink-0" />
            <NativeSelect
              className="h-10 min-w-[180px] text-sm"
              value={warehouseId}
              onChange={(e) => setWarehouseId(e.target.value)}
            >
              <option value="">-- Lager --</option>
              {items.map((w) => (
                <option key={w.id} value={w.id}>{w.name ?? w.code ?? w.id}</option>
              ))}
            </NativeSelect>
          </div>
        }
      />

      <div className="container max-w-2xl py-4 space-y-4">
        {!warehouseId ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <Warehouse className="h-12 w-12 mb-4 opacity-30" />
            <p className="text-sm">Bitte Lager waehlen</p>
          </div>
        ) : (
          <>
            <AutoLotLinkPanel warehouseId={warehouseId} />
            <QuickTransferPanel warehouseId={warehouseId} cells={cells} />
            <FlushChargePanel warehouseId={warehouseId} cells={cells} />
            <CellQuickView cells={cells} />
          </>
        )}
      </div>
    </>
  )
}
