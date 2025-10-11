import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type EinlagerungData = {
  chargenId: string
  artikel: string
  menge: number
  lagerort: string
  lagerplatz: string
}

export default function EinlagerungPage(): JSX.Element {
  const navigate = useNavigate()
  const [einlagerung, setEinlagerung] = useState<EinlagerungData>({
    chargenId: '',
    artikel: '',
    menge: 0,
    lagerort: '',
    lagerplatz: '',
  })

  function updateField<K extends keyof EinlagerungData>(key: K, value: EinlagerungData[K]): void {
    setEinlagerung((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(): Promise<void> {
    console.log('Einlagerung buchen:', einlagerung)
    navigate('/lager/bestandsuebersicht')
  }

  const steps = [
    {
      id: 'charge',
      title: 'Charge',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="chargenId">Chargen-ID *</Label>
            <Input
              id="chargenId"
              value={einlagerung.chargenId}
              onChange={(e) => updateField('chargenId', e.target.value)}
              placeholder="z.B. 251011-WEI-001"
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="artikel">Artikel</Label>
            <Input id="artikel" value={einlagerung.artikel} onChange={(e) => updateField('artikel', e.target.value)} />
          </div>
          <div>
            <Label htmlFor="menge">Menge (t)</Label>
            <Input id="menge" type="number" value={einlagerung.menge} onChange={(e) => updateField('menge', Number(e.target.value))} step="0.001" />
          </div>
        </div>
      ),
    },
    {
      id: 'lagerort',
      title: 'Lagerort',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lagerort">Lagerort *</Label>
            <select
              id="lagerort"
              value={einlagerung.lagerort}
              onChange={(e) => updateField('lagerort', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="silo-1">Silo 1 (Weizen)</option>
              <option value="silo-2">Silo 2 (Gerste)</option>
              <option value="halle-a">Halle A</option>
            </select>
          </div>
          <div>
            <Label htmlFor="lagerplatz">Lagerplatz</Label>
            <Input id="lagerplatz" value={einlagerung.lagerplatz} onChange={(e) => updateField('lagerplatz', e.target.value)} placeholder="z.B. A-12-03" />
          </div>
        </div>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestätigung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Einlagerung bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt className="text-sm font-medium text-muted-foreground">Charge</dt>
                <dd className="text-sm font-semibold font-mono">{einlagerung.chargenId}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt className="text-sm font-medium text-muted-foreground">Artikel</dt>
                <dd className="text-sm font-semibold">{einlagerung.artikel}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt className="text-sm font-medium text-muted-foreground">Menge</dt>
                <dd className="text-sm font-semibold">{einlagerung.menge} t</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-muted-foreground">Lagerort</dt>
                <dd className="text-sm font-semibold">{einlagerung.lagerort} / {einlagerung.lagerplatz || 'Auto'}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard title="Einlagerung" steps={steps} onFinish={handleSubmit} onCancel={() => navigate('/lager/bestandsuebersicht')} />
    </div>
  )
}
