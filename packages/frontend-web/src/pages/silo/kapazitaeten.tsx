import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Box } from 'lucide-react'

export default function SiloKapazitaetenPage(): JSX.Element {
  const silos = {
    gesamt: 4,
    kapazitaet: 2500,
    belegt: 1850,
    liste: [
      { nummer: 'SILO-01', artikel: 'Weizen Premium', kapazitaet: 800, belegt: 125, prozent: 15.6 },
      { nummer: 'SILO-02', artikel: 'Raps', kapazitaet: 600, belegt: 480, prozent: 80.0 },
      { nummer: 'SILO-03', artikel: 'Mais', kapazitaet: 700, belegt: 620, prozent: 88.6 },
      { nummer: 'SILO-04', artikel: 'Sojaschrot', kapazitaet: 400, belegt: 280, prozent: 70.0 },
    ],
  }

  const auslastung = ((silos.belegt / silos.kapazitaet) * 100).toFixed(1)
  const kritisch = silos.liste.filter((s) => s.prozent > 85).length

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Silo-Kapazitäten</h1>
        <p className="text-muted-foreground">Auslastung & Übersicht</p>
      </div>

      {kritisch > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{kritisch} Silo(s) über 85% Auslastung!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Silos Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Box className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{silos.gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Kapazität</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{silos.kapazitaet} t</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Belegt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{silos.belegt} t</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{auslastung}%</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Silos & Auslastung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {silos.liste.map((silo, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-semibold text-lg flex items-center gap-2">
                      <span className="font-mono">{silo.nummer}</span>
                      {silo.prozent > 85 && <Badge variant="secondary">Kritisch</Badge>}
                    </div>
                    <div className="text-sm text-muted-foreground">{silo.artikel}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{silo.prozent.toFixed(1)}%</div>
                    <div className="text-sm text-muted-foreground">{silo.belegt} / {silo.kapazitaet} t</div>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-4 rounded-full ${silo.prozent > 85 ? 'bg-orange-500' : silo.prozent > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${silo.prozent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
