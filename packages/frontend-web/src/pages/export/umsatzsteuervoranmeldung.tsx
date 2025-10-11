import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, FileDown } from 'lucide-react'
import { Button } from '@/components/ui/button'

type UStVAData = {
  zeitraum: string
  umsatz: number
  vorsteuer: number
  zahllast: number
}

export default function UmsatzsteuerVoranmeldungPage(): JSX.Element {
  const navigate = useNavigate()
  const [ustData, setUstData] = useState<UStVAData>({
    zeitraum: '',
    umsatz: 0,
    vorsteuer: 0,
    zahllast: 0,
  })

  function updateField<K extends keyof UStVAData>(key: K, value: UStVAData[K]): void {
    if (key === 'umsatz' || key === 'vorsteuer') {
      const newUmsatz = key === 'umsatz' ? Number(value) : ustData.umsatz
      const newVorsteuer = key === 'vorsteuer' ? Number(value) : ustData.vorsteuer
      const ustUmsatz = newUmsatz * 0.19
      setUstData((prev) => ({ ...prev, [key]: value, zahllast: ustUmsatz - newVorsteuer }))
    } else {
      setUstData((prev) => ({ ...prev, [key]: value }))
    }
  }

  const steps = [
    {
      id: 'zeitraum',
      title: 'Zeitraum',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="zeitraum">Voranmeldungszeitraum *</Label>
            <select
              id="zeitraum"
              value={ustData.zeitraum}
              onChange={(e) => updateField('zeitraum', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="2025-Q1">Q1 2025 (Januar - März)</option>
              <option value="2025-Q2">Q2 2025 (April - Juni)</option>
              <option value="2025-Q3">Q3 2025 (Juli - September)</option>
              <option value="2025-Q4">Q4 2025 (Oktober - Dezember)</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'betraege',
      title: 'Beträge',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="umsatz">Umsatz (netto) *</Label>
            <Input
              id="umsatz"
              type="number"
              value={ustData.umsatz}
              onChange={(e) => updateField('umsatz', Number(e.target.value))}
              step="0.01"
            />
            <p className="text-sm text-muted-foreground mt-1">Umsatzsteuer (19%): {(ustData.umsatz * 0.19).toFixed(2)} €</p>
          </div>
          <div>
            <Label htmlFor="vorsteuer">Vorsteuer *</Label>
            <Input
              id="vorsteuer"
              type="number"
              value={ustData.vorsteuer}
              onChange={(e) => updateField('vorsteuer', Number(e.target.value))}
              step="0.01"
            />
          </div>
          <div className="rounded-lg bg-muted p-4">
            <div className="text-sm text-muted-foreground mb-1">Umsatzsteuer-Zahllast</div>
            <div className="text-3xl font-bold text-blue-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(ustData.zahllast)}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {ustData.zahllast > 0 ? 'Zahlung an Finanzamt' : 'Erstattung vom Finanzamt'}
            </p>
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
            <h3 className="text-center text-2xl font-bold mb-6">UStVA bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Zeitraum</dt>
                <dd className="font-semibold">{ustData.zeitraum}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Umsatz (netto)</dt>
                <dd className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(ustData.umsatz)}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Umsatzsteuer (19%)</dt>
                <dd className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(ustData.umsatz * 0.19)}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Vorsteuer</dt>
                <dd className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(ustData.vorsteuer)}</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Zahllast</dt>
                <dd className="font-bold text-blue-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(ustData.zahllast)}</dd>
              </div>
            </dl>
            <div className="mt-6 space-y-2">
              <Button className="w-full gap-2" variant="outline">
                <FileDown className="h-4 w-4" />
                ELSTER-XML Export
              </Button>
              <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
                <p className="font-semibold">Übermittlung an Finanzamt</p>
                <p className="mt-1">Via ELSTER-Schnittstelle</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Umsatzsteuer-Voranmeldung"
        steps={steps}
        onFinish={() => navigate('/fibu')}
        onCancel={() => navigate('/fibu')}
      />
    </div>
  )
}
