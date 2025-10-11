import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'

export default function GuvPage(): JSX.Element {
  const guv = {
    periode: 'Januar - Dezember 2024',
    ertraege: {
      gesamt: 1250000,
      positionen: [
        { name: 'Umsatzerlöse', betrag: 1180000 },
        { name: 'Sonstige betriebliche Erträge', betrag: 45000 },
        { name: 'Zinserträge', betrag: 25000 },
      ],
    },
    aufwendungen: {
      gesamt: 1095000,
      positionen: [
        { name: 'Materialaufwand', betrag: 520000 },
        { name: 'Personalaufwand', betrag: 385000 },
        { name: 'Abschreibungen', betrag: 85000 },
        { name: 'Sonstige betriebliche Aufwendungen', betrag: 75000 },
        { name: 'Zinsaufwendungen', betrag: 30000 },
      ],
    },
  }

  const jahresueberschuss = guv.ertraege.gesamt - guv.aufwendungen.gesamt
  const umsatzrendite = ((jahresueberschuss / guv.ertraege.gesamt) * 100).toFixed(1)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gewinn- und Verlustrechnung</h1>
          <p className="text-muted-foreground">Periode: {guv.periode}</p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          Umsatzrendite: {umsatzrendite}%
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erträge</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(guv.ertraege.gesamt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufwendungen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(guv.aufwendungen.gesamt)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Jahresüberschuss</CardTitle>
          </CardHeader>
          <CardContent>
            <span className={`text-2xl font-bold ${jahresueberschuss > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(jahresueberschuss)}
            </span>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        {/* ERTRÄGE */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-green-600">ERTRÄGE</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {guv.ertraege.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span>{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold text-lg">
                <span>Gesamterträge</span>
                <span className="text-green-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(guv.ertraege.gesamt)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AUFWENDUNGEN */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-red-600">AUFWENDUNGEN</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {guv.aufwendungen.positionen.map((pos, i) => (
                <div key={i} className="flex justify-between py-2 border-b last:border-0">
                  <span>{pos.name}</span>
                  <span className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(pos.betrag)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold text-lg">
                <span>Gesamtaufwendungen</span>
                <span className="text-red-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(guv.aufwendungen.gesamt)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* ERGEBNIS */}
        <Card className={jahresueberschuss > 0 ? 'border-green-500' : 'border-red-500'}>
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">JAHRESÜBERSCHUSS/-FEHLBETRAG</span>
              <span className={`text-3xl font-bold ${jahresueberschuss > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(jahresueberschuss)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
