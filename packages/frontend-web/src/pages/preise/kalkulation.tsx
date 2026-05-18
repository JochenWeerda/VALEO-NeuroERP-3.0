import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'
import { Calculator } from 'lucide-react'

type KalkSchritt = { schritt: string; wert: number; delta: number }
type KalkResult = { netto_preis: number; brutto_preis: number; mwst_betrag: number; kalkulationsweg: KalkSchritt[] }

export default function PreisKalkulationPage(): JSX.Element {
  const [form, setForm] = useState({
    artikel_id: '',
    menge_kg: '',
    kundengruppe: 'GROSSHANDEL',
    sorte_klasse: '',
    kontrakt_id: '',
  })
  const [result, setResult] = useState<KalkResult | null>(null)

  const calcMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post<KalkResult>('/api/v1/preise/berechnen', {
        artikel_id: form.artikel_id,
        menge_kg: Number(form.menge_kg),
        kundengruppe: form.kundengruppe,
        sorte_klasse: form.sorte_klasse || undefined,
        kontrakt_id: form.kontrakt_id || undefined,
      })).data,
    onSuccess: (data) => setResult(data),
  })

  const fmt = (n: number) => n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-3xl font-bold">Preis-Kalkulation</h1>
          <p className="text-muted-foreground">Preisberechnung mit Kalkulationsweg</p>
        </div>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Calculator className="h-5 w-5" />Eingabe</CardTitle></CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium">Artikel-ID</label>
                <Input placeholder="z.B. ART-0001" value={form.artikel_id} onChange={(e) => setForm({ ...form, artikel_id: e.target.value })} />
              </div>
              <div>
                <label className="text-sm font-medium">Menge (kg)</label>
                <Input type="number" placeholder="1000" value={form.menge_kg} onChange={(e) => setForm({ ...form, menge_kg: e.target.value })} />
              </div>
              <div>
                <label className="text-sm font-medium">Kundengruppe</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={form.kundengruppe}
                  onChange={(e) => setForm({ ...form, kundengruppe: e.target.value })}
                >
                  <option value="GROSSHANDEL">Großhandel</option>
                  <option value="EINZELHANDEL">Einzelhandel</option>
                  <option value="GENOSSENSCHAFT">Genossenschaft</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Sortenklasse (optional)</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={form.sorte_klasse}
                  onChange={(e) => setForm({ ...form, sorte_klasse: e.target.value })}
                >
                  <option value="">– keine –</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Kontrakt-ID (optional)</label>
                <Input placeholder="z.B. KON-2024-001" value={form.kontrakt_id} onChange={(e) => setForm({ ...form, kontrakt_id: e.target.value })} />
              </div>
            </div>
            <div className="mt-4">
              <Button onClick={() => calcMutation.mutate()} disabled={!form.artikel_id || !form.menge_kg || calcMutation.isPending}>
                {calcMutation.isPending ? 'Berechne...' : 'Preis berechnen'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {result && (
          <>
            <div className="grid gap-4 md:grid-cols-3">
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Netto</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{fmt(result.netto_preis)} €</span></CardContent></Card>
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">MwSt.</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-muted-foreground">{fmt(result.mwst_betrag)} €</span></CardContent></Card>
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Brutto</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{fmt(result.brutto_preis)} €</span></CardContent></Card>
            </div>

            <Card>
              <CardHeader><CardTitle>Kalkulationsweg</CardTitle></CardHeader>
              <CardContent>
                <table className="w-full text-sm">
                  <thead><tr className="border-b"><th className="text-left pb-2">Schritt</th><th className="text-right pb-2">Wert</th><th className="text-right pb-2">Delta</th></tr></thead>
                  <tbody>
                    {result.kalkulationsweg.map((k, i) => (
                      <tr key={i} className="border-b">
                        <td className="py-1">{k.schritt}</td>
                        <td className="py-1 text-right font-mono">{fmt(k.wert)} €</td>
                        <td className={`py-1 text-right font-mono ${k.delta < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {k.delta >= 0 ? '+' : ''}{fmt(k.delta)} €
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}
