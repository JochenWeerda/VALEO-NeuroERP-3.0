import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, Flower2, MapPin } from 'lucide-react'

export default function BiodiversitaetPage(): JSX.Element {
  const bio = {
    flaechen: {
      bluehstreifen: 8.5,
      brachflaechen: 5.2,
      hecken: 2.1,
    },
    massnahmen: [
      { name: 'Blühstreifen Nordfeld', flaeche: 3.5, typ: 'Blühstreifen', status: 'aktiv' },
      { name: 'Brachfläche Südacker', flaeche: 2.8, typ: 'Brachfläche', status: 'aktiv' },
      { name: 'Hecke Wiesengrund', flaeche: 1.2, typ: 'Hecke', status: 'geplant' },
    ],
  }

  const gesamtFlaeche = bio.flaechen.bluehstreifen + bio.flaechen.brachflaechen + bio.flaechen.hecken

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Biodiversitäts-Monitoring</h1>
        <p className="text-muted-foreground">Ökologische Ausgleichsflächen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtfläche Biodiversität</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Flower2 className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{gesamtFlaeche.toFixed(1)} ha</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Blühstreifen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{bio.flaechen.bluehstreifen} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Brachflächen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{bio.flaechen.brachflaechen} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hecken</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{bio.flaechen.hecken} ha</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Biodiversitäts-Maßnahmen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bio.massnahmen.map((m, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{m.name}</div>
                  <div className="text-sm text-muted-foreground">{m.flaeche} ha</div>
                  <Badge variant="outline" className="mt-1">{m.typ}</Badge>
                </div>
                <div>
                  {m.status === 'aktiv' ? (
                    <Badge variant="outline">
                      <CheckCircle className="h-3 w-3 mr-1 inline" />
                      Aktiv
                    </Badge>
                  ) : (
                    <Badge variant="secondary">Geplant</Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
