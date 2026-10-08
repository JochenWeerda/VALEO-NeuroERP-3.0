import { useEffect, useMemo, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'
import { apiClient } from '@/lib/api-client'
import { UniversalMaskRenderer } from './UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from './render-plan/schema-compiler'
import { useUniversalFormState } from './runtime/useUniversalFormState'
import { useScreenPermissions } from './runtime/screen-permissions'
import type { ScreenDefinition } from './schema'

/** Creation stays in the native ScreenDefinition/RenderPlan/form-state chain. */
export function UniversalNativeCreatePage({ screenId, testId }: { screenId: string; testId?: string }): JSX.Element {
  const navigate = useNavigate()
  const schemaQuery = useScreenDefinition(screenId)
  const original = schemaQuery.data
  const permissions = useScreenPermissions(original)
  const screen = useMemo<ScreenDefinition | undefined>(() => {
    if (!original) return undefined
    // Unsaved entities have no related registers, lifecycle actions or live totals.
    return {
      ...original,
      dataSources: [],
      actions: [],
      summary: [],
      tabs: (original.tabs ?? []).filter(tab => (tab.fields ?? []).length > 0).map(tab => ({
        ...tab, dataSourceKey: undefined, tables: [], lazy: false,
      })),
    }
  }, [original])
  const canCreate = Boolean(original?.creation && permissions.includes(original.creation.permission))
  const form = useUniversalFormState({
    screen,
    initialValues: original?.creation?.defaults,
    onSubmit: async values => {
      if (!original?.creation || !canCreate) throw new Error('Keine Berechtigung zur Anlage.')
      const fields = [...(original.fields ?? []), ...(original.tabs ?? []).flatMap(tab => tab.fields ?? [])]
      const allowed = new Set(fields.filter(field => !field.readOnly).map(field => field.key))
      const payload = Object.fromEntries(Object.entries({ ...original.creation.defaults, ...values })
        .filter(([key, value]) => allowed.has(key) && value !== undefined && value !== ''))
      const response = await apiClient.post<{ id: string }>(original.creation.endpoint, payload)
      if (!response.data?.id) throw new Error('Anlageantwort enthält keine Datensatz-ID.')
      navigate(original.creation.detailRoute.replace('{entity_id}', encodeURIComponent(response.data.id)))
    },
  })
  const initialized = useRef<string>()
  useEffect(() => {
    if (original?.creation && initialized.current !== screenId) {
      form.resetForm(original.creation.defaults ?? {})
      initialized.current = screenId
    }
  }, [original, screenId, form.resetForm])
  const plan = useMemo(() => screen ? compileRenderPlanFromScreenDefinition(screen, { permissions }) : undefined,
    [screen, permissions])

  if (schemaQuery.isError) return <p role="alert">Die Anlagemaske konnte nicht geladen werden.</p>
  if (!original) return <p role="status">Anlagemaske wird geladen…</p>
  if (!original.creation) return <p role="alert">Für diese Maske ist keine Neuanlage freigegeben.</p>
  if (!canCreate) return <p role="alert">Keine Berechtigung zur Anlage.</p>
  return (
    <div data-testid={testId}>
      <UniversalMaskRenderer plan={plan} formState={form} allowedPermissions={permissions} />
    </div>
  )
}
