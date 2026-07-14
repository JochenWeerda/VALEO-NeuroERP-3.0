import { useState } from 'react'
import { AlertTriangle, Beaker, Leaf, Scale, Sprout, TrendingUp } from 'lucide-react'
import {
  usePortalDuengebilanz,
  usePortalDuengebedarf,
  usePortalStoffstrombilanz,
  usePortalPflanzenschutzUebersicht,
  usePortalErnteAuswertung,
} from '@/lib/api/portal'

type TabId = 'bilanz' | 'bedarf' | 'stoffstrom' | 'psm' | 'ernte'

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: 'bedarf', label: 'Düngebedarf', icon: <Sprout className="h-4 w-4" /> },
  { id: 'bilanz', label: 'Düngebilanz (170 kg N)', icon: <Scale className="h-4 w-4" /> },
  { id: 'stoffstrom', label: 'Stoffstrombilanz', icon: <TrendingUp className="h-4 w-4" /> },
  { id: 'psm', label: 'Pflanzenschutz', icon: <Beaker className="h-4 w-4" /> },
  { id: 'ernte', label: 'Ernte & Leistung', icon: <Leaf className="h-4 w-4" /> },
]

function num(v: unknown, d = 1): string {
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) ? n.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) : '–'
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="border-b px-3 py-2 text-left text-xs font-semibold text-slate-500">{children}</th>
}
function Td({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <td className={`border-b px-3 py-2 text-sm ${className}`}>{children}</td>
}

function rows(data: unknown): Record<string, unknown>[] {
  const s = (data as { schlaege?: unknown } | undefined)?.schlaege
  return Array.isArray(s) ? (s as Record<string, unknown>[]) : []
}

export default function PortalFeldbuchAuswertungen() {
  const [tab, setTab] = useState<TabId>('bedarf')
  const bilanz = usePortalDuengebilanz()
  const bedarf = usePortalDuengebedarf()
  const stoffstrom = usePortalStoffstrombilanz()
  const psm = usePortalPflanzenschutzUebersicht()
  const ernte = usePortalErnteAuswertung()

  return (
    <main className="mx-auto w-full max-w-6xl space-y-5 p-5 text-slate-900">
      <header className="rounded-2xl bg-linear-to-r from-emerald-800 to-emerald-950 p-5 text-white shadow">
        <div className="flex items-center gap-2 text-emerald-200">
          <Scale className="h-5 w-5" />
          <span className="text-xs font-semibold uppercase tracking-wide">Ackerschlagkartei</span>
        </div>
        <h1 className="mt-1 text-2xl font-bold">DüV-Auswertungen</h1>
        <p className="mt-1 text-sm text-emerald-100">
          Düngebedarf, Düngebilanz (170 kg N/ha org.), Nährstoffvergleich/Stoffstrombilanz, Spritztagebuch und
          Ernte-Auswertung nach Düngeverordnung, StoffBilV und Pflanzenschutzgesetz.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-semibold transition-colors"
            style={{ background: tab === t.id ? '#059669' : '#fff', color: tab === t.id ? '#fff' : '#334155', borderColor: tab === t.id ? '#059669' : '#e2e8f0' }}
          >
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      <section className="overflow-x-auto rounded-2xl border bg-white p-1 shadow-sm">
        {tab === 'bedarf' && (
          <table className="w-full">
            <thead><tr><Th>Schlag</Th><Th>Kultur</Th><Th>Sollwert N</Th><Th>Nmin</Th><Th>N-Bedarf kg/ha</Th><Th>Ausgebracht kg/ha</Th><Th>Restbedarf kg</Th></tr></thead>
            <tbody>
              {rows(bedarf.data).map((r, i) => (
                <tr key={i}>
                  <Td>{String(r.schlagName ?? '–')}</Td><Td>{String(r.kultur ?? '–')}</Td>
                  <Td>{num(r.nSollwertKgHa, 0)}</Td><Td>{num(r.nminFruehjahrKgHa, 0)}</Td>
                  <Td className="font-semibold">{num(r.nBedarfKgHa, 0)}</Td><Td>{num(r.nAusgebrachtKgHa, 0)}</Td>
                  <Td className={Number(r.nRestbedarfKg) < 0 ? 'font-semibold text-red-600' : 'text-emerald-700'}>{num(r.nRestbedarfKg, 0)}</Td>
                </tr>
              ))}
              {rows(bedarf.data).length === 0 && <tr><Td className="text-slate-500">Keine Schläge mit Sollwert erfasst.</Td></tr>}
            </tbody>
          </table>
        )}
        {tab === 'bilanz' && (
          <table className="w-full">
            <thead><tr><Th>Schlag</Th><Th>N gesamt</Th><Th>N organisch</Th><Th>N org. kg/ha</Th><Th>P₂O₅</Th><Th>K₂O</Th><Th>170-kg-Grenze</Th></tr></thead>
            <tbody>
              {rows(bilanz.data).map((r, i) => {
                const chk = (r.duevOrgCheck ?? {}) as Record<string, unknown>
                const over = Boolean(chk.ueberschritten)
                return (
                  <tr key={i}>
                    <Td>{String(r.schlagName ?? '–')}</Td><Td>{num(r.nKg)}</Td><Td>{num(r.nOrganischKg)}</Td>
                    <Td>{num(chk.nOrganischProHa)}</Td><Td>{num(r.p2o5Kg)}</Td><Td>{num(r.k2oKg)}</Td>
                    <Td className={over ? 'font-semibold text-red-600' : 'text-emerald-700'}>
                      {over ? <span className="inline-flex items-center gap-1"><AlertTriangle className="h-4 w-4" />überschritten</span> : `${num(chk.auslastungPct, 0)} %`}
                    </Td>
                  </tr>
                )
              })}
              {rows(bilanz.data).length === 0 && <tr><Td className="text-slate-500">Keine Düngungsmaßnahmen erfasst.</Td></tr>}
            </tbody>
          </table>
        )}
        {tab === 'stoffstrom' && (
          <div className="p-3">
            <div className="mb-3 grid gap-3 sm:grid-cols-2">
              {(['n', 'p2o5'] as const).map((k) => {
                const betrieb = (stoffstrom.data as { betrieb?: Record<string, Record<string, unknown>> } | undefined)?.betrieb
                const b: Record<string, unknown> = betrieb?.[k] ?? {}
                const saldo = Number(b.saldo_kg)
                return (
                  <div key={k} className="rounded-xl border p-3">
                    <div className="text-xs font-semibold uppercase text-slate-500">{k === 'n' ? 'N' : 'P₂O₅'} Betriebssaldo</div>
                    <div className={`text-2xl font-bold ${saldo > 0 ? 'text-amber-600' : 'text-emerald-700'}`}>{num(saldo)} kg</div>
                    <div className="text-xs text-slate-500">Zufuhr {num((b as Record<string, unknown>).zufuhr_kg)} − Abfuhr {num((b as Record<string, unknown>).abfuhr_kg)}</div>
                  </div>
                )
              })}
            </div>
            <table className="w-full">
              <thead><tr><Th>Kultur</Th><Th>N Zufuhr</Th><Th>N Abfuhr</Th><Th>N Saldo</Th><Th>P₂O₅ Saldo</Th></tr></thead>
              <tbody>
                {rows(stoffstrom.data).map((r, i) => (
                  <tr key={i}>
                    <Td>{String(r.kultur ?? '–')}</Td><Td>{num(r.nZufuhrKg)}</Td><Td>{num(r.nAbfuhrKg)}</Td>
                    <Td className={Number(r.nSaldoKg) > 0 ? 'text-amber-600' : 'text-emerald-700'}>{num(r.nSaldoKg)}</Td>
                    <Td>{num(r.p2o5SaldoKg)}</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {tab === 'psm' && (
          <div className="p-3">
            <div className="mb-3 flex flex-wrap gap-2 text-sm">
              {(() => {
                const s = ((psm.data as { kostensplit?: Record<string, unknown> } | undefined)?.kostensplit ?? {})
                return (['herbizide', 'fungizide', 'insektizide', 'sonstiges', 'gesamt'] as const).map((k) => (
                  <span key={k} className="rounded-lg border px-3 py-1"><b>{num(s[k], 2)} €</b> <span className="text-slate-500">{k}</span></span>
                ))
              })()}
            </div>
            <table className="w-full">
              <thead><tr><Th>Datum</Th><Th>Schlag</Th><Th>Mittel</Th><Th>Wirkungsbereich</Th><Th>Anwender</Th><Th>Pflichtangaben</Th></tr></thead>
              <tbody>
                {(((psm.data as { massnahmen?: Record<string, unknown>[] } | undefined)?.massnahmen) ?? []).map((r, i) => (
                  <tr key={i}>
                    <Td>{String(r.datum ?? '–')}</Td><Td>{String(r.schlagName ?? '–')}</Td><Td>{String(r.mittel ?? '–')}</Td>
                    <Td>{String(r.wirkungsbereich ?? '–')}</Td><Td>{String(r.anwender ?? '–')}</Td>
                    <Td className={r.compliant ? 'text-emerald-700' : 'font-semibold text-red-600'}>
                      {r.compliant ? 'vollständig' : `fehlt: ${(r.fehlendePflichtangaben as string[] | undefined)?.join(', ') ?? ''}`}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {tab === 'ernte' && (
          <table className="w-full">
            <thead><tr><Th>Schlag</Th><Th>Kultur</Th><Th>Ertrag dt/ha</Th><Th>Erlös €</Th><Th>Direktkosten €</Th><Th>DfL €</Th><Th>DfL €/ha</Th></tr></thead>
            <tbody>
              {rows(ernte.data).map((r, i) => (
                <tr key={i}>
                  <Td>{String(r.schlagName ?? '–')}</Td><Td>{String(r.kultur ?? '–')}</Td><Td>{num(r.ertragDtHa)}</Td>
                  <Td>{num(r.erloesEur, 2)}</Td><Td>{num(r.direktkostenEur, 2)}</Td>
                  <Td className="font-semibold">{num(r.direktkostenfreieLeistungEur, 2)}</Td><Td>{num(r.direktkostenfreieLeistungEurHa, 2)}</Td>
                </tr>
              ))}
              {rows(ernte.data).length === 0 && <tr><Td className="text-slate-500">Noch keine Ernte-/Kostendaten erfasst.</Td></tr>}
            </tbody>
          </table>
        )}
      </section>

      <p className="text-center text-[11px] text-slate-500">
        Auswertungen nach DüV/StoffBilV/PflSchG · Orientierungswerte, betriebsspezifisch zu prüfen · kein Ersatz für die amtliche Meldung.
      </p>
    </main>
  )
}
