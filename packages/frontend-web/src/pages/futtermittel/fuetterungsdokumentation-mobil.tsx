import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, ChevronLeft, ClipboardCheck, Save, Scale, Thermometer, Wheat } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { fetchFeedingControlLogs, saveFeedingControlLog, type FeedingControlResult } from '@/lib/api/rations-optimization'

const ACTIVE_RATION_KEY = 'valeo.rations.active-mobile.v1'

type ActiveRation = {
  version: 1
  updatedAt: string
  group: { id: string; name: string; count: number }
  milkYield: number
  milkPriceEur: number
  totalCostEurDay: number
  pendfSollGKgdm: number | null
  ndfProxyGKgdm: number | null
  components: Array<{ feed_id: string; name: string; soll_kg: number }>
}

type Phase = 'plan' | 'record' | 'result'

function readActiveRation(): ActiveRation | null {
  try {
    const raw = localStorage.getItem(ACTIVE_RATION_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as ActiveRation
    return parsed?.version === 1 && Array.isArray(parsed.components) ? parsed : null
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
  const [ration] = useState<ActiveRation | null>(() => readActiveRation())
  const [phase, setPhase] = useState<Phase>('plan')
  const [actual, setActual] = useState<Record<string, number>>({})
  const [restKg, setRestKg] = useState(0)
  const [tmPct, setTmPct] = useState(40)
  const [topPct, setTopPct] = useState(8)
  const [middlePct, setMiddlePct] = useState(42)
  const [feedTemp, setFeedTemp] = useState(20)
  const [ambientTemp, setAmbientTemp] = useState(18)
  const groupId = ration?.group.id ?? ''
  const history = useQuery({ queryKey: ['feeding-control-mobile', groupId], queryFn: () => fetchFeedingControlLogs(groupId, 14), enabled: Boolean(groupId) })
  const save = useMutation({ mutationFn: saveFeedingControlLog, onSuccess: () => { setPhase('result'); void history.refetch() } })

  useEffect(() => {
    if (!ration) return
    setActual(Object.fromEntries(ration.components.map((item) => [item.feed_id, item.soll_kg])))
  }, [ration])

  const totalSoll = useMemo(() => ration?.components.reduce((sum, item) => sum + item.soll_kg, 0) ?? 0, [ration])
  const totalIst = useMemo(() => Object.values(actual).reduce((sum, value) => sum + Math.max(value || 0, 0), 0), [actual])
  const latest: FeedingControlResult | undefined = save.data?.control_result ?? history.data?.[0]?.control_result
  const shakerRemainder = 100 - topPct - middlePct
  const canSave = Boolean(ration?.components.length && shakerRemainder >= 0 && tmPct > 0 && tmPct <= 100)

  if (!ration) return <main className="mx-auto min-h-screen max-w-md bg-slate-50 p-4 text-slate-900">
    <section className="mt-12 rounded-2xl border bg-white p-6 text-center shadow-sm"><Wheat className="mx-auto mb-4 h-10 w-10 text-emerald-700" /><h1 className="text-xl font-bold">Keine aktive Ration</h1><p className="mt-2 text-sm text-slate-600">Ration zuerst in der Rationsoptimierung berechnen und freigeben. Danach steht sie hier ohne Solver für die Stallarbeit bereit.</p><Button className="mt-5 w-full" asChild><a href="/futtermittel/rationsoptimierung">Zur Rationsoptimierung</a></Button></section>
  </main>

  const submit = () => save.mutate({
    group_id: ration.group.id,
    feeding_date: new Date().toISOString().slice(0, 10),
    ration_ref: `mobile:${ration.updatedAt}`,
    komponenten: ration.components.map((item) => ({ ...item, ist_kg: actual[item.feed_id] ?? 0 })),
    restfutter_kg: restKg,
    tierzahl: ration.group.count,
    tm_pct: tmPct,
    milch_kg_kuh: ration.milkYield,
    milchpreis_eur_kg: ration.milkPriceEur,
    futterkosten_eur_kuh: ration.totalCostEurDay,
    futtertisch_temp_c: feedTemp,
    umgebung_temp_c: ambientTemp,
    schuettelbox: { oben_pct: topPct, mitte_pct: middlePct, unten_pct: shakerRemainder, fein_pct: 0, pendf_soll_g_kgdm: ration.pendfSollGKgdm, ndf_g_kgdm: ration.ndfProxyGKgdm },
  })

  return <main className="mx-auto min-h-screen w-full max-w-md overflow-x-hidden bg-slate-50 pb-28 text-slate-900">
    <header className="sticky top-0 z-20 border-b bg-emerald-950 px-4 py-3 text-white shadow-sm"><div className="flex items-center gap-3"><a aria-label="Zurück" href="/futtermittel/rationsoptimierung" className="rounded-full p-2 hover:bg-white/10"><ChevronLeft /></a><div><p className="text-xs text-emerald-200">Jetzt füttern</p><h1 className="font-bold">{ration.group.name}</h1></div></div></header>
    <div className="space-y-4 p-4">
      <section className="rounded-2xl border bg-white p-4 shadow-sm"><div className="flex items-center justify-between text-xs text-slate-500"><span>{ration.group.count} Kühe</span><span>Stand {new Date(ration.updatedAt).toLocaleString('de-DE')}</span></div><div className="mt-3 grid grid-cols-3 gap-2 text-center"><div><b className="block text-lg">{totalSoll.toFixed(0)}</b><span className="text-[11px] text-slate-500">kg FM SOLL</span></div><div><b className="block text-lg">{ration.milkYield.toFixed(1)}</b><span className="text-[11px] text-slate-500">kg Milch</span></div><div><b className="block text-lg">{ration.totalCostEurDay.toFixed(2)}</b><span className="text-[11px] text-slate-500">€/Kuh</span></div></div></section>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-semibold"><div className={phase === 'plan' ? 'text-emerald-800' : 'text-slate-400'}>1 SOLL</div><div className={phase === 'record' ? 'text-emerald-800' : 'text-slate-400'}>2 IST</div><div className={phase === 'result' ? 'text-emerald-800' : 'text-slate-400'}>3 Kontrolle</div></div><Progress value={phase === 'plan' ? 33 : phase === 'record' ? 66 : 100} />
      {phase === 'plan' && <section className="space-y-2"><h2 className="flex items-center gap-2 font-bold"><Scale className="h-5 w-5 text-emerald-700" />Mischfolge und SOLL-Mengen</h2>{ration.components.map((item, index) => <div key={item.feed_id} className="flex items-center justify-between rounded-xl border bg-white p-3"><span><small className="mr-2 text-slate-400">{index + 1}</small>{item.name}</span><b>{item.soll_kg.toFixed(1)} kg</b></div>)}<Button size="lg" className="mt-3 h-12 w-full" onClick={() => setPhase('record')}>Jetzt füttern</Button></section>}
      {phase === 'record' && <section className="space-y-4"><h2 className="flex items-center gap-2 font-bold"><ClipboardCheck className="h-5 w-5 text-emerald-700" />Ist-Mengen dokumentieren</h2><div className="space-y-2">{ration.components.map((item) => <NumberField key={item.feed_id} label={`${item.name} · SOLL ${item.soll_kg.toFixed(1)} kg`} value={actual[item.feed_id] ?? 0} onChange={(value) => setActual((current) => ({ ...current, [item.feed_id]: value }))} suffix="kg FM" />)}</div><div className="grid grid-cols-2 gap-2"><NumberField label="Restfutter" value={restKg} onChange={setRestKg} suffix="kg" /><NumberField label="TM gemessen" value={tmPct} onChange={setTmPct} suffix="%" /></div><h3 className="pt-2 text-sm font-bold">Schüttelbox</h3><div className="grid grid-cols-2 gap-2"><NumberField label="> 19 mm" value={topPct} onChange={setTopPct} suffix="%" /><NumberField label="8–19 mm" value={middlePct} onChange={setMiddlePct} suffix="%" /></div><p className={shakerRemainder < 0 ? 'text-xs text-status-error' : 'text-xs text-slate-500'}>Unter 8 mm: {shakerRemainder.toFixed(1)} % (automatisch)</p><h3 className="flex items-center gap-2 pt-2 text-sm font-bold"><Thermometer className="h-4 w-4" />Temperatur</h3><div className="grid grid-cols-2 gap-2"><NumberField label="Futtertisch" value={feedTemp} onChange={setFeedTemp} suffix="°C" /><NumberField label="Umgebung" value={ambientTemp} onChange={setAmbientTemp} suffix="°C" /></div>{save.error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">Speichern fehlgeschlagen. Verbindung und Eingaben prüfen.</p>}<div className="rounded-xl bg-slate-100 p-3 text-xs text-slate-600">IST gesamt {totalIst.toFixed(1)} kg · SOLL {totalSoll.toFixed(1)} kg</div><Button size="lg" className="h-12 w-full" disabled={!canSave || save.isPending} onClick={submit}><Save className="mr-2 h-5 w-5" />{save.isPending ? 'Speichert…' : 'Protokoll speichern'}</Button></section>}
      {phase === 'result' && latest && <section className="space-y-4"><div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4"><CheckCircle2 className="mb-2 h-8 w-8 text-emerald-700" /><h2 className="text-lg font-bold">Kontrolle gespeichert</h2><p className="text-sm text-emerald-900">Der DLG-Regelkreis ist für heute dokumentiert.</p></div><div className="grid grid-cols-2 gap-2">{[[`${latest.mischgenauigkeit_pct ?? '–'} %`,'Mischabweichung'],[`${latest.tm_verzehr_kg_kuh ?? '–'} kg`,'TM-Verzehr/Kuh'],[`${latest.iofc_eur_kuh ?? '–'} €`,'IOFC/Kuh'],[`${latest.schuettelbox?.pendf_ist_g_kgdm ?? '–'}`,'peNDF IST g/kg']].map(([value,label]) => <div key={label} className="rounded-xl border bg-white p-3"><b className="block text-lg">{value}</b><span className="text-xs text-slate-500">{label}</span></div>)}</div>{latest.warnungen.map((warning) => <div key={warning} className="flex gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"><AlertTriangle className="h-5 w-5 shrink-0" />{warning}</div>)}{latest.anpassungsvorschlaege.map((item) => <div key={item} className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900"><b className="block">Nächster Schritt</b>{item}</div>)}<Button variant="outline" className="h-12 w-full" onClick={() => setPhase('record')}>Protokoll korrigieren</Button></section>}
      <p className="text-center text-[11px] text-slate-500">{history.data?.length ?? 0} Protokolle der letzten 14 Einträge · kein Solver auf dem Mobilgerät</p>
    </div>
  </main>
}