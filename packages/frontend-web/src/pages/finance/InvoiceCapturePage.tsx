import { useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useNavigate } from '@/app/routing/typed-router'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

type Line = { article: string; qty: number; price: number; taxCode: string | null }
type TaxKey = { code: string; bezeichnung: string; steuersatz: number | string }
type TaxPreview = { geklaert: boolean; pruefgrund?: string | null; netto: number | string | null; steuer: number | string | null; brutto: number | string | null }
const str = (raw: unknown): string => String(raw ?? '').trim()
const num = (raw: unknown): number => Number(str(raw).replace(',', '.'))
const euro = (raw: unknown): string => raw == null ? 'offen' : Number(raw).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
function dateAfter(days: number): string {
  const day = new Date()
  day.setDate(day.getDate() + days)
  return `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
}

export function InvoiceCapturePage({ purchase }: { purchase: boolean }): JSX.Element {
  const id = purchase ? 'einkauf/rechnungseingang/neu' : 'finance/invoices/new'
  const query = useScreenDefinition(id)
  if (query.isLoading) return <p role="status">Rechnungserfassung wird geladen …</p>
  if (query.error || !query.data) return <p role="alert">Rechnungsvertrag konnte nicht geladen werden.</p>
  return <Workspace purchase={purchase} definition={query.data} />
}

function Workspace({ purchase, definition }: { purchase: boolean; definition: ScreenDefinition }): JSX.Element {
  const id = definition.id
  const navigate = useNavigate()
  const permissions = useScreenPermissions(definition)
  const [lines, setLines] = useState<Line[]>([])
  const [busy, setBusy] = useState(false)
  const lock = useRef(false)
  const keys = useQuery({
    queryKey: ['finance-tax-selection', purchase ? 'einkauf' : 'verkauf'],
    queryFn: async () => (await apiClient.get<TaxKey[]>('/api/v1/finance/tax-keys/auswahl', {
      params: { richtung: purchase ? 'einkauf' : 'verkauf' },
    })).data,
    staleTime: 5 * 60 * 1000,
  })
  const preview = useQuery({
    queryKey: ['invoice-tax-preview', id, lines], enabled: lines.length > 0, retry: false,
    queryFn: async () => (await apiClient.post<TaxPreview>(purchase
      ? '/api/v1/finance/ap/invoices/steuer-vorschau' : '/api/v1/finance/invoices/steuer-vorschau', { lines })).data,
  })
  const schema = useMemo<ScreenDefinition>(() => ({
    ...definition,
    fields: (definition.fields ?? []).map(field => field.key === 'pos_taxCode' ? {
      ...field,
      options: (keys.data ?? []).map(key => ({ value: key.code,
        label: `${key.code} – ${key.bezeichnung} (${Number(key.steuersatz).toLocaleString('de-DE')} %)` })),
      placeholder: keys.isError ? 'Steuerschlüssel nicht geladen' : 'Steuerschlüssel wählen',
    } : field),
    actions: (definition.actions ?? []).map(action => ({ ...action, disabled: busy || action.disabled })),
    summary: (definition.summary ?? []).map(item => ({ ...item, value: item.key === 'netto' ? euro(preview.data?.netto)
      : item.key === 'steuer' ? euro(preview.data?.steuer) : euro(preview.data?.brutto) })),
  }), [definition, keys.data, keys.isError, busy, preview.data])
  const runtime = useUniversalMaskRuntime({ screenId: id, schema, permissions })
  const form = useUniversalFormState({ screen: schema, initialValues: {
    number: '', date: dateAfter(0), dueDate: dateAfter(30), paymentTerms: 'net30', customerId: '',
    sourceOrder: '', sourceDelivery: '', notes: '', pos_article: '', pos_qty: 1, pos_price: '', pos_taxCode: '',
  } })
  const plan = runtime.plan
  const can = (key: string) => Boolean(plan?.actions.some(action => action.key === key && !action.disabled))
  const add = () => {
    if (!can('position') || lock.current) return
    const article = str(form.values.pos_article), qty = num(form.values.pos_qty), price = num(form.values.pos_price)
    if (!article || !Number.isFinite(qty) || qty <= 0 || !Number.isFinite(price) || price <= 0) {
      toast.error('Position unvollständig', { description: 'Artikel, positive Menge und Einzelpreis eintragen.' })
      return
    }
    setLines(old => [...old, { article, qty, price, taxCode: str(form.values.pos_taxCode) || null }])
    Object.entries({ pos_article: '', pos_qty: 1, pos_price: '', pos_taxCode: '' })
      .forEach(([field, value]) => form.setValue(field, value))
  }
  const save = async () => {
    if (!can('save') || lock.current) return
    const raw = form.values
    const number = str(raw.number), date = str(raw.date), dueDate = str(raw.dueDate), customerId = str(raw.customerId)
    if (!number || !date || !dueDate || !customerId || lines.length === 0) {
      form.revealErrors?.()
      toast.error('Rechnung unvollständig', { description: 'Nummer, Datum, Partner, Fälligkeit und Positionen sind erforderlich.' })
      return
    }
    lock.current = true; setBusy(true)
    try {
      const response = await apiClient.post<{ ok?: boolean; id?: string; status?: string; data?: { number?: string } }>(
        purchase ? '/api/v1/finance/ap/invoices/' : '/api/v1/finance/invoices', {
          number, date, dueDate, customerId, paymentTerms: str(raw.paymentTerms) || 'net30',
          sourceOrder: str(raw.sourceOrder) || null, sourceDelivery: str(raw.sourceDelivery) || null,
          notes: str(raw.notes), status: 'ENTWURF', lines,
        })
      if (purchase ? response.data?.status !== 'ok' : response.data?.ok !== true) {
        throw new Error('Die Anlageantwort konnte nicht bestätigt werden.')
      }
      toast.success('Rechnung als Entwurf gespeichert')
      if (purchase) navigate(`/finance/ap-invoice/${encodeURIComponent(response.data.data?.number || number)}`)
      else navigate('/finance/invoices')
    } catch (error) {
      toast.error('Rechnung nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally { lock.current = false; setBusy(false) }
  }
  const context = createScreenContext({
    data: { positionen: lines }, permissions: { granted: permissions }, state: { values: form.values, policies: {} },
    actions: { 'finance.invoicePosition': add, 'finance.invoiceSpeichern': () => { void save() },
      'finance.invoicePositionEntfernen': payload => {
        if (!busy) setLines(old => old.filter((_, index) => index !== Number(payload.id)))
      } },
    navigation: { push: navigate },
  })
  const lookupEndpoint = definition.dataSources?.find(source => source.key === 'partners')?.endpoint ?? ''
  if (!plan) return <p role="status">Rechnungserfassung wird vorbereitet …</p>
  return <div data-testid={id.replaceAll('/', '-')} className="space-y-4 p-3 md:p-6">
    {keys.isError && <p role="alert">Steuerschlüssel konnten nicht geladen werden.</p>}
    {preview.isError && <p role="alert">Steuervorschau konnte nicht geladen werden.</p>}
    {preview.data && !preview.data.geklaert && <p role="alert">{preview.data.pruefgrund}</p>}
    <UniversalMaskRenderer plan={plan} formState={form} hideFormSubmit screenContext={context}
      allowedPermissions={permissions} lookupBindings={{ customerId: { fieldKey: 'customerId', lookupEndpoint,
        minSearchChars: 2, resultLimit: 25, cacheTtlMs: 0, debounceMs: 300 } }}
      tables={{ positionen: lines.map((line, index) => ({ id: String(index), ...line,
        taxCode: line.taxCode || 'nicht gewählt' })) }} />
    {lines.length > 0 && <p role="status">Netto: {euro(preview.data?.netto)} · Steuer: {euro(preview.data?.steuer)} · Brutto: {euro(preview.data?.brutto)}</p>}
  </div>
}
