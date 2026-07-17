import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, ChevronLeft, ClipboardCheck, Save, Scale, Thermometer, Wheat } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { fetchActualFeedings, recordActualFeeding, type ActualCause, type ActualFeedingRecord } from '@/lib/api/feeding-actual'
import { fetchCurrentFeedingPlans } from '@/lib/api/feeding-plans'
import { FeedingOfflineQueue, isNetworkError, type QueuedItem } from '@/lib/offline/feeding-offline-queue'

const ACTIVE_RATION_KEY = 'valeo.feeding-plan.mobile.v2'

type ActiveRation = {
  version: 2
  planVersionId: string
  planVersionNo: number
  updatedAt: string
  group: { id: string; name: string; count: number }
  milkYield: number | null
  milkPriceEur: number | null
  totalCostEurDay: number | null
  dosingStepKg: number
  pendfSollGKgdm: number | null
  ndfProxyGKgdm: number | null
  components: Array<{ feed_id: string; name: string; soll_kg: number | null }>
}

type Phase = 'plan' | 'record' | 'result'

function readActiveRation(): ActiveRation | null {
  try {
    const raw = localStorage.getItem(ACTIVE_RATION_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as ActiveRation
    return parsed?.version === 2 && Array.isArray(parsed.components) ? parsed : null
  } catch {
    return null
  }
}

function NumberField({ label, value, onChange, suffix, min = 0, step = 0.1 }: { label: string; value: number; onChange: (value: number) => void; suffix: string; min?: number; step?: number }) {
  return <label className="block rounded-xl border border-slate-200 bg-white p-3">
    <span className="mb-2 block text-xs font-semibold text-slate-600">{label}</span>
    <span className="flex items-center gap-2"><Input className="h-11 min-w-0 text-base font-semibold" type="number" inputMode="decimal" min={min} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} /><span className="shrink-0 text-xs text-slate-500">{suffix}</span></span>
  </label>
}

export default function MobileFuetterungsdokumentation() {
  const [ration, setRation] = useState<ActiveRation | null>(() => readActiveRation())
  const currentPlans = useQuery({ queryKey: ['current-feeding-plans-mobile'], queryFn: fetchCurrentFeedingPlans })
  const [phase, setPhase] = useState<Phase>('plan')
  const [actual, setActual] = useState<Record<string, number>>({})
  const [cause, setCause] = useState<ActualCause>('normal')
  const [comment, setComment] = useState('')
  const [restKg, setRestKg] = useState(0)
  const [tmPct, setTmPct] = useState(40)
  const [topPct, setTopPct] = useState(8)
  const [middlePct, setMiddlePct] = useState(42)
  const [feedTemp, setFeedTemp] = useState(20)
  const [ambientTemp, setAmbientTemp] = useState(18)
  const [commandId, setCommandId] = useState(() => crypto.randomUUID())
  const [supersedesId, setSupersedesId] = useState<string | null>(null)
  const groupId = ration?.group.id ?? ''
  const history = useQuery({ queryKey: ['feeding-actual-mobile', groupId], queryFn: fetchActualFeedings, enabled: Boolean(groupId), select: (rows) => rows.filter((row) => row.group_id === groupId).slice(0, 14) })

  // Offline-Warteschlange (FEED-MOB-045): dieselbe API, idempotente Replays.
  const [queue] = useState(() => new FeedingOfflineQueue())
  const [queueItems, setQueueItems] = useState<QueuedItem[]>(() => queue.items())
  const [queuedOffline, setQueuedOffline] = useState(false)

  const replayQueue = async (): Promise<void> => {
    if (queue.pending().length === 0) { setQueueItems(queue.items()); return }
    await queue.replay({ actual_feeding: (payload) => recordActualFeeding(payload as Parameters<typeof recordActualFeeding>[0]) })
    setQueueItems(queue.items())
    void history.refetch()
  }

  useEffect(() => {
    void replayQueue()
    const onOnline = (): void => { void replayQueue() }
    window.addEventListener('online', onOnline)
    return () => window.removeEventListener('online', onOnline)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Queue-Replay ist bewusst mount-/online-gebunden
  }, [])

  const save = useMutation({
    mutationFn: recordActualFeeding,
    onSuccess: () => { setQueuedOffline(false); setPhase('result'); void history.refetch() },
    onError: (error, variables) => {
      if (!isNetworkError(error)) return
      // Netzwerkfehler: Eingabe geht nicht verloren — mit fixiertem
      // idempotency_key einreihen; der Replay trifft den idempotenten Vertrag.
      queue.enqueue('actual_feeding', variables as unknown as QueuedItem['payload'])
      setQueueItems(queue.items())
      setQueuedOffline(true)
    },
  })
  const pendingCount = queueItems.filter((item) => item.status === 'pending').length
  const conflictItems = queueItems.filter((item) => item.status === 'conflict' || item.status === 'failed')

  useEffect(() => {
    const plan = currentPlans.data?.[0]
    if (!plan || plan.plan_status !== 'current') return
    const candidate: ActiveRation = {
      version: 2,
      planVersionId: plan.id,
      planVersionNo: plan.version_no,
      updatedAt: plan.published_at,
      group: { id: plan.group_id, name: plan.group_name, count: plan.animal_count },
      milkYield: null,
      milkPriceEur: null,
      totalCostEurDay: null,
      dosingStepKg: Number(plan.dosing_step_kg),
      pendfSollGKgdm: null,
      ndfProxyGKgdm: null,
      components: plan.instructions.map((item) => ({
        feed_id: item.feed_id,
        name: item.feed_name ?? item.feed_id,
        soll_kg: item.target_batch_kg == null ? null : Number(item.target_batch_kg),
      })),
    }
    setRation(candidate)
    localStorage.setItem(ACTIVE_RATION_KEY, JSON.stringify(candidate))
  }, [currentPlans.data])

  useEffect(() => {
    if (!ration) return
    setActual(Object.fromEntries(ration.components.map((item) => [item.feed_id, item.soll_kg ?? 0])))
  }, [ration])

  const totalSoll = useMemo(() => ration?.components.reduce((sum, item) => sum + (item.soll_kg ?? 0), 0) ?? 0, [ration])
  const totalIst = useMemo(() => Object.values(actual).reduce((sum, value) => sum + Math.max(value || 0, 0), 0), [actual])
  const latest: ActualFeedingRecord | undefined = save.data ?? history.data?.[0]
  const shakerRemainder = 100 - topPct - middlePct
  const canSave = Boolean(ration?.components.length && ration.components.every((item) => item.soll_kg != null) && shakerRemainder >= 0 && tmPct > 0 && tmPct <= 100 && (cause !== 'other' || comment.trim().length >= 10))

  if (!ration && currentPlans.isLoading) return <main className="mx-auto min-h-screen max-w-md bg-slate-50 p-6 text-sm text-slate-600">Aktueller Fuetterungsplan wird geladen…</main>

  if (!ration) return <main className="mx-auto min-h-screen max-w-md bg-slate-50 p-4 text-slate-900">
    <section className="mt-12 rounded-2xl border bg-white p-6 text-center shadow-sm"><Wheat className="mx-auto mb-4 h-10 w-10 text-emerald-700" /><h1 className="text-xl font-bold">Kein aktueller Fuetterungsplan</h1><p className="mt-2 text-sm text-slate-600">Eine freigegebene Ration muss zuerst als Planversion publiziert werden. Geplante oder veraltete Versionen werden hier nicht als aktuelle Stallanweisung angeboten.</p><Button className="mt-5 w-full" asChild><a href="/futtermittel/rationsoptimierung">Zur Rationsoptimierung</a></Button></section>
  </main>

  const submit = () => save.mutate({
    plan_version_id: ration.planVersionId,
    feeding_at: new Date().toISOString(), source: 'manual', source_ref: `mobile:${commandId}`,
    cause_class: cause, comment: comment.trim() || null, supersedes_id: supersedesId,
    context: { rest_feed_kg: restKg, dry_matter_pct: tmPct,
      shaker_box: { top_pct: topPct, middle_pct: middlePct, below_8mm_pct: shakerRemainder },
      feed_temperature_c: feedTemp, ambient_temperature_c: ambientTemp },
    idempotency_key: `mobile-actual-${commandId}`,
    components: ration.components.map((item) => ({ feed_id: item.feed_id, actual_kg: actual[item.feed_id] ?? 0 })),
  })

  return <main className="mx-auto min-h-screen w-full max-w-md overflow-x-hidden bg-slate-50 pb-28 text-slate-900">
    <header className="sticky top-0 z-20 border-b bg-emerald-950 px-4 py-3 text-white shadow-sm"><div className="flex items-center gap-3"><a aria-label="Zurück" href="/futtermittel/rationsoptimierung" className="rounded-full p-2 hover:bg-white/10"><ChevronLeft /></a><div><p className="text-xs text-emerald-200">Jetzt füttern</p><h1 className="font-bold">{ration.group.name}</h1></div></div></header>
    <div className="space-y-4 p-4">
      <section className="rounded-2xl border bg-white p-4 shadow-sm"><div className="flex items-center justify-between text-xs text-slate-500"><span>{ration.group.count} Tiere</span><span>Plan v{ration.planVersionNo} · {new Date(ration.updatedAt).toLocaleString('de-DE')}</span></div><div className="mt-3 grid grid-cols-3 gap-2 text-center"><div><b className="block text-lg">{totalSoll.toFixed(0)}</b><span className="text-[11px] text-slate-500">kg FM SOLL</span></div><div><b className="block text-lg">{ration.components.length}</b><span className="text-[11px] text-slate-500">Komponenten</span></div><div><b className="block text-lg">{ration.dosingStepKg.toLocaleString('de-DE')}</b><span className="text-[11px] text-slate-500">kg Dosierschritt</span></div></div></section>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-semibold"><div className={phase === 'plan' ? 'text-emerald-800' : 'text-slate-400'}>1 SOLL</div><div className={phase === 'record' ? 'text-emerald-800' : 'text-slate-400'}>2 IST</div><div className={phase === 'result' ? 'text-emerald-800' : 'text-slate-400'}>3 Kontrolle</div></div><Progress value={phase === 'plan' ? 33 : phase === 'record' ? 66 : 100} />
      {pendingCount > 0 ? <p role="status" className="rounded-xl border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900">{pendingCount} Ist-Fütterung{pendingCount > 1 ? 'en' : ''} wartet offline auf Übertragung — wird bei Verbindung automatisch gesendet.</p> : null}
      {conflictItems.map((item) => <div key={item.id} role="alert" className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
        <p className="font-semibold">{item.status === 'conflict' ? 'Konflikt bei der Übertragung' : 'Übertragung fehlgeschlagen'}</p>
        <p className="mt-1">{item.last_error ?? 'Details unbekannt.'}</p>
        <span className="mt-2 flex gap-2">
          {item.status === 'failed' ? <Button size="sm" variant="outline" onClick={() => { queue.retry(item.id); setQueueItems(queue.items()); void replayQueue() }}>Erneut senden</Button> : null}
          <Button size="sm" variant="ghost" onClick={() => { queue.remove(item.id); setQueueItems(queue.items()) }}>Verwerfen</Button>
        </span>
      </div>)}
      {queuedOffline ? <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">Offline gespeichert — die Ist-Fütterung wird bei Verbindung automatisch und ohne Doppelstand übertragen.</p> : null}
      {phase === 'plan' && <section className="space-y-2"><h2 className="flex items-center gap-2 font-bold"><Scale className="h-5 w-5 text-emerald-700" />Mischfolge und SOLL-Mengen</h2>{ration.components.map((item, index) => <div key={item.feed_id} className="flex items-center justify-between rounded-xl border bg-white p-3"><span><small className="mr-2 text-slate-400">{index + 1}</small>{item.name}</span><b>{item.soll_kg == null ? 'Menge unbekannt' : `${item.soll_kg.toFixed(1)} kg`}</b></div>)}{ration.components.some((item) => item.soll_kg == null) ? <p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">Dieser Plan enthaelt eine unbekannte Zielmenge und kann mobil nicht als gefuettert dokumentiert werden.</p> : null}<Button size="lg" className="mt-3 h-12 w-full" disabled={!canSave} onClick={() => setPhase('record')}>Jetzt füttern</Button></section>}
      {phase === 'record' && <section className="space-y-4"><h2 className="flex items-center gap-2 font-bold"><ClipboardCheck className="h-5 w-5 text-emerald-700" />Ist-Mengen dokumentieren</h2><div className="space-y-2">{ration.components.map((item) => <NumberField key={item.feed_id} label={`${item.name} · SOLL ${item.soll_kg?.toFixed(1) ?? 'unbekannt'} kg`} value={actual[item.feed_id] ?? 0} onChange={(value) => setActual((current) => ({ ...current, [item.feed_id]: value }))} suffix="kg FM" />)}</div><div className="grid grid-cols-2 gap-2"><NumberField label="Restfutter" value={restKg} onChange={setRestKg} suffix="kg" /><NumberField label="TM gemessen" value={tmPct} onChange={setTmPct} suffix="%" /></div><h3 className="pt-2 text-sm font-bold">Schüttelbox</h3><div className="grid grid-cols-2 gap-2"><NumberField label="> 19 mm" value={topPct} onChange={setTopPct} suffix="%" /><NumberField label="8–19 mm" value={middlePct} onChange={setMiddlePct} suffix="%" /></div><p className={shakerRemainder < 0 ? 'text-xs text-status-error' : 'text-xs text-slate-500'}>Unter 8 mm: {shakerRemainder.toFixed(1)} % (automatisch)</p><h3 className="flex items-center gap-2 pt-2 text-sm font-bold"><Thermometer className="h-4 w-4" />Temperatur</h3><div className="grid grid-cols-2 gap-2"><NumberField label="Futtertisch" value={feedTemp} onChange={setFeedTemp} suffix="°C" /><NumberField label="Umgebung" value={ambientTemp} onChange={setAmbientTemp} suffix="°C" /></div><div className="grid gap-2 text-sm font-medium"><Label htmlFor="actual-cause">Ursache</Label><select id="actual-cause" className="h-11 rounded-xl border bg-white px-3" value={cause} onChange={(event) => setCause(event.target.value as ActualCause)}><option value="normal">Planmaessig</option><option value="stock_substitution">Bestandsbedingter Ersatz</option><option value="dosing_error">Dosierabweichung</option><option value="feed_quality">Futterqualitaet</option><option value="animal_intake">Tieraufnahme/Restfutter</option><option value="technical">Technische Ursache</option><option value="other">Sonstige Ursache</option></select></div><div className="grid gap-2 text-sm font-medium"><Label htmlFor="actual-comment">Kommentar</Label><Input id="actual-comment" value={comment} onChange={(event) => setComment(event.target.value)} placeholder={cause === 'other' ? 'Mindestens 10 Zeichen erforderlich' : 'Optionaler Kontext'} /></div>{save.error && !queuedOffline && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">Speichern fehlgeschlagen. Verbindung, Planstatus und Eingaben prüfen; ein Retry erzeugt keinen Doppelstand.</p>}<div className="rounded-xl bg-slate-100 p-3 text-xs text-slate-600">IST gesamt {totalIst.toFixed(1)} kg · SOLL {totalSoll.toFixed(1)} kg</div><Button size="lg" className="h-12 w-full" disabled={!canSave || save.isPending} onClick={submit}><Save className="mr-2 h-5 w-5" />{save.isPending ? 'Speichert…' : 'Ist-Fütterung speichern'}</Button></section>}
      {phase === 'result' && latest && <section className="space-y-4"><div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4"><CheckCircle2 className="mb-2 h-8 w-8 text-emerald-700" /><h2 className="text-lg font-bold">Ist-Fütterung gespeichert</h2><p className="text-sm text-emerald-900">Planversion, Komponenten und Ursache sind revisionssicher dokumentiert.</p></div>{latest.components.map((item) => <div key={item.id} className="rounded-xl border bg-white p-3"><div className="flex justify-between gap-3"><b>{item.feed_name ?? item.feed_id}</b><span className={item.delta_kg === 0 ? 'text-emerald-700' : 'text-amber-800'}>{item.delta_kg > 0 ? '+' : ''}{Number(item.delta_kg).toLocaleString('de-DE')} kg · {item.delta_pct == null ? 'Prozent nicht ableitbar' : `${Number(item.delta_pct).toLocaleString('de-DE')} %`}</span></div>{item.value_consequences.cost ? <p className="mt-1 text-xs text-slate-600">Kostenfolge {Number(item.value_consequences.cost.delta_eur).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</p> : <p className="mt-1 flex gap-1 text-xs text-amber-800"><AlertTriangle className="h-4 w-4" />Kostenfolge wegen fehlendem Preis unbekannt</p>}</div>)}<Button variant="outline" className="h-12 w-full" onClick={() => { setSupersedesId(latest.id); setCommandId(crypto.randomUUID()); setPhase('record') }}>Als neue Korrektur erfassen</Button></section>}
      <p className="text-center text-[11px] text-slate-500">{history.data?.length ?? 0} Protokolle der letzten 14 Einträge · kein Solver auf dem Mobilgerät</p>
    </div>
  </main>
}
