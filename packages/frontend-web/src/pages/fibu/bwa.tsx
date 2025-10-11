import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'

export default function BwaPage(): JSX.Element {
  const bwa = {
    periode: 'Oktober 2025',
    kumuliert: 'Januar - Oktober 2025',
    data: {
      umsatz: { monat: 125000, kumuliert: 1050000 },
      wareneingang: { monat: 52000, kumuliert: 480000 },
      rohertrag: { monat: 73000, kumuliert: 570000 },
      personalkosten: { monat: 38000, kumuliert: 350000 },
      raumkosten: { monat: 8500, kumuliert: 85000 },
      sonstigeKosten: { monat: 12000, kumuliert: 105000 },
      betriebsergebnis: { monat: 14500, kumuliert: 30000 },
      zinsen: { monat: 2500, kumuliert: 25000 },
      ergebnis: { monat: 12000, kumuliert: 5000 },
    },
  }

  const rohertragQuote = ((bwa.data.rohertrag.monat / bwa.data.umsatz.monat) * 100).toFixed(1)
  const personalkostenQuote = ((bwa.data.personalkosten.monat / bwa.data.umsatz.monat) * 100).toFixed(1)
  const betriebsergebnisQuote = ((bwa.data.betriebsergebnis.monat / bwa.data.umsatz.monat) * 100).toFixed(1)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Betriebswirtschaftliche Auswertung (BWA)</h1>
        <p className="text-muted-foreground">
          Monat: {bwa.periode} | Kumuliert: {bwa.kumuliert}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umsatz (Monat)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bwa.data.umsatz.monat)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rohertrag-Quote</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{rohertragQuote}%</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Personalkosten-Quote</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{personalkostenQuote}%</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Betriebsergebnis-Quote</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{betriebsergebnisQuote}%</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>BWA-Schema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2">
                  <th className="text-left py-3">Position</th>
                  <th className="text-right py-3">Monat (€)</th>
                  <th className="text-right py-3">Kumuliert (€)</th>
                  <th className="text-right py-3">Quote (%)</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr className="border-b">
                  <td className="py-3 font-semibold">Umsatzerlöse</td>
                  <td className="text-right font-bold">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.umsatz.monat)}
                  </td>
                  <td className="text-right">{new Intl.NumberFormat('de-DE').format(bwa.data.umsatz.kumuliert)}</td>
                  <td className="text-right">100,0</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 pl-4">- Wareneinsatz</td>
                  <td className="text-right text-red-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.wareneingang.monat)}
                  </td>
                  <td className="text-right text-red-600">{new Intl.NumberFormat('de-DE').format(bwa.data.wareneingang.kumuliert)}</td>
                  <td className="text-right">{((bwa.data.wareneingang.monat / bwa.data.umsatz.monat) * 100).toFixed(1)}</td>
                </tr>
                <tr className="border-b bg-green-50">
                  <td className="py-3 font-bold">= Rohertrag</td>
                  <td className="text-right font-bold text-green-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.rohertrag.monat)}
                  </td>
                  <td className="text-right font-bold text-green-600">{new Intl.NumberFormat('de-DE').format(bwa.data.rohertrag.kumuliert)}</td>
                  <td className="text-right font-bold">{rohertragQuote}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 pl-4">- Personalkosten</td>
                  <td className="text-right text-red-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.personalkosten.monat)}
                  </td>
                  <td className="text-right text-red-600">{new Intl.NumberFormat('de-DE').format(bwa.data.personalkosten.kumuliert)}</td>
                  <td className="text-right">{personalkostenQuote}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 pl-4">- Raumkosten</td>
                  <td className="text-right text-red-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.raumkosten.monat)}
                  </td>
                  <td className="text-right text-red-600">{new Intl.NumberFormat('de-DE').format(bwa.data.raumkosten.kumuliert)}</td>
                  <td className="text-right">{((bwa.data.raumkosten.monat / bwa.data.umsatz.monat) * 100).toFixed(1)}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 pl-4">- Sonstige Kosten</td>
                  <td className="text-right text-red-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.sonstigeKosten.monat)}
                  </td>
                  <td className="text-right text-red-600">{new Intl.NumberFormat('de-DE').format(bwa.data.sonstigeKosten.kumuliert)}</td>
                  <td className="text-right">{((bwa.data.sonstigeKosten.monat / bwa.data.umsatz.monat) * 100).toFixed(1)}</td>
                </tr>
                <tr className="border-b bg-blue-50">
                  <td className="py-3 font-bold">= Betriebsergebnis (EBIT)</td>
                  <td className="text-right font-bold text-blue-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.betriebsergebnis.monat)}
                  </td>
                  <td className="text-right font-bold text-blue-600">{new Intl.NumberFormat('de-DE').format(bwa.data.betriebsergebnis.kumuliert)}</td>
                  <td className="text-right font-bold">{betriebsergebnisQuote}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 pl-4">- Zinsen</td>
                  <td className="text-right text-red-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.zinsen.monat)}
                  </td>
                  <td className="text-right text-red-600">{new Intl.NumberFormat('de-DE').format(bwa.data.zinsen.kumuliert)}</td>
                  <td className="text-right">{((bwa.data.zinsen.monat / bwa.data.umsatz.monat) * 100).toFixed(1)}</td>
                </tr>
                <tr className="bg-green-100 font-bold">
                  <td className="py-4 text-lg">= Ergebnis vor Steuern (EBT)</td>
                  <td className="text-right text-lg text-green-600">
                    {new Intl.NumberFormat('de-DE').format(bwa.data.ergebnis.monat)}
                  </td>
                  <td className="text-right text-lg text-green-600">{new Intl.NumberFormat('de-DE').format(bwa.data.ergebnis.kumuliert)}</td>
                  <td className="text-right text-lg">{((bwa.data.ergebnis.monat / bwa.data.umsatz.monat) * 100).toFixed(1)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">💡 Hinweis</p>
        <p className="mt-1">BWA nach DATEV-Standard (SKR03) • Monatliche Aktualisierung • DATEV-Export verfügbar</p>
      </div>
    </div>
  )
}
