/**
 * WMS unter `/api/v1/lager/wms` — Zonen, Gänge, Lagerplätze (Bins).
 * Antworten sind tenant-isoliert; Backend nutzt lose Dicts (extra fields).
 */

import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '../api-client'

export type WmsRow = Record<string, unknown>

export const warehouseWmsKeys = {
  all: ['lager', 'wms'] as const,
  zones: (warehouseId: string) => [...warehouseWmsKeys.all, 'zones', warehouseId] as const,
  aisles: (zoneId: string) => [...warehouseWmsKeys.all, 'aisles', zoneId] as const,
  bins: (params: { warehouse_id: string; zone_id: string; aisle_id: string }) =>
    [...warehouseWmsKeys.all, 'bins', params] as const,
}

export type WmsBinPatch = {
  bin_type?: string
  capacity_kg?: number | string | null
  is_blocked?: boolean
  block_reason?: string | null
  aisle_id?: string | null
}

function asList(data: unknown): WmsRow[] {
  return Array.isArray(data) ? (data as WmsRow[]) : []
}

export function wmsStr(row: WmsRow, key: string): string {
  const v = row[key]
  return v == null ? '' : String(v)
}

export async function fetchWmsZones(warehouseId: string): Promise<WmsRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/zones', {
    params: { warehouse_id: warehouseId },
  })
  return asList(data)
}

export async function fetchWmsAisles(zoneId: string): Promise<WmsRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/aisles', {
    params: { zone_id: zoneId },
  })
  return asList(data)
}

export async function patchWmsBin(binId: string, body: WmsBinPatch): Promise<WmsRow> {
  const { data } = await apiClient.patch<unknown>(`/api/v1/lager/wms/bins/${binId}`, body)
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    return data as WmsRow
  }
  return {}
}

export async function fetchWmsBins(params: {
  warehouse_id: string
  zone_id?: string
  aisle_id?: string
  only_active?: boolean
}): Promise<WmsRow[]> {
  const { data } = await apiClient.get<unknown>('/api/v1/lager/wms/bins', {
    params: {
      warehouse_id: params.warehouse_id,
      zone_id: params.zone_id,
      aisle_id: params.aisle_id,
      only_active: params.only_active ?? true,
    },
  })
  return asList(data)
}

export function useWmsZones(warehouseId: string | undefined, options?: { enabled?: boolean }) {
  const wid = warehouseId ?? ''
  return useQuery({
    queryKey: warehouseWmsKeys.zones(wid),
    queryFn: () => fetchWmsZones(wid),
    enabled: Boolean(wid) && (options?.enabled ?? true),
    staleTime: 30_000,
  })
}

export function useWmsBins(
  params: { warehouse_id: string | undefined; zone_id?: string; aisle_id?: string },
  options?: { enabled?: boolean },
) {
  const wid = params.warehouse_id ?? ''
  const keyParams = {
    warehouse_id: wid,
    zone_id: params.zone_id ?? '',
    aisle_id: params.aisle_id ?? '',
  }
  return useQuery({
    queryKey: warehouseWmsKeys.bins(keyParams),
    queryFn: () =>
      fetchWmsBins({
        warehouse_id: wid,
        zone_id: params.zone_id,
        aisle_id: params.aisle_id,
      }),
    enabled: Boolean(wid) && (options?.enabled ?? true),
    staleTime: 30_000,
  })
}

/** Pro Zone ein Gänge-Abruf (parallel über useQueries). */
export function useWmsAislesForZones(zoneIds: string[], enabled: boolean) {
  return useQueries({
    queries: zoneIds.map((zoneId) => ({
      queryKey: warehouseWmsKeys.aisles(zoneId),
      queryFn: () => fetchWmsAisles(zoneId),
      enabled: enabled && zoneIds.length > 0,
      staleTime: 30_000,
    })),
  })
}

export function usePatchWmsBin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ binId, body }: { binId: string; body: WmsBinPatch }) => patchWmsBin(binId, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: warehouseWmsKeys.all })
    },
  })
}

// ── Pick-Listen (WMS-PICK-LINK-001) ────────────────────────────────────────

export type PickListLine = {
  id: string
  pick_list_id: string
  article_id: string
  bin_id: string | null
  bin_code?: string | null
  batch_number: string | null
  best_before_date: string | null
  quantity_required: number
  quantity_picked: number
  unit: string
  status: string
  sort_order: number
}

export type PickList = {
  id: string
  tenant_id?: string
  warehouse_id: string | null
  source_doc_ref: string | null
  source_doc_type: string | null
  status: string
  strategy: string
  created_by: string | null
  created_at?: string | null
  completed_at?: string | null
  delivery_note_id?: string | null
  delivery_note_number?: string | null
  lines?: PickListLine[]
}

export const pickListKeys = {
  all: ['lager', 'wms', 'pick-lists'] as const,
  detail: (id: string) => [...pickListKeys.all, id] as const,
  forDeliveryNote: (lsId: string) => [...pickListKeys.all, 'dn', lsId] as const,
}

export async function fetchPickList(pickListId: string): Promise<PickList> {
  const { data } = await apiClient.get<PickList>(`/api/v1/lager/wms/pick-lists/${pickListId}`)
  return data
}

export async function fetchPickLists(params?: { source_doc_ref?: string }): Promise<PickList[]> {
  const { data } = await apiClient.get<PickList[]>('/api/v1/lager/wms/pick-lists', {
    params,
  })
  return Array.isArray(data) ? data : []
}

export async function createPickListFromDeliveryNote(
  lsId: string,
  payload: { warehouse_id?: string | null; strategy?: string; created_by?: string },
): Promise<PickList> {
  const { data } = await apiClient.post<PickList>(
    `/api/v1/lager/wms/pick-lists/from-delivery-note/${encodeURIComponent(lsId)}`,
    {
      warehouse_id: payload.warehouse_id ?? null,
      strategy: payload.strategy ?? 'FEFO',
      created_by: payload.created_by ?? null,
    },
  )
  return data
}

export async function confirmPickList(
  pickListId: string,
  pickedLines: Array<{ line_id: string; quantity_picked: number }>,
): Promise<{ pick_list_id: string; status: string }> {
  const { data } = await apiClient.post<{ pick_list_id: string; status: string }>(
    `/api/v1/lager/wms/pick-lists/${encodeURIComponent(pickListId)}/confirm`,
    { picked_lines: pickedLines },
  )
  return data
}

export function usePickList(pickListId: string | null) {
  return useQuery({
    queryKey: pickListKeys.detail(pickListId ?? ''),
    queryFn: () => fetchPickList(pickListId ?? ''),
    enabled: Boolean(pickListId),
    staleTime: 15_000,
  })
}

export function useCreatePickListFromDeliveryNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      lsId,
      payload,
    }: {
      lsId: string
      payload: { warehouse_id?: string | null; strategy?: string; created_by?: string }
    }) => createPickListFromDeliveryNote(lsId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: pickListKeys.all })
    },
  })
}

export function useConfirmPickList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      pickListId,
      pickedLines,
    }: {
      pickListId: string
      pickedLines: Array<{ line_id: string; quantity_picked: number }>
    }) => confirmPickList(pickListId, pickedLines),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: pickListKeys.all })
    },
  })
}

// ── Bestandsbewertung ─────────────────────────────────────────────────────

export type StockValuationRow = {
  article_id: string
  batch_number: string | null
  total_quantity_kg: number
  total_value_eur: number
  avg_cost_per_kg: number
}

export const stockValuationKeys = {
  all: ['lager', 'wms', 'stock-valuation'] as const,
  byWarehouse: (warehouseId?: string) =>
    [...stockValuationKeys.all, warehouseId ?? 'all'] as const,
}

export async function fetchStockValuation(warehouseId?: string): Promise<StockValuationRow[]> {
  const params = warehouseId ? `?warehouse_id=${encodeURIComponent(warehouseId)}` : ''
  const res = await apiClient.get<StockValuationRow[] | { items?: StockValuationRow[] }>(`/api/v1/lager/wms/stock-valuation${params}`)
  const payload = res.data
  if (Array.isArray(payload)) return payload
  if (payload && Array.isArray(payload.items)) return payload.items
  return []
}

export function useStockValuation(warehouseId?: string) {
  return useQuery({
    queryKey: stockValuationKeys.byWarehouse(warehouseId),
    queryFn: () => fetchStockValuation(warehouseId),
    staleTime: 60_000,
  })
}
