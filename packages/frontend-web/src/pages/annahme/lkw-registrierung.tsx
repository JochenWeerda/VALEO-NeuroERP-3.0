import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Camera, Clock, Truck } from 'lucide-react'

type LKWData = {
  kennzeichen: string
  lieferant: string
  lieferscheinNr: string
  artikel: string
  ankunftszeit: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
}

export default function LKWRegistrierungPage(): JSX.Element {
  const navigate = useNavigate()
  const [lkw, setLKW] = useState<LKWData>({
    kennzeichen: '',
    lieferant: '',
    lieferscheinNr: '',
    artikel: '',
    ankunftszeit: new Date().toISOString().slice(0, 16),
    prioritaet: 'normal',
  })

  function updateField<K extends keyof LKWData>(key: K, value: LKWData[K]): void {
    setLKW((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(): Promise<void> {
    console.log('LKW registrieren:', lkw)
    navigate('/annahme/warteschlange')
  }

  const steps = [
    {
      id: 'kennzeichen',
      title: 'Kennzeichen',
      content: (
        <div className="space-y-6">
          <div className="flex items-center justify-center">
            <Truck className="h-24 w-24 text-muted-foreground" />
          </div>
          <div>
            <Label htmlFor="kennzeichen">Kennzeichen *</Label>
            <div className="flex gap-2">
              <Input
                id="kennzeichen"
                value={lkw.kennzeichen}
                onChange={(e) => updateField('kennzeichen', e.target.value.toUpperCase())}
                placeholder="z.B. AB-CD 1234"
                required
                className="text-lg font-semibold text-center"
              />
              <button
                type="button"
                className="flex items-center gap-2 rounded-md border border-input bg-background px-4 hover:bg-accent"
              >
                <Camera className="h-4 w-4" />
                Scan
              </button>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Kennzeichen eingeben oder mit Kamera scannen
            </p>
          </div>
          <div>
            <Label htmlFor="ankunftszeit">Ankunftszeit</Label>
            <Input
              id="ankunftszeit"
              type="datetime-local"
              value={lkw.ankunftszeit}
              onChange={(e) => updateField('ankunftszeit', e.target.value)}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'lieferung',
      title: 'Lieferung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferant">Lieferant *</Label>
            <Input
              id="lieferant"
              value={lkw.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder="Name des Lieferanten"
              required
            />
          </div>
          <div>
            <Label htmlFor="lieferscheinNr">Lieferschein-Nr.</Label>
            <div className="flex gap-2">
              <Input
                id="lieferscheinNr"
                value={lkw.lieferscheinNr}
                onChange={(e) => updateField('lieferscheinNr', e.target.value)}
                placeholder="z.B. LS-2025-0042"
              />
              <button
                type="button"
                className="flex items-center gap-2 rounded-md border border-input bg-background px-4 hover:bg-accent"
              >
                <Camera className="h-4 w-4" />
                Scan
              </button>
            </div>
          </div>
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <Input
              id="artikel"
              value={lkw.artikel}
              onChange={(e) => updateField('artikel', e.target.value)}
              placeholder="z.B. Weizen"
              required
            />
          </div>
          <div>
            <Label htmlFor="prioritaet">Priorität</Label>
            <select
              id="prioritaet"
              value={lkw.prioritaet}
              onChange={(e) => updateField('prioritaet', e.target.value as LKWData['prioritaet'])}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="hoch">Hoch (Express)</option>
              <option value="normal">Normal</option>
              <option value="niedrig">Niedrig</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestätigung',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center mb-6">
                <div className="rounded-full bg-muted p-6">
                  <Truck className="h-16 w-16" />
                </div>
              </div>
              <h3 className="text-center text-2xl font-bold mb-6">{lkw.kennzeichen || 'KENNZEICHEN'}</h3>
              <dl className="grid gap-4">
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferant</dt>
                  <dd className="text-sm font-semibold">{lkw.lieferant || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Lieferschein-Nr.</dt>
                  <dd className="text-sm font-semibold">{lkw.lieferscheinNr || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Artikel</dt>
                  <dd className="text-sm font-semibold">{lkw.artikel || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Ankunftszeit</dt>
                  <dd className="text-sm font-semibold flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    {new Date(lkw.ankunftszeit).toLocaleString('de-DE')}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-muted-foreground">Priorität</dt>
                  <dd>
                    <Badge
                      variant={lkw.prioritaet === 'hoch' ? 'destructive' : lkw.prioritaet === 'normal' ? 'default' : 'secondary'}
                    >
                      {lkw.prioritaet === 'hoch' ? 'Hoch (Express)' : lkw.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
                    </Badge>
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">LKW wird in die Warteschlange eingereiht</p>
            <p className="mt-1">Der Fahrer erhält eine Wartenummer per SMS</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="LKW-Registrierung"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/annahme/warteschlange')}
      />
    </div>
  )
}
