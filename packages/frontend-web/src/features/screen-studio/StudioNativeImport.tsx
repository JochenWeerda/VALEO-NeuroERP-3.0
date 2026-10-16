import { useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import type { StudioDraftRecord } from '@/lib/api/studio'

interface NativeSource { screen_id: string; title: string; source_hash: string }

export function StudioNativeImport({ onImported }: {
  onImported: (_record: StudioDraftRecord) => void
}): JSX.Element {
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()
  const keys = useRef(new Map<string, string>())
  const tenant = tenantFromToken(auth.getAccessToken())
  const subject = auth.getUser()?.sub
  const sources = useQuery({ queryKey: ['studio-native-sources', tenant, subject, query],
    queryFn: async () => (await apiClient.get<{ items: NativeSource[]; total: number }>(
      '/api/v1/studio/native-sources', { params: { q: query, limit: 100 } })).data })
  const source = sources.data?.items.find(item => item.screen_id === selected)

  async function importSelected(): Promise<void> {
    if (!source || busy) return
    setBusy(true); setError(undefined)
    try {
      const intent = `${tenant}:${subject}:${source.screen_id}:${source.source_hash}`
      const key = keys.current.get(intent) ?? crypto.randomUUID()
      keys.current.set(intent, key)
      const result = await apiClient.post<StudioDraftRecord>('/api/v1/studio/native-imports', {
        screen_id: source.screen_id, expected_source_hash: source.source_hash, idempotency_key: key,
      })
      onImported(result.data)
    } catch (failure) { setError(getAxiosErrorMessage(failure)) }
    finally { setBusy(false) }
  }

  return <section className="space-y-3" aria-label="Vorhandene Maske versionieren">
    <p>Die vorhandene Maske bleibt aktiv. Die Übernahme erzeugt eine nachvollziehbare Studio-Ausgangsfassung;
      sie aktiviert keine Änderung und erteilt keine Freigabe.</p>
    <Label htmlFor="studio-native-search">Maske nach Bezeichnung suchen</Label>
    <Input id="studio-native-search" value={query} onChange={event => {
      setQuery(event.target.value); setSelected('')
    }} disabled={busy} />
    <Label htmlFor="studio-native-source">Vorhandene Maske</Label>
    <NativeSelect id="studio-native-source" value={selected} onChange={event => setSelected(event.target.value)}
      disabled={busy || sources.isFetching} className="w-full rounded border bg-background px-2 py-1.5 text-sm">
      <option value="">Maske auswählen</option>
      {(sources.data?.items ?? []).map(item => <option key={item.screen_id} value={item.screen_id}>{item.title}</option>)}
    </NativeSelect>
    {sources.data && sources.data.total > sources.data.items.length && <p>Bitte die Suche eingrenzen, um weitere Masken zu finden.</p>}
    <Button type="button" disabled={!source || busy || sources.isFetching} onClick={() => { void importSelected() }}>
      {busy ? 'Wird übernommen…' : 'Als versionierte Ausgangsfassung übernehmen'}
    </Button>
    {(error || sources.error) && <p role="alert">{error ?? 'Vorhandene Masken konnten nicht geladen werden.'}</p>}
  </section>
}
