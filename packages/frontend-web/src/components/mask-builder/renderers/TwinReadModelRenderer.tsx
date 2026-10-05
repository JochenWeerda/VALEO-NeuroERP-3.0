import { memo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useNavigate } from '@/app/routing/typed-router'
import type { RenderTwinPlan } from '../render-plan/types'
import { TwinPanelRenderer } from './TwinPanelRenderer'
import type { TwinMetricDef, TwinPlan } from './twin-geometry'

type TwinReadModel = {
  plan: TwinPlan
  metrics?: TwinMetricDef[]
  cellData: Record<string, Record<string, unknown>>
  cellLinks?: Record<string, { route?: string; screen_id?: string }>
  updatedAt?: string
  cacheTtlSeconds?: number
}

function formatUpdated(value: string | undefined): string | undefined {
  if (!value) return undefined
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

function routeFromTemplate(template: string, cellId: string): string {
  return template.replace('{cellId}', encodeURIComponent(cellId))
}

export const TwinReadModelRenderer = memo(function TwinReadModelRenderer({
  twin,
  initialModel,
}: {
  twin?: RenderTwinPlan
  /** Test hook; production fetches from twin.endpoint. */
  initialModel?: TwinReadModel
}): JSX.Element | null {
  const navigate = useNavigate()
  const endpoint = twin?.endpoint
  const ttlMs = (twin?.cacheTtlSeconds ?? 30) * 1000

  const query = useQuery({
    queryKey: ['twin-read-model', endpoint],
    enabled: Boolean(endpoint) && !initialModel,
    queryFn: async () => {
      if (!endpoint) return undefined
      const response = await apiClient.get<TwinReadModel>(endpoint)
      return response.data
    },
    staleTime: ttlMs,
  })

  if (!twin) return null
  const model = initialModel ?? query.data

  if (!model?.plan) {
    return (
      <section data-testid="twin-read-model" className="rounded-md border bg-muted/20 p-3 text-sm text-muted-foreground">
        Twin-Daten werden geladen
      </section>
    )
  }

  const metrics = model.metrics && model.metrics.length > 0 ? model.metrics : twin.metrics

  return (
    <section data-testid="twin-read-model" data-twin-plan={twin.planId} className="space-y-2">
      <TwinPanelRenderer
        plan={model.plan}
        metrics={metrics}
        cellData={model.cellData ?? {}}
        updatedLabel={formatUpdated(model.updatedAt)}
        onCellActivate={(cellId) => {
          const route = model.cellLinks?.[cellId]?.route ?? routeFromTemplate(twin.activateRouteTemplate, cellId)
          if (route) navigate(route)
        }}
      />
    </section>
  )
})
