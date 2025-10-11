import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle } from 'lucide-react'

type LaborData = {
  chargenId: string
  artikel: string
  labor: string
  analysen: string[]
  prioritaet: 'standard' | 'express'
  bemerkungen: string
}

export default function LaborAuftragPage(): JSX.Element {
  const navigate = useNavigate()
  const [labor, setLabor] = useState<LaborData>({
    chargenId: '',
    artikel: '',
    labor: '',
    analysen: [],
    prioritaet: 'standard',
    bemerkungen: '',
  })

  function updateField<K extends keyof LaborData>(key: K, value: LaborData[K]): void {
    setLabor((prev) => ({ ...prev, [key]: value }))
  }

  function toggleAnalyse(analyseType: string): void {
    setLabor((prev) => ({
      ...prev,
      analysen: prev.analysen.includes(analyseType)
        ? prev.analysen.filter((a) => a !== analyseType)
        : [...prev.analysen, analyseType],
    }))
  }

  const steps = [
    {
      id: 'probe',
      title: 'Probe',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="chargenId">Chargen-ID *</Label>
            <Input
              id="chargenId"
              value={labor.chargenId}
              onChange={(e) => updateField('chargenId', e.target.value)}
              placeholder="z.B. 251011-WEI-001"
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="artikel">Artikel</Label>
            <Input id="artikel" value={labor.artikel} onChange={(e) => updateField('artikel', e.target.value)} />
          </div>
        </div>
      ),
    },
    {
      id: 'analysen',
      title: 'Analysen',
      content: (
        <div className="space-y-4">
          <Label>Analysen auswählen *</Label>
          <div className="space-y-2">
            {['Feuchtigkeit', 'Protein', 'Verunreinigung', 'Mykotoxine', 'Pestizide', 'Schwermetalle'].map((a) => (
              <label key={a} className="flex items-center gap-2 rounded-lg border p-3 cursor-pointer hover:bg-accent">
                <input type="checkbox" checked={labor.analysen.includes(a)} onChange={() => toggleAnalyse(a)} className="h-4 w-4" />
                <span className="font-medium">{a}</span>
                {a === 'Mykotoxine' && <Badge variant="secondary">Empfohlen</Badge>}
              </label>
            ))}
          </div>
        </div>
      ),
    },
    {
      id: 'labor',
      title: 'Labor',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="labor">Labor *</Label>
            <select
              id="labor"
              value={labor.labor}
              onChange={(e) => updateField('labor', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="labor-nord">Labor Nord GmbH (5-7 Tage)</option>
              <option value="labor-sued">Labor Süd (3-5 Tage)</option>
              <option value="labor-express">Express Labor (24h)</option>
            </select>
          </div>
          <div>
            <Label>Priorität</Label>
            <div className="mt-2 space-y-2">
              <label className="flex items-center gap-2 rounded-lg border p-3 cursor-pointer hover:bg-accent">
                <input
                  type="radio"
                  name="prioritaet"
                  checked={labor.prioritaet === 'standard'}
                  onChange={() => updateField('prioritaet', 'standard')}
                />
                <div>
                  <div className="font-semibold">Standard</div>
                  <div className="text-sm text-muted-foreground">Reguläre Bearbeitung</div>
                </div>
              </label>
              <label className="flex items-center gap-2 rounded-lg border p-3 cursor-pointer hover:bg-accent">
                <input
                  type="radio"
                  name="prioritaet"
                  checked={labor.prioritaet === 'express'}
                  onChange={() => updateField('prioritaet', 'express')}
                />
                <div>
                  <div className="font-semibold">Express</div>
                  <div className="text-sm text-muted-foreground">Beschleunigte Bearbeitung (+50% Kosten)</div>
                </div>
              </label>
            </div>
          </div>
          <div>
            <Label htmlFor="bemerkungen">Bemerkungen</Label>
            <Textarea
              id="bemerkungen"
              value={labor.bemerkungen}
              onChange={(e) => updateField('bemerkungen', e.target.value)}
              rows={3}
            />
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
            <h3 className="text-center text-2xl font-bold mb-6">Labor-Auftrag bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Charge</dt>
                <dd className="font-mono font-semibold">{labor.chargenId}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Analysen</dt>
                <dd className="font-semibold">{labor.analysen.length} ausgewählt</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Labor</dt>
                <dd className="font-semibold">{labor.labor || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Priorität</dt>
                <dd>
                  <Badge variant={labor.prioritaet === 'express' ? 'destructive' : 'outline'}>
                    {labor.prioritaet === 'express' ? 'Express' : 'Standard'}
                  </Badge>
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Labor-Auftrag erstellen"
        steps={steps}
        onFinish={() => navigate('/qualitaet/labor-liste')}
        onCancel={() => navigate('/qualitaet/labor-liste')}
      />
    </div>
  )
}
