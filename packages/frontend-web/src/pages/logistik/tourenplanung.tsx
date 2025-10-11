import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, MapPin, Truck } from 'lucide-react'

export default function TourenplanungPage(): JSX.Element {
  const touren = {
    heute: 12,
    offen: 5,
    unterwegs: 4,
    abgeschlossen: 3,
    tourenListe: [
      { id: 'T-001', fahrer: 'Schmidt', stopps: 5, km: 85, status: 'unterwegs' },
      { id: 'T-002', fahrer: 'Müller', stopps: 3, km: 45, status: 'geplant' },
      { id: 'T-003', fahrer: 'Weber', stopps: 7, km: 120, status: 'abgeschlossen' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tourenplanung</h1>
          <p className="text-muted-foreground">Liefertouren & Disposition</p>
        </div>
        <Button className="gap-2">
          <Truck className="h-4 w-4" />
          Neue Tour
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Touren Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{touren.heute}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{touren.offen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unterwegs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{touren.unterwegs}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{touren.abgeschlossen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Aktive Touren
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {touren.tourenListe.map((tour, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{tour.id} - Fahrer: {tour.fahrer}</div>
                  <div className="text-sm text-muted-foreground">{tour.stopps} Stopps • {tour.km} km</div>
                </div>
                <Badge variant={tour.status === 'unterwegs' ? 'secondary' : tour.status === 'abgeschlossen' ? 'outline' : 'default'}>
                  {tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
