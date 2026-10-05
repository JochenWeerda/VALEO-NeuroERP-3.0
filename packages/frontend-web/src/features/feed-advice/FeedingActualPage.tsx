import { useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { createActualMeasure, createDeviationPolicy, exportActualFeedingsCsv, fetchActualMeasures, fetchDeviationFindings, fetchDeviationPolicies, type DeviationFinding } from '@/lib/api/feeding-actual'

function tomorrow(): string {
  const result = new Date()
  result.setDate(result.getDate() + 1)
  return result.toISOString().slice(0, 10)
}

export function FeedingActualPage(): JSX.Element {
  const [feedback, setFeedback] = useState<string | null>(null)
  const [measureOpen, setMeasureOpen] = useState(false)
  const [findings, setFindings] = useState<DeviationFinding[]>([])
  const [findingId, setFindingId] = useState('')
  const [title, setTitle] = useState('')
  const [owner, setOwner] = useState('')
  const [dueDate, setDueDate] = useState(tomorrow)
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [policyOpen, setPolicyOpen] = useState(false)
  const [feedClass, setFeedClass] = useState('forage')
  const [warningPct, setWarningPct] = useState('5')
  const [criticalPct, setCriticalPct] = useState('10')
  const [policyReason, setPolicyReason] = useState('')

  async function exportCsv(): Promise<void> {
    setFeedback(null)
    try {
      const blob = await exportActualFeedingsCsv()
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'ist-fuetterung.csv'
      anchor.click()
      URL.revokeObjectURL(url)
      setFeedback('CSV-Export wurde aus den aktuell berechtigten Ist-Fuetterungen erstellt.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    }
  }

  async function beginMeasure(): Promise<void> {
    setFeedback(null)
    try {
      const [rows, measures] = await Promise.all([fetchDeviationFindings(), fetchActualMeasures()])
      const actionable = rows.filter((row) => row.severity === 'warning' || row.severity === 'critical')
      setFindings(actionable)
      setFindingId(actionable[0]?.actual_component_id ?? '')
      setMeasureOpen(true)
      if (actionable.length === 0) {
        const unconfigured = rows.filter((row) => row.severity === 'unconfigured').length
        setFeedback(unconfigured > 0
          ? `${unconfigured} Komponentenklassen besitzen noch keine explizite Schwellenkonfiguration.`
          : 'Aktuell liegt kein massnahmenfaehiger Abweichungsbefund vor.')
      } else if (measures.length > 0) {
        setFeedback(`${measures.length} offene Massnahmen sind bereits dokumentiert.`)
      }
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    }
  }

  async function saveMeasure(): Promise<void> {
    if (!findingId) return
    setSaving(true); setFeedback(null)
    try {
      await createActualMeasure({ actual_component_id: findingId, title: title.trim(),
        owner_subject: owner.trim(), due_date: dueDate, reason: reason.trim(),
        idempotency_key: `feeding-measure-${crypto.randomUUID()}` })
      setMeasureOpen(false); setTitle(''); setOwner(''); setReason(''); setDueDate(tomorrow())
      setFeedback('Massnahme wurde mit Befund, Verantwortlichem und Termin revisionssicher angelegt.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  async function beginPolicy(): Promise<void> {
    setFeedback(null)
    try {
      const policies = await fetchDeviationPolicies()
      const current = policies.find((item) => item.feed_class === feedClass)
      if (current) {
        setWarningPct(String(current.warning_pct)); setCriticalPct(String(current.critical_pct))
        setFeedback(`Aktuelle Regel ${feedClass} ist Version ${current.version}; Speichern erzeugt eine neue Version.`)
      }
      setPolicyOpen(true)
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    }
  }

  async function savePolicy(): Promise<void> {
    setSaving(true); setFeedback(null)
    try {
      const policy = await createDeviationPolicy({ feed_class: feedClass,
        warning_pct: Number(warningPct), critical_pct: Number(criticalPct),
        valid_from: new Date().toISOString().slice(0, 10), reason: policyReason.trim() })
      setPolicyOpen(false); setPolicyReason('')
      setFeedback(`Schwellen fuer ${policy.feed_class} wurden als Regelversion ${policy.version} angelegt.`)
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return <div data-testid="feeding-actual-page" data-runtime="native">
    {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
    <UniversalNativeCockpitPage
      screenId="agrar/feeding-actuals" testId="feeding-actual-worklist"
      permissions={['futtermittel.rations.read', 'futtermittel.rations.update']}
      onAction={(key) => {
        if (key === 'export_csv') void exportCsv()
        if (key === 'create_measure') void beginMeasure()
        if (key === 'configure_threshold') void beginPolicy()
        if (key === 'open_mobile') window.location.assign('/futtermittel/fuetterungsdokumentation-mobil')
      }}
    />
    <Dialog open={measureOpen} onOpenChange={setMeasureOpen}>
      <DialogContent>
        <DialogHeader><DialogTitle>Massnahme aus Abweichung</DialogTitle><DialogDescription>Die Massnahme entsteht erst nach dieser menschlichen Bestaetigung und bleibt mit Plan, Komponente und Schwelle verknuepft.</DialogDescription></DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-2"><Label htmlFor="measure-finding">Abweichungsbefund</Label><select id="measure-finding" className="h-10 rounded-md border bg-background px-3" value={findingId} onChange={(event) => setFindingId(event.target.value)}>{findings.map((finding) => <option key={finding.actual_component_id} value={finding.actual_component_id}>{finding.severity === 'critical' ? 'Kritisch' : 'Warnung'} · {finding.feed_name ?? finding.feed_id} · {finding.delta_pct}%</option>)}</select></div>
          <div className="grid gap-2"><Label htmlFor="measure-title">Massnahme</Label><Input id="measure-title" value={title} onChange={(event) => setTitle(event.target.value)} /></div>
          <div className="grid gap-2"><Label htmlFor="measure-owner">Verantwortlich</Label><Input id="measure-owner" value={owner} onChange={(event) => setOwner(event.target.value)} /></div>
          <div className="grid gap-2"><Label htmlFor="measure-due">Faellig am</Label><Input id="measure-due" type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} /></div>
          <div className="grid gap-2"><Label htmlFor="measure-reason">Begruendung</Label><Input id="measure-reason" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Mindestens 10 Zeichen" /></div>
        </div>
        <DialogFooter><Button variant="outline" onClick={() => setMeasureOpen(false)}>Abbrechen</Button><Button disabled={saving || !findingId || title.trim().length < 3 || !owner.trim() || reason.trim().length < 10 || !dueDate} onClick={() => { void saveMeasure() }}>{saving ? 'Speichert...' : 'Massnahme anlegen'}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog open={policyOpen} onOpenChange={setPolicyOpen}>
      <DialogContent>
        <DialogHeader><DialogTitle>Komponenten-Schwellen konfigurieren</DialogTitle><DialogDescription>Jedes Speichern erzeugt eine neue, zeitlich nachvollziehbare Regelversion. Es gibt keinen stillen Universalwert.</DialogDescription></DialogHeader>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="grid gap-2 sm:col-span-2"><Label htmlFor="policy-class">Komponentenklasse</Label><select id="policy-class" className="h-10 rounded-md border bg-background px-3" value={feedClass} onChange={(event) => setFeedClass(event.target.value)}><option value="forage">Grundfutter</option><option value="concentrate">Kraftfutter</option><option value="mineral">Mineralfutter</option><option value="additive">Zusatzstoff</option><option value="byproduct">Nebenprodukt</option><option value="liquid">Fluessigfutter</option><option value="other">Sonstige</option></select></div>
          <div className="grid gap-2"><Label htmlFor="policy-warning">Warnung ab %</Label><Input id="policy-warning" type="number" min="0.001" max="100" step="0.1" value={warningPct} onChange={(event) => setWarningPct(event.target.value)} /></div>
          <div className="grid gap-2"><Label htmlFor="policy-critical">Kritisch ab %</Label><Input id="policy-critical" type="number" min="0.001" max="100" step="0.1" value={criticalPct} onChange={(event) => setCriticalPct(event.target.value)} /></div>
          <div className="grid gap-2 sm:col-span-2"><Label htmlFor="policy-reason">Aenderungsgrund</Label><Input id="policy-reason" value={policyReason} onChange={(event) => setPolicyReason(event.target.value)} placeholder="Mindestens 10 Zeichen" /></div>
        </div>
        <DialogFooter><Button variant="outline" onClick={() => setPolicyOpen(false)}>Abbrechen</Button><Button disabled={saving || !warningPct || !criticalPct || Number(criticalPct) <= Number(warningPct) || policyReason.trim().length < 10} onClick={() => { void savePolicy() }}>{saving ? 'Speichert...' : 'Neue Regelversion anlegen'}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
}
