import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Truck } from 'lucide-react'

type BeladungData = {
  kennzeichen: string
  lieferscheinNr: string
  artikel: string
  menge: number
  chargenId: string
  verladeort: string
}

export default function LKWBeladungPage(): JSX.Element {
  const navigate = useNavigate()
  const [beladung, setBeladung] = useState<BeladungData>({
    kennzeichen: '',
    lieferscheinNr: '',
    artikel: '',
    menge: 0,
    chargenId: '',
    verladeort: '',
  })

  function updateField<K extends keyof BeladungData>(key: K, value: BeladungData[K]): void {
    setBeladung((prev) => ({ ...prev, [key]: value }))
  }

  const steps = [
    {
      id: 'lkw',
      title: 'LKW',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="kennzeichen">Kennzeichen *</Label>
            <Input
              id="kennzeichen"
              value={beladung.kennzeichen}
              onChange={(e) => updateField('kennzeichen', e.target.value.toUpperCase())}
              placeholder="z.B. AB-CD 1234"
              className="font-mono text-center text-lg font-bold"
            />
          </div>
          <div>
            <Label htmlFor="lieferscheinNr">Lieferschein-Nr. *</Label>
            <Input
              id="lieferscheinNr"
              value={beladung.lieferscheinNr}
              onChange={(e) => updateField('lieferscheinNr', e.target.value)}
              placeholder="z.B. LS-2025-042"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'artikel',
      title: 'Artikel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <Input id="artikel" value={beladung.artikel} onChange={(e) => updateField('artikel', e.target.value)} />
          </div>
          <div>
            <Label htmlFor="menge">Menge (t) *</Label>
            <Input id="menge" type="number" value={beladung.menge} onChange={(e) => updateField('menge', Number(e.target.value))} step="0.001" />
          </div>
          <div>
            <Label htmlFor="chargenId">Chargen-ID *</Label>
            <Input
              id="chargenId"
              value={beladung.chargenId}
              onChange={(e) => updateField('chargenId', e.target.value)}
              placeholder="z.B. 251011-WEI-001"
              className="font-mono"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'verladeort',
      title: 'Verladeort',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="verladeort">Verladeort *</Label>
            <select
              id="verladeort"
              value={beladung.verladeort}
              onChange={(e) => updateField('verladeort', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="silo-1">Silo 1</option>
              <option value="silo-2">Silo 2</option>
              <option value="halle-a">Halle A</option>
            </select>
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
              <div className="rounded-full bg-muted p-6">
                <Truck className="h-16 w-16" />
              </div>
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Beladung bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Kennzeichen</dt>
                <dd className="font-mono font-bold">{beladung.kennzeichen}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Artikel</dt>
                <dd className="font-semibold">{beladung.artikel}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Menge</dt>
                <dd className="font-semibold">{beladung.menge} t</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Charge</dt>
                <dd className="font-mono">{beladung.chargenId}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Verladeort</dt>
                <dd className="font-semibold">{beladung.verladeort}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Beladung wird dokumentiert</p>
              <p className="mt-1">Lieferschein wird automatisch erstellt</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="LKW-Beladung"
        steps={steps}
        onFinish={() => navigate('/logistik/verladungen')}
        onCancel={() => navigate('/logistik/verladungen')}
      />
    </div>
  )
}
