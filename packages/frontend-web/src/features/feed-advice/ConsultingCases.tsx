import { useCallback, useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  addConsultingObservation,
  closeConsultingCase,
  createConsultingReportDraft,
  getConsultingCase,
  listCaseMeasures,
  listConsultingCases,
  transitionFeedingMeasure,
  type ConsultingCase,
  type ConsultingCaseDetail,
  type ConsultingMeasure,
} from '@/lib/api/feeding-consulting'
import { getAxiosErrorMessage } from '@/lib/api-client'

const CATEGORIES = [
  { value: 'fuetterung', label: 'Fütterung' },
  { value: 'tier', label: 'Tierbeobachtung' },
  { value: 'silo', label: 'Silo/Futterlager' },
  { value: 'sonstiges', label: 'Sonstiges' },
]

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' })
}

/** Beratungsfälle: Worklist + Falldetail mit idempotenter Beobachtungserfassung
 * (FEED-CONS-031). Responsives Layout = mobiler Erfassungspfad. */
export function ConsultingCases({ initialCaseId }: { initialCaseId?: string }): JSX.Element {
  const [cases, setCases] = useState<ConsultingCase[]>([])
  const [detail, setDetail] = useState<ConsultingCaseDetail | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(initialCaseId ?? null)
  const [listError, setListError] = useState<string | null>(null)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const [category, setCategory] = useState('fuetterung')
  const [text, setText] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [closing, setClosing] = useState(false)
  const [measures, setMeasures] = useState<ConsultingMeasure[]>([])
  const [reporting, setReporting] = useState(false)
  const [reportMessage, setReportMessage] = useState<string | null>(null)
  const [reviewingMeasure, setReviewingMeasure] = useState<ConsultingMeasure | null>(null)
  const [effectiveness, setEffectiveness] = useState<'effective' | 'partial' | 'ineffective'>('effective')
  const [effectivenessResult, setEffectivenessResult] = useState('')

  const loadList = useCallback(async (): Promise<void> => {
    setLoading(true)
    setListError(null)
    try {
      setCases(await listConsultingCases())
    } catch (error) {
      setListError(getAxiosErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [])

  const loadDetail = useCallback(async (caseId: string): Promise<void> => {
    setDetailError(null)
    try {
      const [caseDetail, caseMeasures] = await Promise.all([
        getConsultingCase(caseId), listCaseMeasures(caseId),
      ])
      setDetail(caseDetail)
      setMeasures(caseMeasures)
    } catch (error) {
      setDetailError(getAxiosErrorMessage(error))
    }
  }, [])

  function openEffectivenessReview(measure: ConsultingMeasure): void {
    setReviewingMeasure(measure)
    setEffectiveness('effective')
    setEffectivenessResult('')
    setSaveError(null)
  }

  async function confirmEffectiveness(): Promise<void> {
    if (!reviewingMeasure || effectivenessResult.trim().length < 10) return
    setSaving(true)
    setSaveError(null)
    try {
      await transitionFeedingMeasure(reviewingMeasure.measure_id, {
        expected_version: reviewingMeasure.version,
        target_status: 'completed',
        reason: 'Wirksamkeitskontrolle im Beratungsfall abgeschlossen',
        effectiveness,
        effectiveness_result: effectivenessResult.trim(),
      })
      setSaveMessage('Maßnahme mit Wirksamkeitskontrolle abgeschlossen.')
      setReviewingMeasure(null)
      setEffectivenessResult('')
      if (detail) setMeasures(await listCaseMeasures(detail.id))
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  async function advanceMeasure(
    measure: ConsultingMeasure,
    targetStatus: 'in_progress' | 'review_due',
    reason: string,
  ): Promise<void> {
    setSaving(true)
    setSaveError(null)
    try {
      await transitionFeedingMeasure(measure.measure_id, {
        expected_version: measure.version,
        target_status: targetStatus,
        reason,
      })
      setSaveMessage(
        targetStatus === 'in_progress'
          ? 'Maßnahme ist jetzt in Bearbeitung.'
          : 'Wirksamkeitskontrolle ist eingeplant.',
      )
      if (detail) setMeasures(await listCaseMeasures(detail.id))
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  async function createReportDraft(): Promise<void> {
    if (!detail || reporting) return
    setReporting(true)
    setSaveError(null)
    try {
      const draft = await createConsultingReportDraft(
        detail.id, 'Aktuellen Beratungsstand reproduzierbar festhalten')
      setReportMessage(`Berichtentwurf v${draft.version} gespeichert · noch kein PDF`)
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setReporting(false)
    }
  }

  useEffect(() => { void loadList() }, [loadList])
  useEffect(() => {
    if (selectedId) void loadDetail(selectedId)
    else setDetail(null)
  }, [selectedId, loadDetail])

  async function submitObservation(): Promise<void> {
    if (!detail || saving || text.trim() === '') return
    setSaving(true)
    setSaveError(null)
    setSaveMessage(null)
    try {
      // Idempotenzschluessel je Erfassung — Doppel-Submit/Retry erzeugt keine Dublette.
      const clientRef = `web-${crypto.randomUUID()}`
      await addConsultingObservation(detail.id, {
        category, text: text.trim(), client_ref: clientRef,
      })
      setText('')
      setSaveMessage('Beobachtung gespeichert.')
      await loadDetail(detail.id)
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  async function closeCase(): Promise<void> {
    if (!detail || closing) return
    const summary = window.prompt('Abschlussbewertung des Beratungsfalls:')
    if (!summary) return
    setClosing(true)
    setSaveError(null)
    try {
      await closeConsultingCase(detail.id, summary)
      setSaveMessage('Fall abgeschlossen.')
      await Promise.all([loadDetail(detail.id), loadList()])
    } catch (error) {
      setSaveError(getAxiosErrorMessage(error))
    } finally {
      setClosing(false)
    }
  }

  if (loading) {
    return <div className="h-64 animate-pulse rounded-lg bg-muted/40" aria-hidden />
  }

  if (listError) {
    return (
      <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
        <p className="font-medium text-status-error">Die Beratungsfälle konnten nicht geladen werden.</p>
        <p className="mt-1 text-muted-foreground">{listError}</p>
        <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => { void loadList() }}>
          Erneut laden
        </Button>
      </div>
    )
  }

  return (
    <section className="grid gap-4 lg:grid-cols-[20rem_1fr]" data-testid="consulting-cases">
      <aside className="space-y-2 rounded-lg border bg-card p-3" aria-label="Beratungsfälle">
        <h2 className="font-medium">Beratungsfälle</h2>
        {cases.length === 0 ? (
          <p className="text-sm text-muted-foreground" role="status">
            Noch keine Fälle — der erste Beratungsbesuch legt einen an.
          </p>
        ) : (
          <ul className="space-y-1.5">
            {cases.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className="w-full rounded-md border p-2 text-left text-sm hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring"
                  onClick={() => setSelectedId(item.id)}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className="font-medium">{item.title}</span>
                    <Badge variant={item.status === 'open' ? 'default' : 'secondary'}>
                      {item.status === 'open' ? 'Offen' : 'Abgeschlossen'}
                    </Badge>
                  </span>
                  <span className="mt-0.5 block text-muted-foreground">
                    {item.case_type === 'visit' ? 'Besuch' : 'Remote'} · {formatDateTime(item.created_at)}
                    {typeof item.observation_count === 'number' ? ` · ${item.observation_count} Beobachtungen` : ''}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <div className="space-y-4">
        {detailError ? (
          <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
            <p className="font-medium text-status-error">Der Fall konnte nicht geladen werden.</p>
            <p className="mt-1 text-muted-foreground">{detailError}</p>
          </div>
        ) : null}
        {!detail && !detailError ? (
          <div className="rounded-lg border bg-muted/30 p-6 text-sm text-muted-foreground" role="status">
            Links einen Beratungsfall wählen, um Beobachtungen zu sehen und zu erfassen.
          </div>
        ) : null}
        {detail ? (
          <>
            <header className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h1 className="text-lg font-semibold">{detail.title}</h1>
                {detail.initial_situation ? (
                  <p className="text-sm text-muted-foreground">{detail.initial_situation}</p>
                ) : null}
              </div>
              <div className="flex items-center gap-3">
                {saveMessage ? <p className="text-sm text-status-success" role="status">{saveMessage}</p> : null}
                {saveError ? <p className="text-sm text-status-error" role="alert">{saveError}</p> : null}
                <Button type="button" variant="outline" disabled={reporting}
                        onClick={() => { void createReportDraft() }}>
                  {reporting ? 'Erzeugt…' : 'Berichtentwurf erzeugen'}
                </Button>
                {detail.status === 'open' ? (
                  <Button type="button" variant="outline" disabled={closing} onClick={() => { void closeCase() }}>
                    {closing ? 'Schließt…' : 'Fall abschließen'}
                  </Button>
                ) : (
                  <Badge variant="secondary">Abgeschlossen</Badge>
                )}
              </div>
            </header>

            {detail.closing_summary ? (
              <p className="rounded-md border bg-muted/30 p-3 text-sm">
                <span className="font-medium">Abschluss: </span>{detail.closing_summary}
              </p>
            ) : null}
            {reportMessage ? (
              <p className="text-sm text-status-success" role="status">{reportMessage}</p>
            ) : null}

            <section className="space-y-2 rounded-lg border bg-card p-4" aria-label="Maßnahmen">
              <h2 className="font-medium">Maßnahmen und Wirksamkeit</h2>
              {measures.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Noch keine Maßnahme mit diesem Fall verknüpft.
                </p>
              ) : measures.map((measure) => (
                <div key={measure.measure_id}
                     className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-3 text-sm">
                  <div>
                    <p className="font-medium">{measure.title}</p>
                    <p className="text-muted-foreground">
                      {measure.owner_subject} · fällig {new Date(measure.due_date).toLocaleDateString('de-DE')} · {measure.status}
                    </p>
                  </div>
                  {measure.status === 'open' ? (
                    <Button
                      type="button"
                      variant="outline"
                      disabled={saving}
                      onClick={() => { void advanceMeasure(
                        measure, 'in_progress', 'Bearbeitung im Beratungsfall gestartet') }}
                    >
                      Bearbeitung starten
                    </Button>
                  ) : measure.status === 'in_progress' ? (
                    <Button
                      type="button"
                      variant="outline"
                      disabled={saving}
                      onClick={() => { void advanceMeasure(
                        measure,
                        'review_due',
                        'Umsetzung erfolgt und Wirksamkeitskontrolle eingeplant',
                      ) }}
                    >
                      Wirksamkeitskontrolle einplanen
                    </Button>
                  ) : measure.status === 'review_due' ? (
                    <Button type="button" variant="outline" disabled={saving}
                            onClick={() => openEffectivenessReview(measure)}>
                      Wirksamkeit bestätigen
                    </Button>
                  ) : <Badge variant="secondary">{measure.status}</Badge>}
                </div>
              ))}
              {reviewingMeasure ? (
                <div
                  className="space-y-3 rounded-md border bg-muted/20 p-3"
                  role="dialog"
                  aria-labelledby="effectiveness-review-title"
                >
                  <div>
                    <h3 id="effectiveness-review-title" className="font-medium">
                      Wirksamkeitskontrolle: {reviewingMeasure.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Die Maßnahme wird erst nach einer nachvollziehbaren Bewertung abgeschlossen.
                    </p>
                  </div>
                  <div className="grid gap-3 md:grid-cols-[14rem_1fr]">
                    <div className="grid gap-1.5">
                      <Label htmlFor="measure-effectiveness">Bewertung der Wirksamkeit</Label>
                      <select
                        id="measure-effectiveness"
                        className="h-9 rounded-md border bg-background px-3 text-sm"
                        value={effectiveness}
                        onChange={(event) => setEffectiveness(
                          event.target.value as 'effective' | 'partial' | 'ineffective')}
                      >
                        <option value="effective">Wirksam</option>
                        <option value="partial">Teilweise wirksam</option>
                        <option value="ineffective">Nicht wirksam</option>
                      </select>
                    </div>
                    <div className="grid gap-1.5">
                      <Label htmlFor="measure-effectiveness-result">
                        Ergebnis der Wirksamkeitskontrolle
                      </Label>
                      <Input
                        id="measure-effectiveness-result"
                        value={effectivenessResult}
                        onChange={(event) => setEffectivenessResult(event.target.value)}
                        placeholder="Messbares Ergebnis oder Beobachtung dokumentieren"
                        aria-describedby="measure-effectiveness-result-help"
                      />
                      <p id="measure-effectiveness-result-help" className="text-xs text-muted-foreground">
                        Mindestens 10 Zeichen; die Angabe wird revisionsfest versioniert.
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      disabled={saving}
                      onClick={() => setReviewingMeasure(null)}
                    >
                      Abbrechen
                    </Button>
                    <Button
                      type="button"
                      disabled={saving || effectivenessResult.trim().length < 10}
                      onClick={() => { void confirmEffectiveness() }}
                    >
                      {saving ? 'Wird abgeschlossen…' : 'Maßnahme abschließen'}
                    </Button>
                  </div>
                </div>
              ) : null}
            </section>

            <section className="space-y-2 rounded-lg border bg-card p-4" aria-label="Beobachtungen">
              <h2 className="font-medium">Beobachtungen</h2>
              {detail.observations.length === 0 ? (
                <p className="text-sm text-muted-foreground" role="status">
                  Noch keine Beobachtungen erfasst.
                </p>
              ) : (
                <ol className="space-y-2">
                  {detail.observations.map((observation) => (
                    <li key={observation.id} className="rounded-md border p-2 text-sm">
                      <p className="flex items-center gap-2 text-2xs tracking-wide uppercase text-muted-foreground">
                        {CATEGORIES.find((c) => c.value === observation.category)?.label ?? observation.category}
                        <span aria-hidden>·</span>
                        {formatDateTime(observation.created_at)}
                      </p>
                      <p className="mt-1">{observation.text}</p>
                      {observation.photo_document_refs.length > 0 ? (
                        <p className="mt-1 text-xs text-muted-foreground">
                          {observation.photo_document_refs.length} Foto-Beleg(e) im DMS
                        </p>
                      ) : null}
                    </li>
                  ))}
                </ol>
              )}
            </section>

            {detail.status === 'open' ? (
              <section className="space-y-3 rounded-lg border bg-card p-4" aria-label="Beobachtung erfassen">
                <div className="grid gap-1.5">
                  <Label htmlFor="obs-category">Kategorie</Label>
                  <select
                    id="obs-category"
                    className="h-9 w-56 rounded-md border bg-background px-3 text-sm"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    {CATEGORIES.map((item) => (
                      <option key={item.value} value={item.value}>{item.label}</option>
                    ))}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="obs-text">Beobachtung</Label>
                  <Input
                    id="obs-text"
                    value={text}
                    onChange={(event) => setText(event.target.value)}
                    placeholder="Was wurde beobachtet?"
                  />
                </div>
                <Button type="button" disabled={saving || text.trim() === ''}
                        onClick={() => { void submitObservation() }}>
                  {saving ? 'Speichert…' : 'Beobachtung erfassen'}
                </Button>
              </section>
            ) : null}
          </>
        ) : null}
      </div>
    </section>
  )
}
