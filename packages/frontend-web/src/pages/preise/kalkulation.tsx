import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { Calculator } from 'lucide-react'

type KalkSchritt = { schritt: string; wert: number; delta: number }
type KalkResult = {
  netto_preis: number; brutto_preis: number | null; mwst_betrag: number | null
  kalkulationsweg: KalkSchritt[]; steuerhinweis?: string
}

export default function PreisKalkulationPage(): JSX.Element {
  const [form, setForm] = useState({
    artikel_id: '',
    menge_kg: '',
    kunde_id: '',
    kontrakt_id: '',
  })
  const [result, setResult] = useState<KalkResult | null>(null)

  const calcMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post<KalkResult>('/api/v1/preise/berechnen', {
        artikel_id: form.artikel_id,
        menge_kg: Number(form.menge_kg),
        kunde_id: form.kunde_id || undefined,
        kontrakt_id: form.kontrakt_id || undefined,
      })).data,
    onSuccess: (data) => setResult(data),
    onError: () => setResult(null),
  })

  const fmt = (n: number | null) => n === null ? '—' : n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

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
                <label className="text-sm font-medium">Menge (Artikeleinheit)</label>
                <Input type="number" placeholder="1000" value={form.menge_kg} onChange={(e) => setForm({ ...form, menge_kg: e.target.value })} />
              </div>
              <div>
                <label className="text-sm font-medium">Kunden-ID (optional)</label>
                <Input placeholder="Kundenkennung fuer Kundenpreise" value={form.kunde_id} onChange={(e) => setForm({ ...form, kunde_id: e.target.value })} />
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

        {calcMutation.isError && (
          <p role="alert" className="text-sm text-status-error">
            Preis nicht ermittelbar: {getAxiosErrorMessage(calcMutation.error)}
          </p>
        )}
        {result?.steuerhinweis && <p className="text-sm text-status-warning">Keine Steuer berechnet: {result.steuerhinweis}</p>}
        {result && (
          <>
            <div className="grid gap-4 md:grid-cols-3">
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Netto</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{fmt(result.netto_preis)} €</span></CardContent></Card>
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">MwSt.</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-muted-foreground">{fmt(result.mwst_betrag)} €</span></CardContent></Card>
              <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Brutto</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{fmt(result.brutto_preis)} €</span></CardContent></Card>
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
                        <td className={`py-1 text-right font-mono ${k.delta < 0 ? 'text-status-error' : 'text-status-success'}`}>
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
