import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { BarChart3, TrendingDown, TrendingUp } from 'lucide-react'

export default function PreishistoriePage(): JSX.Element {
  const preise = {
    artikel: 'Weizen Premium',
    aktuell: 220.5,
    vorwoche: 218.0,
    vormonat: 215.0,
    veraenderung: {
      woche: 1.1,
      monat: 2.6,
    },
    verlauf: [
      { datum: '2025-09-11', preis: 215.0 },
      { datum: '2025-09-18', preis: 216.5 },
      { datum: '2025-09-25', preis: 218.0 },
      { datum: '2025-10-02', preis: 219.5 },
      { datum: '2025-10-09', preis: 220.5 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Preishistorie</h1>
          <p className="text-muted-foreground">{preise.artikel}</p>
        </div>
        <Button variant="outline">Artikel wechseln</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktueller Preis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(preise.aktuell)} / t
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vorwoche</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(preise.vorwoche)} / t
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Veränderung (Woche)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">+{preise.veraenderung.woche}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Veränderung (Monat)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">+{preise.veraenderung.monat}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Preisverlauf (4 Wochen)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {preise.verlauf.map((v, i) => {
              const isLast = i === preise.verlauf.length - 1
              const trend = i > 0 ? v.preis - preise.verlauf[i - 1].preis : 0
              return (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">{new Date(v.datum).toLocaleDateString('de-DE')}</div>
                    {isLast && <Badge variant="outline" className="mt-1">Aktuell</Badge>}
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v.preis)} / t
                    </div>
                    {trend !== 0 && (
                      <div className={`text-sm font-semibold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trend > 0 ? <TrendingUp className="inline h-3 w-3" /> : <TrendingDown className="inline h-3 w-3" />}
                        {trend > 0 ? '+' : ''}{trend.toFixed(2)} €
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
