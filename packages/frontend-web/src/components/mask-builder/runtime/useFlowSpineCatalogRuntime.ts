import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useFlowSpineCatalogHook, warmFlowSpineCache, type FlowSpineCatalog } from '@/lib/api/flow-spines'

export interface FlowSpineCatalogState {
  catalog?: FlowSpineCatalog
  loading: boolean
  failed: boolean
  retry: () => void
}

/** One registered read adapter; no domain writes or arbitrary endpoints. */
export function useFlowSpineCatalogRuntime(enabled: boolean, warm: boolean): FlowSpineCatalogState {
  const queryClient = useQueryClient()
  const { i18n } = useTranslation()
  const language = i18n.resolvedLanguage ?? i18n.language ?? 'de'
  const query = useFlowSpineCatalogHook({ enabled })
  useEffect(() => {
    if (enabled && warm && query.isSuccess) return warmFlowSpineCache(queryClient, language)
    return undefined
  }, [enabled, warm, query.isSuccess, queryClient, language])
  return { catalog: query.data, loading: query.isLoading, failed: query.isError, retry: () => { void query.refetch() } }
}
