import { useState } from 'react'
import { Droplets, Wheat, Users, Euro } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  useMilchviehCrossSell,
  useMilchviehCrossSellSummary,
  type CrossSellFilter,
} from '@/lib/api/milchvieh-crosssell'

/**
 * Cross-Sell-Maske Milchvieh: Kunden nach Hygiene-Bedarf (Zellzahl) und
 * Herdengröße mit Mengenpotenzial Dippmittel/Reiniger, Kraftfutter (219–237 g/kg
 * ECM) und Landhandel-Umsatzpotenzial (€/1.000 l Milch), aufgeschlüsselt nach
 * Produktgruppen. Reine Lese-/Auswertungsmaske.
 */

const nf = (n: number | null | undefined, d = 0): string =>
  n === null || n === undefined ? '–' : n.toLocaleString('de-DE', { maximumFractionDigits: d, minimumFractionDigits: d })

const eur = (n: number | null | undefined): string =>
  n === null || n === undefined ? '–' : `${n.toLocaleString('de-DE', { maximumFractionDigits: 0 })} €`

const eurMio = (n: number | null | undefined): string =>
  n === null || n === undefined ? '–' : `${(n / 1_000_000).toLocaleString('de-DE', { maximumFractionDigits: 1, minimumFractionDigits: 1 })} Mio €`

const BEDARF_BADGE: Record<string, string> = {
  hoch: 'bg-red-100 text-red-800',
  mittel: 'bg-yellow-100 text-yellow-800',
  niedrig: 'bg-green-100 text-green-800',
}

function Kpi({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub?: string }): JSX.Element {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <div className="rounded-md bg-muted p-2 text-muted-foreground">{icon}</div>
        <div className="min-w-0">
          <div className="truncate text-xs text-muted-foreground">{label}</div>
          <div className="text-lg font-semibold">{value}</div>
          {sub && <div className="text-xs text-muted-foreground">{sub}</div>}
        </div>
      </CardContent>
    </Card>
  )
}

export default function MilchviehCrossSellPage(): JSX.Element {
  const [filter, setFilter] = useState<CrossSellFilter>({ sort: 'umsatz' })
  const list = useMilchviehCrossSell(filter)
  const summary = useMilchviehCrossSellSummary()
  const items = list.data ?? []
  const s = summary.data

  return (
    <div className="p-6">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold">Milchvieh Cross-Sell</h1>
        <p className="text-sm text-muted-foreground">
          Landhandel-Umsatzpotenzial (€/1.000 l Milch), Kraftfutter (219–237 g/kg ECM) und
          Eutergesundheit/Hygiene (Zellzahl × Herde) — nach Produktgruppen aufgeschlüsselt.
        </p>
      </div>

      {/* KPIs */}
      <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi icon={<Users className="h-5 w-5" />} label="Milchvieh-Kunden" value={nf(s?.kunden)}
          sub={s ? `${nf(s.milchmenge_l_jahr_gesamt / 1_000_000, 1)} Mio l/J` : undefined} />
        <Kpi icon={<Euro className="h-5 w-5" />} label="Cross-Sell Ziel (200 €/1.000 l)"
          value={s ? eurMio(s.crosssell_eur_jahr_ziel) : '–'}
          sub={s ? `gewinnbar ${eurMio(s.crosssell_eur_jahr_gewinnbar_min)}–${eurMio(s.crosssell_eur_jahr_gewinnbar_max)}` : undefined} />
        <Kpi icon={<Wheat className="h-5 w-5" />} label="Kraftfutter-Potenzial"
          value={s ? `${nf(s.kraftfutter_t_jahr_gesamt_min)}–${nf(s.kraftfutter_t_jahr_gesamt_max)} t/J` : '–'}
          sub={s ? `${s.kf_g_je_kg_ecm[0]}–${s.kf_g_je_kg_ecm[1]} g/kg ECM` : undefined} />
        <Kpi icon={<Droplets className="h-5 w-5" />} label="Dippmittel/Reiniger"
          value={s ? `${nf(s.dippmittel_l_jahr_gesamt)} L/J` : '–'} />
      </div>

      {/* Produktgruppen-Aufschlüsselung */}
      <Card className="mb-4">
        <CardHeader><CardTitle className="text-base">Potenzial nach Produktgruppe (gesamt)</CardTitle></CardHeader>
        <CardContent className="overflow-x-auto">
          {!s ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="py-2 pr-3">Produktgruppe</th>
                  <th className="py-2 pr-3 text-right">€/1.000 l</th>
                  <th className="py-2 pr-3 text-right">Potenzial €/Jahr (min–max)</th>
                </tr>
              </thead>
              <tbody>
                {s.produktgruppen.map((g) => (
                  <tr key={g.key} className="border-b last:border-0">
                    <td className="py-2 pr-3 font-medium">{g.label}</td>
                    <td className="py-2 pr-3 text-right text-muted-foreground">{g.eur_per_1000l[0]}–{g.eur_per_1000l[1]}</td>
                    <td className="py-2 pr-3 text-right">{eurMio(g.eur_jahr_min)} – {eurMio(g.eur_jahr_max)}</td>
                  </tr>
                ))}
                <tr className="border-t-2 font-semibold">
                  <td className="py-2 pr-3">Adressierbar gesamt</td>
                  <td className="py-2 pr-3 text-right text-muted-foreground">{s.crosssell_eur_je_1000l.adressierbar[0]}–{s.crosssell_eur_je_1000l.adressierbar[1]}</td>
                  <td className="py-2 pr-3 text-right">{eurMio(s.crosssell_eur_jahr_adressierbar_min)} – {eurMio(s.crosssell_eur_jahr_adressierbar_max)}</td>
                </tr>
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* Filter */}
      <Card className="mb-4">
        <CardContent className="flex flex-wrap items-end gap-3 p-4">
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Hygiene-Bedarf</span>
            <NativeSelect value={filter.hygiene_bedarf ?? ''} onValueChange={(v) => setFilter((f) => ({ ...f, hygiene_bedarf: v || undefined }))} className="w-40">
              <option value="">Alle</option>
              <option value="hoch">hoch</option>
              <option value="mittel">mittel</option>
              <option value="niedrig">niedrig</option>
            </NativeSelect>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Mindest-Herde (Kühe)</span>
            <Input type="number" min={0} className="w-36" value={filter.min_kuehe ?? ''}
              onChange={(e) => setFilter((f) => ({ ...f, min_kuehe: e.target.value ? Number(e.target.value) : undefined }))} />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Sortierung</span>
            <NativeSelect value={filter.sort ?? 'umsatz'} onValueChange={(v) => setFilter((f) => ({ ...f, sort: v as CrossSellFilter['sort'] }))} className="w-52">
              <option value="umsatz">Umsatzpotenzial (€)</option>
              <option value="kraftfutter">Kraftfutter-Potenzial</option>
              <option value="hygiene">Hygiene-Bedarf</option>
            </NativeSelect>
          </label>
        </CardContent>
      </Card>

      {/* Kundenliste */}
      <Card>
        <CardHeader><CardTitle className="text-base">Kunden ({nf(items.length)})</CardTitle></CardHeader>
        <CardContent className="overflow-x-auto">
          {list.isLoading ? (
            <div className="space-y-2">{Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          ) : items.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">Keine Treffer.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="py-2 pr-3">Betrieb</th>
                  <th className="py-2 pr-3">Ort</th>
                  <th className="py-2 pr-3 text-right">Kühe</th>
                  <th className="py-2 pr-3 text-right">Milch l/J</th>
                  <th className="py-2 pr-3 text-right">Zellzahl</th>
                  <th className="py-2 pr-3">Hygiene</th>
                  <th className="py-2 pr-3 text-right">Kraftfutter t/J</th>
                  <th className="py-2 pr-3 text-right">Cross-Sell Ziel</th>
                  <th className="py-2 pr-3 text-right">gewinnbar</th>
                </tr>
              </thead>
              <tbody>
                {items.map((i) => (
                  <tr key={i.kunden_nr} className="border-b last:border-0 hover:bg-muted/40">
                    <td className="py-2 pr-3 font-medium">{i.name ?? i.kunden_nr}</td>
                    <td className="py-2 pr-3 text-muted-foreground">{[i.plz, i.ort].filter(Boolean).join(' ')}</td>
                    <td className="py-2 pr-3 text-right">{nf(i.herd_size_kuehe)}</td>
                    <td className="py-2 pr-3 text-right">{nf(i.milchmenge_l_jahr)}</td>
                    <td className="py-2 pr-3 text-right">
                      {nf(i.zellzahl_tsd_ml)}
                      {i.zellzahl_quelle === 'dev_synthetik' && <span title="synthetischer Schätzwert" className="ml-1 text-xs text-muted-foreground">~</span>}
                    </td>
                    <td className="py-2 pr-3"><Badge className={BEDARF_BADGE[i.hygiene_bedarf] ?? ''}>{i.hygiene_bedarf}</Badge></td>
                    <td className="py-2 pr-3 text-right">{nf(i.kraftfutter_t_jahr_min, 1)}–{nf(i.kraftfutter_t_jahr_max, 1)}</td>
                    <td className="py-2 pr-3 text-right font-medium">{eur(i.crosssell_ziel_eur)}</td>
                    <td className="py-2 pr-3 text-right text-muted-foreground">{eur(i.crosssell_gewinnbar_eur_min)}–{eur(i.crosssell_gewinnbar_eur_max)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      <p className="mt-3 text-xs text-muted-foreground">
        Umsatzpotenzial: 150–260 €/1.000 l Milch adressierbar (Ziel 200 €), konservativ gewinnbar 80–120 €/1.000 l (BZA-/Rinder-Report-Richtwerte).
        ECM = Milch × (0,38·Fett% + 0,21·Eiweiß% + 1,05) / 3,28 (DLG). „~" = synthetischer Zellzahl-Schätzwert. Koeffizienten sind Planungsannahmen.
      </p>
    </div>
  )
}
