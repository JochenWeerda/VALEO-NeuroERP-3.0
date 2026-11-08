import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable } from '../intake/domain-runtime'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useDomainIdentity } from '../intake/domain-data'
import type { Waage } from '@/lib/api/betrieb'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type Calibration = { letztes_eichdatum: string | null; naechste_eichfaelligkeit: string | null; eichamt: string | null; zertifikat_nr: string | null }
const empty: Calibration = { letztes_eichdatum: null, naechste_eichfaelligkeit: null, eichamt: null, zertifikat_nr: null }
const keys = ['letztes_eichdatum', 'naechste_eichfaelligkeit', 'eichamt', 'zertifikat_nr'] as const

export function ScaleCalibrationPanel({ plan, scales, onSaved }: { plan: RenderPlan; scales: Waage[]; onSaved: () => void }): JSX.Element {
  const { tenantId, actor } = useDomainIdentity()
  const [selected, setSelected] = useState('')
  const [draft, setDraft] = useState<Calibration>(empty)
  const [message, setMessage] = useState<string | null>(null)
  const query = useQuery({ queryKey: ['studio-scale-calibration', tenantId, actor, selected], enabled: Boolean(selected && tenantId && actor), queryFn: async () => {
    const response = await apiClient.get<Calibration>(`/api/v1/waage/waagen/${encodeURIComponent(selected)}/kalibrierung`)
    return response.data
  } })
  useEffect(() => { setDraft(query.data ?? empty) }, [query.data, selected, tenantId])
  useEffect(() => { setSelected(''); setMessage(null) }, [tenantId, actor])
  const editable = canDomainAction(plan, 'calibrate') && fieldsEditable(plan, [...keys])
  const mutation = useMutation({ mutationFn: async () => {
    if (!editable || !selected || query.isError || !query.data) throw new Error('Eichdaten können nicht bearbeitet werden')
    if (draft.letztes_eichdatum && draft.naechste_eichfaelligkeit && draft.letztes_eichdatum > draft.naechste_eichfaelligkeit) throw new Error('Die nächste Eichung darf nicht vor der letzten Eichung liegen')
    await apiClient.patch(`/api/v1/waage/waagen/${encodeURIComponent(selected)}/kalibrierung`, draft)
  }, onSuccess: async () => { setMessage('Eichdaten gespeichert.'); await query.refetch(); onSaved() } })
  return <section className="space-y-3 rounded border p-4" aria-label="Eichdaten">
    <h2 className="font-semibold">Eichdaten pflegen</h2>
    <Label htmlFor="calibration-scale">Waage</Label>
    <select id="calibration-scale" className="min-h-11 rounded border bg-background px-3" value={selected} onChange={event => setSelected(event.target.value)}>
      <option value="">Waage auswählen</option>{scales.map(scale => <option key={scale.id} value={scale.id}>{scale.standort} · {scale.id}</option>)}
    </select>
    {query.isLoading && selected && <p role="status">Eichdaten werden geladen…</p>}
    {query.isError && <p role="alert">{getAxiosErrorMessage(query.error)}</p>}
    {selected && query.data && !query.isError && <form className="space-y-3" onSubmit={event => { event.preventDefault(); if (!mutation.isPending) mutation.mutate() }}>
      <div className="grid gap-3 md:grid-cols-4">{keys.map(key => <div key={key}>
        <Label htmlFor={`calibration-${key}`}>{plan.fieldsByKey[key]?.label}</Label>
        <Input id={`calibration-${key}`} type={key.includes('datum') || key.includes('faelligkeit') ? 'date' : 'text'}
          disabled={!editable || mutation.isPending} value={draft[key] ?? ''} onChange={event => setDraft(previous => ({ ...previous, [key]: event.target.value || null }))} />
      </div>)}</div>
      {mutation.isError && <p role="alert">{getAxiosErrorMessage(mutation.error)}</p>}
      {message && <p role="status">{message}</p>}
      <Button type="submit" disabled={!editable || mutation.isPending}>{plan.actions.find(action => action.key === 'calibrate')?.label ?? 'Eichdaten speichern'}</Button>
    </form>}
  </section>
}
