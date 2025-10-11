import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle } from 'lucide-react'

type FoerderungData = {
  programm: string
  betriebsnummer: string
  flaeche: number
  massnahme: string
  betrag: number
  bemerkung: string
}

export default function FoerderantragPage(): JSX.Element {
  const navigate = useNavigate()
  const [foerderung, setFoerderung] = useState<FoerderungData>({
    programm: '',
    betriebsnummer: '',
    flaeche: 0,
    massnahme: '',
    betrag: 0,
    bemerkung: '',
  })

  function updateField<K extends keyof FoerderungData>(key: K, value: FoerderungData[K]): void {
    if (key === 'programm' && value === 'greening') {
      setFoerderung((prev) => ({ ...prev, [key]: value, betrag: prev.flaeche * 85 }))
    } else if (key === 'flaeche') {
      setFoerderung((prev) => ({ ...prev, [key]: value, betrag: Number(value) * 85 }))
    } else {
      setFoerderung((prev) => ({ ...prev, [key]: value }))
    }
  }

  const steps = [
    {
      id: 'programm',
      title: 'Programm',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="programm">Förderprogramm *</Label>
            <select
              id="programm"
              value={foerderung.programm}
              onChange={(e) => updateField('programm', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="greening">Greening / Direktzahlungen (85 €/ha)</option>
              <option value="oeko">Öko-Regelung (60 €/ha)</option>
              <option value="biodiversitaet">Biodiversität (1.200 €/ha)</option>
            </select>
          </div>
          <div>
            <Label htmlFor="betriebsnummer">Betriebsnummer *</Label>
            <Input
              id="betriebsnummer"
              value={foerderung.betriebsnummer}
              onChange={(e) => updateField('betriebsnummer', e.target.value)}
              placeholder="z.B. 276123456"
              className="font-mono"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'flaeche',
      title: 'Fläche',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="flaeche">Förderfähige Fläche (ha) *</Label>
            <Input
              id="flaeche"
              type="number"
              value={foerderung.flaeche}
              onChange={(e) => updateField('flaeche', Number(e.target.value))}
              step="0.01"
            />
          </div>
          <div>
            <Label htmlFor="massnahme">Maßnahme</Label>
            <Input id="massnahme" value={foerderung.massnahme} onChange={(e) => updateField('massnahme', e.target.value)} />
          </div>
          <div className="rounded-lg bg-muted p-4">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm text-muted-foreground">Voraussichtliche Förderung</div>
                <div className="text-3xl font-bold text-green-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(foerderung.betrag)}
                </div>
              </div>
              <Badge variant="outline" className="text-lg px-4 py-2">
                {foerderung.flaeche > 0 ? (foerderung.betrag / foerderung.flaeche).toFixed(0) : 0} € / ha
              </Badge>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'bemerkung',
      title: 'Bemerkungen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bemerkung">Bemerkungen (optional)</Label>
            <Textarea
              id="bemerkung"
              value={foerderung.bemerkung}
              onChange={(e) => updateField('bemerkung', e.target.value)}
              rows={6}
              placeholder="Zusätzliche Informationen..."
            />
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
            <h3 className="text-center text-2xl font-bold mb-6">Antrag bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Programm</dt>
                <dd className="font-semibold">{foerderung.programm || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Betriebsnummer</dt>
                <dd className="font-mono font-semibold">{foerderung.betriebsnummer}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Fläche</dt>
                <dd className="font-semibold">{foerderung.flaeche} ha</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Förderbetrag</dt>
                <dd className="font-bold text-green-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(foerderung.betrag)}
                </dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Antrag wird an Behörde übermittelt</p>
              <p className="mt-1">Bearbeitungszeit: ca. 6-8 Wochen</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Förderantrag stellen"
        steps={steps}
        onFinish={() => navigate('/foerderung/liste')}
        onCancel={() => navigate('/foerderung/liste')}
      />
    </div>
  )
}
