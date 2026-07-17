import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { fetchRationDetail, type RationDetail } from '@/lib/api/rations-lifecycle'
import {
  createRationVersion,
  evaluateRationDraft,
  type DraftComponent,
  type RationDraftEvaluation,
} from '@/lib/api/feeding-ration-editor'
import { listFeedingFeeds, type FeedingFeedDetail } from '@/lib/api/feeding-feed-catalog'
import { getAxiosErrorMessage } from '@/lib/api-client'

const EVALUATE_DEBOUNCE_MS = 400

function formatNumber(value: number | undefined, digits = 1): string {
  if (value === undefined || !Number.isFinite(value)) return '–'
  return value.toLocaleString('de-DE', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function snapshotComponents(detail: RationDetail): DraftComponent[] {
  const latest = detail.versions.find((version) => version.id === detail.latest_version_id)
    ?? detail.versions[0]
  const raw = (latest?.snapshot as { components?: unknown })?.components
  if (!Array.isArray(raw)) return []
  const components = raw
    .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
    .map((item, index) => ({
      feed_id: String(item.feed_id ?? ''),
      name: typeof item.name === 'string' ? item.name : undefined,
      kg_fm: Number(item.kg_fm ?? 0),
      min_kg_fm: item.min_kg_fm == null ? null : Number(item.min_kg_fm),
      max_kg_fm: item.max_kg_fm == null ? null : Number(item.max_kg_fm),
      // Mischreihenfolge ist Teil der Version (FEED-EDITOR-041)
      mixing_sequence: item.mixing_sequence == null ? index + 1 : Number(item.mixing_sequence),
    }))
    .filter((item) => item.feed_id !== '')
  return components.sort((a, b) => a.mixing_sequence - b.mixing_sequence)
}

/** Expertenspalten (Mineralstoffe) — progressiv, erst nach Aktivierung (FEED-EDITOR-041). */
const EXPERT_COLUMNS: ReadonlyArray<readonly [string, string]> = [
  ['ca_g', 'Ca (g)'], ['p_g', 'P (g)'], ['na_g', 'Na (g)'],
  ['mg_g', 'Mg (g)'], ['k_g', 'K (g)'],
]

/** Vier Prioritaetsstufen (FEED-EDITOR-022, Maskenvertrag FEED-MASK-009). */
const SEVERITY_LABEL: Record<string, string> = {
  critical: 'Kritisch',
  high: 'Hoch',
  medium: 'Mittel',
  info: 'Hinweis',
}

const SEVERITY_BADGE: Record<string, 'destructive' | 'default' | 'secondary'> = {
  critical: 'destructive',
  high: 'destructive',
  medium: 'default',
  info: 'secondary',
}

/**
 * Produktiver Rationseditor — kleinste Journey (FEED-EDITOR-021, FEED-MASK-009):
 * Positionsflaeche links, permanente Bewertungsleiste rechts; Bewertung ist
 * deterministisch serverseitig (Code-SSOT); Speichern erzeugt append-only eine
 * neue Version ueber den bestehenden Lifecycle (optimistische Revision).
 */
export function RationEditor({ rationId }: { rationId: string }): JSX.Element {
  const [detail, setDetail] = useState<RationDetail | null>(null)
  const [components, setComponents] = useState<DraftComponent[]>([])
  const [feeds, setFeeds] = useState<FeedingFeedDetail[]>([])
  const [selectedFeedId, setSelectedFeedId] = useState('')
  const [evaluation, setEvaluation] = useState<RationDraftEvaluation | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [evaluationError, setEvaluationError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const debounceRef = useRef<number | null>(null)
  const amountInputRefs = useRef(new Map<string, HTMLInputElement>())
  // Undo/Redo fuer ungespeicherte Aenderungen (FEED-EDITOR-041): zusammenhaengende
  // Eingaben am selben Feld werden zu einem Schritt zusammengefasst (lastKey).
  const historyRef = useRef<{ past: DraftComponent[][]; future: DraftComponent[][]; lastKey: string | null }>(
    { past: [], future: [], lastKey: null })
  const [, setHistoryVersion] = useState(0)
  const [showExpert, setShowExpert] = useState(false)

  const load = useCallback(async (): Promise<void> => {
    setLoading(true)
    setLoadError(null)
    try {
      const [rationDetail, feedList] = await Promise.all([
        fetchRationDetail(rationId),
        listFeedingFeeds().catch(() => [] as FeedingFeedDetail[]),
      ])
      setDetail(rationDetail)
      setComponents(snapshotComponents(rationDetail))
      setFeeds(feedList)
      // Historie gilt nur fuer ungespeicherte Aenderungen der geladenen Version.
      historyRef.current = { past: [], future: [], lastKey: null }
      setHistoryVersion((version) => version + 1)
    } catch (error) {
      setLoadError(getAxiosErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [rationId])

  useEffect(() => { void load() }, [load])

  const evaluate = useCallback(async (draft: DraftComponent[], groupId: string): Promise<void> => {
    if (draft.length === 0) {
      setEvaluation(null)
      return
    }
    setEvaluationError(null)
    try {
      const result = await evaluateRationDraft({
        group_id: groupId,
        components: draft.map((component) => ({
          feed_id: component.feed_id, kg_fm: component.kg_fm,
          min_kg_fm: component.min_kg_fm, max_kg_fm: component.max_kg_fm,
        })),
      })
      setEvaluation(result)
    } catch (error) {
      setEvaluationError(getAxiosErrorMessage(error))
    }
  }, [])

  // Live-Bewertung: initial sofort, bei Aenderungen entprellt.
  useEffect(() => {
    if (!detail) return
    if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
    debounceRef.current = window.setTimeout(() => {
      void evaluate(components, detail.group_id)
    }, detail && evaluation === null ? 0 : EVALUATE_DEBOUNCE_MS)
    return () => {
      if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
    }
  }, [components, detail])

  /** Zentrale Draft-Mutation mit Undo-Historie. Gleicher actionKey in Folge
   * (z. B. Tippen im selben Mengenfeld) bildet einen Undo-Schritt. */
  function applyDraft(next: DraftComponent[], actionKey: string | null): void {
    const history = historyRef.current
    if (actionKey === null || actionKey !== history.lastKey) {
      history.past.push(components)
    }
    history.lastKey = actionKey
    history.future = []
    setComponents(next)
    setHistoryVersion((version) => version + 1)
    setSaveMessage(null)
  }

  function undo(): void {
    const history = historyRef.current
    const previous = history.past.pop()
    if (!previous) return
    history.future.push(components)
    history.lastKey = null
    setComponents(previous)
    setHistoryVersion((version) => version + 1)
    setSaveMessage(null)
  }

  function redo(): void {
    const history = historyRef.current
    const next = history.future.pop()
    if (!next) return
    history.past.push(components)
    history.lastKey = null
    setComponents(next)
    setHistoryVersion((version) => version + 1)
    setSaveMessage(null)
  }

  // Tastatur-Undo/Redo auch nach Fokusverlust (z. B. Button wird disabled):
  // Window-Listener, der stets die aktuelle Handler-Fassung aufruft.
  const historyKeyRef = useRef<(event: KeyboardEvent) => void>(() => {})
  historyKeyRef.current = (event: KeyboardEvent): void => {
    if (!(event.ctrlKey || event.metaKey)) return
    const key = event.key.toLowerCase()
    if (key === 'z' && !event.shiftKey) {
      event.preventDefault()
      undo()
    } else if (key === 'y' || (key === 'z' && event.shiftKey)) {
      event.preventDefault()
      redo()
    }
  }
  useEffect(() => {
    const listener = (event: KeyboardEvent): void => historyKeyRef.current(event)
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [])

  function updateAmount(feedId: string, value: string): void {
    const amount = Number(value)
    applyDraft(components.map((component) =>
      component.feed_id === feedId ? { ...component, kg_fm: Number.isFinite(amount) ? amount : 0 } : component),
      `amount:${feedId}`)
  }

  function updateBound(feedId: string, key: 'min_kg_fm' | 'max_kg_fm', rawValue: string): void {
    const value = rawValue === '' ? null : Number(rawValue)
    if (value !== null && (!Number.isFinite(value) || value < 0)) return
    applyDraft(components.map((component) =>
      component.feed_id === feedId ? { ...component, [key]: value } : component),
      `${key}:${feedId}`)
  }

  function removePosition(feedId: string): void {
    applyDraft(components.filter((component) => component.feed_id !== feedId), null)
  }

  function addPosition(): void {
    const feed = feeds.find((item) => item.id === selectedFeedId)
    if (!feed || components.some((component) => component.feed_id === feed.id)) return
    applyDraft([...components, { feed_id: feed.id, name: feed.name, kg_fm: 1 }], null)
    setSelectedFeedId('')
  }

  /** Mischreihenfolge in der UI sortieren (FEED-EDITOR-041). */
  function movePosition(feedId: string, direction: -1 | 1): void {
    const index = components.findIndex((component) => component.feed_id === feedId)
    const target = index + direction
    if (index < 0 || target < 0 || target >= components.length) return
    const next = [...components]
    ;[next[index], next[target]] = [next[target], next[index]]
    applyDraft(next, null)
  }

  /** Tastatur-Journey: Enter springt zur Menge der naechsten Position. */
  function focusNextAmount(feedId: string): void {
    const index = components.findIndex((component) => component.feed_id === feedId)
    const next = components[index + 1]
    if (next) amountInputRefs.current.get(next.feed_id)?.focus()
    else document.getElementById('editor-add-feed')?.focus()
  }

  async function save(): Promise<void> {
    if (!detail || saving) return
    setSaving(true)
    setSaveError(null)
    setSaveMessage(null)
    try {
      const created = await createRationVersion(detail.id, {
        // Mischreihenfolge wird Teil der Version (FEED-EDITOR-041).
        snapshot: { components: components.map((component, index) => ({ ...component, mixing_sequence: index + 1 })) },
        expected_latest_version_no: detail.latest_version_no,
        comment: 'Editor-Bearbeitung',
      })
      setSaveMessage(`Version ${created.version_no} gespeichert.`)
      await load()
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  const positionByFeed = useMemo(() => {
    const map = new Map<string, Record<string, unknown>>()
    for (const position of evaluation?.positions ?? []) map.set(position.feed_id, position)
    return map
  }, [evaluation])

  /** Warnung → Ursache: Befund fokussiert die verursachende Position
   * (fehlender Analysewert → betroffenes Futter, Kennzahl → erste Position). */
  function focusFindingCause(finding: { code: string; metric: string; feed_id?: string | null }): void {
    const missing = evaluation?.coverage?.[finding.metric]?.missing_feed_ids ?? []
    const targetFeedId = finding.feed_id
      ?? (finding.code.endsWith('_incomplete') && missing.length > 0 ? missing[0] : components[0]?.feed_id)
    if (!targetFeedId) return
    amountInputRefs.current.get(targetFeedId)?.focus()
  }

  if (loading) {
    return <div className="h-64 animate-pulse rounded-lg bg-muted/40" aria-hidden data-testid="ration-editor-loading" />
  }

  if (loadError || !detail) {
    return (
      <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
        <p className="font-medium text-status-error">Die Ration konnte nicht geladen werden.</p>
        {loadError ? <p className="mt-1 text-muted-foreground">{loadError}</p> : null}
        <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => { void load() }}>
          Erneut laden
        </Button>
      </div>
    )
  }

  const canUndo = historyRef.current.past.length > 0
  const canRedo = historyRef.current.future.length > 0

  return (
    <section className="space-y-4" data-testid="ration-editor">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">{detail.name}</h1>
          <p className="text-sm text-muted-foreground">
            {detail.group_name} · Version {detail.latest_version_no} · Status {detail.latest_status}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {saveMessage ? <p className="text-sm text-status-success" role="status">{saveMessage}</p> : null}
          {saveError ? <p className="text-sm text-status-error" role="alert">{saveError}</p> : null}
          <Button type="button" variant="outline" size="sm" disabled={!canUndo} onClick={undo}>
            Rückgängig
          </Button>
          <Button type="button" variant="outline" size="sm" disabled={!canRedo} onClick={redo}>
            Wiederholen
          </Button>
          <Button type="button" disabled={saving || components.length === 0} onClick={() => { void save() }}>
            {saving ? 'Speichert…' : 'Als neue Version speichern'}
          </Button>
        </div>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-3 rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between gap-2">
            <h2 className="font-medium">Rationspositionen</h2>
            <Button type="button" variant="outline" size="sm" aria-pressed={showExpert}
                    onClick={() => setShowExpert((current) => !current)}>
              Expertenspalten
            </Button>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="py-1.5 pr-2 font-medium">Futtermittel</th>
                <th className="py-1.5 pr-2 font-medium text-right">kg FM</th>
                <th className="py-1.5 pr-2 font-medium text-right">Min kg FM</th>
                <th className="py-1.5 pr-2 font-medium text-right">Max kg FM</th>
                <th className="py-1.5 pr-2 font-medium text-right">kg TM</th>
                <th className="py-1.5 pr-2 font-medium text-right">EUR</th>
                {showExpert ? EXPERT_COLUMNS.map(([key, label]) => (
                  <th key={key} className="py-1.5 pr-2 font-medium text-right">{label}</th>
                )) : null}
                <th className="py-1.5" aria-hidden />
              </tr>
            </thead>
            <tbody>
              {components.map((component, index) => {
                const position = positionByFeed.get(component.feed_id)
                const label = component.name ?? String(position?.name ?? component.feed_id)
                return (
                  <tr key={component.feed_id} className="border-b last:border-b-0">
                    <td className="py-1.5 pr-2">{label}</td>
                    <td className="py-1.5 pr-2 text-right">
                      <Input
                        aria-label={`Menge ${label} (kg FM)`}
                        className="ml-auto h-8 w-24 text-right tabular-nums"
                        type="number"
                        min="0"
                        step="0.1"
                        value={String(component.kg_fm)}
                        onChange={(event) => updateAmount(component.feed_id, event.target.value)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter') {
                            event.preventDefault()
                            focusNextAmount(component.feed_id)
                          }
                        }}
                        ref={(element) => {
                          if (element) amountInputRefs.current.set(component.feed_id, element)
                          else amountInputRefs.current.delete(component.feed_id)
                        }}
                      />
                    </td>
                    <td className="py-1.5 pr-2 text-right">
                      <Input aria-label={`Minimum ${label} (kg FM)`} className="ml-auto h-8 w-20 text-right tabular-nums"
                        type="number" min="0" step="0.1" value={component.min_kg_fm == null ? '' : String(component.min_kg_fm)}
                        onChange={(event) => updateBound(component.feed_id, 'min_kg_fm', event.target.value)} />
                    </td>
                    <td className="py-1.5 pr-2 text-right">
                      <Input aria-label={`Maximum ${label} (kg FM)`} className="ml-auto h-8 w-20 text-right tabular-nums"
                        type="number" min="0" step="0.1" value={component.max_kg_fm == null ? '' : String(component.max_kg_fm)}
                        onChange={(event) => updateBound(component.feed_id, 'max_kg_fm', event.target.value)} />
                    </td>
                    <td className="py-1.5 pr-2 text-right font-mono tabular-nums">
                      {formatNumber(position?.kg_tm as number | undefined)}
                    </td>
                    <td className="py-1.5 pr-2 text-right font-mono tabular-nums">
                      {formatNumber(position?.cost_eur as number | undefined, 2)}
                    </td>
                    {showExpert ? EXPERT_COLUMNS.map(([key]) => (
                      <td key={key} className="py-1.5 pr-2 text-right font-mono tabular-nums">
                        {formatNumber(position?.[key] as number | undefined)}
                      </td>
                    )) : null}
                    <td className="py-1.5 text-right">
                      <span className="inline-flex items-center gap-0.5">
                        <Button type="button" variant="ghost" size="sm" disabled={index === 0}
                                aria-label={`${label} nach oben verschieben`}
                                onClick={() => movePosition(component.feed_id, -1)}>
                          ↑
                        </Button>
                        <Button type="button" variant="ghost" size="sm" disabled={index === components.length - 1}
                                aria-label={`${label} nach unten verschieben`}
                                onClick={() => movePosition(component.feed_id, 1)}>
                          ↓
                        </Button>
                        <Button type="button" variant="ghost" size="sm"
                                onClick={() => removePosition(component.feed_id)}>
                          Entfernen
                        </Button>
                      </span>
                    </td>
                  </tr>
                )
              })}
              {components.length === 0 ? (
                <tr>
                  <td colSpan={7 + (showExpert ? EXPERT_COLUMNS.length : 0)}
                      className="py-4 text-center text-muted-foreground" role="status">
                    Noch keine Positionen — unten ein Futtermittel hinzufügen.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>

          <div className="flex items-end gap-2 border-t pt-3">
            <div className="grid flex-1 gap-1.5">
              <label htmlFor="editor-add-feed" className="text-sm font-medium">Futtermittel hinzufügen</label>
              <select
                id="editor-add-feed"
                className="h-9 rounded-md border bg-background px-3 text-sm"
                value={selectedFeedId}
                onChange={(event) => setSelectedFeedId(event.target.value)}
              >
                <option value="">Bitte wählen…</option>
                {feeds
                  .filter((feed) => !components.some((component) => component.feed_id === feed.id))
                  .map((feed) => <option key={feed.id} value={feed.id}>{feed.name}</option>)}
              </select>
            </div>
            <Button type="button" variant="outline" disabled={!selectedFeedId} onClick={addPosition}>
              Hinzufügen
            </Button>
          </div>
        </div>

        <aside className="space-y-3 rounded-lg border bg-card p-4 lg:sticky lg:top-4 lg:self-start"
               aria-label="Bewertung" data-testid="ration-editor-evaluation">
          <h2 className="font-medium">Bewertung</h2>
          {evaluationError ? (
            <p className="text-sm text-status-error" role="alert">{evaluationError}</p>
          ) : null}
          {evaluation ? (
            <>
              <dl className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-sm">
                <dt className="text-muted-foreground">TM gesamt</dt>
                <dd className="text-right font-mono tabular-nums">{formatNumber(evaluation.totals.dm_kg)} kg</dd>
                <dt className="text-muted-foreground">Kosten</dt>
                <dd className="text-right font-mono tabular-nums">{formatNumber(evaluation.totals.cost_eur, 2)} EUR</dd>
                <dt className="text-muted-foreground">Energie (ME)</dt>
                <dd className="text-right font-mono tabular-nums">{formatNumber(evaluation.totals.me_mj, 0)} MJ</dd>
                <dt className="text-muted-foreground">sidP</dt>
                <dd className="text-right font-mono tabular-nums">{formatNumber(evaluation.totals.sidp_g, 0)} g</dd>
              </dl>
              <ul className="space-y-2">
                {evaluation.findings.map((finding) => (
                  <li key={finding.code}>
                    <button
                      type="button"
                      className="w-full rounded-md border p-2 text-left text-sm hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring"
                      aria-label={finding.message}
                      onClick={() => focusFindingCause(finding)}
                    >
                      <Badge variant={SEVERITY_BADGE[finding.severity] ?? 'secondary'}>
                        {SEVERITY_LABEL[finding.severity] ?? finding.severity}
                      </Badge>
                      <span className="mt-1 block text-muted-foreground">{finding.message}</span>
                      {finding.remediation ? <span className="mt-1 block font-medium">Abhilfe: {finding.remediation}</span> : null}
                    </button>
                  </li>
                ))}
                {evaluation.findings.length === 0 ? (
                  <li className="text-sm text-muted-foreground" role="status">
                    Keine Befunde — Ration deckt die geprüften Kennzahlen.
                  </li>
                ) : null}
              </ul>
              <p className="text-2xs tracking-wide text-muted-foreground">
                Bewertung gegen Bedarfsprofil {evaluation.requirement_profile_id}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground" role="status">
              Positionen hinzufügen, um die Bewertung zu sehen.
            </p>
          )}
        </aside>
      </div>
    </section>
  )
}
