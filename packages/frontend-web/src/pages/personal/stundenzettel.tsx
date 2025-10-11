import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Clock, Plus, Save, Truck } from 'lucide-react'

type Tour = {
  id: string
  start: string
  ende: string
  km: number
  pause: number
}

type Stundenzettel = {
  datum: string
  fahrer: string
  kennzeichen: string
  touren: Tour[]
  gesamtArbeitszeit: number
  ueberstunden: number
  unterschrift?: string
}

export default function StundenzettelPage(): JSX.Element {
  const navigate = useNavigate()
  
  const [zettel, setZettel] = useState<Stundenzettel>({
    datum: new Date().toISOString().split('T')[0],
    fahrer: '',
    kennzeichen: '',
    touren: [
      { id: '1', start: '07:00', ende: '12:30', km: 120, pause: 30 },
    ],
    gesamtArbeitszeit: 0,
    ueberstunden: 0,
  })

  function addTour(): void {
    const newTour: Tour = {
      id: String(zettel.touren.length + 1),
      start: '',
      ende: '',
      km: 0,
      pause: 0,
    }
    setZettel({ ...zettel, touren: [...zettel.touren, newTour] })
  }

  function updateTour(id: string, field: keyof Tour, value: string | number): void {
    setZettel({
      ...zettel,
      touren: zettel.touren.map((t) => (t.id === id ? { ...t, [field]: value } : t)),
    })
    calculateTimes()
  }

  function removeTour(id: string): void {
    setZettel({
      ...zettel,
      touren: zettel.touren.filter((t) => t.id !== id),
    })
    calculateTimes()
  }

  function calculateTimes(): void {
    let gesamtMinuten = 0
    
    zettel.touren.forEach((tour) => {
      if (tour.start && tour.ende) {
        const [startH, startM] = tour.start.split(':').map(Number)
        const [endeH, endeM] = tour.ende.split(':').map(Number)
        const minuten = (endeH * 60 + endeM) - (startH * 60 + startM) - tour.pause
        gesamtMinuten += minuten
      }
    })

    const stunden = gesamtMinuten / 60
    const ueberstunden = Math.max(0, stunden - 8)

    setZettel({
      ...zettel,
      gesamtArbeitszeit: Number(stunden.toFixed(2)),
      ueberstunden: Number(ueberstunden.toFixed(2)),
    })
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Truck className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">LKW-Fahrer Stundenzettel</h1>
            <p className="text-muted-foreground">Arbeitszeiterfassung & Tourendokumentation</p>
          </div>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          {new Date(zettel.datum).toLocaleDateString('de-DE')}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Stammdaten */}
        <Card>
          <CardHeader>
            <CardTitle>Stammdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="datum">Datum *</Label>
              <Input
                id="datum"
                type="date"
                value={zettel.datum}
                onChange={(e) => setZettel({ ...zettel, datum: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="fahrer">Fahrer *</Label>
              <Input
                id="fahrer"
                value={zettel.fahrer}
                onChange={(e) => setZettel({ ...zettel, fahrer: e.target.value })}
                placeholder="Name des Fahrers"
              />
            </div>
            <div>
              <Label htmlFor="kennzeichen">KFZ-Kennzeichen *</Label>
              <Input
                id="kennzeichen"
                value={zettel.kennzeichen}
                onChange={(e) => setZettel({ ...zettel, kennzeichen: e.target.value.toUpperCase() })}
                placeholder="z.B. ROW-AB 1234"
                className="font-mono"
              />
            </div>
          </CardContent>
        </Card>

        {/* Zeiterfassung */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Zeiterfassung
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-lg bg-muted p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-muted-foreground">Gesamt-Arbeitszeit</span>
                <span className="text-3xl font-bold">{zettel.gesamtArbeitszeit.toFixed(2)} h</span>
              </div>
              <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${zettel.gesamtArbeitszeit > 10 ? 'bg-red-500' : zettel.gesamtArbeitszeit > 8 ? 'bg-orange-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min((zettel.gesamtArbeitszeit / 10) * 100, 100)}%` }}
                />
              </div>
            </div>

            {zettel.ueberstunden > 0 && (
              <div className="rounded-lg bg-orange-50 p-3 text-orange-900">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold">Überstunden</span>
                  <span className="text-2xl font-bold">{zettel.ueberstunden.toFixed(2)} h</span>
                </div>
              </div>
            )}

            <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
              <p className="font-semibold">Arbeitszeitgesetz (ArbZG)</p>
              <p className="mt-1 text-xs">Max. 10h/Tag • 48h/Woche • Mindestpause 30min (bei &gt;6h)</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Touren */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Touren</CardTitle>
            <Button size="sm" variant="outline" onClick={addTour} className="gap-2">
              <Plus className="h-4 w-4" />
              Tour hinzufügen
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {zettel.touren.map((tour) => (
              <div key={tour.id} className="grid grid-cols-5 gap-3 items-center border rounded-lg p-3">
                <div>
                  <Label className="text-xs">Start</Label>
                  <Input
                    type="time"
                    value={tour.start}
                    onChange={(e) => updateTour(tour.id, 'start', e.target.value)}
                    className="font-mono"
                  />
                </div>
                <div>
                  <Label className="text-xs">Ende</Label>
                  <Input
                    type="time"
                    value={tour.ende}
                    onChange={(e) => updateTour(tour.id, 'ende', e.target.value)}
                    className="font-mono"
                  />
                </div>
                <div>
                  <Label className="text-xs">KM</Label>
                  <Input
                    type="number"
                    value={tour.km}
                    onChange={(e) => updateTour(tour.id, 'km', Number(e.target.value))}
                    className="font-mono"
                  />
                </div>
                <div>
                  <Label className="text-xs">Pause (min)</Label>
                  <Input
                    type="number"
                    value={tour.pause}
                    onChange={(e) => updateTour(tour.id, 'pause', Number(e.target.value))}
                    className="font-mono"
                  />
                </div>
                <div className="flex items-end">
                  <Button size="sm" variant="destructive" onClick={() => removeTour(tour.id)}>
                    ✕
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Unterschrift */}
      <Card>
        <CardHeader>
          <CardTitle>Unterschrift Fahrer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed rounded-lg h-32 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-sm">Unterschrift hier (Touch-Canvas)</p>
              <p className="text-xs mt-1">TODO: React-Signature-Canvas</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={() => navigate('/personal/stundenzettel-liste')}>
          Abbrechen
        </Button>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>
    </div>
  )
}
