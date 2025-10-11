import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle } from 'lucide-react'

type SchadenData = {
  art: string
  datum: string
  ort: string
  beschreibung: string
  schadenhoehe: number
  versicherung: string
  zeuge: string
}

export default function SchadenMeldungPage(): JSX.Element {
  const navigate = useNavigate()
  const [schaden, setSchaden] = useState<SchadenData>({
    art: '',
    datum: new Date().toISOString().slice(0, 10),
    ort: '',
    beschreibung: '',
    schadenhoehe: 0,
    versicherung: '',
    zeuge: '',
  })

  function updateField<K extends keyof SchadenData>(key: K, value: SchadenData[K]): void {
    setSchaden((prev) => ({ ...prev, [key]: value }))
  }

  const steps = [
    {
      id: 'grunddaten',
      title: 'Grunddaten',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="art">Schadenart *</Label>
            <select
              id="art"
              value={schaden.art}
              onChange={(e) => updateField('art', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="hagel">Hagelschaden</option>
              <option value="frost">Frostschaden</option>
              <option value="feuer">Feuerschaden</option>
              <option value="unfall">Fahrzeugunfall</option>
              <option value="diebstahl">Diebstahl</option>
            </select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="datum">Schadendatum *</Label>
              <Input id="datum" type="date" value={schaden.datum} onChange={(e) => updateField('datum', e.target.value)} />
            </div>
            <div>
              <Label htmlFor="ort">Schadenort</Label>
              <Input id="ort" value={schaden.ort} onChange={(e) => updateField('ort', e.target.value)} placeholder="z.B. Schlag S-001" />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'beschreibung',
      title: 'Beschreibung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="beschreibung">Schadenhergang *</Label>
            <Textarea
              id="beschreibung"
              value={schaden.beschreibung}
              onChange={(e) => updateField('beschreibung', e.target.value)}
              rows={6}
              placeholder="Beschreiben Sie den Schadenhergang..."
            />
          </div>
          <div>
            <Label htmlFor="schadenhoehe">Geschätzte Schadenhöhe (€)</Label>
            <Input
              id="schadenhoehe"
              type="number"
              value={schaden.schadenhoehe}
              onChange={(e) => updateField('schadenhoehe', Number(e.target.value))}
              step="100"
            />
          </div>
          <div>
            <Label htmlFor="zeuge">Zeuge(n)</Label>
            <Input id="zeuge" value={schaden.zeuge} onChange={(e) => updateField('zeuge', e.target.value)} placeholder="Name(n) des/der Zeugen" />
          </div>
        </div>
      ),
    },
    {
      id: 'versicherung',
      title: 'Versicherung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="versicherung">Zuständige Versicherung</Label>
            <select
              id="versicherung"
              value={schaden.versicherung}
              onChange={(e) => updateField('versicherung', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="hagel">Vereinigte Hagel (VH-2024-5678)</option>
              <option value="haftpflicht">R+V Haftpflicht (RV-2024-1234)</option>
              <option value="feuer">LVM Feuerversicherung (LVM-2024-9012)</option>
            </select>
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
            <h3 className="text-center text-2xl font-bold mb-6">Schadenmeldung bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Schadenart</dt>
                <dd className="font-semibold">{schaden.art || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Datum</dt>
                <dd className="font-semibold">{new Date(schaden.datum).toLocaleDateString('de-DE')}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Ort</dt>
                <dd className="font-semibold">{schaden.ort || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Schadenhöhe</dt>
                <dd className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(schaden.schadenhoehe)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Versicherung</dt>
                <dd className="font-semibold">{schaden.versicherung || 'Nicht ausgewählt'}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Schadenmeldung wird an Versicherung übermittelt</p>
              <p className="mt-1">Ein Sachverständiger wird Sie kontaktieren</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Schadenmeldung"
        steps={steps}
        onFinish={() => navigate('/schaeden/liste')}
        onCancel={() => navigate('/schaeden/liste')}
      />
    </div>
  )
}
