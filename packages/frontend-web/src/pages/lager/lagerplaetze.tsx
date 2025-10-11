import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react'

export default function LagerplaetzePage(): JSX.Element {
  const lager = {
    plaetze: 42,
    belegt: 35,
    frei: 7,
    auslastung: 83.3,
    bereiche: [
      { name: 'Silo 1', plaetze: 8, belegt: 8, kapazitaet: 450, bestand: 445 },
      { name: 'Silo 2', plaetze: 8, belegt: 6, kapazitaet: 400, bestand: 280 },
      { name: 'Halle A', plaetze: 12, belegt: 10, kapazitaet: 250, bestand: 220 },
      { name: 'Halle B', plaetze: 14, belegt: 11, kapazitaet: 300, bestand: 245 },
    ],
  }

  const kritisch = lager.bereiche.filter((b) => b.belegt / b.plaetze > 0.95).length

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Lagerplätze</h1>
        <p className="text-muted-foreground">Lagerverwaltung & Auslastung</p>
      </div>

      {kritisch > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{kritisch} Lagerbereich(e) über 95% ausgelastet!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lagerplätze Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{lager.plaetze}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Belegt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{lager.belegt}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Frei</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{lager.frei}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{lager.auslastung}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Warehouse className="h-5 w-5" />
            Lagerbereiche
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {lager.bereiche.map((bereich, i) => {
              const auslastung = (bereich.belegt / bereich.plaetze) * 100
              const fuellstand = (bereich.bestand / bereich.kapazitaet) * 100
              return (
                <div key={i} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-semibold text-lg">{bereich.name}</div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">
                        {bereich.belegt} / {bereich.plaetze} Plätze
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {bereich.bestand} / {bereich.kapazitaet} t
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Plätze:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${auslastung > 95 ? 'bg-red-600' : auslastung > 80 ? 'bg-orange-600' : 'bg-green-600'}`}
                          style={{ width: `${auslastung}%` }}
                        />
                      </div>
                      <Badge variant={auslastung > 95 ? 'destructive' : 'outline'}>
                        {auslastung.toFixed(0)}%
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Füllstand:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600" style={{ width: `${fuellstand}%` }} />
                      </div>
                      <Badge variant="outline">{fuellstand.toFixed(0)}%</Badge>
                    </div>
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
