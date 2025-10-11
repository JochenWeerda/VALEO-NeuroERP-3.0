import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type EtikettenData = {
  chargenId: string
  artikel: string
  menge: number
  lieferant: string
  eingang: string
  anzahlEtiketten: number
  drucker: string
}

export default function EtikettenDruckenPage(): JSX.Element {
  const navigate = useNavigate()
  const [etiketten, setEtiketten] = useState<EtikettenData>({
    chargenId: '',
    artikel: '',
    menge: 0,
    lieferant: '',
    eingang: new Date().toISOString().slice(0, 10),
    anzahlEtiketten: 1,
    drucker: '',
  })

  function updateField<K extends keyof EtikettenData>(key: K, value: EtikettenData[K]): void {
    setEtiketten((prev) => ({ ...prev, [key]: value }))
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
              value={etiketten.chargenId}
              onChange={(e) => updateField('chargenId', e.target.value)}
              placeholder="z.B. 251011-WEI-001"
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="artikel">Artikel</Label>
            <Input id="artikel" value={etiketten.artikel} onChange={(e) => updateField('artikel', e.target.value)} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="menge">Menge (t)</Label>
              <Input id="menge" type="number" value={etiketten.menge} onChange={(e) => updateField('menge', Number(e.target.value))} step="0.001" />
            </div>
            <div>
              <Label htmlFor="lieferant">Lieferant</Label>
              <Input id="lieferant" value={etiketten.lieferant} onChange={(e) => updateField('lieferant', e.target.value)} />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'druck',
      title: 'Druck',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="anzahl">Anzahl Etiketten *</Label>
            <Input
              id="anzahl"
              type="number"
              value={etiketten.anzahlEtiketten}
              onChange={(e) => updateField('anzahlEtiketten', Number(e.target.value))}
              min="1"
            />
          </div>
          <div>
            <Label htmlFor="drucker">Drucker</Label>
            <select
              id="drucker"
              value={etiketten.drucker}
              onChange={(e) => updateField('drucker', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="zebra-1">Zebra ZT230 (Annahme)</option>
              <option value="zebra-2">Zebra ZT410 (Lager)</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'vorschau',
      title: 'Vorschau',
      content: (
        <div className="space-y-4">
          <Card className="border-2 border-dashed">
            <CardContent className="pt-6">
              <div className="space-y-2 font-mono text-sm">
                <div className="text-center font-bold text-lg">{etiketten.artikel || 'ARTIKEL'}</div>
                <div className="border-t pt-2">
                  <div className="flex justify-between">
                    <span>Charge:</span>
                    <span className="font-bold">{etiketten.chargenId || '---'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Menge:</span>
                    <span className="font-bold">{etiketten.menge} t</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lieferant:</span>
                    <span>{etiketten.lieferant || '---'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Eingang:</span>
                    <span>{new Date(etiketten.eingang).toLocaleDateString('de-DE')}</span>
                  </div>
                </div>
                <div className="border-t pt-2 text-center">
                  <div className="text-xs">QR-Code Placeholder</div>
                  <div className="mt-1 flex items-center justify-center">
                    <div className="h-16 w-16 border-2 border-black bg-white" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">{etiketten.anzahlEtiketten} Etikett(en) werden gedruckt</p>
            <p className="mt-1">Drucker: {etiketten.drucker || 'Nicht ausgewählt'}</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Etiketten drucken"
        steps={steps}
        onFinish={() => navigate('/charge/liste')}
        onCancel={() => navigate('/charge/liste')}
      />
    </div>
  )
}
