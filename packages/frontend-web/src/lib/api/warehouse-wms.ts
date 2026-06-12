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
