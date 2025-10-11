import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle } from 'lucide-react'

type MahnlaufData = {
  bezeichnung: string
  stufe: '1' | '2' | '3'
  faelligePosten: Array<{
    id: string
    kunde: string
    rechnungsNr: string
    betrag: number
    tageUeberfaellig: number
    selected: boolean
  }>
}

export default function MahnlaufPage(): JSX.Element {
  const navigate = useNavigate()
  const [mahnlauf, setMahnlauf] = useState<MahnlaufData>({
    bezeichnung: '',
    stufe: '1',
    faelligePosten: [
      { id: '1', kunde: 'Landhandel Nord', rechnungsNr: 'RE-2025-035', betrag: 12500, tageUeberfaellig: 38, selected: true },
      { id: '2', kunde: 'Müller GmbH', rechnungsNr: 'RE-2025-032', betrag: 8900, tageUeberfaellig: 45, selected: true },
    ],
  })

  function updateField<K extends keyof MahnlaufData>(key: K, value: MahnlaufData[K]): void {
    setMahnlauf((prev) => ({ ...prev, [key]: value }))
  }

  function togglePosten(id: string): void {
    setMahnlauf((prev) => ({
      ...prev,
      faelligePosten: prev.faelligePosten.map((p) => (p.id === id ? { ...p, selected: !p.selected } : p)),
    }))
  }

  const selected = mahnlauf.faelligePosten.filter((p) => p.selected)
  const gesamtbetrag = selected.reduce((sum, p) => sum + p.betrag, 0)

  const steps = [
    {
      id: 'auswahl',
      title: 'Auswahl',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bezeichnung">Bezeichnung *</Label>
            <Input
              id="bezeichnung"
              value={mahnlauf.bezeichnung}
              onChange={(e) => updateField('bezeichnung', e.target.value)}
              placeholder="z.B. Mahnlauf KW 41"
            />
          </div>
          <div>
            <Label htmlFor="stufe">Mahnstufe</Label>
            <select
              id="stufe"
              value={mahnlauf.stufe}
              onChange={(e) => updateField('stufe', e.target.value as MahnlaufData['stufe'])}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="1">1. Mahnung (Erinnerung)</option>
              <option value="2">2. Mahnung (+Gebühr 5€)</option>
              <option value="3">3. Mahnung (+Gebühr 10€)</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label>Fällige Posten ({selected.length} von {mahnlauf.faelligePosten.length})</Label>
            {mahnlauf.faelligePosten.map((posten) => (
              <Card key={posten.id} className={posten.selected ? 'border-blue-500' : ''}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={posten.selected}
                      onChange={() => togglePosten(posten.id)}
                      className="h-4 w-4"
                    />
                    <div className="flex-1">
                      <div className="font-semibold">{posten.kunde}</div>
                      <div className="text-sm text-muted-foreground">
                        Rechnung: {posten.rechnungsNr} • {posten.tageUeberfaellig} Tage überfällig
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">
                        {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(posten.betrag)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
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
            <h3 className="text-center text-2xl font-bold mb-6">Mahnlauf bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Bezeichnung</dt>
                <dd className="font-semibold">{mahnlauf.bezeichnung || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Mahnstufe</dt>
                <dd>
                  <Badge variant="destructive">{mahnlauf.stufe}. Mahnung</Badge>
                </dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Anzahl Kunden</dt>
                <dd className="font-semibold">{selected.length}</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Gesamtbetrag</dt>
                <dd className="font-bold text-red-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtbetrag)}
                </dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-center text-sm text-red-900">
              <p className="font-semibold">Mahnungen werden erstellt und versendet</p>
              <p className="mt-1">{selected.length} Kunden erhalten Mahnung per E-Mail</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Mahnlauf erstellen"
        steps={steps}
        onFinish={() => navigate('/fibu/offene-posten')}
        onCancel={() => navigate('/fibu/offene-posten')}
      />
    </div>
  )
}
