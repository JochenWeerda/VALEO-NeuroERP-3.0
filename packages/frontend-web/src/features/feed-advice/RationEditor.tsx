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
  return raw
    .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
    .map((item) => ({
      feed_id: String(item.feed_id ?? ''),
      name: typeof item.name === 'string' ? item.name : undefined,
      kg_fm: Number(item.kg_fm ?? 0),
    }))
    .filter((item) => item.feed_id !== '')
}

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
        components: draft.map((component) => ({ feed_id: component.feed_id, kg_fm: component.kg_fm })),
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [components, detail])

  function updateAmount(feedId: string, value: string): void {
    const amount = Number(value)
    setComponents((current) => current.map((component) =>
      component.feed_id === feedId ? { ...component, kg_fm: Number.isFinite(amount) ? amount : 0 } : component))
    setSaveMessage(null)
  }

  function removePosition(feedId: string): void {
    setComponents((current) => current.filter((component) => component.feed_id !== feedId))
    setSaveMessage(null)
  }

  function addPosition(): void {
    const feed = feeds.find((item) => item.id === selectedFeedId)
    if (!feed || components.some((component) => component.feed_id === feed.id)) return
    setComponents((current) => [...current, { feed_id: feed.id, name: feed.name, kg_fm: 1 }])
    setSelectedFeedId('')
    setSaveMessage(null)
  }

  async function save(): Promise<void> {
    if (!detail || saving) return
    setSaving(true)
    setSaveError(null)
    setSaveMessage(null)
    try {
      const created = await createRationVersion(detail.id, {
        snapshot: { components },
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
  function focusFindingCause(finding: { code: string; metric: string }): void {
    const missing = evaluation?.coverage?.[finding.metric]?.missing_feed_ids ?? []
    const targetFeedId = finding.code.endsWith('_incomplete') && missing.length > 0
      ? missing[0]
      : components[0]?.feed_id
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
          <Button type="button" disabled={saving || components.length === 0} onClick={() => { void save() }}>
            {saving ? 'Speichert…' : 'Als neue Version speichern'}
          </Button>
        </div>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-3 rounded-lg border bg-card p-4">
          <h2 className="font-medium">Rationspositionen</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="py-1.5 pr-2 font-medium">Futtermittel</th>
                <th className="py-1.5 pr-2 font-medium text-right">kg FM</th>
                <th className="py-1.5 pr-2 font-medium text-right">kg TM</th>
                <th className="py-1.5 pr-2 font-medium text-right">EUR</th>
                <th className="py-1.5" aria-hidden />
              </tr>
            </thead>
            <tbody>
              {components.map((component) => {
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
                        ref={(element) => {
                          if (element) amountInputRefs.current.set(component.feed_id, element)
                          else amountInputRefs.current.delete(component.feed_id)
                        }}
                      />
                    </td>
                    <td className="py-1.5 pr-2 text-right font-mono tabular-nums">
                      {formatNumber(position?.kg_tm as number | undefined)}
                    </td>
                    <td className="py-1.5 pr-2 text-right font-mono tabular-nums">
                      {formatNumber(position?.cost_eur as number | undefined, 2)}
                    </td>
                    <td className="py-1.5 text-right">
                      <Button type="button" variant="ghost" size="sm"
                              onClick={() => removePosition(component.feed_id)}>
                        Entfernen
                      </Button>
                    </td>
                  </tr>
                )
              })}
              {components.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-4 text-center text-muted-foreground" role="status">
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
