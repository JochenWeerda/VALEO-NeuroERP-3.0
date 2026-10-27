import { useEffect, useMemo, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'
import { apiClient } from '@/lib/api-client'
import { useAuth } from '@/hooks/useAuth'
import { getAccessToken } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { checkedInvoicePrefill, clearInboxPrefill, inboxPrefillToCreationValues, type InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import { UniversalMaskRenderer } from './UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from './render-plan/schema-compiler'
import { useUniversalFormState } from './runtime/useUniversalFormState'
import { useScreenPermissions } from './runtime/screen-permissions'
import type { ScreenDefinition } from './schema'
import { prepareDocflowCreation } from './runtime/docflow-create-input'

/** Creation stays in the native ScreenDefinition/RenderPlan/form-state chain. */
export function UniversalNativeCreatePage({ screenId, testId }: { screenId: string; testId?: string }): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const inboxId = searchParams.get('inbox')?.trim() || null
  const { user } = useAuth()
  // Cache isolation only. The authenticated backend remains the tenant authority.
  const tokenTenantId = inboxId ? tenantFromToken(getAccessToken()) : null
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
  const isInvoiceCreate = screenId === 'beleg/purchase-invoice' && original?.documentVariant?.variantId === 'purchase_invoice'
  const inboxQuery = useQuery({
    queryKey: ['native-create-inbox-prepare', user?.sub ?? null, tokenTenantId, screenId, inboxId],
    enabled: Boolean(inboxId && isInvoiceCreate && user?.sub && tokenTenantId && canCreate),
    queryFn: async () => {
      if (!inboxId) throw new Error('Inbox-ID fehlt.')
      const response = await apiClient.post<{ ok: boolean; booking_allowed: boolean; item: InboxQueueItem }>(
        `/api/mcp/documents/inbox/${encodeURIComponent(inboxId)}/prepare`, {},
      )
      return checkedInvoicePrefill(response.data, inboxId)
    },
    retry: false,
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: 'always',
    refetchOnWindowFocus: false,
  })
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
  const formContext = JSON.stringify([screenId, original?.creationContext?.definition_hash,
    original?.creation?.endpoint, inboxId, user?.sub, tokenTenantId])
  useEffect(() => {
    if (!original?.creation || initialized.current === formContext || (inboxId && (!inboxQuery.data || inboxQuery.isFetching))) return
    const defaults = original.creation.defaults ?? {}
    const allowed = new Set((original.creation.fields ?? [])
      .filter(field => !field.readOnly).map(field => field.key))
    const suggested = inboxId && inboxQuery.data ? inboxPrefillToCreationValues(inboxQuery.data) : {}
    const values = Object.fromEntries(Object.entries(suggested)
      .filter(([key, value]) => allowed.has(key) && value !== undefined && value !== ''))
    form.resetForm({ ...defaults, ...values })
    initialized.current = formContext
  }, [original, formContext, inboxId, inboxQuery.data, inboxQuery.isFetching, form.resetForm])
  useEffect(() => { clearInboxPrefill() }, [])
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
  if (inboxId && !isInvoiceCreate) return <p role="alert">Dieser Inbox-Vorschlag gehört nicht zu dieser Belegmaske.</p>
  if (inboxId && !user?.sub) return <p role="alert">Für den Inbox-Vorschlag ist eine Anmeldung erforderlich.</p>
  if (inboxId && !tokenTenantId) return <p role="alert">Der Mandant der Anmeldung konnte nicht geprüft werden.</p>
  if (inboxId && inboxQuery.isError) return <p role="alert">Der Inbox-Vorschlag konnte nicht geprüft werden.</p>
  if (inboxId && (!inboxQuery.data || inboxQuery.isFetching)) return <p role="status">Inbox-Vorschlag wird geprüft…</p>
  if (initialized.current !== formContext) return <p role="status">Anlagemaske wird vorbereitet…</p>
  return (
    <div data-testid={testId}>
      <UniversalMaskRenderer plan={plan} formState={form} allowedPermissions={permissions} lookupBindings={lookupBindings} />
    </div>
  )
}
