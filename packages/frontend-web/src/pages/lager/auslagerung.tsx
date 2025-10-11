import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type AuslagerungData = {
  artikel: string
  menge: number
  strategie: 'fifo' | 'fefo' | 'manuell'
  chargenId: string
  verwendungszweck: string
}

export default function AuslagerungPage(): JSX.Element {
  const navigate = useNavigate()
  const [auslagerung, setAuslagerung] = useState<AuslagerungData>({
    artikel: '',
    menge: 0,
    strategie: 'fifo',
    chargenId: '',
    verwendungszweck: '',
  })

  function updateField<K extends keyof AuslagerungData>(key: K, value: AuslagerungData[K]): void {
    if (key === 'strategie' && value === 'fifo') {
      setAuslagerung((prev) => ({ ...prev, [key]: value, chargenId: '251001-WEI-001 (älteste)' }))
    } else {
      setAuslagerung((prev) => ({ ...prev, [key]: value }))
    }
  }

  const steps = [
    {
      id: 'artikel',
      title: 'Artikel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <Input id="artikel" value={auslagerung.artikel} onChange={(e) => updateField('artikel', e.target.value)} />
          </div>
          <div>
            <Label htmlFor="menge">Menge (t) *</Label>
            <Input id="menge" type="number" value={auslagerung.menge} onChange={(e) => updateField('menge', Number(e.target.value))} step="0.001" />
          </div>
        </div>
      ),
    },
    {
      id: 'strategie',
      title: 'Strategie',
      content: (
        <div className="space-y-4">
          <div>
            <Label>Auslagerungs-Strategie</Label>
            <div className="mt-2 space-y-2">
              <label className="flex items-center gap-2 rounded-lg border p-3 cursor-pointer hover:bg-accent">
                <input
                  type="radio"
                  name="strategie"
                  checked={auslagerung.strategie === 'fifo'}
                  onChange={() => updateField('strategie', 'fifo')}
                />
                <div>
                  <div className="font-semibold">FIFO (First In, First Out)</div>
                  <div className="text-sm text-muted-foreground">Älteste Charge zuerst</div>
                </div>
                <Badge className="ml-auto">Empfohlen</Badge>
              </label>
              <label className="flex items-center gap-2 rounded-lg border p-3 cursor-pointer hover:bg-accent">
                <input
                  type="radio"
                  name="strategie"
                  checked={auslagerung.strategie === 'fefo'}
                  onChange={() => updateField('strategie', 'fefo')}
                />
                <div>
                  <div className="font-semibold">FEFO (First Expired, First Out)</div>
                  <div className="text-sm text-muted-foreground">Kürzeste Haltbarkeit zuerst</div>
                </div>
              </label>
            </div>
          </div>
          <div>
            <Label>Ausgewählte Charge</Label>
            <div className="mt-2 font-mono font-semibold">{auslagerung.chargenId || '-'}</div>
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
            <h3 className="text-center text-2xl font-bold mb-6">Auslagerung bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Artikel</dt>
                <dd className="font-semibold">{auslagerung.artikel}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Menge</dt>
                <dd className="font-semibold">{auslagerung.menge} t</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Strategie</dt>
                <dd><Badge>{auslagerung.strategie.toUpperCase()}</Badge></dd>
              </div>
              <div className="flex justify-between">
                <dt>Charge</dt>
                <dd className="font-mono">{auslagerung.chargenId}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard title="Auslagerung" steps={steps} onFinish={() => navigate('/lager/bestandsuebersicht')} onCancel={() => navigate('/lager/bestandsuebersicht')} />
    </div>
  )
}
