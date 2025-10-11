import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Sprout, TrendingUp } from 'lucide-react'

export default function DuengungsplanungPage(): JSX.Element {
  const planung = {
    schlaege: [
      { schlag: 'S-001 Hinterfeld', kultur: 'Weizen', flaeche: 25, npk: { n: 180, p: 60, k: 120 }, geplant: 'KW 12' },
      { schlag: 'S-002 Vorderfeld', kultur: 'Raps', flaeche: 18, npk: { n: 200, p: 70, k: 140 }, geplant: 'KW 13' },
    ],
    gesamtFlaeche: 43,
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Düngungsplanung</h1>
        <p className="text-muted-foreground">Nährstoffbedarf & Planung</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{planung.schlaege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Fläche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{planung.gesamtFlaeche} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="outline" className="text-base px-4 py-2">Planung läuft</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Schläge & Nährstoffbedarf
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {planung.schlaege.map((schlag, i) => (
              <Card key={i}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="font-semibold text-lg">{schlag.schlag}</div>
                      <div className="text-sm text-muted-foreground">{schlag.kultur} • {schlag.flaeche} ha</div>
                    </div>
                    <Badge variant="outline">Geplant: {schlag.geplant}</Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="rounded-lg bg-blue-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">N (Stickstoff)</div>
                      <div className="text-2xl font-bold text-blue-600">{schlag.npk.n}</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
                    </div>
                    <div className="rounded-lg bg-orange-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">P (Phosphor)</div>
                      <div className="text-2xl font-bold text-orange-600">{schlag.npk.p}</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
                    </div>
                    <div className="rounded-lg bg-green-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">K (Kalium)</div>
                      <div className="text-2xl font-bold text-green-600">{schlag.npk.k}</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
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
