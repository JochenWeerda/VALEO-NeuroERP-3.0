import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Cloud, CloudRain } from 'lucide-react'

export default function WetterwarnungPage(): JSX.Element {
  const warnungen = {
    aktiv: 2,
    warnliste: [
      { stufe: 'orange', typ: 'Starkregen', beginn: '2025-10-12 18:00', ende: '2025-10-13 06:00', region: 'Nordhausen' },
      { stufe: 'gelb', typ: 'Gewitter', beginn: '2025-10-12 14:00', ende: '2025-10-12 20:00', region: 'Gesamtgebiet' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wetterwarnungen</h1>
        <p className="text-muted-foreground">DWD-Warnlagebericht</p>
      </div>

      {warnungen.aktiv > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{warnungen.aktiv} aktive Wetterwarnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Warnungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{warnungen.aktiv}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Quelle</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="outline" className="text-base px-4 py-2">DWD Deutscher Wetterdienst</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cloud className="h-5 w-5" />
            Aktuelle Warnungen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {warnungen.warnliste.map((warnung, i) => (
              <Card key={i} className={warnung.stufe === 'orange' ? 'border-orange-500' : 'border-yellow-500'}>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-4">
                    {warnung.typ === 'Starkregen' ? (
                      <CloudRain className="h-8 w-8 text-blue-600" />
                    ) : (
                      <Cloud className="h-8 w-8 text-gray-600" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-lg">{warnung.typ}</span>
                        <Badge variant={warnung.stufe === 'orange' ? 'secondary' : 'outline'}>
                          {warnung.stufe === 'orange' ? 'Stufe Orange (2)' : 'Stufe Gelb (1)'}
                        </Badge>
                      </div>
                      <div className="text-sm space-y-1">
                        <div className="flex gap-2">
                          <span className="text-muted-foreground w-24">Beginn:</span>
                          <span className="font-mono">{warnung.beginn}</span>
                        </div>
                        <div className="flex gap-2">
                          <span className="text-muted-foreground w-24">Ende:</span>
                          <span className="font-mono">{warnung.ende}</span>
                        </div>
                        <div className="flex gap-2">
                          <span className="text-muted-foreground w-24">Region:</span>
                          <span className="font-semibold">{warnung.region}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
