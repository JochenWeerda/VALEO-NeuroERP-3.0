import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, Copy, Database, FileJson, Radio, TestTube, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  importRationsData,
  fetchRationsImports,
  getRationsApiErrorMessage,
  type RationsIntegrationAdapter,
  type RationsImportResult,
} from '@/lib/api/rations-optimization'

type AdapterMeta = {
  id: RationsIntegrationAdapter
  label: string
  target: string
  hint: string
  icon: React.ReactNode
  sample: Record<string, unknown>
}

// Beispiel-Payloads spiegeln die Adapter-Vertraege (bereits dekodiertes JSON an der Transportgrenze).
const ADAPTERS: AdapterMeta[] = [
  {
    id: 'agrirouter',
    label: 'agrirouter (Mischwagen)',
    target: 'F1-Fütterungsprotokoll',
    hint: 'EFDI/TaskData-Ist-Mengen vom Mischwagen → SOLL/IST-Kontrolle & IOFC.',
    icon: <Radio className="h-4 w-4" />,
    sample: {
      message_type: 'iso:11783:-10:time_log:protobuf',
      context_id: 'ctx-2026-07-13-01',
      group_id: 'g1',
      feeding_date: '2026-07-13',
      animal_count: 58,
      dry_matter_pct: 40,
      rest_feed_kg: 45,
      milk_kg_cow: 32,
      milk_price_eur_kg: 0.45,
      feed_cost_eur_cow: 6.2,
      feed_temp_c: 21,
      ambient_temp_c: 18,
      components: [
        { ddi: 'ddi-1', label: 'Maissilage', target_kg: 600, actual_kg: 612 },
        { ddi: 'ddi-2', label: 'Grassilage', target_kg: 300, actual_kg: 296 },
      ],
    },
  },
  {
    id: 'icar-ade',
    label: 'ICAR-ADE (LKV/MLP)',
    target: 'CowProfile',
    hint: 'Milchleistungsprüfung → Tierprofil inkl. Laktose & Milchharnstoff.',
    icon: <Database className="h-4 w-4" />,
    sample: {
      ade_version: '1.5.0',
      event_id: 'mlp-2026-07-13-01',
      milkRecordingStatistics: {
        milkYield: 36.2,
        fatPercent: 4.1,
        proteinPercent: 3.45,
        lactosePercent: 4.82,
        liveWeight: 680,
        daysInMilk: 95,
        parity: 3,
        ureaMgDl: 21,
      },
    },
  },
  {
    id: 'laboratory',
    label: 'Labor (LKS/LUFA/Eurofins)',
    target: 'FeedIngredient',
    hint: 'Normalisierte Futteranalyse je Charge/Silo → Futtermittel-Stammwerte.',
    icon: <TestTube className="h-4 w-4" />,
    sample: {
      laboratory: 'LKS',
      sampleId: 'LKS-2026-42',
      feedName: 'Grassilage Silo 2',
      dryMatterPercent: 36.5,
      metabolizableEnergyMjKgDm: 10.8,
      sidProteinGKgDm: 152,
      ndfGKgDm: 415,
      starchGKgDm: 18,
      crudeFatGKgDm: 34,
      sampledAt: '2026-07-10',
      batchId: 'silo-2',
    },
  },
]

export default function RationsSchnittstellenImport() {
  const [adapterId, setAdapterId] = useState<RationsIntegrationAdapter>('agrirouter')
  const adapter = useMemo(() => ADAPTERS.find((a) => a.id === adapterId) ?? ADAPTERS[0], [adapterId])
  const [raw, setRaw] = useState<string>(() => JSON.stringify(ADAPTERS[0].sample, null, 2))
  const [result, setResult] = useState<RationsImportResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const journal = useQuery({
    queryKey: ['rations-imports', adapterId],
    queryFn: () => fetchRationsImports(adapterId, 25),
  })

  const importMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) => importRationsData(adapterId, payload),
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      void journal.refetch()
    },
    onError: (err: unknown) => {
      setResult(null)
      setError(getRationsApiErrorMessage(err, 'Import fehlgeschlagen'))
    },
  })

  function selectAdapter(next: RationsIntegrationAdapter) {
    setAdapterId(next)
    setResult(null)
    setError(null)
    const meta = ADAPTERS.find((a) => a.id === next) ?? ADAPTERS[0]
    setRaw(JSON.stringify(meta.sample, null, 2))
  }

  function loadSample() {
    setRaw(JSON.stringify(adapter.sample, null, 2))
    setError(null)
  }

  function submit() {
    if (importMut.isPending) return
    let payload: Record<string, unknown>
    try {
      payload = JSON.parse(raw) as Record<string, unknown>
    } catch {
      setError('Ungültiges JSON — bitte Eingabe prüfen.')
      setResult(null)
      return
    }
    importMut.mutate(payload)
  }

  return (
    <main className="mx-auto w-full max-w-5xl space-y-5 p-5 text-slate-900">
      <header className="rounded-2xl bg-gradient-to-r from-emerald-800 to-emerald-950 p-5 text-white shadow">
        <div className="flex items-center gap-2 text-emerald-200">
          <Upload className="h-5 w-5" />
          <span className="text-xs font-semibold uppercase tracking-wide">Rations-Schnittstellen</span>
        </div>
        <h1 className="mt-1 text-2xl font-bold">Datenimport agrirouter · ICAR-ADE · Labor</h1>
        <p className="mt-1 text-sm text-emerald-100">
          Bereits dekodiertes JSON je Standard einreichen. Ergebnisse münden in die kanonischen Modelle
          (Fütterungsprotokoll, Tierprofil, Futtermittel); der Transport/Provider-Anschluss bleibt konfigurativ.
        </p>
      </header>

      {/* Adapterauswahl */}
      <div className="grid gap-3 sm:grid-cols-3">
        {ADAPTERS.map((a) => (
          <button
            key={a.id}
            type="button"
            onClick={() => selectAdapter(a.id)}
            className="rounded-xl border p-3 text-left transition-colors"
            style={{
              background: a.id === adapterId ? '#ECFDF5' : '#fff',
              borderColor: a.id === adapterId ? '#059669' : '#E2E8F0',
            }}
          >
            <div className="flex items-center gap-2 font-semibold text-emerald-900">{a.icon}{a.label}</div>
            <div className="mt-1 text-[11px] font-medium text-slate-500">→ {a.target}</div>
            <div className="mt-1 text-xs text-slate-600">{a.hint}</div>
          </button>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Eingabe */}
        <section className="rounded-2xl border bg-white p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-bold"><FileJson className="h-5 w-5 text-emerald-700" />Payload ({adapter.label})</h2>
            <Button variant="outline" size="sm" onClick={loadSample}><Copy className="mr-1 h-4 w-4" />Beispiel laden</Button>
          </div>
          <textarea
            className="h-80 w-full rounded-lg border border-slate-300 p-3 font-mono text-xs outline-none focus:ring-2 focus:ring-emerald-500"
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            spellCheck={false}
            aria-label="JSON-Payload"
          />
          {error && (
            <div role="alert" className="mt-2 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />{error}
            </div>
          )}
          <Button className="mt-3 h-11 w-full" disabled={importMut.isPending} onClick={submit}>
            <Upload className="mr-2 h-5 w-5" />{importMut.isPending ? 'Importiert…' : 'Importieren'}
          </Button>
        </section>

        {/* Ergebnis */}
        <section className="rounded-2xl border bg-white p-4 shadow-sm">
          <h2 className="mb-2 font-bold">Import-Ergebnis</h2>
          {!result && <p className="text-sm text-slate-500">Noch kein Import in dieser Sitzung.</p>}
          {result && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 rounded-lg border p-3" style={{ borderColor: result.duplicate ? '#FCD34D' : '#6EE7B7', background: result.duplicate ? '#FFFBEB' : '#ECFDF5' }}>
                {result.duplicate
                  ? <AlertTriangle className="h-5 w-5 text-amber-600" />
                  : <CheckCircle2 className="h-5 w-5 text-emerald-600" />}
                <span className="text-sm font-semibold">
                  {result.duplicate ? 'Bereits importiert (idempotent übersprungen)' : 'Import erfolgreich'}
                </span>
              </div>
              <dl className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded-lg border p-2"><dt className="text-slate-500">Zielmodell</dt><dd className="font-semibold">{String(result.target_model ?? '–')}</dd></div>
                <div className="rounded-lg border p-2"><dt className="text-slate-500">Externe ID</dt><dd className="font-mono">{String(result.external_id ?? '–')}</dd></div>
                <div className="rounded-lg border p-2"><dt className="text-slate-500">Quelle/Version</dt><dd>{String(result.source ?? adapter.id)} · {String(result.source_version ?? '–')}</dd></div>
                <div className="rounded-lg border p-2"><dt className="text-slate-500">Importiert</dt><dd>{result.imported_at ? new Date(result.imported_at).toLocaleString('de-DE') : '–'}</dd></div>
              </dl>
              {result.feeding_control != null && (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs">
                  <div className="font-semibold text-emerald-900">F1-Kontrolle erzeugt</div>
                  <pre className="mt-1 max-h-40 overflow-auto whitespace-pre-wrap break-all text-[11px] text-emerald-900">
                    {JSON.stringify(result.feeding_control, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      {/* Importjournal */}
      <section className="rounded-2xl border bg-white p-4 shadow-sm">
        <h2 className="mb-2 font-bold">Importjournal ({adapter.label})</h2>
        {journal.isLoading && <p className="text-sm text-slate-500">Lade Journal…</p>}
        {journal.isError && <p className="text-sm text-red-600">Journal konnte nicht geladen werden.</p>}
        {journal.data && journal.data.length === 0 && <p className="text-sm text-slate-500">Noch keine Importe für diesen Adapter.</p>}
        {journal.data && journal.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b text-slate-500">
                  <th className="py-2 pr-3">Zeitpunkt</th>
                  <th className="py-2 pr-3">Externe ID</th>
                  <th className="py-2 pr-3">Zielmodell</th>
                  <th className="py-2 pr-3">Version</th>
                </tr>
              </thead>
              <tbody>
                {journal.data.map((row) => (
                  <tr key={row.id} className="border-b last:border-0">
                    <td className="py-2 pr-3">{new Date(row.imported_at).toLocaleString('de-DE')}</td>
                    <td className="py-2 pr-3 font-mono">{row.external_id}</td>
                    <td className="py-2 pr-3">{row.target_model}</td>
                    <td className="py-2 pr-3">{row.source_version ?? '–'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}
