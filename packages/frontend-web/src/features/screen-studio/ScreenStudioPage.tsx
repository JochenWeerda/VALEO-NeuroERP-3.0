import { useEffect, useMemo, useReducer, useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAxiosErrorMessage } from '@/lib/api-client'
import {
  fetchStudioCatalog,
  proposeStudioDraft,
  publishStudioDraft,
  saveStudioDraft,
  submitStudioReview,
  validateStudioDraft,
  type StudioReport,
} from '@/lib/api/studio'
import { emptyStudioDraft } from './studio-defaults'
import { mockRowsFor, studioReducer } from './studio-reducer'

const previewClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

export function ScreenStudioPage(): JSX.Element {
  const [definition, dispatch] = useReducer(studioReducer, emptyStudioDraft())
  const [intent, setIntent] = useState('Lieferanten bewerten und auswählen')
  const [draftId, setDraftId] = useState<string>()
  const [publishedRoute, setPublishedRoute] = useState<string>()
  const [report, setReport] = useState<StudioReport>()
  const [pending, setPending] = useState<string>()
  const [feedback, setFeedback] = useState<string | null>(null)
  const catalog = useQuery({ queryKey: ['studio-catalog'], queryFn: fetchStudioCatalog })
  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(definition), [definition])
  const tables = useMemo(() => mockRowsFor(definition), [definition])

  useEffect(() => {
    let cancelled = false
    void validateStudioDraft(definition).then((next) => {
      if (!cancelled) setReport(next)
    }).catch(() => {
      if (!cancelled) setReport(undefined)
    })
    return () => { cancelled = true }
  }, [definition])

  async function run(key: string, work: () => Promise<void>): Promise<void> {
    if (pending) return
    setPending(key)
    setFeedback(null)
    try {
      await work()
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setPending(undefined)
    }
  }

  return (
    <div className="grid gap-4 p-4 lg:grid-cols-[minmax(18rem,22rem)_minmax(0,1fr)_minmax(16rem,20rem)]" data-testid="screen-studio">
      <section className="space-y-4">
        <div>
          <h1 className="text-lg font-semibold">Masken-Studio</h1>
          <p className="text-sm text-muted-foreground">ScreenDefinition erzeugen, prüfen und als temporären Entwurf speichern.</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="studio-intent">Agent-Vorschlag</Label>
          <Input id="studio-intent" value={intent} onChange={(event) => setIntent(event.target.value)} aria-label="Maskenabsicht" />
          <Button type="button" disabled={Boolean(pending)} onClick={() => void run('propose', async () => {
            const next = await proposeStudioDraft(intent)
            dispatch({ type: 'replace', definition: next.definition })
            setReport(next)
          })}>
            {pending === 'propose' ? 'Vorschlag…' : 'Aus Absicht erzeugen'}
          </Button>
        </div>
        <div className="space-y-2">
          <Label htmlFor="studio-title">Titel</Label>
          <Input id="studio-title" value={definition.title} onChange={(event) => dispatch({ type: 'setTitle', title: event.target.value })} />
          <Label htmlFor="studio-floorplan">Floorplan</Label>
          <select id="studio-floorplan" className="w-full rounded border bg-background px-2 py-1.5 text-sm" value={definition.layout?.floorplan ?? 'worklist'}
            onChange={(event) => dispatch({ type: 'setFloorplan', floorplan: event.target.value as never })}>
            {(catalog.data?.floorplans ?? ['worklist']).map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <Label htmlFor="studio-columns">Spaltennavigation</Label>
          <select id="studio-columns" className="w-full rounded border bg-background px-2 py-1.5 text-sm" value={definition.layout?.columnNavigation ?? 'single'}
            onChange={(event) => dispatch({ type: 'setColumnNavigation', columnNavigation: event.target.value as never })}>
            {(catalog.data?.columnNavigation ?? ['single', 'listDetail']).map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
        <Button type="button" variant="outline" disabled={Boolean(pending)} data-testid="studio-add-column" onClick={() => dispatch({
          type: 'addColumn',
          tableKey: definition.tables?.[0]?.key ?? 'list',
          column: { key: `feld_${(definition.tables?.[0]?.columns.length ?? 0) + 1}`, label: 'Neues Feld', sortable: true, filterable: true },
        })}>
          Spalte hinzufügen
        </Button>
        <p className="text-sm text-muted-foreground" data-testid="studio-column-count">
          {definition.tables?.[0]?.columns.length ?? 0} Felder
        </p>
        <div className="flex flex-wrap gap-2">
          <Button type="button" disabled={Boolean(pending)} onClick={() => void run('save', async () => {
            const saved = await saveStudioDraft(definition, draftId)
            setDraftId(saved.id)
            setReport(saved)
            setFeedback(`Gespeichert (${saved.status}).`)
          })}>
            {pending === 'save' ? 'Speichern…' : 'Speichern'}
          </Button>
          <Button type="button" variant="outline" disabled={!draftId || Boolean(pending)} onClick={() => void run('review', async () => {
            await submitStudioReview(draftId ?? '')
            setFeedback('Zur Prüfung gegeben.')
          })}>
            Prüfung
          </Button>
          <Button type="button" variant="outline" disabled={!draftId || Boolean(pending) || !report?.canPublish} onClick={() => void run('publish', async () => {
            const published = await publishStudioDraft(draftId ?? '')
            setReport(published)
            setPublishedRoute(published.route)
            setFeedback(`Veröffentlicht als ${published.status}.`)
          })}>
            Freigeben
          </Button>
        </div>
        {feedback ? <p className="text-sm" role="status">{feedback}</p> : null}
        {publishedRoute ? (
          <a className="text-sm underline" href={publishedRoute} data-testid="studio-run-link">
            Freigegebene Maske öffnen
          </a>
        ) : null}
      </section>

      <section className="min-w-0 overflow-auto rounded border" data-testid="studio-preview">
        <QueryClientProvider client={previewClient}>
          <UniversalMaskRenderer plan={plan} tables={tables} />
        </QueryClientProvider>
      </section>

      <aside className="space-y-3" data-testid="studio-gates">
        <h2 className="text-sm font-semibold uppercase tracking-wide">Gates</h2>
        {report?.violations.length ? (
          <ul className="list-disc pl-4 text-sm text-destructive">
            {report.violations.map((item) => <li key={item}>{item}</li>)}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">Keine Studio-Verletzungen.</p>
        )}
        <p className="text-sm">{report?.canPublish ? 'Publish möglich.' : 'Publish gesperrt, bis Gates grün sind.'}</p>
        {(report?.readiness.errors ?? []).map((item) => <p key={item} className="text-sm text-destructive">{item}</p>)}
      </aside>
    </div>
  )
}
