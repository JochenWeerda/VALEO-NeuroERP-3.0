import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type BedarfData = {
  flaeche: number
  kultur: string
  bodenanalyse: {
    n: number
    p: number
    k: number
  }
  ertragsziel: number
  empfehlung: {
    n: number
    p: number
    k: number
  }
}

export default function BedarfsrechnerPage(): JSX.Element {
  const navigate = useNavigate()
  const [bedarf, setBedarf] = useState<BedarfData>({
    flaeche: 0,
    kultur: '',
    bodenanalyse: { n: 0, p: 0, k: 0 },
    ertragsziel: 0,
    empfehlung: { n: 0, p: 0, k: 0 },
  })

  function updateFlaeche(value: number): void {
    setBedarf((prev) => ({ ...prev, flaeche: value }))
  }

  function updateKultur(value: string): void {
    setBedarf((prev) => ({ ...prev, kultur: value }))
  }

  function updateBodenanalyse(key: keyof BedarfData['bodenanalyse'], value: number): void {
    setBedarf((prev) => ({
      ...prev,
      bodenanalyse: { ...prev.bodenanalyse, [key]: value },
    }))
  }

  function updateErtragsziel(value: number): void {
    const n = value * 2.5
    const p = value * 0.8
    const k = value * 1.2
    setBedarf((prev) => ({
      ...prev,
      ertragsziel: value,
      empfehlung: { n, p, k },
    }))
  }

  const steps = [
    {
      id: 'grunddaten',
      title: 'Grunddaten',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="flaeche">Fläche (ha) *</Label>
            <Input
              id="flaeche"
              type="number"
              value={bedarf.flaeche}
              onChange={(e) => updateFlaeche(Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="kultur">Kultur *</Label>
            <select
              id="kultur"
              value={bedarf.kultur}
              onChange={(e) => updateKultur(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="weizen">Weizen</option>
              <option value="gerste">Gerste</option>
              <option value="raps">Raps</option>
              <option value="mais">Mais</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'bodenanalyse',
      title: 'Bodenanalyse',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="n">Stickstoff (N) mg/100g</Label>
            <Input
              id="n"
              type="number"
              value={bedarf.bodenanalyse.n}
              onChange={(e) => updateBodenanalyse('n', Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="p">Phosphor (P) mg/100g</Label>
            <Input
              id="p"
              type="number"
              value={bedarf.bodenanalyse.p}
              onChange={(e) => updateBodenanalyse('p', Number(e.target.value))}
              step="0.1"
            />
          </div>
          <div>
            <Label htmlFor="k">Kalium (K) mg/100g</Label>
            <Input
              id="k"
              type="number"
              value={bedarf.bodenanalyse.k}
              onChange={(e) => updateBodenanalyse('k', Number(e.target.value))}
              step="0.1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'ertrag',
      title: 'Ertragsziel',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="ertragsziel">Ertragsziel (dt/ha) *</Label>
            <Input
              id="ertragsziel"
              type="number"
              value={bedarf.ertragsziel}
              onChange={(e) => updateErtragsziel(Number(e.target.value))}
              step="1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'empfehlung',
      title: 'Empfehlung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Dünge-Empfehlung</h3>
            <div className="space-y-3">
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Stickstoff (N)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">{bedarf.empfehlung.n.toFixed(0)} kg/ha</div>
                  <div className="text-sm text-muted-foreground">{(bedarf.empfehlung.n * bedarf.flaeche).toFixed(0)} kg gesamt</div>
                </div>
              </div>
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Phosphor (P)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">{bedarf.empfehlung.p.toFixed(0)} kg/ha</div>
                  <div className="text-sm text-muted-foreground">{(bedarf.empfehlung.p * bedarf.flaeche).toFixed(0)} kg gesamt</div>
                </div>
              </div>
              <div className="flex justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">Kalium (K)</div>
                  <Badge variant="outline">Hauptnährstoff</Badge>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">{bedarf.empfehlung.k.toFixed(0)} kg/ha</div>
                  <div className="text-sm text-muted-foreground">{(bedarf.empfehlung.k * bedarf.flaeche).toFixed(0)} kg gesamt</div>
                </div>
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
        title="Düngebedarf berechnen"
        steps={steps}
        onFinish={() => navigate('/agrar/duenger/liste')}
        onCancel={() => navigate('/agrar/duenger/liste')}
      />
    </div>
  )
}
