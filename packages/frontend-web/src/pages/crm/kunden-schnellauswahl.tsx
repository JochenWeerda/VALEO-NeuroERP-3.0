import { useEffect, useState } from 'react'
import { Search, Loader2, MapPin, CreditCard, Hash } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useKundenLookup, useKundenDetail } from '@/lib/api/kunden-lookup'

/**
 * Kunden-Schnellauswahl (Stammdaten-Konsolidierung, Phase 2D).
 *
 * Liest Such-/Listenfelder aus der kunden_lookup-View (GET /customers/lookup)
 * und lädt beim Öffnen eines Kunden Adresse/Zahlung/External-Refs on-demand aus
 * den kunden_*-Satelliten (GET /customers/lookup/{kunden_nr}/detail). Reine
 * Lese-/Auswahlmaske — keine Mutationen.
 */

function useDebounced<T>(value: T, delay = 250): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

const ADRESSE_LABELS: Record<string, string> = {
  strasse: 'Straße',
  plz: 'PLZ',
  ort: 'Ort',
  land: 'Land',
  postfach: 'Postfach',
  postfach_plz: 'Postfach-PLZ',
  postfach_ort: 'Postfach-Ort',
}

const ZAHLUNG_LABELS: Record<string, string> = {
  zahlungsbedingungen_tage: 'Zahlungsziel (Tage)',
  skonto: 'Skonto',
  netto_kasse: 'Netto Kasse',
  mahnwesen: 'Mahnwesen',
  lastschriftverfahren: 'Lastschrift',
  sepa_verfahren: 'SEPA',
  mandat: 'Mandat',
  kontonutzung_rechnung: 'Kontonutzung Rechnung',
  kontoauszug_gewuenscht: 'Kontoauszug gewünscht',
}

const REF_LABELS: Record<string, string> = {
  legacy_kunden_nr: 'Alt-Kundennummer',
  webshop_kunden_nr: 'Webshop-Kundennummer',
  tankkarte_ean: 'Tankkarte (EAN)',
  kundenkarte: 'Kundenkarte',
}

function formatValue(v: string | number | boolean | null): string {
  if (v === null || v === undefined || v === '') return '–'
  if (typeof v === 'boolean') return v ? 'Ja' : 'Nein'
  return String(v)
}

function DefinitionList({
  data,
  labels,
}: {
  data: Record<string, string | number | boolean | null>
  labels: Record<string, string>
}): JSX.Element {
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined && v !== '')
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">Keine Angaben.</p>
  }
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
      {entries.map(([k, v]) => (
        <div key={k} className="contents">
          <dt className="text-muted-foreground">{labels[k] ?? k}</dt>
          <dd className="font-medium">{formatValue(v)}</dd>
        </div>
      ))}
    </dl>
  )
}

export default function KundenSchnellauswahlPage(): JSX.Element {
  const [query, setQuery] = useState('')
  const debounced = useDebounced(query, 250)
  const [selected, setSelected] = useState<string | null>(null)

  const lookup = useKundenLookup(debounced, 25)
  const detail = useKundenDetail(selected ?? undefined, Boolean(selected))

  const items = lookup.data ?? []

  return (
    <div className="p-6">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold">Kunden-Schnellauswahl</h1>
        <p className="text-sm text-muted-foreground">
          Schnelle Auswahl aus dem Kundenstamm; Detaildaten werden beim Öffnen aus den Domänentabellen geladen.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        {/* Suche + Trefferliste */}
        <Card>
          <CardHeader>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Name, Kundennummer, Matchcode oder PLZ ..."
                className="pl-9"
                aria-label="Kunden suchen"
              />
            </div>
          </CardHeader>
          <CardContent>
            {lookup.isLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : items.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                {debounced.trim() ? 'Keine Treffer.' : 'Tippen, um zu suchen …'}
              </p>
            ) : (
              <ul className="divide-y">
                {items.map((k) => {
                  const isActive = selected === k.kunden_nr
                  return (
                    <li key={k.kunden_nr}>
                      <button
                        type="button"
                        onClick={() => setSelected(k.kunden_nr)}
                        className={`flex w-full items-center justify-between gap-3 px-2 py-2 text-left text-sm transition-colors hover:bg-muted/60 ${
                          isActive ? 'bg-muted' : ''
                        }`}
                        aria-pressed={isActive}
                      >
                        <span className="min-w-0">
                          <span className="block truncate font-medium">{k.name ?? k.kunden_nr}</span>
                          <span className="block truncate text-xs text-muted-foreground">
                            {[k.plz, k.ort].filter(Boolean).join(' ') || '—'}
                          </span>
                        </span>
                        <span className="flex shrink-0 items-center gap-2">
                          {!k.aktiv && <Badge variant="secondary">inaktiv</Badge>}
                          <span className="font-mono text-xs text-muted-foreground">{k.kunden_nr}</span>
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Detail aus Satelliten */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {selected ? `Detail · ${selected}` : 'Kunde wählen'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                Wähle links einen Kunden, um Adresse, Zahlung und Referenzen zu laden.
              </p>
            ) : detail.isLoading ? (
              <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Detail wird geladen …
              </div>
            ) : detail.isError ? (
              <p className="py-8 text-center text-sm text-destructive">
                Detail konnte nicht geladen werden.
              </p>
            ) : detail.data ? (
              <div className="space-y-6">
                <section>
                  <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                    <MapPin className="h-4 w-4" /> Adresse
                  </h2>
                  <DefinitionList data={detail.data.adresse} labels={ADRESSE_LABELS} />
                </section>
                <section>
                  <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                    <CreditCard className="h-4 w-4" /> Zahlung
                  </h2>
                  <DefinitionList data={detail.data.zahlung} labels={ZAHLUNG_LABELS} />
                </section>
                <section>
                  <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                    <Hash className="h-4 w-4" /> Referenzen / Altnummern
                  </h2>
                  <DefinitionList data={detail.data.external_refs} labels={REF_LABELS} />
                </section>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
