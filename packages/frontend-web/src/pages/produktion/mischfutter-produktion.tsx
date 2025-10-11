import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type ProduktionData = {
  rezeptur: string
  menge: number
  komponenten: Array<{ name: string; bedarf: number; verfuegbar: number }>
  chargenId: string
}

export default function MischfutterProduktionPage(): JSX.Element {
  const navigate = useNavigate()
  const [produktion, setProduktion] = useState<ProduktionData>({
    rezeptur: '',
    menge: 0,
    komponenten: [],
    chargenId: '',
  })

  function updateMenge(value: number): void {
    const komp = [
      { name: 'Sojaschrot 44%', bedarf: value * 0.25, verfuegbar: 280 },
      { name: 'Weizen', bedarf: value * 0.3, verfuegbar: 450 },
      { name: 'Mais', bedarf: value * 0.2, verfuegbar: 320 },
      { name: 'Mineralfutter', bedarf: value * 0.05, verfuegbar: 50 },
    ]
    setProduktion((prev) => ({
      ...prev,
      menge: value,
      komponenten: komp,
      chargenId: `MF-${new Date().toISOString().slice(2, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
    }))
  }

  const steps = [
    {
      id: 'rezeptur',
      title: 'Rezeptur',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="rezeptur">Rezeptur *</Label>
            <select
              id="rezeptur"
              value={produktion.rezeptur}
              onChange={(e) => setProduktion({ ...produktion, rezeptur: e.target.value })}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="milchvieh">Milchviehfutter Hochleistung</option>
              <option value="mast">Mastbullenfutter</option>
              <option value="sauen">Sauenfutter</option>
            </select>
          </div>
          <div>
            <Label htmlFor="menge">Produktionsmenge (t) *</Label>
            <Input
              id="menge"
              type="number"
              value={produktion.menge}
              onChange={(e) => updateMenge(Number(e.target.value))}
              step="0.1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'komponenten',
      title: 'Komponenten',
      content: (
        <div className="space-y-3">
          <Label>Rezeptur-Komponenten (Bedarf vs. Verfügbar)</Label>
          {produktion.komponenten.map((k, i) => {
            const ausreichend = k.verfuegbar >= k.bedarf
            return (
              <Card key={i} className={ausreichend ? 'border-green-500' : 'border-red-500'}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{k.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Verfügbar: {k.verfuegbar.toFixed(1)} t
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{k.bedarf.toFixed(1)} t</div>
                      <Badge variant={ausreichend ? 'outline' : 'destructive'}>
                        {ausreichend ? '✓ OK' : '✗ Fehlt'}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ),
    },
    {
      id: 'produktion',
      title: 'Produktion',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Produktion bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Rezeptur</dt>
                <dd className="font-semibold">{produktion.rezeptur || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Menge</dt>
                <dd className="font-semibold">{produktion.menge} t</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Komponenten</dt>
                <dd className="font-semibold">{produktion.komponenten.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Chargen-ID</dt>
                <dd className="font-mono font-semibold">{produktion.chargenId}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Produktionsauftrag wird erstellt</p>
              <p className="mt-1">Komponenten werden automatisch ausgebucht</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Mischfutter-Produktion"
        steps={steps}
        onFinish={() => navigate('/futter/misch/liste')}
        onCancel={() => navigate('/futter/misch/liste')}
      />
    </div>
  )
}
