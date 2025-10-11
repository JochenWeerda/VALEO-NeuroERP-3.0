import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Map, Sprout } from 'lucide-react'

export default function SchlagKartePage(): JSX.Element {
  const schlaege = {
    gesamt: 5,
    flaeche: 125.5,
    liste: [
      { nummer: 'S-001', name: 'Hinterfeld', kultur: 'Weizen', flaeche: 25.0, farbe: 'bg-yellow-200' },
      { nummer: 'S-002', name: 'Vorderfeld', kultur: 'Raps', flaeche: 18.5, farbe: 'bg-yellow-300' },
      { nummer: 'S-003', name: 'Ostacker', kultur: 'Mais', flaeche: 32.0, farbe: 'bg-green-200' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Schlagkarte</h1>
        <p className="text-muted-foreground">Übersicht Schläge & Kulturen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{schlaege.gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Fläche</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{schlaege.flaeche} ha</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Schlaggröße</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{(schlaege.flaeche / schlaege.gesamt).toFixed(1)} ha</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Schlagkarte (vereinfacht)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border-2 border-dashed p-6 min-h-[400px] flex items-center justify-center bg-green-50">
            <div className="text-center">
              <Map className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-muted-foreground font-semibold">Interaktive Karte</p>
              <p className="text-sm text-muted-foreground mt-2">Integration: OpenStreetMap / Google Maps</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Schlag-Übersicht</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {schlaege.liste.map((schlag, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-lg ${schlag.farbe} flex items-center justify-center font-mono font-bold`}>
                      {schlag.nummer}
                    </div>
                    <div>
                      <div className="font-semibold text-lg">{schlag.name}</div>
                      <div className="text-sm text-muted-foreground">
                        <Badge variant="outline" className="mr-2">{schlag.kultur}</Badge>
                        {schlag.flaeche} ha
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
