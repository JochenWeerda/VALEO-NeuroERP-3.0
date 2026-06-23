/**
 * Layout-Werkstatt + Graph-Editor: Silozellen-Layout und Materialfluss-Graph bearbeiten.
 * Positionen: PATCH layout_x/y (WM-AGRI-SILO-001). Knoten/Kanten: Create/Delete (WM-AGRI-FLOW-002).
 */

import { memo, useCallback, useEffect, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Panel,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
  type NodeTypes,
  useEdgesState,
  useNodesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { useNavigate } from '@/app/routing/typed-router'
import { PageToolbar } from '@/components/navigation/PageToolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useWarehouses } from '@/lib/api/inventory'
import {
  agriStr,
  useAgriFlowEdges,
  useAgriFlowNodes,
  useAgriSiloCells,
  useCreateAgriFlowEdge,
  useCreateAgriFlowNode,
  useDeleteAgriFlowEdge,
  useDeleteAgriFlowNode,
  usePatchAgriFlowNode,
  usePatchAgriSiloCell,
} from '@/lib/api/agri-material-flow'
import { flowNodeStatusBorderClass, flowNodeStatusGermanLabel, qsStatusGermanLabel } from '@/lib/material-flow-display'
import { ArrowLeft, BookOpen, GitBranch, LayoutGrid, Plus, Share2, Trash2 } from 'lucide-react'

type SiloCellNodeData = { label: string; sub?: string; qs?: string; realId: string }

const SiloCellRfNode = memo(function SiloCellRfNode(props: NodeProps): JSX.Element {
  const d = props.data as SiloCellNodeData
  const qs = d?.qs ?? 'frei'
  const border =
    qs === 'gesperrt'
      ? 'border-red-600'
      : qs === 'in_pruefung'
        ? 'border-amber-500'
        : 'border-border'
  return (
    <div
      className={`rounded-lg border-2 bg-card text-card-foreground px-2 py-2 text-xs shadow-sm min-w-[140px] max-w-[180px] ${border}`}
    >
      <Handle type="target" position={Position.Top} className="!h-2 !w-2 !bg-muted-foreground" />
      <div className="font-semibold leading-tight">{d?.label ?? '—'}</div>
      {d?.sub ? <div className="text-[10px] text-muted-foreground mt-0.5">{d.sub}</div> : null}
      <div className="text-[10px] mt-1">{qsStatusGermanLabel(qs)}</div>
      <Handle type="source" position={Position.Bottom} className="!h-2 !w-2 !bg-muted-foreground" />
    </div>
  )
})

type FlowProcData = { label: string; sub?: string; status?: string }

const FlowProcRfNode = memo(function FlowProcRfNode(props: NodeProps): JSX.Element {
  const d = props.data as FlowProcData
  const st = d?.status ?? 'active'
  const border = flowNodeStatusBorderClass(st)
  return (
    <div
      className={`rounded-md border-2 bg-card text-card-foreground px-2 py-1.5 text-xs shadow-sm min-w-[130px] max-w-[200px] ${border}`}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !bg-muted-foreground" />
      <div className="font-semibold leading-tight">{d?.label ?? '—'}</div>
      {d?.sub ? <div className="text-[10px] text-muted-foreground mt-0.5">{d.sub}</div> : null}
      <div className="text-[10px] mt-1 opacity-90">{flowNodeStatusGermanLabel(st)}</div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !bg-muted-foreground" />
    </div>
  )
})

const siloNodeTypes = { siloCell: SiloCellRfNode } satisfies NodeTypes
const flowNodeTypes = { flowProc: FlowProcRfNode } satisfies NodeTypes

function parseLayoutNum(v: unknown): number | undefined {
  if (v == null || v === '') return undefined
  const n = typeof v === 'number' ? v : Number(String(v))
  return Number.isFinite(n) ? n : undefined
}

// ── Create-Node-Dialog ────────────────────────────────────────────────────────

interface CreateNodeDialogProps {
  warehouseId: string
  onClose: () => void
}

function CreateNodeDialog({ warehouseId, onClose }: CreateNodeDialogProps): JSX.Element {
  const { toast } = useToast()
  const createNode = useCreateAgriFlowNode()
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [nodeType, setNodeType] = useState('process')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!code.trim()) return
    try {
      await createNode.mutateAsync({
        warehouseId,
        body: { code: code.trim(), name: name.trim() || code.trim(), node_type: nodeType },
      })
      toast({ title: 'Knoten angelegt' })
      onClose()
    } catch (err) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(err), variant: 'destructive' })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <Card className="w-full max-w-sm shadow-xl" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Neuer Materialfluss-Knoten</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Code *</label>
              <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="z. B. FOERDER-01" className="h-9" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Name</label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="z. B. Förderer 1" className="h-9" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Typ</label>
              <NativeSelect value={nodeType} onChange={(e) => setNodeType(e.target.value)} className="h-9 w-full">
                <option value="process">Prozess</option>
                <option value="silo_cell">Silozelle</option>
                <option value="conveyor">Förderband</option>
                <option value="elevator">Elevator</option>
                <option value="intake">Annahme</option>
                <option value="dispatch">Verladestation</option>
              </NativeSelect>
            </div>
            <div className="flex gap-2 pt-1">
              <Button type="submit" size="sm" disabled={!code.trim() || createNode.isPending} className="flex-1">
                {createNode.isPending ? 'Anlegen…' : 'Anlegen'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={onClose} className="flex-1">Abbrechen</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

// ── Create-Edge-Dialog ────────────────────────────────────────────────────────

interface CreateEdgeDialogProps {
  warehouseId: string
  nodes: Record<string, unknown>[]
  onClose: () => void
}

function CreateEdgeDialog({ warehouseId, nodes, onClose }: CreateEdgeDialogProps): JSX.Element {
  const { toast } = useToast()
  const createEdge = useCreateAgriFlowEdge()
  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [conveyorType, setConveyorType] = useState('belt')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!fromId || !toId || fromId === toId) return
    try {
      await createEdge.mutateAsync({
        warehouseId,
        body: { from_node_id: fromId, to_node_id: toId, conveyor_type: conveyorType, status: 'open' },
      })
      toast({ title: 'Kante angelegt' })
      onClose()
    } catch (err) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(err), variant: 'destructive' })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <Card className="w-full max-w-sm shadow-xl" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Neue Kante</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Von *</label>
              <NativeSelect value={fromId} onChange={(e) => setFromId(e.target.value)} className="h-9 w-full">
                <option value="">— wählen —</option>
                {nodes.map((n) => <option key={agriStr(n, 'id')} value={agriStr(n, 'id')}>{agriStr(n, 'name') || agriStr(n, 'code')}</option>)}
              </NativeSelect>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Nach *</label>
              <NativeSelect value={toId} onChange={(e) => setToId(e.target.value)} className="h-9 w-full">
                <option value="">— wählen —</option>
                {nodes.map((n) => <option key={agriStr(n, 'id')} value={agriStr(n, 'id')}>{agriStr(n, 'name') || agriStr(n, 'code')}</option>)}
              </NativeSelect>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Fördertyp</label>
              <NativeSelect value={conveyorType} onChange={(e) => setConveyorType(e.target.value)} className="h-9 w-full">
                <option value="belt">Förderband</option>
                <option value="elevator">Elevator</option>
                <option value="pipe">Rohrleitung</option>
                <option value="truck">LKW</option>
                <option value="gravity">Schwerkraft</option>
              </NativeSelect>
            </div>
            <div className="flex gap-2 pt-1">
              <Button type="submit" size="sm" disabled={!fromId || !toId || fromId === toId || createEdge.isPending} className="flex-1">
                {createEdge.isPending ? 'Anlegen…' : 'Anlegen'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={onClose} className="flex-1">Abbrechen</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function MaterialflussVisualisierungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const warehousesQ = useWarehouses({ is_active: true })
  const items = warehousesQ.data?.items ?? []
  const [warehouseId, setWarehouseId] = useState('')
  const [showCreateNode, setShowCreateNode] = useState(false)
  const [showCreateEdge, setShowCreateEdge] = useState(false)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null)

  const siloQ = useAgriSiloCells(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const nodesQ = useAgriFlowNodes(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const edgesQ = useAgriFlowEdges(warehouseId || undefined, { enabled: Boolean(warehouseId) })

  const patchCell = usePatchAgriSiloCell()
  const patchNode = usePatchAgriFlowNode()
  const deleteNode = useDeleteAgriFlowNode()
  const deleteEdge = useDeleteAgriFlowEdge()
  const layoutBusy = patchCell.isPending || patchNode.isPending

  const siloNodesInit = useMemo((): Node[] => {
    const rows = siloQ.data ?? []
    return rows.map((row, i) => {
      const id = agriStr(row, 'id')
      const lx = parseLayoutNum(row.layout_x)
      const ly = parseLayoutNum(row.layout_y)
      const col = i % 4
      const rowIdx = Math.floor(i / 4)
      return {
        id: `silo-${id}`,
        type: 'siloCell',
        position: {
          x: lx ?? 40 + col * 200,
          y: ly ?? 40 + rowIdx * 130,
        },
        data: {
          realId: id,
          label: agriStr(row, 'name') || agriStr(row, 'cell_code'),
          sub: agriStr(row, 'cell_code'),
          qs: agriStr(row, 'qs_status') || 'frei',
        },
      }
    })
  }, [siloQ.data])

  const flowNodesInit = useMemo((): Node[] => {
    const rows = nodesQ.data ?? []
    return rows.map((row, i) => {
      const id = agriStr(row, 'id')
      const lx = parseLayoutNum(row.layout_x)
      const ly = parseLayoutNum(row.layout_y)
      const col = i % 5
      const rowIdx = Math.floor(i / 5)
      return {
        id,
        type: 'flowProc',
        position: {
          x: lx ?? 30 + col * 200,
          y: ly ?? 30 + rowIdx * 100,
        },
        data: {
          label: agriStr(row, 'name') || agriStr(row, 'code'),
          sub: agriStr(row, 'code'),
          status: agriStr(row, 'status') || 'active',
        },
      }
    })
  }, [nodesQ.data])

  const flowEdgesInit = useMemo((): Edge[] => {
    const rows = edgesQ.data ?? []
    return rows.map((row) => ({
      id: agriStr(row, 'id'),
      source: agriStr(row, 'from_node_id'),
      target: agriStr(row, 'to_node_id'),
      animated: agriStr(row, 'status') === 'open',
    }))
  }, [edgesQ.data])

  const [siloNodes, setSiloNodes, onSiloNodesChange] = useNodesState<Node>([])
  const [flowNodes, setFlowNodes, onFlowNodesChange] = useNodesState<Node>([])
  const [flowEdges, setFlowEdges, onFlowEdgesChange] = useEdgesState<Edge>([])

  useEffect(() => {
    setSiloNodes(siloNodesInit)
  }, [siloNodesInit, setSiloNodes])

  useEffect(() => {
    setFlowNodes(flowNodesInit)
  }, [flowNodesInit, setFlowNodes])

  useEffect(() => {
    setFlowEdges(flowEdgesInit)
  }, [flowEdgesInit, setFlowEdges])

  const persistSiloLayout = useCallback(
    async (cellId: string, x: number, y: number) => {
      if (!warehouseId || layoutBusy) return
      try {
        await patchCell.mutateAsync({
          cellId,
          warehouseId,
          body: { layout_x: x, layout_y: y },
        })
        toast({ title: 'Silozelle-Layout gespeichert' })
      } catch (err) {
        toast({ title: 'Speichern fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
      }
    },
    [patchCell, toast, warehouseId, layoutBusy],
  )

  const persistFlowLayout = useCallback(
    async (nodeId: string, x: number, y: number) => {
      if (!warehouseId || layoutBusy) return
      try {
        await patchNode.mutateAsync({
          nodeId,
          warehouseId,
          body: { layout_x: x, layout_y: y },
        })
        toast({ title: 'Materialfluss-Layout gespeichert' })
      } catch (err) {
        toast({ title: 'Speichern fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
      }
    },
    [patchNode, toast, warehouseId, layoutBusy],
  )

  const handleDeleteNode = useCallback(async () => {
    if (!selectedNodeId || !warehouseId) return
    try {
      await deleteNode.mutateAsync({ nodeId: selectedNodeId, warehouseId })
      toast({ title: 'Knoten gelöscht' })
      setSelectedNodeId(null)
    } catch (err) {
      toast({ title: 'Löschen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    }
  }, [selectedNodeId, warehouseId, deleteNode, toast])

  const handleDeleteEdge = useCallback(async () => {
    if (!selectedEdgeId || !warehouseId) return
    try {
      await deleteEdge.mutateAsync({ edgeId: selectedEdgeId, warehouseId })
      toast({ title: 'Kante gelöscht' })
      setSelectedEdgeId(null)
    } catch (err) {
      toast({ title: 'Löschen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    }
  }, [selectedEdgeId, warehouseId, deleteEdge, toast])

  return (
    <>
      <PageToolbar
        title="Materialfluss — Visualisierung"
        subtitle="Statische Silos und Materialfluss-Graph: Ziehen & loslassen speichert layout_x / layout_y (WM-AGRI-SILO-001)."
        mcpContext={{
          pageDomain: 'inventory',
          currentDocument: 'materialfluss-visualisierung',
          availableActions: ['back-betrieb', 'open-traceability'],
        }}
        primaryActions={[
          {
            id: 'back-betrieb',
            label: 'Zur Betriebsansicht',
            icon: <ArrowLeft className="h-4 w-4" aria-hidden />,
            variant: 'outline',
            onClick: () => {
              navigate('/lager/materialfluss')
            },
            mcp: { intent: 'open-agri-material-operations' },
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
            <Badge variant="secondary" className="font-normal">
              Layout-Editor
            </Badge>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground whitespace-nowrap">Lager</span>
              <NativeSelect
                className="h-11 min-w-[220px] text-sm"
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
          </div>
        }
      />
      <div className="container max-w-7xl py-6 space-y-6">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <BookOpen className="h-4 w-4 shrink-0" />
            Referenz-Hofplan (Beispielbetrieb)
          </CardTitle>
          <CardDescription>
            Luftbild-Schemata <strong>Folkerts Landhandel</strong>: Lage der Metall-Siloreihe, hexagonale Siloanlage,
            Annahme/Verladung, Schüttgut- und Sackwarenlager sowie Verkehrsfluss (Pfeile). Dient der Orientierung beim
            Anordnen von Silozellen und Materialfluss-Knoten. Ausführliche Bild-Legende:{' '}
            <code className="text-xs">docs/warehouse/folkerts-landhandel-hofplan.md</code>.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="rounded-md border border-border bg-muted/30 overflow-hidden flex justify-center">
            <img
              src="/warehouse/folkerts-landhandel-hofplan.png"
              alt="Hofplan Folkerts Landhandel: Silos links, Lager Mitte/Rechts, Verkehrsfluss"
              className="max-h-[min(420px,55vh)] w-full object-contain"
              loading="lazy"
            />
          </div>
          <ul className="text-xs text-muted-foreground mt-3 space-y-1 list-disc pl-4">
            <li>
              <strong className="text-foreground">Links:</strong> sieben zylindrische Silos, davor Annahme/Verladung,
              daneben ältere hexagonale Siloanlage.
            </li>
            <li>
              <strong className="text-foreground">Mitte:</strong> Sackwarenlager / Hochregal; <strong>rechts:</strong>{' '}
              großflächiges Schüttgutlager (Amazone).
            </li>
            <li>
              <strong className="text-foreground">Verkehr:</strong> Einfahrt unten rechts, Hof-Fahrwege mit
              Umlaufrichtung — später mit Bird-View (MapLibre, WM-AGRI-MAP-001) koppelbar.
            </li>
          </ul>
        </CardContent>
      </Card>

      <Tabs defaultValue="silos" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2 h-11">
          <TabsTrigger value="silos" className="gap-2">
            <LayoutGrid className="h-4 w-4" />
            Statische Silos
          </TabsTrigger>
          <TabsTrigger value="flow" className="gap-2">
            <Share2 className="h-4 w-4" />
            Materialfluss
          </TabsTrigger>
        </TabsList>

        <TabsContent value="silos" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Silozellen-Layout</CardTitle>
              <CardDescription>
                Darstellung der Zellen als Werkstatt-Schema. Ohne Lagerdaten: leer. Kanten optional später (Bird-View:
                WM-AGRI-MAP-001).
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[540px] min-h-[400px] rounded-md border border-border bg-muted/20 p-0 overflow-hidden">
              {!warehouseId ? (
                <p className="p-4 text-sm text-muted-foreground">Bitte ein Lager wählen.</p>
              ) : siloQ.isLoading ? (
                <p className="p-4 text-sm text-muted-foreground">Lade Silozellen…</p>
              ) : siloNodes.length === 0 ? (
                <p className="p-4 text-sm text-muted-foreground">Keine Silozellen für dieses Lager.</p>
              ) : (
                <ReactFlow
                  nodes={siloNodes}
                  edges={[]}
                  onNodesChange={onSiloNodesChange}
                  nodeTypes={siloNodeTypes}
                  onNodeDragStop={(_, n) => {
                    if (n.type !== 'siloCell') return
                    const data = n.data as SiloCellNodeData
                    void persistSiloLayout(data.realId, n.position.x, n.position.y)
                  }}
                  fitView
                  className="bg-muted/10"
                  proOptions={{ hideAttribution: true }}
                >
                  <Background />
                  <Controls className="!bg-card !border-border !shadow-md" />
                  <MiniMap pannable zoomable className="!bg-card/95 !border-border" />
                  <Panel
                    position="top-right"
                    className="text-xs text-muted-foreground rounded-md border border-border bg-card/95 px-2 py-1.5 shadow-sm"
                  >
                    {layoutBusy ? 'Speichern…' : 'Ziehen & loslassen = speichern'}
                  </Panel>
                </ReactFlow>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="flow" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <CardTitle>Materialfluss-Graph</CardTitle>
                  <CardDescription className="mt-1">
                    Knoten und Kanten anlegen, löschen und positionieren (WM-AGRI-FLOW-002). Auswählen -&gt; Löschen-Button aktiv.
                  </CardDescription>
                </div>
                {warehouseId && (
                  <div className="flex gap-2 shrink-0 flex-wrap justify-end">
                    {selectedNodeId && (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="gap-1.5 h-8"
                        disabled={deleteNode.isPending}
                        onClick={handleDeleteNode}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Knoten löschen
                      </Button>
                    )}
                    {selectedEdgeId && (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="gap-1.5 h-8"
                        disabled={deleteEdge.isPending}
                        onClick={handleDeleteEdge}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Kante löschen
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      className="gap-1.5 h-8"
                      disabled={!warehouseId || nodesQ.isLoading}
                      onClick={() => setShowCreateEdge(true)}
                    >
                      <Plus className="h-3.5 w-3.5" />
                      Kante
                    </Button>
                    <Button
                      size="sm"
                      className="gap-1.5 h-8"
                      disabled={!warehouseId}
                      onClick={() => setShowCreateNode(true)}
                    >
                      <Plus className="h-3.5 w-3.5" />
                      Knoten
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="h-[540px] min-h-[400px] rounded-md border border-border bg-muted/20 p-0 overflow-hidden">
              {!warehouseId ? (
                <p className="p-4 text-sm text-muted-foreground">Bitte ein Lager wählen.</p>
              ) : nodesQ.isLoading || edgesQ.isLoading ? (
                <p className="p-4 text-sm text-muted-foreground">Lade Knoten/Kanten…</p>
              ) : flowNodes.length === 0 ? (
                <p className="p-4 text-sm text-muted-foreground">Keine Materialfluss-Knoten für dieses Lager.</p>
              ) : (
                <ReactFlow
                  nodes={flowNodes}
                  edges={flowEdges}
                  onNodesChange={onFlowNodesChange}
                  onEdgesChange={onFlowEdgesChange}
                  nodeTypes={flowNodeTypes}
                  onNodeDragStop={(_, n) => {
                    if (n.type !== 'flowProc') return
                    void persistFlowLayout(n.id, n.position.x, n.position.y)
                  }}
                  onNodeClick={(_, n) => {
                    setSelectedNodeId((prev) => (prev === n.id ? null : n.id))
                    setSelectedEdgeId(null)
                  }}
                  onEdgeClick={(_, e) => {
                    setSelectedEdgeId((prev) => (prev === e.id ? null : e.id))
                    setSelectedNodeId(null)
                  }}
                  onPaneClick={() => { setSelectedNodeId(null); setSelectedEdgeId(null) }}
                  fitView
                  className="bg-muted/10"
                  proOptions={{ hideAttribution: true }}
                >
                  <Background />
                  <Controls className="!bg-card !border-border !shadow-md" />
                  <MiniMap pannable zoomable className="!bg-card/95 !border-border" />
                  <Panel
                    position="top-right"
                    className="text-xs text-muted-foreground rounded-md border border-border bg-card/95 px-2 py-1.5 shadow-sm"
                  >
                    {layoutBusy ? 'Speichern…' : 'Ziehen & loslassen = speichern'}
                  </Panel>
                </ReactFlow>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>

    {showCreateNode && warehouseId && (
      <CreateNodeDialog warehouseId={warehouseId} onClose={() => setShowCreateNode(false)} />
    )}
    {showCreateEdge && warehouseId && (
      <CreateEdgeDialog
        warehouseId={warehouseId}
        nodes={nodesQ.data ?? []}
        onClose={() => setShowCreateEdge(false)}
      />
    )}
    </>
  )
}
