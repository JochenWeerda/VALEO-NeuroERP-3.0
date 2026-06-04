import { Fragment, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Target, TrendingUp, Sparkles, Loader2, ArrowRight, Milk, Search } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useBedarfsdeckung, usePipeline, type ProduktgruppeDeckung } from '@/lib/api/bedarfsdeckung'

/**
 * Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — „Die Lücke ist das Vertriebsobjekt".
 *
 * Pro Betrieb: objektiver Jahresbedarf je Produktgruppe vs. Ist-Bezug (12 M) →
 * Deckungsgrad, Bedarfslücke €, Next-Best-Offer als direkt ausführbare Aktion.
 * Betrieb über ?kunde= oder die Schnellauswahl (größte Chancen) wählen.
 */

const EUR = (n: number) => `${n.toLocaleString('de-DE', { maximumFractionDigits: 0 })  } €`

const AKTION_BADGE: Record<string, string> = {
  Einstieg: 'bg-violet-100 text-violet-700',
  'Cross-Sell': 'bg-amber-100 text-amber-700',
  Ausbauen: 'bg-blue-100 text-blue-700',
  Halten: 'bg-emerald-100 text-emerald-700',
}

const SPARTE_LABEL: Record<string, string> = { milchvieh: 'Milchvieh', ackerbau: 'Ackerbau' }
const SPARTE_BADGE: Record<string, string> = {
  milchvieh: 'bg-sky-100 text-sky-700',
  ackerbau: 'bg-lime-100 text-lime-700',
}

function deckungColor(pct: number): string {
  if (pct >= 80) return 'bg-emerald-500'
  if (pct >= 40) return 'bg-blue-500'
  if (pct > 0) return 'bg-amber-500'
  return 'bg-violet-500'
}

function DeckungBar({ pct }: { pct: number }): JSX.Element {
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
        <div className={`h-full ${deckungColor(pct)}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="w-9 text-right text-xs tabular-nums">{pct}%</span>
    </div>
  )
}

export default function BedarfsdeckungCockpitPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const kundenNr = searchParams.get('kunde') || ''
  const [term, setTerm] = useState('')

  const cockpit = useBedarfsdeckung(kundenNr || undefined)
  const pipeline = usePipeline(100)

  const data = cockpit.data
  const quickPicks = useMemo(() => {
    const list = pipeline.data ?? []
    if (!term.trim()) return list.slice(0, 8)
    const t = term.trim().toLowerCase()
    return list.filter((p) => (p.name ?? '').toLowerCase().includes(t) || p.kunden_nr.toLowerCase().includes(t)).slice(0, 8)
  }, [pipeline.data, term])

  function pick(nr: string) {
    setSearchParams({ kunde: nr })
  }

  function angebot(gruppeKey?: string) {
    if (!data) return
    const params = new URLSearchParams({ kunde: data.kunden_nr, entryMode: 'bedarfsluecke' })
    if (data.name) params.set('kundeName', data.name)
    if (gruppeKey) params.set('subject', `Bedarfslücke ${gruppeKey}`)
    navigate(`/sales/angebot-erstellen?${params.toString()}`)
  }

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold"><Target className="h-7 w-7 text-blue-600" />Bedarfsdeckung</h1>
        <p className="text-muted-foreground">Objektiver Jahresbedarf je Produktgruppe vs. Ist-Bezug — die Lücke ist das Vertriebsobjekt.</p>
      </div>

      {/* Betrieb-Auswahl */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 p-3">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Betrieb suchen (Name/Nr.)…" value={term} onChange={(e) => setTerm(e.target.value)} className="pl-10" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {quickPicks.map((p) => (
              <button key={p.kunden_nr} onClick={() => pick(p.kunden_nr)}
                className={`rounded border px-2 py-1 text-xs hover:bg-muted ${p.kunden_nr === kundenNr ? 'border-blue-500 bg-blue-50' : ''}`}>
                {p.name} <span className="text-muted-foreground">· {EUR(p.luecke_eur_gesamt)} Lücke</span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {!kundenNr ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Milk className="mx-auto mb-2 h-8 w-8 opacity-40" />Betrieb oben auswählen — sortiert nach größter Chance.</CardContent></Card>
      ) : cockpit.isLoading ? (
        <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : !data ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground">Kein Milchvieh-Profil für diesen Betrieb.</CardContent></Card>
      ) : (
        <>
          {/* Kopf-Kennzahlen */}
          <div className="grid gap-3 md:grid-cols-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap items-center gap-1.5">
                  <p className="text-sm font-medium">{data.name}</p>
                  {data.sparten.map((s) => (
                    <span key={s} className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${SPARTE_BADGE[s]}`}>{SPARTE_LABEL[s]}</span>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.plz} {data.ort}
                  {data.herd_size_kuehe > 0 ? ` · ${data.herd_size_kuehe} Kühe` : ''}
                  {data.ackerflaeche_ha > 0 ? ` · ${data.ackerflaeche_ha} ha Acker` : ''}
                </p>
              </CardContent>
            </Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Bedarf/Jahr</p><p className="text-2xl font-bold">{EUR(data.bedarf_jahr_eur_gesamt)}</p></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Ist (12 M)</p><p className="text-2xl font-bold text-emerald-600">{EUR(data.ist_12m_eur_gesamt)}</p></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Offene Lücke · Deckung</p><p className="text-2xl font-bold text-amber-600">{EUR(data.luecke_eur_gesamt)}</p><DeckungBar pct={data.deckung_pct_gesamt} /></CardContent></Card>
          </div>

          {/* Next-Best-Offer */}
          {data.next_best_offer && (
            <Card className="border-blue-200 bg-blue-50/50">
              <CardContent className="flex flex-wrap items-start gap-3 p-4">
                <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-blue-900">Next-Best-Offer · {data.next_best_offer.label} <span className="font-normal text-blue-700">({EUR(data.next_best_offer.luecke_eur)} Lücke)</span></p>
                  <p className="text-sm text-blue-800">{data.next_best_offer.empfehlung}</p>
                </div>
                <Button size="sm" className="gap-2" onClick={() => angebot(data.next_best_offer?.produktgruppe)}>
                  Angebot erstellen <ArrowRight className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Produktgruppen-Matrix */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-base"><TrendingUp className="h-4 w-4" />Produktgruppen</CardTitle></CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-xs text-muted-foreground">
                      <th className="px-4 py-2 font-medium">Produktgruppe</th>
                      <th className="px-4 py-2 text-right font-medium">Bedarf/Jahr</th>
                      <th className="px-4 py-2 text-right font-medium">Ist (12 M)</th>
                      <th className="px-4 py-2 font-medium">Deckung</th>
                      <th className="px-4 py-2 text-right font-medium">Lücke</th>
                      <th className="px-4 py-2 font-medium">Aktion</th>
                      <th className="px-4 py-2" />
                    </tr>
                  </thead>
                  <tbody>
                    {data.produktgruppen.map((g: ProduktgruppeDeckung, i: number) => (
                      <Fragment key={g.key}>
                        {(i === 0 || data.produktgruppen[i - 1].sparte !== g.sparte) && (
                          <tr className="bg-muted/40">
                            <td colSpan={7} className="px-4 py-1.5">
                              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${SPARTE_BADGE[g.sparte]}`}>{SPARTE_LABEL[g.sparte]}</span>
                            </td>
                          </tr>
                        )}
                      <tr className="border-b last:border-0 hover:bg-muted/40">
                        <td className="px-4 py-2.5"><span className="font-medium">{g.label}</span></td>
                        <td className="px-4 py-2.5 text-right tabular-nums">{EUR(g.bedarf_jahr_eur)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums text-emerald-700">{EUR(g.ist_12m_eur)}</td>
                        <td className="px-4 py-2.5"><DeckungBar pct={g.deckung_pct} /></td>
                        <td className="px-4 py-2.5 text-right font-medium tabular-nums text-amber-700">{EUR(g.luecke_eur)}</td>
                        <td className="px-4 py-2.5"><span className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${AKTION_BADGE[g.aktion] ?? 'bg-slate-100 text-slate-700'}`}>{g.aktion}</span></td>
                        <td className="px-4 py-2.5 text-right">
                          {g.luecke_eur > 0 && (
                            <Button size="sm" variant="ghost" className="h-7 gap-1 text-xs" onClick={() => angebot(g.key)}>
                              Angebot <ArrowRight className="h-3 w-3" />
                            </Button>
                          )}
                        </td>
                      </tr>
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="px-4 py-2 text-[11px] text-muted-foreground">
                Bedarf = objektives Potenzial (Milchvieh aus Herde/Leistung €/1.000 l, Ackerbau aus Marktfrucht-Fläche €/ha;
                Grundfutterfläche ist abgezogen). Ist {data.produktgruppen[0]?.quelle === 'geschaetzt' ? '(modelliert — echte Belegaggregation dockt an)' : '(aus Verkaufsbelegen, 12 M)'}.
              </p>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate(`/crm/kunden-cockpit`)}>Zum Kunden-Cockpit</Button>
            <Button variant="outline" onClick={() => navigate(`/crm/kunden-karte`)}>Auf der Karte</Button>
          </div>
        </>
      )}
    </div>
  )
}
