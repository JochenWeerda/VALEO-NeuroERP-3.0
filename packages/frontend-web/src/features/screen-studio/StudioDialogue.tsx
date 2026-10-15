import { useEffect, useState } from 'react'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { Button } from '@/components/ui/button'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { fetchStudioBudgets, sendStudioDialogue, type StudioDialogueTurn, type StudioDialogueResult } from '@/lib/api/studio'

export function StudioDialogue({ onProposal, disabled }: { onProposal: (_definition: ScreenDefinition) => void; disabled: boolean }): JSX.Element {
  const [turns, setTurns] = useState<StudioDialogueTurn[]>([])
  const [message, setMessage] = useState('Ich brauche eine Getreideannahme mit Verwiegung, Feuchtigkeit, Besatz und Abrechnungspreis.')
  const [weighing, setWeighing] = useState<'' | 'manual' | 'automatic'>('')
  const [accepted, setAccepted] = useState(false)
  const [answer, setAnswer] = useState<StudioDialogueResult>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()
  const [model, setModel] = useState(false)
  const [budget, setBudget] = useState('')
  const [budgets, setBudgets] = useState<Array<{ id: string; available: number; kind: string }>>([])
  useEffect(() => {
    let active = true
    if (model) void fetchStudioBudgets().then(items => { if (active) setBudgets(items) }).catch(failure => { if (active) setError(getAxiosErrorMessage(failure)) })
    return () => { active = false }
  }, [model])
  async function send(): Promise<void> {
    if (busy || !message.trim()) return
    const next: StudioDialogueTurn[] = [...turns, { role: 'user', content: message.trim() }]
    if (next.length > 19) { setError('Bitte ein neues Fachgespraech beginnen; die bisherigen Entscheidungen bleiben im uebernommenen Entwurf erhalten.'); return }
    setBusy(true)
    setError(undefined)
    try {
      const result = model ? await sendStudioDialogue(next, weighing || undefined, accepted, { budget })
        : await sendStudioDialogue(next, weighing || undefined, accepted)
      setTurns([...next, { role: 'assistant', content: result.message }])
      setAnswer(result)
      setMessage('')
    } catch (failure) { setError(getAxiosErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  return <section className="space-y-2 rounded border p-3" aria-label="Fachgespraech">
    <h2 className="font-semibold">Maske im Fachgespräch</h2>
    <p className="text-sm text-muted-foreground">{model ? 'Modellgestützte Vertragsauswahl mit zentralem Tokenkontingent.' : 'Kataloggeführter Dialog ohne Sprachmodell.'} Keine Tabellen- oder Spaltenkenntnisse nötig.</p>
    <label className="flex gap-2 text-sm"><input type="checkbox" checked={model} onChange={event => { setModel(event.target.checked); setAnswer(undefined) }} />Konfiguriertes Sprachmodell zur Anforderungsinterpretation nutzen</label>
    {model && <div className="space-y-1">
      <p className="text-xs">Nur Ihre Anforderungen werden an den für diesen Mandanten konfigurierten Anbieter gesendet. Keine echten Kunden- oder Zugangsdaten eingeben. Verbrauch wird vorab reserviert und im technischen Nebenbuch abgerechnet.</p>
      <label htmlFor="studio-model-budget">Eigenes Tokenkontingent</label>
      <select id="studio-model-budget" value={budget} onChange={event => { setBudget(event.target.value); setAnswer(undefined) }}>
        <option value="">Kontingent wählen</option>{budgets.map(item => <option key={item.id} value={item.id}>{item.kind} · {item.available} Token verfügbar</option>)}
      </select>
      {!budgets.length && <p className="text-xs">Kein eigenes Kontingent verfügbar. Eine berechtigte Administration muss es zuweisen. Der Katalogdialog funktioniert ohne Modell.</p>}
    </div>}
    <ol aria-live="polite" className="max-h-64 space-y-2 overflow-auto text-sm">
      {turns.map((turn, index) => <li key={index}><strong>{turn.role === 'user' ? 'Sie' : 'Studio'}:</strong> {turn.content}</li>)}
    </ol>
    <label className="block text-sm" htmlFor="studio-dialogue-text">Anforderung oder Antwort</label>
    <textarea id="studio-dialogue-text" className="w-full rounded border bg-background p-2 text-sm" value={message} maxLength={4000}
      onChange={event => { setMessage(event.target.value); setAnswer(undefined) }} />
    <label className="block text-sm" htmlFor="studio-weighing">Wiegewerte übernehmen</label>
    <select id="studio-weighing" value={weighing} onChange={event => { setWeighing(event.target.value as typeof weighing); setAnswer(undefined) }}>
      <option value="">Bitte klären</option><option value="manual">Manuelle Testeingabe</option><option value="automatic">Automatische Waage</option>
    </select>
    <label className="flex gap-2 text-sm"><input type="checkbox" checked={accepted} onChange={event => { setAccepted(event.target.checked); setAnswer(undefined) }} />Nur Kalkulationsprobe ohne Waagen-/Kontraktbindung, Meldungen oder Buchungen akzeptieren</label>
    <Button type="button" disabled={disabled || busy || !message.trim() || (model && !budget)} onClick={() => void send()}>{busy ? 'Wird geprüft…' : 'Im Fachgespräch prüfen'}</Button>
    {answer?.limitations && <ul className="list-disc pl-4 text-xs">{answer.limitations.map(limit => <li key={limit}>{limit}</li>)}</ul>}
    {answer?.ready && answer.definition && <Button type="button" disabled={disabled || busy} onClick={() => {
      if (answer.definition) onProposal(answer.definition)
    }}>Geprüften Vorschlag übernehmen</Button>}
    {error && <p role="alert">{error}</p>}
    <Button type="button" variant="outline" disabled={busy} onClick={() => { setTurns([]); setAnswer(undefined); setAccepted(false); setWeighing(''); setError(undefined) }}>Neues Fachgespräch</Button>
  </section>
}
