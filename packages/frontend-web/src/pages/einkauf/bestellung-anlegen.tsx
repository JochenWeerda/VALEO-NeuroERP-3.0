import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'

type BestellungData = {
  lieferant: string
  liefertermin: string
  zahlungsbedingung: string
  positionen: Array<{
    artikel: string
    menge: number
    einheit: string
    preis: number
  }>
  lieferadresse: string
  notizen: string
}

export default function BestellungAnlegenPage(): JSX.Element {
  const navigate = useNavigate()
  const [bestellung, setBestellung] = useState<BestellungData>({
    lieferant: '',
    liefertermin: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    zahlungsbedingung: 'net30',
    positionen: [{ artikel: '', menge: 1, einheit: 't', preis: 0 }],
    lieferadresse: '',
    notizen: '',
  })

  function updateField<K extends keyof BestellungData>(key: K, value: BestellungData[K]): void {
    setBestellung((prev) => ({ ...prev, [key]: value }))
  }

  function addPosition(): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: [...prev.positionen, { artikel: '', menge: 1, einheit: 't', preis: 0 }],
    }))
  }

  function updatePosition(index: number, field: string, value: string | number): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: prev.positionen.map((pos, i) => (i === index ? { ...pos, [field]: value } : pos)),
    }))
  }

  function removePosition(index: number): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: prev.positionen.filter((_, i) => i !== index),
    }))
  }

  async function handleSubmit(): Promise<void> {
    console.log('Bestellung erstellen:', bestellung)
    navigate('/einkauf/bestellungen-liste')
  }

  const gesamtBetrag = bestellung.positionen.reduce((sum, pos) => sum + pos.menge * pos.preis, 0)

  const steps = [
    {
      id: 'lieferant',
      title: 'Lieferant',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferant">Lieferant *</Label>
            <Input
              id="lieferant"
              value={bestellung.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder="z.B. Saatgut AG"
              required
            />
          </div>
          <div>
            <Label htmlFor="liefertermin">Gewünschter Liefertermin *</Label>
            <Input
              id="liefertermin"
              type="date"
              value={bestellung.liefertermin}
              onChange={(e) => updateField('liefertermin', e.target.value)}
              required
            />
            <p className="mt-1 text-sm text-muted-foreground">Standard: 14 Tage ab heute</p>
          </div>
          <div>
            <Label htmlFor="zahlungsbedingung">Zahlungsbedingung</Label>
            <select
              id="zahlungsbedingung"
              value={bestellung.zahlungsbedingung}
              onChange={(e) => updateField('zahlungsbedingung', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="net30">30 Tage netto</option>
              <option value="net14">14 Tage 2% Skonto</option>
              <option value="net7">7 Tage 3% Skonto</option>
              <option value="prepay">Vorkasse</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'positionen',
      title: 'Positionen',
      content: (
        <div className="space-y-4">
          {bestellung.positionen.map((pos, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <Label>Artikel *</Label>
                    <Input
                      value={pos.artikel}
                      onChange={(e) => updatePosition(index, 'artikel', e.target.value)}
                      placeholder="z.B. Weizen Premium"
                    />
                  </div>
                  <div className="w-24">
                    <Label>Menge</Label>
                    <Input
                      type="number"
                      value={pos.menge}
                      onChange={(e) => updatePosition(index, 'menge', Number(e.target.value))}
                      min="0"
                    />
                  </div>
                  <div className="w-20">
                    <Label>Einheit</Label>
                    <select
                      value={pos.einheit}
                      onChange={(e) => updatePosition(index, 'einheit', e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2"
                    >
                      <option value="t">t</option>
                      <option value="kg">kg</option>
                      <option value="l">l</option>
                      <option value="Stk">Stk</option>
                    </select>
                  </div>
                  <div className="w-32">
                    <Label>EK-Preis (€)</Label>
                    <Input
                      type="number"
                      value={pos.preis}
                      onChange={(e) => updatePosition(index, 'preis', Number(e.target.value))}
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removePosition(index)}
                      disabled={bestellung.positionen.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="mt-2 text-right text-sm text-muted-foreground">
                  Summe:{' '}
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                    pos.menge * pos.preis
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
          <Button type="button" variant="outline" className="w-full gap-2" onClick={addPosition}>
            <Plus className="h-4 w-4" />
            Position hinzufügen
          </Button>
        </div>
      ),
    },
    {
      id: 'lieferung',
      title: 'Lieferung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferadresse">Lieferadresse</Label>
            <Textarea
              id="lieferadresse"
              value={bestellung.lieferadresse}
              onChange={(e) => updateField('lieferadresse', e.target.value)}
              placeholder="Straße, PLZ Ort..."
              rows={4}
            />
          </div>
          <div>
            <Label htmlFor="notizen">Interne Notizen (optional)</Label>
            <Textarea
              id="notizen"
              value={bestellung.notizen}
              onChange={(e) => updateField('notizen', e.target.value)}
              placeholder="Zusätzliche Informationen zur Bestellung..."
              rows={4}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: 'Zusammenfassung',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">Bestelldaten</h3>
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Lieferant</dt>
                  <dd className="text-sm">{bestellung.lieferant || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Liefertermin</dt>
                  <dd className="text-sm">
                    {new Date(bestellung.liefertermin).toLocaleDateString('de-DE')}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Zahlungsbedingung</dt>
                  <dd className="text-sm">{bestellung.zahlungsbedingung}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Lieferadresse</dt>
                  <dd className="text-sm">{bestellung.lieferadresse || 'Standard'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">Positionen ({bestellung.positionen.length})</h3>
              <div className="space-y-2">
                {bestellung.positionen.map((pos, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span>
                      {pos.artikel || 'Artikel'} ({pos.menge} {pos.einheit})
                    </span>
                    <span className="font-medium">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        pos.menge * pos.preis
                      )}
                    </span>
                  </div>
                ))}
                <div className="mt-4 flex justify-between border-t pt-2 font-semibold">
                  <span>Gesamtsumme</span>
                  <span>
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      gesamtBetrag
                    )}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Neue Bestellung anlegen"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/einkauf/bestellungen-liste')}
      />
    </div>
  )
}
