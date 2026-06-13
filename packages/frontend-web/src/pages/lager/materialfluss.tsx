/**
 * Agrar-Materialfluss — UI-Skizze (WM-AGRI-SILO-001).
 *
 * Der React-Flow-Bereich zeigt **fest verdrahtete Demo-Knoten** zur Layout-/Status-Vorschau
 * (VALEO-Domain-Typen). Live-Daten: Tabellen unten über GET `/lager/wms/agri/*`, sobald
 * Migration ausgeführt und Stammdaten angelegt sind. Bird-View-Karte: WM-AGRI-MAP-001.
 */

import { memo, useEffect, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
  type NodeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { useNavigate } from '@/app/routing/typed-router'
import { PageToolbar } from '@/components/navigation/PageToolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useWarehouses } from '@/lib/api/inventory'
import {
  agriStr,
  useAgriFlowEdges,
  useAgriFlowNodes,
  useAgriSiloCells,
  usePatchAgriFlowEdge,
  usePatchAgriFlowNode,
  usePatchAgriSiloCell,
  validateAgriMaterialRoute,
} from '@/lib/api/agri-material-flow'
import {
  flowEdgeStatusGermanLabel,
  flowNodeStatusBorderClass,
  flowNodeStatusGermanLabel,
  qsStatusGermanLabel,
} from '@/lib/material-flow-display'
import { AlertTriangle, GitBranch, LayoutGrid, MapPin, Route } from 'lucide-react'

const QS_SELECT_VALUES = ['frei', 'gesperrt', 'in_pruefung', 'reinigung', 'reserviert'] as const
const NODE_STATUS_VALUES = ['active', 'blocked', 'maintenance', 'cleaning'] as const
const EDGE_STATUS_VALUES = ['open', 'blocked', 'maintenance', 'cleaning'] as const

type MfNodeData = { label: string; sub?: string; status?: string }

const MfProcessNode = memo(function MfProcessNode(props: NodeProps): JSX.Element {
  const data = props.data as MfNodeData
  const st = data?.status ?? 'active'
  const border = flowNodeStatusBorderClass(st)
  return (
    <div
      className={`rounded-md border-2 bg-card text-card-foreground px-2 py-1.5 text-xs shadow-sm min-w-[130px] max-w-[200px] ${border}`}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !bg-muted-foreground" />
      <div className="font-semibold leading-tight">{data?.label}</div>
      {data?.sub ? (
        <div className="text-[10px] text-muted-foreground mt-0.5 leading-snug">{data.sub}</div>
      ) : null}
      <div className="text-[10px] mt-1 opacity-90">{flowNodeStatusGermanLabel(st)}</div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !bg-muted-foreground" />
    </div>
  )
})

const demoNodeTypes = { mfProcess: MfProcessNode } satisfies NodeTypes

const demoNodes: Node[] = [
  { id: 'n-intake', type: 'mfProcess', position: { x: 0, y: 120 }, data: { label: 'Annahme', status: 'active' } },
  { id: 'n-scale', type: 'mfProcess', position: { x: 200, y: 120 }, data: { label: 'Waage', status: 'active' } },
  { id: 'n-elev', type: 'mfProcess', position: { x: 400, y: 80 }, data: { label: 'Elevator', status: 'active' } },
  {
    id: 'n-cell-a1',
    type: 'mfProcess',
    position: { x: 620, y: 20 },
    data: { label: 'Silozelle A1', sub: 'Weizen', status: 'active' },
  },
  {
    id: 'n-cell-a2',
    type: 'mfProcess',
    position: { x: 620, y: 200 },
    data: { label: 'Silozelle A2', sub: 'QS gesperrt', status: 'blocked' },
  },
  {
    id: 'n-mixer',
    type: 'mfProcess',
    position: { x: 860, y: 100 },
    data: { label: 'Mischer / MMX', sub: 'Reinigung', status: 'cleaning' },
  },
]

const demoEdges: Edge[] = [
  { id: 'e1', source: 'n-intake', target: 'n-scale', animated: true },
  { id: 'e2', source: 'n-scale', target: 'n-elev', animated: true },
  { id: 'e3', source: 'n-elev', target: 'n-cell-a1', animated: true },
  {
    id: 'e4',
    source: 'n-elev',
    target: 'n-cell-a2',
    label: 'Ziel gesperrt',
    style: { stroke: '#b91c1c', strokeDasharray: '5 4' },
    animated: false,
  },
  { id: 'e5', source: 'n-cell-a1', target: 'n-mixer', animated: true },
]

function SiloCellQsSelect(props: {
  cellId: string
  warehouseId: string
  qsValue: string
  disabled: boolean
  onPatch: (cellId: string, qs: string) => Promise<void>
}): JSX.Element {
  const [local, setLocal] = useState(props.qsValue)
  useEffect(() => {
    setLocal(props.qsValue)
  }, [props.qsValue])
  return (
    <NativeSelect
      className="max-w-[200px] text-xs h-8"
      value={local}
      disabled={props.disabled}
      onChange={(e) => {
        const next = e.target.value
        if (next === props.qsValue) return
        setLocal(next)
        void props.onPatch(props.cellId, next).catch(() => {
          setLocal(props.qsValue)
        })
      }}
    >
      {QS_SELECT_VALUES.map((v) => (
        <option key={v} value={v}>
          {qsStatusGermanLabel(v)}
        </option>
      ))}
    </NativeSelect>
  )
}

function FlowNodeStatusSelect(props: {
  nodeId: string
  warehouseId: string
  statusValue: string
  disabled: boolean
  onPatch: (nodeId: string, status: string) => Promise<void>
}): JSX.Element {
  const [local, setLocal] = useState(props.statusValue)
  useEffect(() => {
    setLocal(props.statusValue)
  }, [props.statusValue])
  return (
    <NativeSelect
      className="max-w-[200px] text-xs h-8"
      value={local}
      disabled={props.disabled}
      onChange={(e) => {
        const next = e.target.value
        if (next === props.statusValue) return
        setLocal(next)
        void props.onPatch(props.nodeId, next).catch(() => {
          setLocal(props.statusValue)
        })
      }}
    >
      {NODE_STATUS_VALUES.map((v) => (
        <option key={v} value={v}>
          {flowNodeStatusGermanLabel(v)}
        </option>
      ))}
    </NativeSelect>
  )
}

function FlowEdgeStatusSelect(props: {
  edgeId: string
  warehouseId: string
  statusValue: string
  disabled: boolean
  onPatch: (edgeId: string, status: string) => Promise<void>
}): JSX.Element {
  const [local, setLocal] = useState(props.statusValue)
  useEffect(() => {
    setLocal(props.statusValue)
  }, [props.statusValue])
  return (
    <NativeSelect
      className="max-w-[200px] text-xs h-8"
      value={local}
      disabled={props.disabled}
      onChange={(e) => {
        const next = e.target.value
        if (next === props.statusValue) return
        setLocal(next)
        void props.onPatch(props.edgeId, next).catch(() => {
          setLocal(props.statusValue)
        })
      }}
    >
      {EDGE_STATUS_VALUES.map((v) => (
        <option key={v} value={v}>
          {flowEdgeStatusGermanLabel(v)}
        </option>
      ))}
    </NativeSelect>
  )
}

export default function MaterialflussPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const patchSiloCell = usePatchAgriSiloCell()
  const patchFlowNode = usePatchAgriFlowNode()
  const patchFlowEdge = usePatchAgriFlowEdge()
  const [patchingCellId, setPatchingCellId] = useState<string | null>(null)
  const [patchingNodeId, setPatchingNodeId] = useState<string | null>(null)
  const [patchingEdgeId, setPatchingEdgeId] = useState<string | null>(null)
  const [routeFrom, setRouteFrom] = useState('')
  const [routeTo, setRouteTo] = useState('')
  const [routeMat, setRouteMat] = useState('')
  const [routePrevMat, setRoutePrevMat] = useState('')
  const [routeResult, setRouteResult] = useState<Record<string, unknown> | null>(null)
  const [routePending, setRoutePending] = useState(false)

  const warehousesQ = useWarehouses({ is_active: true })
  const items = warehousesQ.data?.items ?? []
  const [warehouseId, setWarehouseId] = useState('')

  const siloQ = useAgriSiloCells(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const nodesQ = useAgriFlowNodes(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const edgesQ = useAgriFlowEdges(warehouseId || undefined, { enabled: Boolean(warehouseId) })

  useEffect(() => {
    setRouteFrom('')
    setRouteTo('')
    setRouteMat('')
    setRoutePrevMat('')
    setRouteResult(null)
  }, [warehouseId])

  async function handlePatchSiloQs(cellId: string, qs: string): Promise<void> {
    if (!warehouseId) return
    if (patchingCellId !== null) {
      throw new Error('busy')
    }
    setPatchingCellId(cellId)
    try {
      await patchSiloCell.mutateAsync({ cellId, warehouseId, body: { qs_status: qs } })
      toast({ title: 'QS-Status gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
      throw err
    } finally {
      setPatchingCellId(null)
    }
  }

  async function handlePatchNodeStatus(nodeId: string, status: string): Promise<void> {
    if (!warehouseId) return
    if (patchingNodeId !== null) {
      throw new Error('busy')
    }
    setPatchingNodeId(nodeId)
    try {
      await patchFlowNode.mutateAsync({ nodeId, warehouseId, body: { status } })
      toast({ title: 'Knoten-Status gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
      throw err
    } finally {
      setPatchingNodeId(null)
    }
  }

  async function handlePatchEdgeStatus(edgeId: string, status: string): Promise<void> {
    if (!warehouseId) return
    if (patchingEdgeId !== null) {
      throw new Error('busy')
    }
    setPatchingEdgeId(edgeId)
    try {
      await patchFlowEdge.mutateAsync({ edgeId, warehouseId, body: { status } })
      toast({ title: 'Kanten-Status gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
      throw err
    } finally {
      setPatchingEdgeId(null)
    }
  }

  async function handleValidateRoute(): Promise<void> {
    if (!warehouseId || routePending) return
    if (!routeFrom || !routeTo) {
      toast({
        title: 'Knoten fehlen',
        description: 'Bitte Start- und Zielknoten auswählen.',
        variant: 'destructive',
      })
      return
    }
    setRoutePending(true)
    setRouteResult(null)
    try {
      const res = await validateAgriMaterialRoute({
        warehouse_id: warehouseId,
        from_node_id: routeFrom,
        to_node_id: routeTo,
        material_id: routeMat.trim() || undefined,
        previous_material_id: routePrevMat.trim() || undefined,
      })
      setRouteResult(res)
      if (res.ok === true) {
        toast({ title: 'Route geprüft', description: 'Kein harter Blocker (Hinweise ggf. unten).' })
      } else {
        toast({
          title: 'Route nicht freigegeben',
          description: typeof res.reason === 'string' ? res.reason : 'Details siehe unten.',
          variant: 'destructive',
        })
      }
    } catch (err) {
      toast({ title: 'API-Fehler', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setRoutePending(false)
    }
  }

  const nodeTypes = useMemo(() => demoNodeTypes, [])

  return (
    <>
      <PageToolbar
        title="Materialfluss (Agrar)"
        subtitle="Siloanlagen, Förderwege, QS — digitales Modell (WM-AGRI-SILO-001)"
        mcpContext={{
          pageDomain: 'inventory',
          currentDocument: 'materialfluss-agrar',
          availableActions: ['layout-workshop', 'open-traceability'],
        }}
        primaryActions={[
          {
            id: 'layout-workshop',
            label: 'Layout-Werkstatt',
            icon: <LayoutGrid className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => {
              navigate('/lager/materialfluss-visualisierung')
            },
            mcp: { intent: 'open-agri-material-layout' },
          },
        ]}
        overflowActions={[
          {
            id: 'open-traceability',
            label: 'Rückverfolgbarkeit (Lieferkette)',
            icon: <GitBranch className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => {
              navigate('/lager/rueckverfolgbarkeit')
            },
            mcp: { intent: 'open-supply-chain-traceability', requiredData: ['tenant'] },
          },
        ]}
        rightSlot={
          <div className="flex flex-col items-end gap-2 sm:flex-row sm:items-center sm:gap-3">
            <Badge variant="secondary" className="font-normal tabular-nums">
              WM-AGRI-SILO-001
            </Badge>
            <div className="flex items-center gap-2">
              <label htmlFor="wh-sel" className="text-sm text-muted-foreground whitespace-nowrap">
                Lager
              </label>
              <NativeSelect
                id="wh-sel"
                className="min-w-[220px] h-11 text-sm"
                value={warehouseId}
                onChange={(e) => setWarehouseId(e.target.value)}
              >
                <option value="">— bitte wählen —</option>
                {items.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.code} — {w.name}
                  </option>
                ))}
              </NativeSelect>
            </div>
          </div>
        }
      />
      <div className="container max-w-7xl py-6 space-y-6">
      <p className="text-muted-foreground text-sm max-w-3xl">
        Graph: <strong>Demo-Vorschau</strong> (feste Knoten). Tabellen: API nach Migration. Koordinaten{' '}
        <code className="text-xs">layout_x</code>/<code className="text-xs">layout_y</code>, Bird-View später MapLibre
        (WM-AGRI-MAP-001). Referenz-Hofplan und Zellen-Layout in der Layout-Werkstatt.
      </p>

      <Card className="border-amber-200/80 bg-amber-50/50 dark:bg-amber-950/20">
        <CardHeader className="flex flex-row items-start gap-2 py-3">
          <AlertTriangle className="h-5 w-5 text-amber-700 shrink-0 mt-0.5" />
          <div>
            <CardTitle className="text-base">Hinweis Prototyp</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Keine PLC-Steuerung. Routen-Prüfung:{' '}
              <code className="text-xs">POST …/material-flow/validate-route</code>. Stammdaten:{' '}
              <code className="text-xs">PATCH …/silo-cells/…</code>,{' '}
              <code className="text-xs">PATCH …/material-flow/nodes/…</code>,{' '}
              <code className="text-xs">PATCH …/material-flow/edges/…</code>.
            </p>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            Bird-View Hof / Siloanlage
          </CardTitle>
          <CardDescription>
            Platzhalter für Slice <strong>WM-AGRI-MAP-001</strong> (MapLibre-Luftbild-Overlay, zeichnbare Silos/Zellen).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border border-dashed border-border bg-muted/30 h-32 flex items-center justify-center text-sm text-muted-foreground">
            Karte noch nicht angebunden
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Materialfluss (React Flow — Demo)</CardTitle>
        </CardHeader>
        <CardContent className="h-[520px] min-h-[400px] rounded-md border bg-muted/20 p-0 overflow-hidden">
          <ReactFlow
            nodes={demoNodes}
            edges={demoEdges}
            nodeTypes={nodeTypes}
            fitView
            className="bg-muted/10"
          >
            <Background gap={16} />
            <MiniMap pannable zoomable className="!bg-card/95 !border-border" />
            <Controls className="!bg-card !border-border !shadow-md" />
          </ReactFlow>
        </CardContent>
      </Card>

      {warehouseId ? (
        <div className="grid gap-6 lg:grid-cols-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Silozellen (API)</CardTitle>
              {siloQ.isError ? (
                <p className="text-sm text-destructive">Fehler beim Laden — Migration oder Endpoint prüfen.</p>
              ) : null}
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-2">Code</th>
                    <th className="py-2 pr-2">Name</th>
                    <th className="py-2 pr-2">QS</th>
                    <th className="py-2">kg</th>
                  </tr>
                </thead>
                <tbody>
                  {siloQ.isLoading ? (
                    <tr>
                      <td colSpan={4} className="py-3 text-muted-foreground">
                        Lade…
                      </td>
                    </tr>
                  ) : (siloQ.data ?? []).length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-3 text-muted-foreground">
                        Keine Silozellen — Stammdaten anlegen oder andere Siloanlage wählen.
                      </td>
                    </tr>
                  ) : (
                    (siloQ.data ?? []).map((row) => (
                      <tr key={agriStr(row, 'id')} className="border-b border-border/60">
                        <td className="py-2 pr-2 font-mono text-xs">{agriStr(row, 'cell_code')}</td>
                        <td className="py-2 pr-2">{agriStr(row, 'name')}</td>
                        <td className="py-2 pr-2">
                          <SiloCellQsSelect
                            cellId={agriStr(row, 'id')}
                            warehouseId={warehouseId}
                            qsValue={agriStr(row, 'qs_status')}
                            disabled={patchingCellId !== null}
                            onPatch={handlePatchSiloQs}
                          />
                        </td>
                        <td className="py-2 tabular-nums">{agriStr(row, 'capacity_kg')}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Knoten & Kanten (API)</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <div className="overflow-x-auto">
                <h3 className="text-sm font-medium mb-2">Knoten</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="py-2 pr-2">Code</th>
                      <th className="py-2 pr-2">Typ</th>
                      <th className="py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nodesQ.isLoading ? (
                      <tr>
                        <td colSpan={3} className="py-2 text-muted-foreground">
                          Lade…
                        </td>
                      </tr>
                    ) : (nodesQ.data ?? []).length === 0 ? (
                      <tr>
                        <td colSpan={3} className="py-2 text-muted-foreground">
                          Keine Knoten
                        </td>
                      </tr>
                    ) : (
                      (nodesQ.data ?? []).map((row) => (
                        <tr key={agriStr(row, 'id')} className="border-b border-border/60">
                          <td className="py-2 pr-2 font-mono text-xs">{agriStr(row, 'code')}</td>
                          <td className="py-2 pr-2">{agriStr(row, 'node_type')}</td>
                          <td className="py-2">
                            <FlowNodeStatusSelect
                              nodeId={agriStr(row, 'id')}
                              warehouseId={warehouseId}
                              statusValue={agriStr(row, 'status')}
                              disabled={patchingNodeId !== null}
                              onPatch={handlePatchNodeStatus}
                            />
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div className="overflow-x-auto">
                <h3 className="text-sm font-medium mb-2">Kanten</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="py-2 pr-2">Von</th>
                      <th className="py-2 pr-2">Nach</th>
                      <th className="py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {edgesQ.isLoading ? (
                      <tr>
                        <td colSpan={3} className="py-2 text-muted-foreground">
                          Lade…
                        </td>
                      </tr>
                    ) : (edgesQ.data ?? []).length === 0 ? (
                      <tr>
                        <td colSpan={3} className="py-2 text-muted-foreground">
                          Keine Kanten
                        </td>
                      </tr>
                    ) : (
                      (edgesQ.data ?? []).map((row) => (
                        <tr key={agriStr(row, 'id')} className="border-b border-border/60">
                          <td className="py-2 pr-2 font-mono text-[10px]">{agriStr(row, 'from_node_id')}</td>
                          <td className="py-2 pr-2 font-mono text-[10px]">{agriStr(row, 'to_node_id')}</td>
                          <td className="py-2">
                            <FlowEdgeStatusSelect
                              edgeId={agriStr(row, 'id')}
                              warehouseId={warehouseId}
                              statusValue={agriStr(row, 'status')}
                              disabled={patchingEdgeId !== null}
                              onPatch={handlePatchEdgeStatus}
                            />
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Route className="h-4 w-4" />
                Route prüfen (API)
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Gerichteter Materialfluss: gültige Pfade nur in Kanten-Richtung <code className="text-xs">from → to</code>.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="route-from">
                    Von-Knoten
                  </label>
                  <NativeSelect
                    id="route-from"
                    value={routeFrom}
                    onChange={(e) => setRouteFrom(e.target.value)}
                    disabled={nodesQ.isLoading}
                  >
                    <option value="">— wählen —</option>
                    {(nodesQ.data ?? []).map((n) => (
                      <option key={agriStr(n, 'id')} value={agriStr(n, 'id')}>
                        {agriStr(n, 'code')} ({agriStr(n, 'node_type')})
                      </option>
                    ))}
                  </NativeSelect>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="route-to">
                    Nach-Knoten
                  </label>
                  <NativeSelect
                    id="route-to"
                    value={routeTo}
                    onChange={(e) => setRouteTo(e.target.value)}
                    disabled={nodesQ.isLoading}
                  >
                    <option value="">— wählen —</option>
                    {(nodesQ.data ?? []).map((n) => (
                      <option key={`t-${agriStr(n, 'id')}`} value={agriStr(n, 'id')}>
                        {agriStr(n, 'code')} ({agriStr(n, 'node_type')})
                      </option>
                    ))}
                  </NativeSelect>
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="route-mat">
                    Material neu (optional)
                  </label>
                  <Input
                    id="route-mat"
                    value={routeMat}
                    onChange={(e) => setRouteMat(e.target.value)}
                    placeholder="Artikel-/Material-ID"
                    autoComplete="off"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="route-prevmat">
                    Vorheriges Material (optional)
                  </label>
                  <Input
                    id="route-prevmat"
                    value={routePrevMat}
                    onChange={(e) => setRoutePrevMat(e.target.value)}
                    placeholder="für Verschleppungs-Hinweis"
                    autoComplete="off"
                  />
                </div>
              </div>
              <Button type="button" disabled={routePending} onClick={() => void handleValidateRoute()}>
                {routePending ? 'Prüfe…' : 'Route validieren'}
              </Button>
              {routeResult ? (
                <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-72 whitespace-pre-wrap">
                  {JSON.stringify(routeResult, null, 2)}
                </pre>
              ) : null}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
    </>
  )
}
