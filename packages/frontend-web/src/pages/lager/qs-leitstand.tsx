/**
 * WM-AGRI-QS-004 — QS-Leitstand: Worklist, Freigabe/Sperre, Produktionsfreigabe-Vorschlag.
 */

import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { PageToolbar } from '@/components/navigation/PageToolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import {
  qsStatusLabel,
  qsStatusVariant,
  useQsReleaseSuggest,
  useQsTransition,
  useQsWorklist,
  type QsWorklistCell,
  type QsWorklistLot,
} from '@/lib/api/agri-qs-workflow'
import {
  AlertTriangle,
  CheckCircle2,
  LayoutGrid,
  Loader2,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from 'lucide-react'

type FilterKey = 'all' | 'in_pruefung' | 'gesperrt'

function lotQsStatus(lot: QsWorklistLot): string {
  return lot.qs_status || lot.status || ''
}

function LotActionRow({
  lot,
  operatorDefault,
  onDone,
}: {
  lot: QsWorklistLot
  operatorDefault: string
  onDone: () => void
}): JSX.Element {
  const { toast } = useToast()
  const transition = useQsTransition()
  const [expanded, setExpanded] = useState(false)
  const [operator, setOperator] = useState(operatorDefault)
  const [reason, setReason] = useState('')
  const [sampleId, setSampleId] = useState('')
  const [analysisId, setAnalysisId] = useState('')
  const [labDocumentId, setLabDocumentId] = useState('')
  const [productionRef, setProductionRef] = useState('')
  const status = lotQsStatus(lot)
  const lotKey = lot.virtual_lot_number || lot.id

  const suggest = useQsReleaseSuggest(lotKey, expanded)

  const applySuggest = () => {
    const s = suggest.data?.suggested
    if (!s) return
    if (s.reason) setReason(s.reason)
    if (s.sampleId) setSampleId(s.sampleId)
    if (s.analysisId) setAnalysisId(s.analysisId)
    if (s.labDocumentId) setLabDocumentId(s.labDocumentId)
    if (s.productionReleaseRef) setProductionRef(s.productionReleaseRef)
  }

  const runTransition = async (targetStatus: string) => {
    if (!reason.trim() || !operator.trim()) {
      toast({ title: 'Pflichtfelder', description: 'Grund und Bediener sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      await transition.mutateAsync({
        lotId: lotKey,
        body: {
          targetStatus,
          reason: reason.trim(),
          operator: operator.trim(),
          sampleId: sampleId.trim() || undefined,
          analysisId: analysisId.trim() || undefined,
          labDocumentId: labDocumentId.trim() || undefined,
          productionReleaseRef: productionRef.trim() || undefined,
        },
      })
      toast({
        title: 'QS-Status geändert',
        description: `${lotKey} → ${qsStatusLabel(targetStatus)}`,
      })
      setExpanded(false)
      onDone()
    } catch (err: unknown) {
      const detail =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined
      toast({
        title: 'QS-Wechsel fehlgeschlagen',
        description: typeof detail === 'string' ? detail : 'Bitte Eingaben prüfen.',
        variant: 'destructive',
      })
    }
  }

  const pending = transition.isPending

  return (
    <>
      <tr className="border-b last:border-0">
        <td className="px-3 py-2 font-medium">{lotKey}</td>
        <td className="px-3 py-2 text-muted-foreground">{lot.article_id || '—'}</td>
        <td className="px-3 py-2 tabular-nums">
          {lot.quantity_kg != null ? `${lot.quantity_kg.toLocaleString('de-DE')} kg` : '—'}
        </td>
        <td className="px-3 py-2">
          <Badge variant={qsStatusVariant(status)}>{qsStatusLabel(status)}</Badge>
        </td>
        <td className="px-3 py-2 tabular-nums">{lot.linked_cell_count ?? 0}</td>
        <td className="px-3 py-2">
          <div className="flex flex-wrap gap-1">
            <Button size="sm" variant="outline" onClick={() => setExpanded((v) => !v)} disabled={pending}>
              Aktionen
            </Button>
          </div>
        </td>
      </tr>
      {expanded ? (
        <tr className="bg-muted/30">
          <td colSpan={6} className="px-3 py-3">
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              <Input value={operator} onChange={(e) => setOperator(e.target.value)} placeholder="Bediener *" disabled={pending} />
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Grund *" disabled={pending} className="md:col-span-2" />
              <Input value={sampleId} onChange={(e) => setSampleId(e.target.value)} placeholder="Probe-ID" disabled={pending} />
              <Input value={analysisId} onChange={(e) => setAnalysisId(e.target.value)} placeholder="Analyse-ID" disabled={pending} />
              <Input value={labDocumentId} onChange={(e) => setLabDocumentId(e.target.value)} placeholder="Labordokument" disabled={pending} />
              <Input value={productionRef} onChange={(e) => setProductionRef(e.target.value)} placeholder="Produktionsfreigabe-Ref" disabled={pending} className="md:col-span-2" />
            </div>
            {suggest.isFetching ? (
              <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                <Loader2 className="animate-spin" size={12} /> Vorschlag wird geladen …
              </p>
            ) : suggest.data ? (
              <div className="mt-2 text-xs space-y-1">
                {suggest.data.production_release_allowed ? (
                  <p className="text-emerald-700 flex items-center gap-1">
                    <CheckCircle2 size={12} /> Produktionsfreigabe laut Regelwerk möglich
                  </p>
                ) : (
                  <p className="text-amber-700 flex items-center gap-1">
                    <AlertTriangle size={12} />
                    {(suggest.data.blockers ?? []).join(' · ') || 'Manuelle Freigabe erforderlich'}
                  </p>
                )}
                <Button size="sm" variant="ghost" className="h-7 px-2" onClick={applySuggest} disabled={pending}>
                  Vorschlag übernehmen
                </Button>
              </div>
            ) : null}
            <div className="flex flex-wrap gap-2 mt-3">
              <Button size="sm" onClick={() => void runTransition('frei')} disabled={pending}>
                {pending ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
                <span className="ml-1">Freigeben</span>
              </Button>
              <Button size="sm" variant="secondary" onClick={() => void runTransition('in_pruefung')} disabled={pending}>
                In Prüfung
              </Button>
              <Button size="sm" variant="destructive" onClick={() => void runTransition('gesperrt')} disabled={pending}>
                <XCircle size={14} className="mr-1" />
                Sperren
              </Button>
            </div>
          </td>
        </tr>
      ) : null}
    </>
  )
}

function CellRow({ cell }: { cell: QsWorklistCell }): JSX.Element {
  const status = cell.qs_status || ''
  return (
    <tr className="border-b last:border-0">
      <td className="px-3 py-2 font-medium">{cell.cell_code || cell.id}</td>
      <td className="px-3 py-2 text-muted-foreground">{cell.name || '—'}</td>
      <td className="px-3 py-2">{cell.virtual_lot_number || cell.current_lot_id || '—'}</td>
      <td className="px-3 py-2">
        <Badge variant={qsStatusVariant(status)}>{qsStatusLabel(status)}</Badge>
      </td>
      <td className="px-3 py-2 tabular-nums">
        {cell.current_stock_kg != null ? `${Number(cell.current_stock_kg).toLocaleString('de-DE')} kg` : '—'}
      </td>
      <td className="px-3 py-2 text-xs text-muted-foreground">QS über Lot-Aktion</td>
    </tr>
  )
}

export default function QsLeitstandPage(): JSX.Element {
  const navigate = useNavigate()
  const { data, isLoading, isFetching, refetch } = useQsWorklist(100)
  const [filter, setFilter] = useState<FilterKey>('all')
  const [operatorDefault] = useState('qs-leitstand')

  const lots = useMemo(() => {
    const items = data?.lots ?? []
    if (filter === 'all') return items
    return items.filter((l) => lotQsStatus(l) === filter)
  }, [data?.lots, filter])

  const cells = useMemo(() => {
    const items = data?.cells ?? []
    if (filter === 'all') return items
    return items.filter((c) => (c.qs_status || '') === filter)
  }, [data?.cells, filter])

  const summary = data?.summary

  return (
    <div className="flex flex-col min-h-0 flex-1">
      <PageToolbar
        title="QS-Leitstand"
        subtitle="Silo-Lots und Silozellen — Freigabe, Sperre, Produktionsfreigabe"
        mcpContext={{
          pageDomain: 'inventory',
          currentDocument: 'qs-leitstand',
          availableActions: ['refresh', 'bird-view'],
        }}
        primaryActions={[
          {
            id: 'refresh',
            label: 'Aktualisieren',
            icon: <RefreshCw className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => void refetch(),
            disabled: isFetching,
          },
          {
            id: 'bird-view',
            label: 'Silo-Übersicht',
            icon: <LayoutGrid className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => navigate('/lager/silo-uebersicht'),
          },
        ]}
      />

      <div className="p-4 space-y-4 flex-1 overflow-auto">
        <div className="flex flex-wrap items-center gap-2">
          <ShieldCheck className="text-primary" size={20} />
          <Badge variant="secondary">{summary?.lot_count ?? 0} Lots</Badge>
          <Badge variant="secondary">{summary?.cell_count ?? 0} Zellen</Badge>
          {(summary?.blocked_cells ?? 0) > 0 && (
            <Badge variant="destructive">{summary?.blocked_cells} gesperrt</Badge>
          )}
          {(summary?.in_review ?? 0) > 0 && (
            <Badge variant="outline">{summary?.in_review} in Prüfung</Badge>
          )}
          <NativeSelect
            className="ml-auto w-44 h-8 text-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value as FilterKey)}
          >
            <option value="all">Alle Status</option>
            <option value="in_pruefung">In Prüfung</option>
            <option value="gesperrt">Gesperrt</option>
          </NativeSelect>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16 text-muted-foreground">
            <Loader2 className="animate-spin mr-2" size={18} /> Lädt Worklist …
          </div>
        ) : (
          <>
            <Card>
              <CardHeader className="py-3">
                <CardTitle className="text-sm">Silo-Lots ({lots.length})</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {lots.length === 0 ? (
                  <p className="px-4 py-8 text-sm text-muted-foreground text-center">Keine Lots mit offenem QS-Status.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Lot</th>
                          <th className="text-left font-medium px-3 py-1.5">Artikel</th>
                          <th className="text-left font-medium px-3 py-1.5">Menge</th>
                          <th className="text-left font-medium px-3 py-1.5">QS</th>
                          <th className="text-left font-medium px-3 py-1.5">Zellen</th>
                          <th className="text-left font-medium px-3 py-1.5"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {lots.map((lot) => (
                          <LotActionRow
                            key={lot.id}
                            lot={lot}
                            operatorDefault={operatorDefault}
                            onDone={() => void refetch()}
                          />
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="py-3">
                <CardTitle className="text-sm">Silozellen ({cells.length})</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {cells.length === 0 ? (
                  <p className="px-4 py-8 text-sm text-muted-foreground text-center">Keine Zellen mit offenem QS-Status.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Zelle</th>
                          <th className="text-left font-medium px-3 py-1.5">Name</th>
                          <th className="text-left font-medium px-3 py-1.5">Lot</th>
                          <th className="text-left font-medium px-3 py-1.5">QS</th>
                          <th className="text-left font-medium px-3 py-1.5">Bestand</th>
                          <th className="text-left font-medium px-3 py-1.5">Hinweis</th>
                        </tr>
                      </thead>
                      <tbody>
                        {cells.map((cell) => (
                          <CellRow key={cell.id} cell={cell} />
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}
