import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, FileDown } from 'lucide-react'
import { Button } from '@/components/ui/button'

type PSMUmsatz = {
  wirkstoff: string
  menge: number
  einheit: string
}

type BVLMeldungData = {
  jahr: number
  betriebsnummer: string
  umsaetze: PSMUmsatz[]
  gesamtmenge: number
}

export default function BVLUmsatzmeldungPage(): JSX.Element {
  const navigate = useNavigate()
  const [meldung, setMeldung] = useState<BVLMeldungData>({
    jahr: new Date().getFullYear() - 1,
    betriebsnummer: '',
    umsaetze: [
      { wirkstoff: 'Glyphosat', menge: 1250, einheit: 'kg' },
      { wirkstoff: 'Tebuconazol', menge: 850, einheit: 'kg' },
      { wirkstoff: 'Cypermethrin', menge: 320, einheit: 'l' },
    ],
    gesamtmenge: 2420,
  })

  const steps = [
    {
      id: 'grunddaten',
      title: 'Grunddaten',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="jahr">Berichtsjahr *</Label>
            <Input
              id="jahr"
              type="number"
              value={meldung.jahr}
              onChange={(e) => setMeldung({ ...meldung, jahr: Number(e.target.value) })}
            />
          </div>
          <div>
            <Label htmlFor="betriebsnummer">Betriebsnummer (BVL) *</Label>
            <Input
              id="betriebsnummer"
              value={meldung.betriebsnummer}
              onChange={(e) => setMeldung({ ...meldung, betriebsnummer: e.target.value })}
              placeholder="z.B. H-NDS-12345"
              className="font-mono"
            />
          </div>
          <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
            <p className="font-semibold">📋 Meldepflicht nach § 64 PflSchG</p>
            <p className="mt-1">Jährliche Meldung der Inlandsabsätze an das BVL bis 31. März</p>
          </div>
        </div>
      ),
    },
    {
      id: 'umsaetze',
      title: 'Umsätze',
      content: (
        <div className="space-y-4">
          <Label>Umsätze nach Wirkstoff (automatisch aus Verkaufsbelegen)</Label>
          <div className="space-y-2">
            {meldung.umsaetze.map((umsatz, i) => (
              <Card key={i}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{umsatz.wirkstoff}</div>
                      <div className="text-sm text-muted-foreground">Wirkstoff</div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">{umsatz.menge.toLocaleString('de-DE')}</div>
                      <div className="text-sm text-muted-foreground">{umsatz.einheit}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="rounded-lg bg-muted p-4">
            <div className="flex justify-between items-center">
              <span className="font-semibold">Gesamtmenge (Wirkstoffe)</span>
              <span className="text-2xl font-bold">{meldung.gesamtmenge.toLocaleString('de-DE')} kg/l</span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'export',
      title: 'Export',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">BVL-Meldung bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Berichtsjahr</dt>
                <dd className="font-semibold">{meldung.jahr}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Betriebsnummer</dt>
                <dd className="font-mono font-semibold">{meldung.betriebsnummer}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Wirkstoffe</dt>
                <dd className="font-semibold">{meldung.umsaetze.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Gesamtmenge</dt>
                <dd className="font-semibold">{meldung.gesamtmenge.toLocaleString('de-DE')} kg/l</dd>
              </div>
            </dl>
            <div className="mt-6 space-y-2">
              <Button className="w-full gap-2" variant="outline">
                <FileDown className="h-4 w-4" />
                BVL-XML Export
              </Button>
              <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
                <p className="font-semibold">Elektronische Übermittlung an BVL</p>
                <p className="mt-1">Frist: 31. März {meldung.jahr + 1}</p>
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
        title="BVL PSM-Jahresumsatzmeldung"
        subtitle="Meldung der Pflanzenschutzmittel-Inlandsabsätze"
        steps={steps}
        onFinish={() => navigate('/compliance/bvl-meldungen')}
        onCancel={() => navigate('/compliance/bvl-meldungen')}
      />
    </div>
  )
}
