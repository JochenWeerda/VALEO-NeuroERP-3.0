import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Cloud, CloudRain, Sun } from 'lucide-react'

export default function WetterPrognosePage(): JSX.Element {
  const wetter = {
    heute: {
      temperatur: 18,
      niederschlag: 0,
      wind: 12,
      bedingung: 'Sonnig',
    },
    warnung: 'Starkregen am Wochenende erwartet',
    prognose: [
      { tag: 'Morgen', temperatur: 16, niederschlag: 5, icon: 'cloud-rain', bedingung: 'Leichter Regen' },
      { tag: 'Übermorgen', temperatur: 14, niederschlag: 15, icon: 'cloud-rain', bedingung: 'Regen' },
      { tag: 'In 3 Tagen', temperatur: 15, niederschlag: 2, icon: 'cloud', bedingung: 'Bewölkt' },
      { tag: 'In 4 Tagen', temperatur: 17, niederschlag: 0, icon: 'sun', bedingung: 'Sonnig' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wetter-Prognose</h1>
        <p className="text-muted-foreground">7-Tage-Vorhersage</p>
      </div>

      {wetter.warnung && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{wetter.warnung}</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sun className="h-6 w-6 text-yellow-500" />
            Heute
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-muted-foreground">Temperatur</div>
              <div className="text-3xl font-bold">{wetter.heute.temperatur}°C</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Niederschlag</div>
              <div className="text-3xl font-bold">{wetter.heute.niederschlag} mm</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Wind</div>
              <div className="text-3xl font-bold">{wetter.heute.wind} km/h</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Bedingung</div>
              <Badge variant="outline" className="mt-2">{wetter.heute.bedingung}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>4-Tage-Prognose</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {wetter.prognose.map((tag, i) => {
              const Icon = tag.icon === 'sun' ? Sun : tag.icon === 'cloud' ? Cloud : CloudRain
              return (
                <Card key={i}>
                  <CardContent className="pt-4">
                    <div className="text-center">
                      <div className="text-sm font-medium mb-2">{tag.tag}</div>
                      <Icon className={`h-12 w-12 mx-auto mb-2 ${tag.icon === 'sun' ? 'text-yellow-500' : 'text-blue-600'}`} />
                      <div className="text-2xl font-bold">{tag.temperatur}°C</div>
                      <div className="text-sm text-muted-foreground mt-1">{tag.niederschlag} mm</div>
                      <Badge variant="outline" className="mt-2">{tag.bedingung}</Badge>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
