import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type ApplikationData = {
  schlag: string
  kultur: string
  flaeche: number
  mittel: string
  aufwandmenge: number
  wasseraufwand: number
  gesamtmenge: number
  zulassungsnummer: string
}

export default function PflanzenschutzApplikationPage(): JSX.Element {
  const navigate = useNavigate()
  const [applikation, setApplikation] = useState<ApplikationData>({
    schlag: '',
    kultur: '',
    flaeche: 0,
    mittel: '',
    aufwandmenge: 0,
    wasseraufwand: 0,
    gesamtmenge: 0,
    zulassungsnummer: '',
  })

  function updateField<K extends keyof ApplikationData>(key: K, value: ApplikationData[K]): void {
    if (key === 'flaeche' || key === 'aufwandmenge') {
      const newFlaeche = key === 'flaeche' ? Number(value) : applikation.flaeche
      const newAufwand = key === 'aufwandmenge' ? Number(value) : applikation.aufwandmenge
      setApplikation((prev) => ({ ...prev, [key]: value, gesamtmenge: newFlaeche * newAufwand }))
    } else {
      setApplikation((prev) => ({ ...prev, [key]: value }))
    }
  }

  const steps = [
    {
      id: 'schlag',
      title: 'Schlag',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="schlag">Schlag *</Label>
            <select
              id="schlag"
              value={applikation.schlag}
              onChange={(e) => updateField('schlag', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="S-001">S-001 Hinterfeld (Weizen, 25 ha)</option>
              <option value="S-002">S-002 Vorderfeld (Raps, 18 ha)</option>
            </select>
          </div>
          <div>
            <Label htmlFor="kultur">Kultur</Label>
            <Input id="kultur" value={applikation.kultur} onChange={(e) => updateField('kultur', e.target.value)} />
          </div>
          <div>
            <Label htmlFor="flaeche">Fläche (ha) *</Label>
            <Input id="flaeche" type="number" value={applikation.flaeche} onChange={(e) => updateField('flaeche', Number(e.target.value))} step="0.1" />
          </div>
        </div>
      ),
    },
    {
      id: 'mittel',
      title: 'Mittel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="mittel">Pflanzenschutzmittel *</Label>
            <select
              id="mittel"
              value={applikation.mittel}
              onChange={(e) => updateField('mittel', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="fungizid-a">Fungizid A (Wirkstoff: Tebuconazol)</option>
              <option value="herbizid-b">Herbizid B (Wirkstoff: Glyphosat)</option>
            </select>
          </div>
          <div>
            <Label htmlFor="zulassungsnummer">Zulassungsnummer</Label>
            <Input
              id="zulassungsnummer"
              value={applikation.zulassungsnummer}
              onChange={(e) => updateField('zulassungsnummer', e.target.value)}
              placeholder="z.B. 006544-00"
              className="font-mono"
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="aufwandmenge">Aufwandmenge (l/ha) *</Label>
              <Input
                id="aufwandmenge"
                type="number"
                value={applikation.aufwandmenge}
                onChange={(e) => updateField('aufwandmenge', Number(e.target.value))}
                step="0.1"
              />
            </div>
            <div>
              <Label htmlFor="wasseraufwand">Wasseraufwand (l/ha)</Label>
              <Input
                id="wasseraufwand"
                type="number"
                value={applikation.wasseraufwand}
                onChange={(e) => updateField('wasseraufwand', Number(e.target.value))}
                step="10"
              />
            </div>
          </div>
          <div className="rounded-lg bg-muted p-4">
            <div className="text-sm text-muted-foreground mb-1">Gesamtmenge (berechnet)</div>
            <div className="text-3xl font-bold">{applikation.gesamtmenge.toFixed(1)} l</div>
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: 'Zusammenfassung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Applikation bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Schlag</dt>
                <dd className="font-semibold">{applikation.schlag}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Kultur</dt>
                <dd className="font-semibold">{applikation.kultur}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Fläche</dt>
                <dd className="font-semibold">{applikation.flaeche} ha</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Mittel</dt>
                <dd className="font-semibold">{applikation.mittel}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Aufwandmenge</dt>
                <dd className="font-semibold">{applikation.aufwandmenge} l/ha</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Gesamtmenge</dt>
                <dd className="font-bold text-green-600">{applikation.gesamtmenge.toFixed(1)} l</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-orange-50 p-4 text-center text-sm text-orange-900">
              <p className="font-semibold">⚠️ Wartezeit beachten!</p>
              <p className="mt-1">Dokumentation gemäß Pflanzenschutzgesetz</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Pflanzenschutz-Applikation"
        steps={steps}
        onFinish={() => navigate('/agrar/feldbuch/massnahmen')}
        onCancel={() => navigate('/agrar/feldbuch/massnahmen')}
      />
    </div>
  )
}
