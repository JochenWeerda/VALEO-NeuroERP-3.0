import { useQuery, type QueryKey } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { ScreenOverlay } from '@/components/mask-builder/render-plan/overlay'

export interface UserScreenOverlay {
  screen_id: string
  schema_version?: number | null
  overlay: ScreenOverlay
  updated_at?: string | null
}

export interface OverlayPutInput {
  schema_version: number
  overlay: ScreenOverlay
}

export const overlayKeys = {
  all: ['ux-overlays'] as const,
  screen: (screenId: string): QueryKey => [...overlayKeys.all, screenId] as const,
}

function overlayPath(screenId: string): string {
  return screenId.split('/').map(encodeURIComponent).join('/')
}

export async function fetchUserOverlay(screenId: string): Promise<UserScreenOverlay> {
  const response = await apiClient.get<UserScreenOverlay>(`/api/v1/ux/overlays/${overlayPath(screenId)}`)
  return response.data
}

export async function saveUserOverlay(screenId: string, input: OverlayPutInput): Promise<UserScreenOverlay> {
  const response = await apiClient.put<UserScreenOverlay, OverlayPutInput>(
    `/api/v1/ux/overlays/${overlayPath(screenId)}`,
    input,
  )
  return response.data
}

export async function deleteUserOverlay(screenId: string): Promise<void> {
  await apiClient.delete<void>(`/api/v1/ux/overlays/${overlayPath(screenId)}`)
}

export function useUserScreenOverlay(screenId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: overlayKeys.screen(screenId),
    queryFn: () => fetchUserOverlay(screenId),
    enabled: Boolean(screenId) && (options?.enabled ?? true),
    staleTime: 30_000,
  })
}
