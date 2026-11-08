import { lazy, Suspense, useEffect, useReducer, useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { getAxiosErrorMessage } from '@/lib/api-client'
import {
  fetchStudioCatalog,
  fetchStudioDrafts,
  fetchStudioDraft,
  proposeStudioDraft,
  publishStudioDraft,
  saveStudioDraft,
  submitStudioReview,
  simulateStudioDraft,
  type StudioSimulationResult,
  type StudioSavedMigrationPlan,
  validateStudioDraft,
  type StudioReport,
  type StudioDialogueTurn,
} from '@/lib/api/studio'
import { StudioVariantPresentation } from './StudioVariantPresentation'
import { StudioMigrationPlan } from './StudioMigrationPlan'
import { StudioHistoryPanel } from './StudioHistoryPanel'
import { StudioGateSummary } from './StudioGateSummary'
import { emptyStudioDraft } from './studio-defaults'
import { studioReducer } from './studio-reducer'
import { StudioDialogue } from './StudioDialogue'
import { StudioPreview } from './StudioPreview'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const previewClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
const StudioNativeImport = lazy(() => import('./StudioNativeImport').then(module => ({ default: module.StudioNativeImport })))
const HarvestControls = lazy(() => import('./HarvestControls').then(module => ({ default: module.HarvestControls })))

export function ScreenStudioPage(): JSX.Element {
  const controlsInitiallyOpen = new URLSearchParams(window.location.search).get('harvestControls') === '1'
  const [controlsSeen, setControlsSeen] = useState(controlsInitiallyOpen)
  const [nativeImportSeen, setNativeImportSeen] = useState(false)
  const [dialogueRequested, setDialogueRequested] = useState(false)
  const [definition, dispatch] = useReducer(studioReducer, emptyStudioDraft())
  const [intent, setIntent] = useState('Lieferanten bewerten und auswählen')
  const [draftId, setDraftId] = useState<string>()
  const [savedSignature, setSavedSignature] = useState<string>()
  const [savedRevision, setSavedRevision] = useState<string>()
  const [savedStatus, setSavedStatus] = useState<string>()
  const [migrationPlan, setMigrationPlan] = useState<StudioSavedMigrationPlan>()
  const [simulation, setSimulation] = useState<StudioSimulationResult>()
  const [publishedRoute, setPublishedRoute] = useState<string>()
  const [report, setReport] = useState<StudioReport>()
  const [pending, setPending] = useState<string>()
  const [feedback, setFeedback] = useState<string | null>(null)
  const [previewGeneration, setPreviewGeneration] = useState(0)
  const queryClient = useQueryClient()
  const refreshHistory = (id: string) => { void queryClient.invalidateQueries({ predicate: query =>
    query.queryKey.includes(id) && (query.queryKey[0] === 'platform/studio-history' || query.queryKey[1] === 'platform/studio-history') }) }
  const catalog = useQuery({ queryKey: ['studio-catalog'], queryFn: fetchStudioCatalog })
  const drafts = useQuery({ queryKey: ['studio-drafts'], queryFn: fetchStudioDrafts })
  const dirty = savedSignature !== JSON.stringify(definition)
  const migrationReady = migrationPlan && migrationPlan.draft_id === draftId && migrationPlan?.candidate_revision === savedRevision
    && !migrationPlan.requires_definition_update && migrationPlan.schema_changes.length === 0
  const semanticPreview = Boolean((definition as ScreenDefinition & { studioSemantic?: unknown }).studioSemantic)
  const semanticContext = (definition as ScreenDefinition & { studioSemantic?: {
    dialogue?: StudioDialogueTurn[]; decisions?: { weighing?: 'manual'; acceptPreviewLimits?: boolean }
  } }).studioSemantic

  useEffect(() => {
    let cancelled = false
    void validateStudioDraft(definition).then((next) => {
      if (!cancelled) setReport(next)
    }).catch(() => {
      if (!cancelled) setReport(undefined)
    })
    return () => { cancelled = true }
  }, [definition])

  function applyProposal(next: ScreenDefinition): void {
    setDialogueRequested(false)
    setPreviewGeneration(value => value + 1)
    dispatch({ type: 'replace', definition: next })
    setDraftId(undefined)
    setSavedRevision(undefined)
    setSavedSignature(undefined)
    setSavedStatus(undefined)
    setSimulation(undefined)
    setPublishedRoute(undefined)
  }

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
      {controlsInitiallyOpen && <details className="col-span-full min-w-0 rounded border p-3" open
        onToggle={event => { if (event.currentTarget.open) setControlsSeen(true) }}>
        <summary className="cursor-pointer font-medium">Ernte-Abrechnung: Vertragsregeln, Messnachweise und Freigaben</summary>
        {controlsSeen && <Suspense fallback={<p>Abrechnungssteuerung wird geladen…</p>}><HarvestControls /></Suspense>}
      </details>}
      <details className="col-span-full rounded border p-3" onToggle={event => {
        if (event.currentTarget.open) setNativeImportSeen(true)
      }}>
        <summary className="cursor-pointer font-medium">Vorhandene Maske versionieren und ins Studio übernehmen</summary>
        {nativeImportSeen && <Suspense fallback={<p>Vorhandene Masken werden geladen…</p>}>
          <StudioNativeImport onImported={item => {
            setIntent('')
            applyProposal(item.definition)
            setDraftId(item.id); setSavedRevision(item.revision); setSavedStatus(item.status)
            setSavedSignature(JSON.stringify(item.definition))
            void queryClient.invalidateQueries({ queryKey: ['studio-drafts'] })
            refreshHistory(item.id)
            setFeedback('Versionierte Ausgangsfassung übernommen. Die bisherige Maske bleibt bis zur geprüften Umstellung aktiv.')
          }} />
        </Suspense>}
      </details>
      <section className="space-y-4">
        <div>
          <h1 className="text-lg font-semibold">Masken-Studio</h1>
          {definition.documentVariant && <p aria-label="Belegmasken-Version" className="text-sm text-muted-foreground">
            Ausgangsfassung: Belegbasis {definition.documentVariant.baseVersion} · Variante {definition.documentVariant.variantVersion}
          </p>}
          <p className="text-sm text-muted-foreground">ScreenDefinition erzeugen, prüfen und als temporären Entwurf speichern.</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="studio-existing">Gespeicherten Entwurf öffnen</Label>
          <NativeSelect id="studio-existing" value={draftId ?? ''} disabled={Boolean(pending)}
            onChange={(event) => {
              const id = event.target.value
              if (!id) return
              void run('load', async () => {
                const item = await fetchStudioDraft(id)
                setPreviewGeneration(value => value + 1)
                dispatch({ type: 'replace', definition: item.definition })
                setIntent('')
                setDialogueRequested(false)
                setDraftId(item.id)
                setSavedSignature(JSON.stringify(item.definition))
                setSavedRevision(item.revision)
            setSavedStatus(item.status)
                setPublishedRoute(undefined)
                setSimulation(undefined)
                setReport(undefined)
                setFeedback(`Entwurf geladen (${item.status}).`)
              })
            }}>
            <option value="">Entwurf auswählen</option>
            {(drafts.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.definition.title} ({item.status})</option>)}
          </NativeSelect>
        </div>
        <div className="space-y-2">
          <Label htmlFor="studio-intent">Agent-Vorschlag</Label>
          <Input id="studio-intent" value={intent} onChange={(event) => setIntent(event.target.value)} aria-label="Maskenabsicht" placeholder="Neue Maske oder Änderung beschreiben…" />
          <Button type="button" disabled={Boolean(pending) || !intent.trim()} onClick={() => void run('propose', async () => {
            const next = await proposeStudioDraft(intent)
            applyProposal(next.definition)
            setReport(next)
          })}>
            {pending === 'propose' ? 'Vorschlag…' : 'Maskenvorschlag erstellen'}
          </Button>
        </div>
        <div className="space-y-2">
          <Label htmlFor="studio-title">Titel</Label>
          <Input id="studio-title" value={definition.title} onChange={(event) => dispatch({ type: 'setTitle', title: event.target.value })} />
          <Label htmlFor="studio-domain">Fachbereich</Label>
          <NativeSelect id="studio-domain" className="w-full rounded border bg-background px-2 py-1.5 text-sm" value={definition.domain}
            onChange={(event) => dispatch({ type: 'setDomain', domain: event.target.value as typeof definition.domain })}>
            {[...new Set([definition.domain, 'agrar', 'einkauf', 'crm', 'finance', 'lager'])].map((item) => <option key={item} value={item}>{item}</option>)}
          </NativeSelect>
          <Button type="button" variant="outline" disabled={Boolean(pending)} onClick={() => dispatch({ type: 'removeActions' })}>Fachaktionen entfernen</Button>
          <Label htmlFor="studio-floorplan">Floorplan</Label>
          <NativeSelect id="studio-floorplan" className="w-full rounded border bg-background px-2 py-1.5 text-sm" value={definition.layout?.floorplan ?? 'worklist'}
            onChange={(event) => dispatch({ type: 'setFloorplan', floorplan: event.target.value as never })}>
            {(catalog.data?.floorplans ?? ['worklist']).map((item) => <option key={item} value={item}>{item}</option>)}
          </NativeSelect>
          <Label htmlFor="studio-columns">Spaltennavigation</Label>
          <NativeSelect id="studio-columns" className="w-full rounded border bg-background px-2 py-1.5 text-sm" value={definition.layout?.columnNavigation ?? 'single'}
            onChange={(event) => dispatch({ type: 'setColumnNavigation', columnNavigation: event.target.value as never })}>
            {(catalog.data?.columnNavigation ?? ['single', 'listDetail']).map((item) => <option key={item} value={item}>{item}</option>)}
          </NativeSelect>
        </div>
        <StudioVariantPresentation definition={definition}
          disabled={Boolean(pending) || !catalog.data?.permissions?.canDesign}
          onChange={next => dispatch({ type: 'replace', definition: next })} />
        {!semanticPreview && !dialogueRequested && <Button type="button" variant="outline"
          onClick={() => setDialogueRequested(true)}>Neuen Entwurf im Fachgespräch beginnen</Button>}
        {(semanticPreview || dialogueRequested) && <>
        {!semanticPreview && <p className="text-sm text-muted-foreground">Derzeit verfügbar: Getreide-Kalkulationsprobe. Eine Übernahme ersetzt den aktuellen Entwurf erst nach Ihrer Auswahl.</p>}
        <StudioDialogue key={previewGeneration} initialTurns={semanticContext?.dialogue} initialDecisions={semanticContext?.decisions}
          disabled={Boolean(pending) || !catalog.data?.permissions?.canDesign} onProposal={applyProposal} />
        </>}
        {semanticPreview && catalog.data?.semantic && <section aria-label="Freigegebene Fachfelder" className="space-y-1 text-sm">
          <h2 className="font-semibold">Freigegebene Fachfelder · Getreide-Kalkulationsprobe</h2>
          <p className="text-xs text-muted-foreground">Im Katalogvorschlag können Sie optionale Eingaben auswählen. Pflichtfelder sichern den Berechnungsvertrag.</p>
          <ul>{catalog.data.semantic.fields.map(field => <li key={field.key} title={field.contract}>
            <label className="flex gap-2"><input type="checkbox" checked={Boolean(definition.fields?.some(item => item.key === field.key))}
              disabled={Boolean(pending) || field.required || !(definition as ScreenDefinition & { studioSemantic?: unknown }).studioSemantic}
              onChange={event => {
                const fields = definition.fields?.filter(item => item.key !== field.key) ?? []
                dispatch({ type: 'replace', definition: { ...definition, fields: event.target.checked ? [...fields, {
                  key: field.key, label: `${field.label} (${field.unit})`, type: 'number', required: field.required,
                  helpText: 'Manuelle Testeingabe. Keine produktive Wirkung.',
                }] : fields } })
              }} />{field.label} ({field.unit}){field.required ? ' · Pflichtfeld' : ''}</label>
          </li>)}</ul>
        </section>}
        <div className="flex flex-wrap gap-2">
          <Button type="button" disabled={Boolean(pending) || !catalog.data?.permissions?.canDesign || (Boolean(draftId) && !dirty)} onClick={() => void run('save', async () => {
            const saved = await saveStudioDraft(definition, draftId, savedRevision)
            setDraftId(saved.id)
            setSavedSignature(JSON.stringify(saved.definition))
            setSavedRevision(saved.revision)
            setSavedStatus(saved.status)
            refreshHistory(saved.id)
            void drafts.refetch()
            setPublishedRoute(undefined)
            setReport(saved)
            setFeedback(`Gespeichert (${saved.status}).`)
          })}>
            {pending === 'save' ? 'Speichern…' : 'Speichern'}
          </Button>
          <Button type="button" variant="outline" disabled={!draftId || !savedRevision || savedStatus !== 'draft' || dirty || Boolean(pending) || !catalog.data?.permissions?.canDesign} onClick={() => void run('review', async () => {
            if (dirty || !savedRevision || savedStatus !== 'draft') return
            const reviewed = await submitStudioReview(draftId ?? '', savedRevision)
            setSavedRevision(reviewed.revision)
            setSavedStatus(reviewed.status)
            refreshHistory(draftId ?? '')
            void drafts.refetch()
            setFeedback('Zur Prüfung gegeben.')
          })}>
            Prüfung
          </Button>
          <Button type="button" variant="outline" disabled={!draftId || !savedRevision || savedStatus !== 'review' || dirty || Boolean(pending) || !catalog.data?.permissions?.canDesign} onClick={() => void run('simulation', async () => {
            if (!draftId || !savedRevision || dirty) return
            const checked = await simulateStudioDraft(draftId, savedRevision)
            setSimulation(checked.simulation)
            refreshHistory(draftId)
            setFeedback(checked.simulation.passed ? 'Prozesssimulation bestanden.' : 'Prozesssimulation fehlgeschlagen; Freigabe gesperrt.')
          })}>Prozess simulieren</Button>
          <Button type="button" variant="outline" disabled={!draftId || !savedRevision || savedStatus !== 'review' || dirty || Boolean(pending) || !report?.definitionReady || !catalog.data?.permissions?.canPublish || !simulation?.passed || simulation.candidate_revision !== savedRevision || !migrationReady} onClick={() => void run('publish', async () => {
            if (dirty || !savedRevision || savedStatus !== 'review') return
            const published = await publishStudioDraft(draftId ?? '', savedRevision)
            setReport(published)
            setSavedRevision(published.revision)
            setSavedStatus(published.status)
            refreshHistory(draftId ?? '')
            void drafts.refetch()
            setPublishedRoute(published.route)
            setFeedback(`Veröffentlicht als ${published.status}.`)
          })}>
            Freigeben
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">Freigabe erfolgt durch eine andere angemeldete menschliche Administration.</p>
        {catalog.data && !catalog.data.permissions?.canPublish && <p className="text-sm">Ihre Anmeldung besitzt kein Studio-Freigaberecht.</p>}
        {draftId && dirty ? <p role="status">Änderungen zuerst speichern, danach erneut prüfen.</p> : null}
        {feedback ? <p className="text-sm" role="status">{feedback}</p> : null}
        {publishedRoute && !dirty ? (
          <a className="text-sm underline" href={publishedRoute} data-testid="studio-run-link">
            Freigegebene Maske öffnen
          </a>
        ) : null}
      </section>

      <section className="min-w-0 overflow-auto rounded border" data-testid="studio-preview">
        <QueryClientProvider client={previewClient}>
          <StudioPreview key={`${previewGeneration}:${definition.id}`} definition={definition} />
        </QueryClientProvider>
      </section>

      <aside className="space-y-3" data-testid="studio-gates">
        <h2 className="text-sm font-semibold uppercase tracking-wide">Gates</h2>
        <StudioGateSummary report={report} semanticPreview={semanticPreview}
          publishedUnchanged={savedStatus === 'published_temp' && !dirty}
          readyToPublish={Boolean(report?.definitionReady && catalog.data?.permissions?.canPublish && simulation?.passed
            && simulation.candidate_revision === savedRevision && migrationReady && !dirty)} />
      </aside>
      <StudioMigrationPlan key={`plan:${draftId ?? 'new'}:${savedRevision ?? 'unsaved'}`} draftId={draftId} revision={savedRevision}
        disabled={dirty || Boolean(pending) || !catalog.data?.permissions?.canDesign || !['draft', 'review'].includes(savedStatus ?? '')}
        onPrepared={plan => { setMigrationPlan(plan); if (draftId) refreshHistory(draftId) }} />
      {simulation && <p role="status">Simulation: {simulation.passed ? 'bestanden' : 'fehlgeschlagen'}{simulation.failed_checks?.length ? ` (${simulation.failed_checks.map(check => check === 'semantic_preview_not_a_release_profile' ? 'Kalkulationsprobe ist noch kein abgenommener produktiver Prozess' : check).join(', ')})` : ''}</p>}
      {draftId && <StudioHistoryPanel key={`${draftId}:${savedRevision ?? ""}`} draftId={draftId} />}
    </div>
  )
}
