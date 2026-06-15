/**
 * Agrar-Materialfluss — WM-AGRI-SILO-001.
 *
 * React-Flow: **ohne gewähltes Lager** Demo-Vorschau; **mit Lager** und vorhandenen
 * `material_flow_nodes` / `material_flow_edges` **Live-Daten** (layout_x/y oder Raster-Fallback).
 * Tabellen: PATCH/CRUD über `/api/v1/lager/wms/agri/*`. Bird-View: WM-AGRI-MAP-001.
 */

import { memo, useEffect, useMemo, useState } from 'react'
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
  useAgriSiloSystems,
  useCreateAgriFlowEdge,
  useCreateAgriFlowNode,
  useCreateAgriSiloCell,
  useCreateAgriSiloSystem,
  usePatchAgriFlowEdge,
  usePatchAgriFlowNode,
  usePatchAgriSiloCell,
  validateAgriMaterialRoute,
} from '@/lib/api/agri-material-flow'
import {
  agriMaterialFlowApiToReactFlowEdges,
  agriMaterialFlowApiToReactFlowNodes,
  flowEdgeStatusGermanLabel,
  flowNodeStatusBorderClass,
  flowNodeStatusGermanLabel,
  qsStatusGermanLabel,
  type AgriFlowLike,
} from '@/lib/material-flow-display'
import { AlertTriangle, GitBranch, LayoutGrid, MapPin, Route } from 'lucide-react'

const QS_SELECT_VALUES = ['frei', 'gesperrt', 'in_pruefung', 'reinigung', 'reserviert'] as const
const NODE_STATUS_VALUES = ['active', 'blocked', 'maintenance', 'cleaning'] as const
const EDGE_STATUS_VALUES = ['open', 'blocked', 'maintenance', 'cleaning'] as const
const NODE_TYPE_OPTIONS = [
  'intake',
  'scale',
  'silo_cell',
  'elevator',
  'diverter',
  'mixer',
  'valve',
  'mobile_unit',
] as const

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

function SiloCellInventoryEditor(props: {
  cellId: string
  materialServer: string
  lotServer: string
  disabled: boolean
  saving: boolean
  onSave: (cellId: string, materialId: string, lotId: string) => Promise<void>
}): JSX.Element {
  const [mat, setMat] = useState(props.materialServer)
  const [lot, setLot] = useState(props.lotServer)
  useEffect(() => {
    setMat(props.materialServer)
    setLot(props.lotServer)
  }, [props.materialServer, props.lotServer, props.cellId])
  return (
    <div className="flex flex-col gap-1 max-w-[240px]">
      <Input
        className="h-7 text-[10px] font-mono"
        value={mat}
        onChange={(e) => setMat(e.target.value)}
        disabled={props.disabled}
        placeholder="current_material_id"
        autoComplete="off"
        spellCheck={false}
      />
      <Input
        className="h-7 text-[10px] font-mono"
        value={lot}
        onChange={(e) => setLot(e.target.value)}
        disabled={props.disabled}
        placeholder="current_lot_id"
        autoComplete="off"
        spellCheck={false}
      />
      <Button
        type="button"
        size="sm"
        variant="secondary"
        className="h-7 text-xs w-full"
        disabled={props.disabled}
        onClick={() => void props.onSave(props.cellId, mat, lot)}
      >
        {props.saving ? 'Speichere…' : 'Material / Lot speichern'}
      </Button>
    </div>
  )
}

function NodeLayoutEditor(props: {
  nodeId: string
  layoutXServer: string
  layoutYServer: string
  disabled: boolean
  saving: boolean
  onSave: (nodeId: string, layoutX: string, layoutY: string) => Promise<void>
}): JSX.Element {
  const [lx, setLx] = useState(props.layoutXServer)
  const [ly, setLy] = useState(props.layoutYServer)
  useEffect(() => {
    setLx(props.layoutXServer)
    setLy(props.layoutYServer)
  }, [props.layoutXServer, props.layoutYServer, props.nodeId])
  return (
    <div className="flex flex-col gap-1 max-w-[200px]">
      <div className="grid grid-cols-2 gap-1">
        <Input
          className="h-7 text-[10px] font-mono"
          value={lx}
          onChange={(e) => setLx(e.target.value)}
          disabled={props.disabled}
          placeholder="layout_x"
          inputMode="decimal"
          autoComplete="off"
        />
        <Input
          className="h-7 text-[10px] font-mono"
          value={ly}
          onChange={(e) => setLy(e.target.value)}
          disabled={props.disabled}
          placeholder="layout_y"
          inputMode="decimal"
          autoComplete="off"
        />
      </div>
      <Button
        type="button"
        size="sm"
        variant="secondary"
        className="h-7 text-xs w-full"
        disabled={props.disabled}
        onClick={() => void props.onSave(props.nodeId, lx, ly)}
      >
        {props.saving ? 'Speichere…' : 'Position speichern'}
      </Button>
    </div>
  )
}

function FlowEdgeContaminationSelect(props: {
  edgeId: string
  guardEnabled: boolean
  disabled: boolean
  onPatch: (edgeId: string, contamination_guard_enabled: boolean) => Promise<void>
}): JSX.Element {
  const [local, setLocal] = useState(props.guardEnabled ? '1' : '0')
  useEffect(() => {
    setLocal(props.guardEnabled ? '1' : '0')
  }, [props.guardEnabled])
  return (
    <NativeSelect
      className="max-w-[160px] text-xs h-8"
      value={local}
      disabled={props.disabled}
      onChange={(e) => {
        const next = e.target.value === '1'
        if (next === props.guardEnabled) return
        setLocal(e.target.value)
        void props.onPatch(props.edgeId, next).catch(() => {
          setLocal(props.guardEnabled ? '1' : '0')
        })
      }}
    >
      <option value="1">Schutz an</option>
      <option value="0">Schutz aus</option>
    </NativeSelect>
  )
}

function FlowEdgeFlushSelect(props: {
  edgeId: string
  flushRequired: boolean
  disabled: boolean
  onPatch: (edgeId: string, flush_required: boolean) => Promise<void>
}): JSX.Element {
  const [local, setLocal] = useState(props.flushRequired ? '1' : '0')
  useEffect(() => {
    setLocal(props.flushRequired ? '1' : '0')
  }, [props.flushRequired])
  return (
    <NativeSelect
      className="max-w-[160px] text-xs h-8"
      value={local}
      disabled={props.disabled}
      onChange={(e) => {
        const next = e.target.value === '1'
        if (next === props.flushRequired) return
        setLocal(e.target.value)
        void props.onPatch(props.edgeId, next).catch(() => {
          setLocal(props.flushRequired ? '1' : '0')
        })
      }}
    >
      <option value="1">Spülcharge nötig</option>
      <option value="0">keine Pflicht</option>
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
  const [inventorySavingCellId, setInventorySavingCellId] = useState<string | null>(null)
  const [siloLayoutSavingCellId, setSiloLayoutSavingCellId] = useState<string | null>(null)
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
  const systemsQ = useAgriSiloSystems(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const createSiloSystem = useCreateAgriSiloSystem()
  const createSiloCell = useCreateAgriSiloCell()
  const createFlowNode = useCreateAgriFlowNode()
  const createFlowEdge = useCreateAgriFlowEdge()

  const [newSysCode, setNewSysCode] = useState('')
  const [newSysName, setNewSysName] = useState('')
  const [sysSubmitting, setSysSubmitting] = useState(false)
  const [cellSiloSystemId, setCellSiloSystemId] = useState('')
  const [newCellCode, setNewCellCode] = useState('')
  const [newCellName, setNewCellName] = useState('')
  const [newCellCap, setNewCellCap] = useState('')
  const [cellSubmitting, setCellSubmitting] = useState(false)
  const [newNodeType, setNewNodeType] = useState<string>(NODE_TYPE_OPTIONS[0])
  const [newNodeCode, setNewNodeCode] = useState('')
  const [newNodeName, setNewNodeName] = useState('')
  const [newNodeLayoutX, setNewNodeLayoutX] = useState('')
  const [newNodeLayoutY, setNewNodeLayoutY] = useState('')
  const [nodeSubmitting, setNodeSubmitting] = useState(false)
  const [edgeFromId, setEdgeFromId] = useState('')
  const [edgeToId, setEdgeToId] = useState('')
  const [edgeSubmitting, setEdgeSubmitting] = useState(false)

  useEffect(() => {
    setCellSiloSystemId('')
    setNewSysCode('')
    setNewSysName('')
    setNewCellCode('')
    setNewCellName('')
    setNewCellCap('')
    setNewNodeCode('')
    setNewNodeName('')
    setNewNodeLayoutX('')
    setNewNodeLayoutY('')
    setEdgeFromId('')
    setEdgeToId('')
    setRouteFrom('')
    setRouteTo('')
    setRouteMat('')
    setRoutePrevMat('')
    setRouteResult(null)
  }, [warehouseId])

  useEffect(() => {
    const systems = systemsQ.data ?? []
    if (systems.length === 0) {
      setCellSiloSystemId('')
      return
    }
    setCellSiloSystemId((prev) => {
      if (prev && systems.some((s) => agriStr(s, 'id') === prev)) return prev
      return agriStr(systems[0], 'id')
    })
  }, [systemsQ.data])

  const liveNodes = useMemo(
    () => agriMaterialFlowApiToReactFlowNodes((nodesQ.data ?? []) as AgriFlowLike[]),
    [nodesQ.data],
  )
  const nodeIdSet = useMemo(() => {
    const set = new Set<string>()
    for (const row of nodesQ.data ?? []) {
      const id = agriStr(row, 'id')
      if (id) set.add(id)
    }
    return set
  }, [nodesQ.data])
  const liveEdges = useMemo(
    () => agriMaterialFlowApiToReactFlowEdges((edgesQ.data ?? []) as AgriFlowLike[], nodeIdSet),
    [edgesQ.data, nodeIdSet],
  )

  const nodeCodeById = useMemo(() => {
    const m = new Map<string, string>()
    for (const n of nodesQ.data ?? []) {
      const id = agriStr(n, 'id')
      const code = agriStr(n, 'code')
      if (id) m.set(id, code || id.slice(0, 8))
    }
    return m
  }, [nodesQ.data])

  const graphLoading = Boolean(warehouseId) && (nodesQ.isLoading || edgesQ.isLoading)
  const graphError = Boolean(warehouseId) && (nodesQ.isError || edgesQ.isError)
  const graphReady = Boolean(warehouseId) && !graphLoading && !graphError
  const hasLiveGraphData =
    graphReady && ((nodesQ.data?.length ?? 0) > 0 || (edgesQ.data?.length ?? 0) > 0)

  const displayNodes = !warehouseId ? demoNodes : hasLiveGraphData ? liveNodes : []
  const displayEdges = !warehouseId ? demoEdges : hasLiveGraphData ? liveEdges : []

  const siloCellsTableBusy =
    patchingCellId !== null || inventorySavingCellId !== null || siloLayoutSavingCellId !== null

  const flowCardTitle = !warehouseId
    ? 'Materialfluss (React Flow — Demo)'
    : graphLoading
      ? 'Materialfluss (React Flow — lädt …)'
      : graphError
        ? 'Materialfluss (React Flow — API-Fehler)'
        : hasLiveGraphData
          ? 'Materialfluss (React Flow — Live-Stammdaten)'
          : 'Materialfluss (React Flow — noch keine Knoten/Kanten)'

  async function handlePatchSiloQs(cellId: string, qs: string): Promise<void> {
    if (!warehouseId) return
    if (patchingCellId !== null || inventorySavingCellId !== null || siloLayoutSavingCellId !== null) {
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

  async function handlePatchSiloInventory(cellId: string, materialId: string, lotId: string): Promise<void> {
    if (!warehouseId) return
    if (patchingCellId !== null || inventorySavingCellId !== null || siloLayoutSavingCellId !== null) {
      toast({
        title: 'Bitte warten',
        description: 'Es läuft bereits ein Speichervorgang an den Silozellen.',
        variant: 'destructive',
      })
      return
    }
    setInventorySavingCellId(cellId)
    try {
      await patchSiloCell.mutateAsync({
        cellId,
        warehouseId,
        body: {
          current_material_id: materialId.trim() === '' ? null : materialId.trim(),
          current_lot_id: lotId.trim() === '' ? null : lotId.trim(),
        },
      })
      toast({ title: 'Material / Lot gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
    } finally {
      setInventorySavingCellId(null)
    }
  }

  async function handlePatchSiloLayout(cellId: string, layoutX: string, layoutY: string): Promise<void> {
    if (!warehouseId) return
    if (patchingCellId !== null || inventorySavingCellId !== null || siloLayoutSavingCellId !== null) {
      toast({
        title: 'Bitte warten',
        description: 'An Silozellen wird bereits gespeichert.',
        variant: 'destructive',
      })
      return
    }
    const xRaw = layoutX.trim()
    const yRaw = layoutY.trim()
    const body: { layout_x?: number | null; layout_y?: number | null } = {}
    if (xRaw === '') {
      body.layout_x = null
    } else {
      const n = Number(xRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_x ungültig', variant: 'destructive' })
        return
      }
      body.layout_x = n
    }
    if (yRaw === '') {
      body.layout_y = null
    } else {
      const n = Number(yRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_y ungültig', variant: 'destructive' })
        return
      }
      body.layout_y = n
    }
    setSiloLayoutSavingCellId(cellId)
    try {
      await patchSiloCell.mutateAsync({ cellId, warehouseId, body })
      toast({ title: 'Silozellen-Layout gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
    } finally {
      setSiloLayoutSavingCellId(null)
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

  async function handlePatchNodeLayout(nodeId: string, layoutX: string, layoutY: string): Promise<void> {
    if (!warehouseId) return
    if (patchingNodeId !== null) {
      toast({
        title: 'Bitte warten',
        description: 'An einem anderen Knoten wird bereits gespeichert.',
        variant: 'destructive',
      })
      return
    }
    const xRaw = layoutX.trim()
    const yRaw = layoutY.trim()
    const body: { layout_x?: number | null; layout_y?: number | null } = {}
    if (xRaw === '') {
      body.layout_x = null
    } else {
      const n = Number(xRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_x ungültig', variant: 'destructive' })
        return
      }
      body.layout_x = n
    }
    if (yRaw === '') {
      body.layout_y = null
    } else {
      const n = Number(yRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_y ungültig', variant: 'destructive' })
        return
      }
      body.layout_y = n
    }
    setPatchingNodeId(nodeId)
    try {
      await patchFlowNode.mutateAsync({ nodeId, warehouseId, body })
      toast({ title: 'Knoten-Position gespeichert' })
    } catch (err) {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
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

  async function handlePatchEdgeContamination(edgeId: string, contamination_guard_enabled: boolean): Promise<void> {
    if (!warehouseId) return
    if (patchingEdgeId !== null) {
      toast({
        title: 'Bitte warten',
        description: 'An einer anderen Kante wird bereits gespeichert.',
        variant: 'destructive',
      })
      throw new Error('busy')
    }
    setPatchingEdgeId(edgeId)
    try {
      await patchFlowEdge.mutateAsync({ edgeId, warehouseId, body: { contamination_guard_enabled } })
      toast({ title: 'Verschleppungsschutz gespeichert' })
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

  async function handlePatchEdgeFlush(edgeId: string, flush_required: boolean): Promise<void> {
    if (!warehouseId) return
    if (patchingEdgeId !== null) {
      toast({
        title: 'Bitte warten',
        description: 'An einer anderen Kante wird bereits gespeichert.',
        variant: 'destructive',
      })
      throw new Error('busy')
    }
    setPatchingEdgeId(edgeId)
    try {
      await patchFlowEdge.mutateAsync({ edgeId, warehouseId, body: { flush_required } })
      toast({ title: 'Spülcharge-Flag gespeichert' })
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
        const warns = res.warnings
        const warnList = Array.isArray(warns) ? warns.filter((w): w is string => typeof w === 'string') : []
        toast({
          title: 'Route geprüft',
          description:
            warnList.length > 0
              ? `${warnList.length} Hinweis(e): ${warnList.slice(0, 4).join(' · ')}${warnList.length > 4 ? ' …' : ''}`
              : 'Kein harter Blocker (Details unten).',
        })
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

  async function handleCreateSiloSystem(): Promise<void> {
    if (!warehouseId || sysSubmitting) return
    const code = newSysCode.trim()
    const name = newSysName.trim()
    if (!code || !name) {
      toast({
        title: 'Angaben fehlen',
        description: 'Code und Name der Siloanlage sind Pflicht.',
        variant: 'destructive',
      })
      return
    }
    setSysSubmitting(true)
    try {
      await createSiloSystem.mutateAsync({ warehouseId, body: { system_code: code, name } })
      setNewSysCode('')
      setNewSysName('')
      toast({ title: 'Siloanlage angelegt' })
    } catch (err) {
      toast({ title: 'Anlegen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setSysSubmitting(false)
    }
  }

  async function handleCreateSiloCell(): Promise<void> {
    if (!warehouseId || cellSubmitting) return
    if (!cellSiloSystemId) {
      toast({
        title: 'Keine Siloanlage',
        description: 'Legen Sie zuerst eine Siloanlage an.',
        variant: 'destructive',
      })
      return
    }
    const cell_code = newCellCode.trim()
    const name = newCellName.trim()
    if (!cell_code || !name) {
      toast({
        title: 'Angaben fehlen',
        description: 'Zellen-Code und Name sind Pflicht.',
        variant: 'destructive',
      })
      return
    }
    const capRaw = newCellCap.trim()
    const capNum = capRaw === '' ? undefined : Number(capRaw)
    if (capRaw !== '' && !Number.isFinite(capNum)) {
      toast({ title: 'Kapazität ungültig', variant: 'destructive' })
      return
    }
    setCellSubmitting(true)
    try {
      await createSiloCell.mutateAsync({
        siloSystemId: cellSiloSystemId,
        warehouseId,
        body: { cell_code, name, ...(capNum !== undefined ? { capacity_kg: capNum } : {}) },
      })
      setNewCellCode('')
      setNewCellName('')
      setNewCellCap('')
      toast({ title: 'Silozelle angelegt' })
    } catch (err) {
      toast({ title: 'Anlegen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setCellSubmitting(false)
    }
  }

  async function handleCreateFlowNode(): Promise<void> {
    if (!warehouseId || nodeSubmitting) return
    const code = newNodeCode.trim()
    const name = newNodeName.trim()
    if (!code || !name) {
      toast({
        title: 'Angaben fehlen',
        description: 'Knoten-Code und Name sind Pflicht.',
        variant: 'destructive',
      })
      return
    }
    const lxRaw = newNodeLayoutX.trim()
    const lyRaw = newNodeLayoutY.trim()
    let layout_x: number | undefined
    let layout_y: number | undefined
    if (lxRaw !== '') {
      const n = Number(lxRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_x ungültig', variant: 'destructive' })
        return
      }
      layout_x = n
    }
    if (lyRaw !== '') {
      const n = Number(lyRaw)
      if (!Number.isFinite(n)) {
        toast({ title: 'layout_y ungültig', variant: 'destructive' })
        return
      }
      layout_y = n
    }
    setNodeSubmitting(true)
    try {
      await createFlowNode.mutateAsync({
        warehouseId,
        body: {
          node_type: newNodeType,
          code,
          name,
          ...(layout_x !== undefined ? { layout_x } : {}),
          ...(layout_y !== undefined ? { layout_y } : {}),
        },
      })
      setNewNodeCode('')
      setNewNodeName('')
      setNewNodeLayoutX('')
      setNewNodeLayoutY('')
      toast({ title: 'Knoten angelegt' })
    } catch (err) {
      toast({ title: 'Anlegen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setNodeSubmitting(false)
    }
  }

  async function handleCreateFlowEdge(): Promise<void> {
    if (!warehouseId || edgeSubmitting) return
    if (!edgeFromId || !edgeToId) {
      toast({
        title: 'Knoten fehlen',
        description: 'Bitte Von- und Zielknoten wählen.',
        variant: 'destructive',
      })
      return
    }
    if (edgeFromId === edgeToId) {
      toast({
        title: 'Ungültige Kante',
        description: 'Start und Ziel dürfen nicht identisch sein.',
        variant: 'destructive',
      })
      return
    }
    setEdgeSubmitting(true)
    try {
      await createFlowEdge.mutateAsync({
        warehouseId,
        body: { from_node_id: edgeFromId, to_node_id: edgeToId },
      })
      toast({ title: 'Kante angelegt' })
    } catch (err) {
      toast({ title: 'Anlegen fehlgeschlagen', description: getAxiosErrorMessage(err), variant: 'destructive' })
    } finally {
      setEdgeSubmitting(false)
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
        <strong>Ohne Lagerwahl:</strong> React-Flow zeigt eine <strong>Demo-Vorschau</strong>. <strong>Mit Lager:</strong>{' '}
        Knoten und Kanten aus der API (<code className="text-xs">layout_x</code>/<code className="text-xs">layout_y</code>
        , sonst Raster). Bird-View: WM-AGRI-MAP-001. Layout-Werkstatt für Referenz-Hofplan.
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

      {warehouseId ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Stammdaten anlegen (API)</CardTitle>
            <CardDescription>
              Minimaler Aufbau: Siloanlage → Silozelle → Materialfluss-Knoten → Kante. Kein Löschen — Status über
              Tabellen steuern.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3 rounded-md border p-4">
              <h3 className="text-sm font-medium">Siloanlage</h3>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-sys-code">
                  system_code
                </label>
                <Input
                  id="mf-sys-code"
                  value={newSysCode}
                  onChange={(e) => setNewSysCode(e.target.value)}
                  disabled={sysSubmitting}
                  autoComplete="off"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-sys-name">
                  Name
                </label>
                <Input
                  id="mf-sys-name"
                  value={newSysName}
                  onChange={(e) => setNewSysName(e.target.value)}
                  disabled={sysSubmitting}
                  autoComplete="off"
                />
              </div>
              <Button type="button" disabled={sysSubmitting} onClick={() => void handleCreateSiloSystem()}>
                {sysSubmitting ? 'Speichere…' : 'Siloanlage anlegen'}
              </Button>
            </div>

            <div className="space-y-3 rounded-md border p-4">
              <h3 className="text-sm font-medium">Silozelle</h3>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-cell-sys">
                  Siloanlage
                </label>
                <NativeSelect
                  id="mf-cell-sys"
                  value={cellSiloSystemId}
                  onChange={(e) => setCellSiloSystemId(e.target.value)}
                  disabled={cellSubmitting || systemsQ.isLoading}
                >
                  {systemsQ.isLoading ? (
                    <option value="">Lade …</option>
                  ) : (systemsQ.data ?? []).length === 0 ? (
                    <option value="">— zuerst Siloanlage —</option>
                  ) : (
                    (systemsQ.data ?? []).map((s) => (
                      <option key={agriStr(s, 'id')} value={agriStr(s, 'id')}>
                        {agriStr(s, 'system_code')} — {agriStr(s, 'name')}
                      </option>
                    ))
                  )}
                </NativeSelect>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-cell-code">
                  cell_code
                </label>
                <Input
                  id="mf-cell-code"
                  value={newCellCode}
                  onChange={(e) => setNewCellCode(e.target.value)}
                  disabled={cellSubmitting}
                  autoComplete="off"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-cell-name">
                  Name
                </label>
                <Input
                  id="mf-cell-name"
                  value={newCellName}
                  onChange={(e) => setNewCellName(e.target.value)}
                  disabled={cellSubmitting}
                  autoComplete="off"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-cell-cap">
                  capacity_kg (optional)
                </label>
                <Input
                  id="mf-cell-cap"
                  value={newCellCap}
                  onChange={(e) => setNewCellCap(e.target.value)}
                  disabled={cellSubmitting}
                  inputMode="decimal"
                  autoComplete="off"
                />
              </div>
              <Button type="button" disabled={cellSubmitting} onClick={() => void handleCreateSiloCell()}>
                {cellSubmitting ? 'Speichere…' : 'Silozelle anlegen'}
              </Button>
            </div>

            <div className="space-y-3 rounded-md border p-4">
              <h3 className="text-sm font-medium">Materialfluss-Knoten</h3>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-node-type">
                  node_type
                </label>
                <NativeSelect
                  id="mf-node-type"
                  value={newNodeType}
                  onChange={(e) => setNewNodeType(e.target.value)}
                  disabled={nodeSubmitting}
                >
                  {NODE_TYPE_OPTIONS.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </NativeSelect>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-node-code">
                  code
                </label>
                <Input
                  id="mf-node-code"
                  value={newNodeCode}
                  onChange={(e) => setNewNodeCode(e.target.value)}
                  disabled={nodeSubmitting}
                  autoComplete="off"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-node-name">
                  name
                </label>
                <Input
                  id="mf-node-name"
                  value={newNodeName}
                  onChange={(e) => setNewNodeName(e.target.value)}
                  disabled={nodeSubmitting}
                  autoComplete="off"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="mf-node-lx">
                    layout_x
                  </label>
                  <Input
                    id="mf-node-lx"
                    value={newNodeLayoutX}
                    onChange={(e) => setNewNodeLayoutX(e.target.value)}
                    disabled={nodeSubmitting}
                    inputMode="decimal"
                    autoComplete="off"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium" htmlFor="mf-node-ly">
                    layout_y
                  </label>
                  <Input
                    id="mf-node-ly"
                    value={newNodeLayoutY}
                    onChange={(e) => setNewNodeLayoutY(e.target.value)}
                    disabled={nodeSubmitting}
                    inputMode="decimal"
                    autoComplete="off"
                  />
                </div>
              </div>
              <Button type="button" disabled={nodeSubmitting} onClick={() => void handleCreateFlowNode()}>
                {nodeSubmitting ? 'Speichere…' : 'Knoten anlegen'}
              </Button>
            </div>

            <div className="space-y-3 rounded-md border p-4">
              <h3 className="text-sm font-medium">Materialfluss-Kante</h3>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-edge-from">
                  von_node_id
                </label>
                <NativeSelect
                  id="mf-edge-from"
                  value={edgeFromId}
                  onChange={(e) => setEdgeFromId(e.target.value)}
                  disabled={edgeSubmitting || nodesQ.isLoading}
                >
                  <option value="">— wählen —</option>
                  {(nodesQ.data ?? []).map((n) => (
                    <option key={`ef-${agriStr(n, 'id')}`} value={agriStr(n, 'id')}>
                      {agriStr(n, 'code')}
                    </option>
                  ))}
                </NativeSelect>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium" htmlFor="mf-edge-to">
                  nach_node_id
                </label>
                <NativeSelect
                  id="mf-edge-to"
                  value={edgeToId}
                  onChange={(e) => setEdgeToId(e.target.value)}
                  disabled={edgeSubmitting || nodesQ.isLoading}
                >
                  <option value="">— wählen —</option>
                  {(nodesQ.data ?? []).map((n) => (
                    <option key={`et-${agriStr(n, 'id')}`} value={agriStr(n, 'id')}>
                      {agriStr(n, 'code')}
                    </option>
                  ))}
                </NativeSelect>
              </div>
              <Button type="button" disabled={edgeSubmitting} onClick={() => void handleCreateFlowEdge()}>
                {edgeSubmitting ? 'Speichere…' : 'Kante anlegen'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{flowCardTitle}</CardTitle>
          {!warehouseId ? (
            <CardDescription>Wählen Sie ein Lager, um Live-Knoten und Kanten aus der API zu laden.</CardDescription>
          ) : hasLiveGraphData ? (
            <CardDescription>
              Positionen aus <code className="text-xs">layout_x</code>/<code className="text-xs">layout_y</code> oder
              deterministischen Raster.
            </CardDescription>
          ) : graphReady ? (
            <CardDescription>
              Noch keine Stammdaten — unten anlegen oder anderes Lager wählen. Demo bleibt nur ohne Lagerwahl sichtbar.
            </CardDescription>
          ) : null}
        </CardHeader>
        <CardContent className="h-[520px] min-h-[400px] rounded-md border bg-muted/20 p-0 overflow-hidden">
          <ReactFlow
            key={warehouseId || 'demo'}
            nodes={displayNodes}
            edges={displayEdges}
            nodeTypes={nodeTypes}
            fitView
            className="bg-muted/10"
          >
            <Background gap={16} />
            <MiniMap pannable zoomable className="!bg-card/95 !border-border" />
            <Controls className="!bg-card !border-border !shadow-md" />
            {warehouseId && graphLoading ? (
              <Panel position="top-center" className="rounded-md bg-card/95 border px-3 py-2 text-sm shadow">
                Lade Graph …
              </Panel>
            ) : null}
            {warehouseId && graphError ? (
              <Panel
                position="top-center"
                className="rounded-md bg-destructive/10 border border-destructive/40 px-3 py-2 text-sm shadow"
              >
                API-Fehler — Endpunkte oder Migration prüfen.
              </Panel>
            ) : null}
            {warehouseId && graphReady && !hasLiveGraphData ? (
              <Panel
                position="top-center"
                className="rounded-md bg-card/95 border px-3 py-2 text-sm shadow max-w-md text-center"
              >
                Keine Knoten/Kanten. Stammdaten-Anlage nutzen oder Lager wechseln.
              </Panel>
            ) : null}
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
                    <th className="py-2 pr-2">kg</th>
                    <th className="py-2 pr-2 min-w-[160px]">Layout (Hof/Plan)</th>
                    <th className="py-2 pr-2 min-w-[200px]">Material / Lot (Referenz)</th>
                  </tr>
                </thead>
                <tbody>
                  {siloQ.isLoading ? (
                    <tr>
                      <td colSpan={6} className="py-3 text-muted-foreground">
                        Lade…
                      </td>
                    </tr>
                  ) : (siloQ.data ?? []).length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-3 text-muted-foreground">
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
                            disabled={siloCellsTableBusy}
                            onPatch={handlePatchSiloQs}
                          />
                        </td>
                        <td className="py-2 tabular-nums">{agriStr(row, 'capacity_kg')}</td>
                        <td className="py-2 pr-2 align-top">
                          <NodeLayoutEditor
                            nodeId={agriStr(row, 'id')}
                            layoutXServer={agriStr(row, 'layout_x')}
                            layoutYServer={agriStr(row, 'layout_y')}
                            disabled={siloCellsTableBusy}
                            saving={siloLayoutSavingCellId === agriStr(row, 'id')}
                            onSave={handlePatchSiloLayout}
                          />
                        </td>
                        <td className="py-2 pr-0 align-top">
                          <SiloCellInventoryEditor
                            cellId={agriStr(row, 'id')}
                            materialServer={agriStr(row, 'current_material_id')}
                            lotServer={agriStr(row, 'current_lot_id')}
                            disabled={siloCellsTableBusy}
                            saving={inventorySavingCellId === agriStr(row, 'id')}
                            onSave={handlePatchSiloInventory}
                          />
                        </td>
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
                      <th className="py-2 pr-2">Status</th>
                      <th className="py-2 pr-2 min-w-[180px]">Layout (React Flow)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nodesQ.isLoading ? (
                      <tr>
                        <td colSpan={4} className="py-2 text-muted-foreground">
                          Lade…
                        </td>
                      </tr>
                    ) : (nodesQ.data ?? []).length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-2 text-muted-foreground">
                          Keine Knoten
                        </td>
                      </tr>
                    ) : (
                      (nodesQ.data ?? []).map((row) => (
                        <tr key={agriStr(row, 'id')} className="border-b border-border/60">
                          <td className="py-2 pr-2 font-mono text-xs">{agriStr(row, 'code')}</td>
                          <td className="py-2 pr-2">{agriStr(row, 'node_type')}</td>
                          <td className="py-2 pr-2 align-top">
                            <FlowNodeStatusSelect
                              nodeId={agriStr(row, 'id')}
                              warehouseId={warehouseId}
                              statusValue={agriStr(row, 'status')}
                              disabled={patchingNodeId !== null}
                              onPatch={handlePatchNodeStatus}
                            />
                          </td>
                          <td className="py-2 pr-0 align-top">
                            <NodeLayoutEditor
                              nodeId={agriStr(row, 'id')}
                              layoutXServer={agriStr(row, 'layout_x')}
                              layoutYServer={agriStr(row, 'layout_y')}
                              disabled={patchingNodeId !== null}
                              saving={patchingNodeId === agriStr(row, 'id')}
                              onSave={handlePatchNodeLayout}
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
                      <th className="py-2 pr-2">Status</th>
                      <th className="py-2 pr-2">Verschleppung</th>
                      <th className="py-2 pr-2">Spülcharge</th>
                    </tr>
                  </thead>
                  <tbody>
                    {edgesQ.isLoading ? (
                      <tr>
                        <td colSpan={5} className="py-2 text-muted-foreground">
                          Lade…
                        </td>
                      </tr>
                    ) : (edgesQ.data ?? []).length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-2 text-muted-foreground">
                          Keine Kanten
                        </td>
                      </tr>
                    ) : (
                      (edgesQ.data ?? []).map((row) => {
                        const raw = row['contamination_guard_enabled']
                        const guardOn =
                          raw === true ||
                          raw === 'true' ||
                          String(raw).toLowerCase() === 't' ||
                          String(raw) === '1'
                        const fraw = row['flush_required']
                        const flushOn =
                          fraw === true ||
                          fraw === 'true' ||
                          String(fraw).toLowerCase() === 't' ||
                          String(fraw) === '1'
                        const fromId = agriStr(row, 'from_node_id')
                        const toId = agriStr(row, 'to_node_id')
                        const fromCode = nodeCodeById.get(fromId) ?? '—'
                        const toCode = nodeCodeById.get(toId) ?? '—'
                        return (
                          <tr key={agriStr(row, 'id')} className="border-b border-border/60">
                            <td className="py-2 pr-2 align-top">
                              <div className="font-mono text-xs font-medium">{fromCode}</div>
                              <div className="text-[10px] text-muted-foreground font-mono break-all max-w-[140px]">
                                {fromId}
                              </div>
                            </td>
                            <td className="py-2 pr-2 align-top">
                              <div className="font-mono text-xs font-medium">{toCode}</div>
                              <div className="text-[10px] text-muted-foreground font-mono break-all max-w-[140px]">
                                {toId}
                              </div>
                            </td>
                            <td className="py-2 pr-2 align-top">
                              <FlowEdgeStatusSelect
                                edgeId={agriStr(row, 'id')}
                                warehouseId={warehouseId}
                                statusValue={agriStr(row, 'status')}
                                disabled={patchingEdgeId !== null}
                                onPatch={handlePatchEdgeStatus}
                              />
                            </td>
                            <td className="py-2 pr-2 align-top">
                              <FlowEdgeContaminationSelect
                                edgeId={agriStr(row, 'id')}
                                guardEnabled={guardOn}
                                disabled={patchingEdgeId !== null}
                                onPatch={handlePatchEdgeContamination}
                              />
                            </td>
                            <td className="py-2 pr-0 align-top">
                              <FlowEdgeFlushSelect
                                edgeId={agriStr(row, 'id')}
                                flushRequired={flushOn}
                                disabled={patchingEdgeId !== null}
                                onPatch={handlePatchEdgeFlush}
                              />
                            </td>
                          </tr>
                        )
                      })
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
