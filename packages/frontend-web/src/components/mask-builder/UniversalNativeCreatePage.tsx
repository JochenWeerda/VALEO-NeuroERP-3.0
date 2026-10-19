import { useEffect, useMemo, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'
import { apiClient } from '@/lib/api-client'
import { UniversalMaskRenderer } from './UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from './render-plan/schema-compiler'
import { useUniversalFormState } from './runtime/useUniversalFormState'
import { useScreenPermissions } from './runtime/screen-permissions'
import type { ScreenDefinition } from './schema'
import { prepareDocflowCreation } from './runtime/docflow-create-input'

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
      fields: original.creation?.fields ?? original.fields,
      tabs: original.creation?.fields ? [] : (original.tabs ?? []).filter(tab => (tab.fields ?? []).length > 0).map(tab => ({
        ...tab, dataSourceKey: undefined, tables: [], lazy: false,
      })),
    }
  }, [original])
  const canCreate = Boolean(original?.creation && permissions.includes(original.creation.permission))
  const intentRef = useRef<{ signature: string; key: string } | null>(null)
  const destinationRef = useRef<string | null>(null)
  const form = useUniversalFormState({
    screen,
    initialValues: original?.creation?.defaults,
    onSubmit: async values => {
      if (!original?.creation || !canCreate) throw new Error('Keine Berechtigung zur Anlage.')
      const fields = original.creation.fields ?? [...(original.fields ?? []), ...(original.tabs ?? []).flatMap(tab => tab.fields ?? [])]
      const allowed = new Set(fields.filter(field => !field.readOnly).map(field => field.key))
      let payload = Object.fromEntries(Object.entries({ ...original.creation.defaults, ...values })
        .filter(([key, value]) => allowed.has(key) && value !== undefined && value !== ''))
      if (original.creation.adapter === 'docflow.create.v1') {
        const signature = JSON.stringify([screenId, original.documentVariant, original.creationContext, payload])
        if (intentRef.current?.signature !== signature) intentRef.current = { signature, key: crypto.randomUUID() }
        payload = prepareDocflowCreation(original, payload, intentRef.current.key)
      }
      const response = await apiClient.post<{ id: string; doc_type?: string; status?: string; version?: number; screen_context?: { screen_id: string; definition_hash: string } }>(original.creation.endpoint, payload)
      if (!response.data?.id) throw new Error('Anlageantwort enthält keine Datensatz-ID.')
      if (original.creation.adapter === 'docflow.create.v1' && (response.data.doc_type !== original.documentVariant?.variantId ||
        response.data.status !== 'draft' || response.data.version !== 1 ||
        response.data.screen_context?.screen_id !== original.id ||
        response.data.screen_context?.definition_hash !== original.creationContext?.definition_hash)) {
        throw new Error('Anlageantwort entspricht nicht dem geprueften Belegauftrag.')
      }
      destinationRef.current = original.creation.detailRoute.replace('{entity_id}', encodeURIComponent(response.data.id))
    },
  })
  useEffect(() => {
    // Navigate after the successful form commit has removed the unsaved-changes guard.
    if (form.submitState !== 'success' || form.dirtyState.isDirty || !destinationRef.current) return
    const destination = destinationRef.current
    destinationRef.current = null
    navigate(destination)
  }, [form.submitState, form.dirtyState.isDirty, navigate])
  const initialized = useRef<string>()
  useEffect(() => {
    if (original?.creation && initialized.current !== screenId) {
      form.resetForm(original.creation.defaults ?? {})
      initialized.current = screenId
    }
  }, [original, screenId, form.resetForm])
  const plan = useMemo(() => screen ? compileRenderPlanFromScreenDefinition(screen, { permissions }) : undefined,
    [screen, permissions])
  const lookupBindings = useMemo(() => Object.fromEntries((original?.creation?.fields ?? [])
    .filter(field => field.type === 'lookup' && field.dataSourceKey)
    .map(field => [field.key, { fieldKey: field.key,
      lookupEndpoint: original?.creation?.dataSources?.find(source => source.key === field.dataSourceKey)?.endpoint ?? '',
      minSearchChars: 2, resultLimit: 25, cacheTtlMs: 0, debounceMs: 300 }])), [original])

  if (schemaQuery.isError) return <p role="alert">Die Anlagemaske konnte nicht geladen werden.</p>
  if (!original) return <p role="status">Anlagemaske wird geladen…</p>
  if (!original.creation) return <p role="alert">Für diese Maske ist keine Neuanlage freigegeben.</p>
  if (!canCreate) return <p role="alert">Keine Berechtigung zur Anlage.</p>
  return (
    <div data-testid={testId}>
      <UniversalMaskRenderer plan={plan} formState={form} allowedPermissions={permissions} lookupBindings={lookupBindings} />
    </div>
  )
}
