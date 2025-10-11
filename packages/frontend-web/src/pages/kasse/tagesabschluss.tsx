import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type AbschlussData = {
  kassenstand: number
  barverkauf: number
  kartenzahlung: number
  differenz: number
}

export default function TagesabschlussPage(): JSX.Element {
  const navigate = useNavigate()
  const [abschluss, setAbschluss] = useState<AbschlussData>({
    kassenstand: 0,
    barverkauf: 2450.0,
    kartenzahlung: 3200.0,
    differenz: 0,
  })

  function updateKassenstand(value: number): void {
    const soll = abschluss.barverkauf
    const diff = value - soll
    setAbschluss((prev) => ({ ...prev, kassenstand: value, differenz: diff }))
  }

  const steps = [
    {
      id: 'kassenstand',
      title: 'Kassenstand',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="kassenstand">Gezählter Kassenstand (€) *</Label>
            <Input
              id="kassenstand"
              type="number"
              value={abschluss.kassenstand}
              onChange={(e) => updateKassenstand(Number(e.target.value))}
              step="0.01"
              className="text-2xl font-bold text-center"
            />
          </div>
          <div className="rounded-lg bg-muted p-4">
            <div className="grid gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Barverkauf (Soll):</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.barverkauf)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Kassenstand (Ist):</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.kassenstand)}
                </span>
              </div>
              <div className="flex justify-between border-t pt-2">
                <span className="font-medium">Differenz:</span>
                <span className={`font-bold ${abschluss.differenz === 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {abschluss.differenz > 0 ? '+' : ''}
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenz)}
                </span>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'kartenzahlung',
      title: 'Kartenzahlung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="kartenzahlung">Kartenzahlung Terminal (€)</Label>
            <Input
              id="kartenzahlung"
              type="number"
              value={abschluss.kartenzahlung}
              readOnly
              className="text-2xl font-bold text-center bg-muted"
            />
          </div>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">Automatisch aus Terminal ausgelesen</p>
            <p className="mt-1">Keine manuelle Eingabe erforderlich</p>
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
            <h3 className="text-center text-2xl font-bold mb-6">Tagesabschluss bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Barverkauf</dt>
                <dd className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.barverkauf)}
                </dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Kartenzahlung</dt>
                <dd className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.kartenzahlung)}
                </dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Kassenstand</dt>
                <dd className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.kassenstand)}
                </dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Differenz</dt>
                <dd>
                  <Badge variant={abschluss.differenz === 0 ? 'outline' : 'destructive'}>
                    {abschluss.differenz > 0 ? '+' : ''}
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenz)}
                  </Badge>
                </dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Tagesabschluss wird gebucht</p>
              <p className="mt-1">Daten werden an Finanzbuchhaltung übertragen</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Kassen-Tagesabschluss"
        steps={steps}
        onFinish={() => navigate('/kasse/historie')}
        onCancel={() => navigate('/kasse/historie')}
      />
    </div>
  )
}
