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
  legacy_silo_id?: string | null
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

export type MaterialTransferBody = {
  warehouse_id: string
  from_cell_id: string
  to_cell_id: string
  quantity_kg: string | number
  article_id: string
  lot_id?: string | null
  booked_by?: string | null
  reference?: string | null
}

export type SiloSystemCreate = {
  system_code: string
  name: string
  description?: string | null
}

export type SiloCellCreate = {
  cell_code: string
  name: string
  capacity_kg?: string | number | null
  zone_id?: string | null
  aisle_id?: string | null
  bin_id?: string | null
  current_material_id?: string | null
  current_lot_id?: string | null
  qs_status?: string
  contamination_risk_class?: string | null
}

export type MaterialFlowNodeCreate = {
  node_type: string
  code: string
  name: string
  ref_type?: string | null
  ref_id?: string | null
  status?: string
  geo_lat?: string | number | null
  geo_lng?: string | number | null
  layout_x?: string | number | null
  layout_y?: string | number | null
}

export type MaterialFlowEdgeCreate = {
  from_node_id: string
  to_node_id: string
  conveyor_type?: string
  status?: string
  contamination_guard_enabled?: boolean
  flush_required?: boolean
  max_capacity_kg_h?: string | number | null
}

export const agriMaterialFlowKeys = {
  all: ['lager', 'wms', 'agri'] as const,
  siloSystems: (warehouseId: string) => [...agriMaterialFlowKeys.all, 'silo-systems', warehouseId] as const,
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

export async function fetchAgriSiloSystems(warehouseId: string): Promise<AgriFlowRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/agri/silo-systems', {
    params: { warehouse_id: warehouseId },
  })
  return asList(data)
}

export async function createAgriSiloSystem(warehouseId: string, body: SiloSystemCreate): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/silo-systems', body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function createAgriSiloCell(
  siloSystemId: string,
  warehouseId: string,
  body: SiloCellCreate,
): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/silo-cells', body, {
    params: { silo_system_id: siloSystemId, warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function createAgriFlowNode(warehouseId: string, body: MaterialFlowNodeCreate): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/material-flow/nodes', body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function createAgriFlowEdge(warehouseId: string, body: MaterialFlowEdgeCreate): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/material-flow/edges', body, {
    params: { warehouse_id: warehouseId },
  })
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
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

export async function bookAgriMaterialTransfer(body: MaterialTransferBody): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>('/api/v1/lager/wms/agri/material-flow/transfer', body)
  return (data && typeof data === 'object' ? data : {}) as AgriFlowRow
}

export async function syncAgriSiloCellFromLots(cellId: string, warehouseId: string): Promise<AgriFlowRow> {
  const { data } = await apiClient.post<unknown>(
    `/api/v1/lager/wms/agri/silo-cells/${cellId}/sync-from-lots`,
    null,
    { params: { warehouse_id: warehouseId } },
  )
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

export function useAgriSiloSystems(warehouseId: string | undefined, options?: { enabled?: boolean }) {
  const wid = warehouseId ?? ''
  return useQuery({
    queryKey: agriMaterialFlowKeys.siloSystems(wid),
    queryFn: () => fetchAgriSiloSystems(wid),
    enabled: Boolean(wid) && (options?.enabled ?? true),
  })
}

export function useCreateAgriSiloSystem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { warehouseId: string; body: SiloSystemCreate }) =>
      createAgriSiloSystem(vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.siloSystems(vars.warehouseId) })
    },
  })
}

export function useCreateAgriSiloCell() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { siloSystemId: string; warehouseId: string; body: SiloCellCreate }) =>
      createAgriSiloCell(vars.siloSystemId, vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.siloCells(vars.warehouseId) })
    },
  })
}

export function useCreateAgriFlowNode() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { warehouseId: string; body: MaterialFlowNodeCreate }) =>
      createAgriFlowNode(vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.nodes(vars.warehouseId) })
    },
  })
}

export function useCreateAgriFlowEdge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { warehouseId: string; body: MaterialFlowEdgeCreate }) =>
      createAgriFlowEdge(vars.warehouseId, vars.body),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.edges(vars.warehouseId) })
    },
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

export function useBookAgriMaterialTransfer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: bookAgriMaterialTransfer,
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.siloCells(vars.warehouse_id) })
    },
  })
}

export function useSyncAgriSiloCellFromLots() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { cellId: string; warehouseId: string }) =>
      syncAgriSiloCellFromLots(vars.cellId, vars.warehouseId),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: agriMaterialFlowKeys.siloCells(vars.warehouseId) })
    },
  })
}

export function agriStr(row: AgriFlowRow, key: string): string {
  const v = row[key]
  return v == null ? '' : String(v)
}
