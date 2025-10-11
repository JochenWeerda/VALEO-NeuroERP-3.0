import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'

export default function BilanzPage(): JSX.Element {
  const bilanz = {
    periode: '31.12.2024',
    aktiva: {
      anlagevermoegen: {
        gesamt: 450000,
        positionen: [
          { name: 'Grundstücke & Gebäude', betrag: 280000 },
          { name: 'Technische Anlagen', betrag: 120000 },
          { name: 'Fuhrpark', betrag: 50000 },
        ],
      },
      umlaufvermoegen: {
        gesamt: 385000,
        positionen: [
          { name: 'Vorräte', betrag: 185000 },
          { name: 'Forderungen', betrag: 125000 },
          { name: 'Bank', betrag: 65000 },
          { name: 'Kasse', betrag: 10000 },
        ],
      },
    },
    passiva: {
      eigenkapital: {
        gesamt: 485000,
        positionen: [
          { name: 'Gezeichnetes Kapital', betrag: 250000 },
          { name: 'Gewinnrücklage', betrag: 180000 },
          { name: 'Jahresüberschuss', betrag: 55000 },
        ],
      },
      fremdkapital: {
        gesamt: 350000,
        positionen: [
          { name: 'Verbindlichkeiten LuL', betrag: 125000 },
          { name: 'Bankdarlehen', betrag: 185000 },
          { name: 'Sonstige Verbindlichkeiten', betrag: 40000 },
        ],
      },
    },
  }

  const bilanzsumme = bilanz.aktiva.anlagevermoegen.gesamt + bilanz.aktiva.umlaufvermoegen.gesamt
  const eigenkapitalquote = ((bilanz.passiva.eigenkapital.gesamt / bilanzsumme) * 100).toFixed(1)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bilanz</h1>
          <p className="text-muted-foreground">Stichtag: {bilanz.periode}</p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          Eigenkapitalquote: {eigenkapitalquote}%
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bilanzsumme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanzsumme)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eigenkapital</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.passiva.eigenkapital.gesamt)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fremdkapital</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.passiva.fremdkapital.gesamt)}
            </span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* AKTIVA */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">AKTIVA</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Anlagevermögen */}
            <div className="rounded-lg border p-4">
              <div className="font-semibold text-lg mb-3">Anlagevermögen</div>
              {bilanz.aktiva.anlagevermoegen.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold">
                <span>Summe Anlagevermögen</span>
                <span>
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.aktiva.anlagevermoegen.gesamt)}
                </span>
              </div>
            </div>

            {/* Umlaufvermögen */}
            <div className="rounded-lg border p-4">
              <div className="font-semibold text-lg mb-3">Umlaufvermögen</div>
              {bilanz.aktiva.umlaufvermoegen.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold">
                <span>Summe Umlaufvermögen</span>
                <span>
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.aktiva.umlaufvermoegen.gesamt)}
                </span>
              </div>
            </div>

            {/* Gesamtsumme */}
            <div className="rounded-lg bg-blue-50 p-4">
              <div className="flex justify-between text-xl font-bold text-blue-900">
                <span>SUMME AKTIVA</span>
                <span>{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanzsumme)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* PASSIVA */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">PASSIVA</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Eigenkapital */}
            <div className="rounded-lg border p-4">
              <div className="font-semibold text-lg mb-3">Eigenkapital</div>
              {bilanz.passiva.eigenkapital.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold">
                <span>Summe Eigenkapital</span>
                <span className="text-green-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.passiva.eigenkapital.gesamt)}
                </span>
              </div>
            </div>

            {/* Fremdkapital */}
            <div className="rounded-lg border p-4">
              <div className="font-semibold text-lg mb-3">Fremdkapital</div>
              {bilanz.passiva.fremdkapital.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold">
                <span>Summe Fremdkapital</span>
                <span>
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanz.passiva.fremdkapital.gesamt)}
                </span>
              </div>
            </div>

            {/* Gesamtsumme */}
            <div className="rounded-lg bg-blue-50 p-4">
              <div className="flex justify-between text-xl font-bold text-blue-900">
                <span>SUMME PASSIVA</span>
                <span>{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bilanzsumme)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
