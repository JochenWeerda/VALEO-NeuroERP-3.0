import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Leaf, TrendingDown } from 'lucide-react'

export default function CO2BilanzPage(): JSX.Element {
  const co2 = {
    gesamt: 1250,
    vorjahr: 1450,
    reduktion: 13.8,
    nachBereich: [
      { bereich: 'Transport', co2: 450, anteil: 36 },
      { bereich: 'Lagerung', co2: 320, anteil: 26 },
      { bereich: 'Verarbeitung', co2: 280, anteil: 22 },
      { bereich: 'Verwaltung', co2: 200, anteil: 16 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">CO₂-Bilanz</h1>
        <p className="text-muted-foreground">Klimabilanz 2025</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">CO₂-Emissionen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Leaf className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{co2.gesamt.toLocaleString('de-DE')} t</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vorjahr</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{co2.vorjahr.toLocaleString('de-DE')} t</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reduktion</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">-{co2.reduktion}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eingespart</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{co2.vorjahr - co2.gesamt} t</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            CO₂-Emissionen nach Bereich
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {co2.nachBereich.map((bereich, i) => (
              <div key={i} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-semibold">{bereich.bereich}</div>
                  <div className="text-right">
                    <div className="text-xl font-bold">{bereich.co2} t CO₂</div>
                    <div className="text-sm text-muted-foreground">{bereich.anteil}% Gesamtanteil</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-green-600" style={{ width: `${bereich.anteil}%` }} />
                  </div>
                  <Badge variant="outline">{bereich.anteil}%</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
