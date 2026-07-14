import { Fragment, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { Target, TrendingUp, Sparkles, Loader2, ArrowRight, Milk, Search, UserRound } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useBedarfsdeckung, usePipeline, type ProduktgruppeDeckung } from '@/lib/api/bedarfsdeckung'
import { useKaeufergruppenKatalog, useSetKaeufergruppe, useReklassifizieren, useProduktgruppenKlassifizieren } from '@/lib/api/kaeufergruppe'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'

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
  const katalog = useKaeufergruppenKatalog()
  const setGruppe = useSetKaeufergruppe()
  const reklass = useReklassifizieren()
  const pgKlass = useProduktgruppenKlassifizieren()
  const { toast } = useToast()

  async function changeGruppe(group: string) {
    if (!data || group === data.kaeufergruppe.group) return
    try {
      await setGruppe.mutateAsync({ kunden_nr: data.kunden_nr, group })
      toast({ title: 'Käufergruppe gesetzt', description: 'Prioritäten werden neu berechnet.' })
    } catch (e) {
      toast({ title: 'Fehler', description: (e as Error).message, variant: 'destructive' })
    }
  }

  async function reklassifizieren(modus: 'belege' | 'ki') {
    if (!data) return
    try {
      const res = await reklass.mutateAsync({ kunden_nr: data.kunden_nr, modus })
      const src = (res as { buying_group_source?: string })?.buying_group_source
      toast({ title: modus === 'ki' ? 'KI-Einschätzung' : 'Aus Belegen klassifiziert', description: src === 'ai_suggested' ? 'KI-Vorschlag übernommen.' : 'Regelbasiert (Belegsignale).' })
    } catch (e) {
      toast({ title: 'Fehler', description: (e as Error).message, variant: 'destructive' })
    }
  }

  async function gruppenAbleiten() {
    if (!data) return
    try {
      await pgKlass.mutateAsync(data.kunden_nr)
      toast({ title: 'Je Produktgruppe eingestuft' })
    } catch (e) {
      toast({ title: 'Fehler', description: (e as Error).message, variant: 'destructive' })
    }
  }

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
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Bedarf/Jahr · Deckung</p><p className="text-2xl font-bold">{EUR(data.bedarf_jahr_eur_gesamt)}</p><DeckungBar pct={data.deckung_pct_gesamt} /></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Realistisch gewinnbar</p><p className="text-2xl font-bold text-status-warning">{EUR(data.realistische_luecke_eur_gesamt)}</p><p className="text-[11px] text-muted-foreground">von {EUR(data.luecke_eur_gesamt)} theoret. Lücke</p></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Geschützte Restlücke</p><p className="text-2xl font-bold text-slate-400">{EUR(data.geschuetzte_luecke_eur_gesamt)}</p><p className="text-[11px] text-muted-foreground">bewusst woanders — nicht forcieren</p></CardContent></Card>
          </div>

          {/* Käufergruppe */}
          <Card className="border-indigo-200 bg-indigo-50/40">
            <CardContent className="flex flex-wrap items-start gap-3 p-4">
              <UserRound className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />
              <div className="min-w-0 flex-1">
                <p className="flex flex-wrap items-center gap-2 font-semibold text-indigo-900">
                  Käufergruppe: {data.kaeufergruppe.label}
                  <span className="rounded bg-indigo-100 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700">
                    {Math.round(data.kaeufergruppe.confidence * 100)} % · {data.kaeufergruppe.source === 'manual' ? 'bestätigt' : 'KI-Vorschlag'}
                  </span>
                  <span className="text-xs font-normal text-indigo-700">Zielanteil {Math.round(data.kaeufergruppe.ziel_anteil_min * 100)}–{Math.round(data.kaeufergruppe.ziel_anteil_max * 100)} %</span>
                </p>
                {data.kaeufergruppe.reason && <p className="text-sm text-indigo-800">{data.kaeufergruppe.reason}</p>}
                <p className="mt-0.5 text-sm font-medium text-indigo-900">→ {data.kaeufergruppe.ansatz}</p>
              </div>
              <div className="flex flex-col gap-1.5">
                <span className="text-[11px] text-muted-foreground">Korrigieren</span>
                <NativeSelect value={data.kaeufergruppe.group} onValueChange={changeGruppe} className="w-52">
                  {(katalog.data ?? []).map((k) => (
                    <option key={k.group} value={k.group}>{k.label}</option>
                  ))}
                </NativeSelect>
                <div className="flex flex-wrap gap-1">
                  <Button size="sm" variant="outline" className="h-7 gap-1 text-xs" disabled={reklass.isPending} onClick={() => reklassifizieren('ki')}>
                    <Sparkles className="h-3 w-3" />KI-Einschätzung
                  </Button>
                  <Button size="sm" variant="outline" className="h-7 text-xs" disabled={reklass.isPending} onClick={() => reklassifizieren('belege')}>
                    Aus Belegen
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 text-xs" disabled={pgKlass.isPending} onClick={gruppenAbleiten}>
                    je Produktgruppe
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Next-Best-Offer */}
          {data.next_best_offer && (
            <Card className="border-blue-200 bg-blue-50/50">
              <CardContent className="flex flex-wrap items-start gap-3 p-4">
                <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-blue-900">Next-Best-Offer · {data.next_best_offer.label} <span className="font-normal text-blue-700">({EUR(data.next_best_offer.realistische_luecke_eur)} realistisch gewinnbar)</span></p>
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
                      <th className="px-4 py-2 text-right font-medium">Ziel</th>
                      <th className="px-4 py-2 text-right font-medium">realist. Lücke</th>
                      <th className="px-4 py-2 font-medium">Aktion</th>
                      <th className="px-4 py-2" />
                    </tr>
                  </thead>
                  <tbody>
                    {data.produktgruppen.map((g: ProduktgruppeDeckung, i: number) => (
                      <Fragment key={g.key}>
                        {(i === 0 || data.produktgruppen[i - 1].sparte !== g.sparte) && (
                          <tr className="bg-muted/40">
                            <td colSpan={8} className="px-4 py-1.5">
                              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${SPARTE_BADGE[g.sparte]}`}>{SPARTE_LABEL[g.sparte]}</span>
                            </td>
                          </tr>
                        )}
                      <tr className="border-b last:border-0 hover:bg-muted/40">
                        <td className="px-4 py-2.5">
                          <span className="font-medium">{g.label}</span>
                          {g.kaeufergruppe_eigen && (
                            <span className="ml-2 rounded bg-indigo-50 px-1 py-0.5 text-[10px] font-medium text-indigo-600" title="produktgruppenspezifische Käufergruppe">
                              {g.kaeufergruppe_label}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-2.5 text-right tabular-nums">{EUR(g.bedarf_jahr_eur)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums text-emerald-700">{EUR(g.ist_12m_eur)}</td>
                        <td className="px-4 py-2.5"><DeckungBar pct={g.deckung_pct} /></td>
                        <td className="px-4 py-2.5 text-right tabular-nums text-muted-foreground">{Math.round(g.ziel_anteil * 100)} %</td>
                        <td className="px-4 py-2.5 text-right font-medium tabular-nums text-amber-700">
                          {EUR(g.realistische_luecke_eur)}
                          {g.luecke_eur > g.realistische_luecke_eur && (
                            <span className="block text-[10px] font-normal text-slate-400 line-through">{EUR(g.luecke_eur)}</span>
                          )}
                        </td>
                        <td className="px-4 py-2.5"><span className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${AKTION_BADGE[g.aktion] ?? 'bg-slate-100 text-slate-700'}`}>{g.aktion}</span></td>
                        <td className="px-4 py-2.5 text-right">
                          {g.realistische_luecke_eur > 0 && (
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

          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => navigate(`/crm/durchdringungs-pipeline`)}>Durchdringungs-Pipeline</Button>
            <Button variant="outline" onClick={() => navigate(`/crm/kunden-cockpit`)}>Zum Kunden-Cockpit</Button>
            <Button variant="outline" onClick={() => navigate(`/crm/kunden-karte`)}>Auf der Karte</Button>
          </div>
        </>
      )}
    </div>
  )
}
