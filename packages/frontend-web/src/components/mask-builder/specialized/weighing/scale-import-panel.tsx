import { useRef, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable } from '../intake/domain-runtime'
import { useDomainIdentity } from '../intake/domain-data'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import type { Waage } from '@/lib/api/betrieb'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

type QueueEntry = { id: string; waage_id: string; rohdaten: string; fehler_beschreibung: string; retry_count: number; status: string; timestamp: string; ticket_id: string | null }
type ImportResult = { imported: number; skipped: number; errors: Array<{ id: string; fehler: string }>; wiegung_ids: string[]; replayed: boolean }
const importFields = ['importScaleId', 'importFile', 'fehlerToleranz']

export function ScaleImportPanel({ plan, scales, onImported }: { plan: RenderPlan; scales: Waage[]; onImported: () => void }): JSX.Element {
  const identity = useDomainIdentity()
  const [scaleId, setScaleId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [tolerant, setTolerant] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [inputError, setInputError] = useState<string | null>(null)
  const [dismissId, setDismissId] = useState<string | null>(null)
  const busy = useRef(false)
  const queue = useQuery({ queryKey: ['studio-scale-import-queue', identity], enabled: Boolean(identity.tenantId && identity.actor),
    queryFn: async () => (await apiClient.get<QueueEntry[]>('/api/v1/waage/waagen/import/fehlerqueue?limit=100')).data })
  const allowed = canDomainAction(plan, 'import') && fieldsEditable(plan, importFields)
  const upload = useMutation({ mutationFn: async () => {
    if (!allowed || !file || !scales.some(scale => scale.id === scaleId)) throw new Error('Eigene Waage und Datei auswählen')
    if (file.size > 1048576) throw new Error('Datei ist größer als 1 MB')
    if (!file.size) throw new Error('Datei ist leer')
    try { new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer()) } catch { throw new Error('Datei muss UTF-8 sein') }
    const data = new FormData()
    data.append('file', file)
    data.append('waage_id', scaleId)
    data.append('fehler_toleranz', String(tolerant))
    return (await apiClient.post<ImportResult>('/api/v1/waage/waagen/import/ascii', data)).data
  }, onSuccess: async response => { setResult(response); await queue.refetch(); onImported() } })
  const retry = useMutation({ mutationFn: async (entry: QueueEntry) => {
    if (!canDomainAction(plan, 'retryImport') || !queue.data?.some(row => row.id === entry.id)) throw new Error('Wiederholung nicht erlaubt')
    return (await apiClient.post<{ entry: QueueEntry; replayed: boolean }>(`/api/v1/waage/waagen/import/fehlerqueue/${encodeURIComponent(entry.id)}/retry`)).data
  }, onSuccess: async () => { await queue.refetch(); onImported() } })
  const dismiss = useMutation({ mutationFn: async (id: string) => {
    if (!canDomainAction(plan, 'dismissImport') || !queue.data?.some(row => row.id === id)) throw new Error('Verwerfen nicht erlaubt')
    await apiClient.delete(`/api/v1/waage/waagen/import/fehlerqueue/${encodeURIComponent(id)}`)
  }, onSuccess: async () => { setDismissId(null); await queue.refetch() } })
  async function submit(): Promise<void> {
    if (busy.current) return
    busy.current = true
    setResult(null)
    try { await upload.mutateAsync() } catch { /* The mutation renders its error and preserves the file. */ }
    finally { busy.current = false }
  }
  const pending = upload.isPending || retry.isPending || dismiss.isPending
  return <section aria-label="ASCII-Import und Fehlerqueue" className="space-y-4 rounded border p-4">
    <h2 className="font-semibold">ASCII-Wiegescheine importieren</h2>
    <p className="text-sm text-muted-foreground">UTF-8-Datei bis 1 MB. Ohne Fehlertoleranz wird die ganze Datei nur bei vollständiger Gültigkeit übernommen. Fehlerhafte Rohdaten können korrigiert und erneut hochgeladen werden.</p>
    <form className="space-y-3" onSubmit={event => { event.preventDefault(); void submit() }}>
      <Label htmlFor="import-scale">{plan.fieldsByKey.importScaleId?.label}</Label>
      <select id="import-scale" className="min-h-11 rounded border bg-background px-3" value={scaleId} disabled={!allowed || pending} onChange={event => { setScaleId(event.target.value); setResult(null) }}>
        <option value="">Waage auswählen</option>{scales.map(scale => <option key={scale.id} value={scale.id}>{scale.standort} · {scale.id}</option>)}
      </select>
      <Label htmlFor="scale-import-file">{plan.fieldsByKey.importFile?.label}</Label>
      <Input id="scale-import-file" type="file" accept=".txt,.asc,.csv" disabled={!allowed || pending} onChange={event => {
        const selected = event.target.files?.[0] ?? null
        setFile(selected); setResult(null)
        setInputError(selected && selected.size > 1048576 ? 'Datei ist größer als 1 MB' : null)
      }} />
      <label className="flex min-h-11 items-center gap-2"><input type="checkbox" checked={tolerant} disabled={!allowed || pending} onChange={event => setTolerant(event.target.checked)} />{plan.fieldsByKey.fehlerToleranz?.label}</label>
      {inputError && <p role="alert">{inputError}</p>}
      {upload.isError && <p role="alert">{getAxiosErrorMessage(upload.error)}</p>}
      <Button type="submit" disabled={!allowed || pending || !scaleId || !file || Boolean(inputError)}>{plan.actions.find(action => action.key === 'import')?.label ?? 'Datei importieren'}</Button>
    </form>
    {result && <div role="status" className="space-y-1"><p>{result.imported} importiert, {result.skipped} übersprungen, {result.errors.length} Fehler.{result.replayed ? ' Bereits verarbeitete Datei; keine Doppelanlage.' : ''}</p>{result.errors.map(error => <p key={error.id}>{error.fehler}</p>)}</div>}
    <h3 className="font-semibold">Importfehler</h3>
    {queue.isLoading && <p role="status">Fehlerqueue wird geladen…</p>}
    {queue.isError && <p role="alert">{getAxiosErrorMessage(queue.error)}</p>}
    {retry.isError && <p role="alert">{getAxiosErrorMessage(retry.error)}</p>}
    {dismiss.isError && <p role="alert">{getAxiosErrorMessage(dismiss.error)}</p>}
    {retry.isSuccess && <p role="status">{retry.data.entry.status === 'error' ? `Weiterhin fehlerhaft: ${retry.data.entry.fehler_beschreibung}` : 'Importzeile erfolgreich verarbeitet.'}</p>}
    {queue.data?.length === 0 && <p>Keine offenen Importfehler.</p>}
    {Boolean(queue.data?.length) && <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="text-left">Waage</th><th className="text-left">Rohdaten</th><th className="text-left">Fehler</th><th>Versuche</th><th>Aktionen</th></tr></thead><tbody>{queue.data?.map(entry => <tr key={entry.id}>
      <td>{entry.waage_id}</td><td><code className="whitespace-pre-wrap break-all">{entry.rohdaten}</code></td><td>{entry.fehler_beschreibung}</td><td className="text-right">{entry.retry_count}</td><td className="space-x-2 whitespace-nowrap">
        <Button variant="outline" disabled={pending || !canDomainAction(plan, 'retryImport')} onClick={() => retry.mutate(entry)}>Erneut prüfen</Button>
        <Button variant="outline" disabled={pending || !canDomainAction(plan, 'dismissImport')} onClick={() => setDismissId(entry.id)}>Verwerfen</Button>
      </td></tr>)}</tbody></table></div>}
    <AlertDialog open={Boolean(dismissId)} onOpenChange={open => { if (!open && !dismiss.isPending) setDismissId(null) }}>
      <AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Importfehler verwerfen?</AlertDialogTitle><AlertDialogDescription>Die Zeile wird aus der offenen Fehlerqueue entfernt. Ein Wiegeschein wird dabei nicht angelegt.</AlertDialogDescription></AlertDialogHeader><AlertDialogFooter>
        <AlertDialogCancel disabled={dismiss.isPending}>Abbrechen</AlertDialogCancel>
        <AlertDialogAction disabled={dismiss.isPending || !canDomainAction(plan, 'dismissImport')} onClick={event => { event.preventDefault(); if (dismissId) dismiss.mutate(dismissId) }}>Verwerfen bestätigen</AlertDialogAction>
      </AlertDialogFooter></AlertDialogContent>
    </AlertDialog>
  </section>
}
