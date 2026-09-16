import { useMemo } from 'react'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useParams } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'

export default function StudioRunPage(): JSX.Element {
  const { screenId: rawScreenId } = useParams<{ screenId?: string }>()
  const screenId = (rawScreenId ?? '').replace(/__/g, '/')
  const schemaQuery = useScreenDefinition(screenId, { enabled: Boolean(screenId) })
  const plan = useMemo(
    () => (schemaQuery.data ? compileRenderPlanFromScreenDefinition(schemaQuery.data) : null),
    [schemaQuery.data],
  )

  if (!screenId) {
    return <p className="p-4 text-sm text-muted-foreground">Keine Studio-Maske angegeben.</p>
  }
  if (schemaQuery.isLoading) {
    return <p className="p-4 text-sm text-muted-foreground">Studio-Maske wird geladen…</p>
  }
  if (schemaQuery.isError || !schemaQuery.data || !plan) {
    return (
      <p className="p-4 text-sm text-destructive" role="alert">
        Freigegebene Studio-Maske nicht gefunden.
      </p>
    )
  }

  return (
    <div className="p-4" data-testid="studio-run" data-screen-id={screenId}>
      <UniversalMaskRenderer plan={plan} screen={schemaQuery.data} />
    </div>
  )
}
