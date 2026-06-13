/**
 * Agrar-Silo / Materialfluss unter `/api/v1/lager/wms/agri` (WM-AGRI-SILO-001).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '../api-client'

export type AgriFlowRow = Record<string, unknown>

export type SiloCellPatch = {
  qs_status?: string
  name?: string
  capacity_kg?: string | number | null
  current_material_id?: string | null
  current_lot_id?: string | null
  contamination_risk_class?: string | null
  layout_x?: string | number | null
  layout_y?: string | number | null
}

export type MaterialFlowNodePatch = {
  status?: string
  name?: string
  ref_type?: string | null
  ref_id?: string | null
  geo_lat?: string | number | null
  geo_lng?: string | number | null
  layout_x?: string | number | null
  layout_y?: string | number | null
}

export type MaterialFlowEdgePatch = {
  status?: string
  conveyor_type?: string
  contamination_guard_enabled?: boolean
  flush_required?: boolean
  max_capacity_kg_h?: string | number | null
}

export type ValidateAgriRouteBody = {
  warehouse_id: string
  from_node_id: string
  to_node_id: string
  material_id?: string | null
  previous_material_id?: string | null
}

export const agriMaterialFlowKeys = {
  all: ['lager', 'wms', 'agri'] as const,
  siloCells: (warehouseId: string) => [...agriMaterialFlowKeys.all, 'silo-cells', warehouseId] as const,
  nodes: (warehouseId: string) => [...agriMaterialFlowKeys.all, 'nodes', warehouseId] as const,
  edges: (warehouseId: string) => [...agriMaterialFlowKeys.all, 'edges', warehouseId] as const,
}

function asList(data: unknown): AgriFlowRow[] {
  return Array.isArray(data) ? (data as AgriFlowRow[]) : []
}

export async function fetchAgriSiloCells(warehouseId: string): Promise<AgriFlowRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/agri/silo-cells', {
    params: { warehouse_id: warehouseId },
  })
  return asList(data)
}

export async function fetchAgriFlowNodes(warehouseId: string): Promise<AgriFlowRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/agri/material-flow/nodes', {
    params: { warehouse_id: warehouseId },
  })
  return asList(data)
}

export async function fetchAgriFlowEdges(warehouseId: string): Promise<AgriFlowRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/agri/material-flow/edges', {
    params: { warehouse_id: warehouseId },
  })
  return asList(data)
}

export async function patchAgriSiloCell(
  cellId: string,
  warehouseId: string,
  body: SiloCellPatch,
): Promise<AgriFlowRow> {
  const { data } = await apiClient.patch<unknown>(`/api/v1/lager/wms/agri/silo-cells/${cellId}`, body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function patchAgriFlowNode(
  nodeId: string,
  warehouseId: string,
  body: MaterialFlowNodePatch,
): Promise<AgriFlowRow> {
  const { data } = await apiClient.patch<unknown>(`/api/v1/lager/wms/agri/material-flow/nodes/${nodeId}`, body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function patchAgriFlowEdge(
  edgeId: string,
  warehouseId: string,
  body: MaterialFlowEdgePatch,
): Promise<AgriFlowRow> {
  const { data } = await apiClient.patch<unknown>(`/api/v1/lager/wms/agri/material-flow/edges/${edgeId}`, body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function validateAgriMaterialRoute(body: ValidateAgriRouteBody): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/material-flow/validate-route', body)
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export function useAgriSiloCells(warehouseId: string | undefined, options?: { enabled?: boolean }) {
  const wid = warehouseId ?? ''
  return useQuery({
    queryKey: agriMaterialFlowKeys.siloCells(wid),
    queryFn: () => fetchAgriSiloCells(wid),
    enabled: Boolean(wid) && (options?.enabled ?? true),
  })
}

export function useAgriFlowNodes(warehouseId: string | undefined, options?: { enabled?: boolean }) {
  const wid = warehouseId ?? ''
  return useQuery({
    queryKey: agriMaterialFlowKeys.nodes(wid),
    queryFn: () => fetchAgriFlowNodes(wid),
    enabled: Boolean(wid) && (options?.enabled ?? true),
  })
}

export function useAgriFlowEdges(warehouseId: string | undefined, options?: { enabled?: boolean }) {
  const wid = warehouseId ?? ''
  return useQuery({
    queryKey: agriMaterialFlowKeys.edges(wid),
    queryFn: () => fetchAgriFlowEdges(wid),
    enabled: Boolean(wid) && (options?.enabled ?? true),
  })
}

export function usePatchAgriSiloCell() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { cellId: string; warehouseId: string; body: SiloCellPatch }) =>
      patchAgriSiloCell(vars.cellId, vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.siloCells(vars.warehouseId) })
    },
  })
}

export function usePatchAgriFlowNode() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { nodeId: string; warehouseId: string; body: MaterialFlowNodePatch }) =>
      patchAgriFlowNode(vars.nodeId, vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.nodes(vars.warehouseId) })
    },
  })
}

export function usePatchAgriFlowEdge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { edgeId: string; warehouseId: string; body: MaterialFlowEdgePatch }) =>
      patchAgriFlowEdge(vars.edgeId, vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.edges(vars.warehouseId) })
    },
  })
}

export function agriStr(row: AgriFlowRow, key: string): string {
  const v = row[key]
  return v == null ? '' : String(v)
}
