import { useMemo, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

/**
 * Wizard-Futterliste als fachliche Bereichsansicht (FEED-WIZ-051).
 *
 * Vorbild Futter-R/AMTS: je Bereich die gewählten Komponenten als Zeilen
 * (mit Artikel-/DLG-Nummer, TM %, ME, Min/Max) und eine permanente leere
 * Picker-Zeile — Fokus/Hover öffnet die Bereichs-Auswahl, ein Klick füllt
 * die Zeile und die nächste leere Zeile steht bereit.
 */

export type SectionFeed = {
  id: string
  name: string
  /** Artikel-/Rations-/DLG-Nummer (PRIMARYID, artikel_nummer, Produktname) */
  nummer: string | null
  /** DLG-FUTTERART, Katalog-feed_kind oder group-Fallback */
  futterart: string
  tmPct: number | null
  me: number | null
  selected: boolean
}

export type SectionKey =
  | 'rauhfutter' | 'feuchtfutter' | 'schrote'
  | 'mineralfutter' | 'ergaenzer' | 'wasser'

export const SECTION_LABELS: Record<SectionKey, string> = {
  rauhfutter: 'Rauhfutter',
  feuchtfutter: 'Feuchtfutter',
  schrote: 'Mehl- & Eiweißschrote',
  mineralfutter: 'Mineralfutter',
  ergaenzer: 'Sonstige Ergänzer',
  wasser: 'Wasser',
}

const SECTION_ORDER: SectionKey[] = [
  'rauhfutter', 'feuchtfutter', 'schrote', 'mineralfutter', 'ergaenzer', 'wasser',
]

/** Bereichszuordnung aus DLG-FUTTERART / Katalogklasse / Name (deterministisch). */
export function sectionForFeed(feed: Pick<SectionFeed, 'name' | 'futterart'>): SectionKey {
  const haystack = `${feed.futterart} ${feed.name}`.toLowerCase()
  if (/wasser|water/.test(haystack)) return 'wasser'
  if (/mineral|viehsalz|futterkalk|\bkalk\b/.test(haystack)) return 'mineralfutter'
  if (/saftfutter|feuchtkonzentrat|\bfeucht\b/.test(haystack)) return 'feuchtfutter'
  if (/grobfutter|grundfutter|forage|\bheu\b|\bstroh\b/.test(haystack)) return 'rauhfutter'
  if (/trockenkonzentrate, einzelfutter|kraftfutter|concentrate|schrot|byproduct/.test(haystack)) return 'schrote'
  return 'ergaenzer'
}

function formatNumber(value: number | null, digits = 1): string {
  if (value == null || !Number.isFinite(value)) return '–'
  return value.toLocaleString('de-DE', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function SectionPicker({ sectionLabel, candidates, onSelect }: {
  sectionLabel: string
  candidates: SectionFeed[]
  onSelect: (id: string) => void
}): JSX.Element {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const closeTimer = useRef<number | null>(null)

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase()
    const pool = needle
      ? candidates.filter((feed) =>
          feed.name.toLowerCase().includes(needle) ||
          (feed.nummer ?? '').toLowerCase().includes(needle))
      : candidates
    return pool.slice(0, 25)
  }, [candidates, query])

  function scheduleClose(): void {
    if (closeTimer.current !== null) window.clearTimeout(closeTimer.current)
    closeTimer.current = window.setTimeout(() => setOpen(false), 150)
  }
  function cancelClose(): void {
    if (closeTimer.current !== null) window.clearTimeout(closeTimer.current)
  }

  return (
    <div className="relative"
         onMouseEnter={() => { cancelClose(); setOpen(true) }}
         onMouseLeave={scheduleClose}>
      <Input
        placeholder={`+ Futtermittel wählen… (${sectionLabel})`}
        aria-label={`Futtermittel wählen für ${sectionLabel}`}
        className="h-9"
        value={query}
        onChange={(event) => { setQuery(event.target.value); setOpen(true) }}
        onFocus={() => { cancelClose(); setOpen(true) }}
        onBlur={scheduleClose}
      />
      {open ? (
        <ul role="listbox" aria-label={`Vorschläge ${sectionLabel}`}
            className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md border bg-popover p-1 shadow-md">
          {matches.map((feed) => (
            <li key={feed.id} role="option" aria-selected={false}
                className="flex cursor-pointer items-center justify-between gap-3 rounded px-2 py-1.5 text-sm hover:bg-muted"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => { onSelect(feed.id); setQuery(''); setOpen(false) }}>
              <span>{feed.name}</span>
              <span className="shrink-0 font-mono text-xs text-muted-foreground">
                {feed.nummer ?? '–'}
              </span>
            </li>
          ))}
          {matches.length === 0 ? (
            <li className="px-2 py-1.5 text-sm text-muted-foreground" role="status">
              Keine passenden Futtermittel in diesem Bereich.
            </li>
          ) : null}
        </ul>
      ) : null}
    </div>
  )
}

export function WizardFeedSections({ feeds, unit, minFm, maxFm,
                                     onSelect, onRemove, onMinChange, onMaxChange }: {
  feeds: SectionFeed[]
  unit: 'TM' | 'FM'
  minFm: Record<string, number>
  maxFm: Record<string, number>
  onSelect: (id: string) => void
  onRemove: (id: string) => void
  onMinChange: (id: string, value: number) => void
  onMaxChange: (id: string, value: number) => void
}): JSX.Element {
  const bySection = useMemo(() => {
    const map = new Map<SectionKey, SectionFeed[]>()
    for (const key of SECTION_ORDER) map.set(key, [])
    for (const feed of feeds) {
      const bucket = map.get(sectionForFeed(feed)) ?? []
      bucket.push(feed)
      map.set(sectionForFeed(feed), bucket)
    }
    return map
  }, [feeds])

  return (
    <div className="space-y-5">
      {SECTION_ORDER.map((key) => {
        const label = SECTION_LABELS[key]
        const sectionFeeds = bySection.get(key) ?? []
        const chosen = sectionFeeds.filter((feed) => feed.selected)
        const available = sectionFeeds.filter((feed) => !feed.selected)
        return (
          <section key={key} role="region" aria-label={label}
                   className="rounded-lg border bg-card p-3">
            <h3 className="mb-2 flex items-baseline justify-between font-medium">
              {label}
              <span className="text-2xs uppercase tracking-wide text-muted-foreground">
                {chosen.length} gewählt · {available.length} verfügbar
              </span>
            </h3>
            {chosen.length > 0 ? (
              <table className="mb-2 w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-1 pr-2 font-medium">Futtermittel</th>
                    <th className="py-1 pr-2 font-medium">Artikel-/Rationsnr.</th>
                    <th className="py-1 pr-2 text-right font-medium">TM %</th>
                    <th className="py-1 pr-2 text-right font-medium">ME</th>
                    <th className="py-1 pr-2 text-right font-medium">Min {unit} kg/d</th>
                    <th className="py-1 pr-2 text-right font-medium">Max {unit} kg/d</th>
                    <th className="py-1" aria-hidden />
                  </tr>
                </thead>
                <tbody>
                  {chosen.map((feed) => (
                    <tr key={feed.id} className="border-b last:border-b-0">
                      <td className="py-1.5 pr-2">{feed.name}</td>
                      <td className="py-1.5 pr-2 font-mono text-xs">{feed.nummer ?? '–'}</td>
                      <td className="py-1.5 pr-2 text-right tabular-nums">{formatNumber(feed.tmPct)}</td>
                      <td className="py-1.5 pr-2 text-right tabular-nums">{formatNumber(feed.me)}</td>
                      <td className="py-1.5 pr-2 text-right">
                        <Input aria-label={`Min ${unit} ${feed.name}`} type="number" min="0" step="0.1"
                               className="ml-auto h-8 w-20 text-right tabular-nums"
                               value={minFm[feed.id] ?? ''}
                               onChange={(event) => onMinChange(feed.id, Number(event.target.value))} />
                      </td>
                      <td className="py-1.5 pr-2 text-right">
                        <Input aria-label={`Max ${unit} ${feed.name}`} type="number" min="0" step="0.1"
                               className="ml-auto h-8 w-20 text-right tabular-nums"
                               value={maxFm[feed.id] ?? ''}
                               onChange={(event) => onMaxChange(feed.id, Number(event.target.value))} />
                      </td>
                      <td className="py-1.5 text-right">
                        <Button type="button" variant="ghost" size="sm"
                                aria-label={`${feed.name} entfernen`}
                                onClick={() => onRemove(feed.id)}>
                          ✕
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
            {sectionFeeds.length === 0 ? (
              <p className="mb-2 text-sm text-muted-foreground" role="status">
                Für diesen Bereich ist keine Position im Katalog hinterlegt.
              </p>
            ) : null}
            <SectionPicker sectionLabel={label} candidates={available} onSelect={onSelect} />
          </section>
        )
      })}
    </div>
  )
}
