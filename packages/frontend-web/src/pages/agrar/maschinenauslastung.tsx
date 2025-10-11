import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tractor, TrendingUp } from 'lucide-react'

export default function MaschinenauslastungPage(): JSX.Element {
  const maschinen = {
    gesamt: 6,
    liste: [
      { name: 'Traktor John Deere 6210R', typ: 'Traktor', stunden: 420, auslastung: 70, status: 'im-einsatz' },
      { name: 'Mähdrescher Claas Lexion 770', typ: 'Mähdrescher', stunden: 185, auslastung: 92, status: 'im-einsatz' },
      { name: 'Traktor Fendt 724', typ: 'Traktor', stunden: 380, auslastung: 63, status: 'werkstatt' },
    ],
  }

  const imEinsatz = maschinen.liste.filter((m) => m.status === 'im-einsatz').length

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Maschinen-Auslastung</h1>
        <p className="text-muted-foreground">Betriebsstunden & Auslastung</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Maschinen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Tractor className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{maschinen.gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Im Einsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{imEinsatz}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Werkstatt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{maschinen.liste.filter((m) => m.status === 'werkstatt').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {(maschinen.liste.reduce((sum, m) => sum + m.auslastung, 0) / maschinen.liste.length).toFixed(1)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Maschinen & Auslastung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {maschinen.liste.map((maschine, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-semibold text-lg">{maschine.name}</div>
                    <div className="text-sm text-muted-foreground flex items-center gap-2 mt-1">
                      <Badge variant="outline">{maschine.typ}</Badge>
                      <Badge variant={maschine.status === 'im-einsatz' ? 'secondary' : 'default'}>
                        {maschine.status === 'im-einsatz' ? 'Im Einsatz' : 'Werkstatt'}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{maschine.auslastung}%</div>
                    <div className="text-sm text-muted-foreground">{maschine.stunden} h</div>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-4 rounded-full ${maschine.auslastung > 80 ? 'bg-green-500' : maschine.auslastung > 50 ? 'bg-yellow-500' : 'bg-orange-500'}`}
                    style={{ width: `${maschine.auslastung}%` }}
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
