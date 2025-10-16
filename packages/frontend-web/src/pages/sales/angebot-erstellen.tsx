import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'

type AngebotData = {
  kunde: string
  ansprechpartner: string
  email: string
  telefon: string
  gueltigBis: string
  zahlungsbedingung: string
  positionen: Array<{
    artikel: string
    menge: number
    einheit: string
    preis: number
  }>
  notizen: string
}

export default function AngebotErstellenPage(): JSX.Element {
  const navigate = useNavigate()
  const [angebot, setAngebot] = useState<AngebotData>({
    kunde: '',
    ansprechpartner: '',
    email: '',
    telefon: '',
    gueltigBis: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    zahlungsbedingung: 'net30',
    positionen: [{ artikel: '', menge: 1, einheit: 't', preis: 0 }],
    notizen: '',
  })

  function updateField<K extends keyof AngebotData>(key: K, value: AngebotData[K]): void {
    setAngebot((prev) => ({ ...prev, [key]: value }))
  }

  function addPosition(): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: [...prev.positionen, { artikel: '', menge: 1, einheit: 't', preis: 0 }],
    }))
  }

  function updatePosition(index: number, field: string, value: string | number): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: prev.positionen.map((pos, i) =>
        i === index ? { ...pos, [field]: value } : pos
      ),
    }))
  }

  function removePosition(index: number): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: prev.positionen.filter((_, i) => i !== index),
    }))
  }

  async function handleSubmit(): Promise<void> {
    // TODO: API-Call
    console.log('Angebot erstellen:', angebot)
    navigate('/sales/angebote-liste')
  }

  const gesamtBetrag = angebot.positionen.reduce((sum, pos) => sum + pos.menge * pos.preis, 0)

  const steps = [
    {
      id: 'kunde',
      title: 'Kunde',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="kunde">Kunde *</Label>
            <Input
              id="kunde"
              value={angebot.kunde}
              onChange={(e) => updateField('kunde', e.target.value)}
              placeholder="z.B. Landhandel Nord GmbH"
              required
            />
          </div>
          <div>
            <Label htmlFor="ansprechpartner">Ansprechpartner</Label>
            <Input
              id="ansprechpartner"
              value={angebot.ansprechpartner}
              onChange={(e) => updateField('ansprechpartner', e.target.value)}
              placeholder="Name des Ansprechpartners"
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="email">E-Mail</Label>
              <Input
                id="email"
                type="email"
                value={angebot.email}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder="kontakt@kunde.de"
              />
            </div>
            <div>
              <Label htmlFor="telefon">Telefon</Label>
              <Input
                id="telefon"
                type="tel"
                value={angebot.telefon}
                onChange={(e) => updateField('telefon', e.target.value)}
                placeholder="+49 123 456789"
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'konditionen',
      title: 'Konditionen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="gueltigBis">Gültig bis *</Label>
            <Input
              id="gueltigBis"
              type="date"
              value={angebot.gueltigBis}
              onChange={(e) => updateField('gueltigBis', e.target.value)}
              required
            />
            <p className="mt-1 text-sm text-muted-foreground">
              Standard: 30 Tage ab heute
            </p>
          </div>
          <div>
            <Label htmlFor="zahlungsbedingung">Zahlungsbedingung</Label>
            <select
              id="zahlungsbedingung"
              value={angebot.zahlungsbedingung}
              onChange={(e) => updateField('zahlungsbedingung', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="net30">30 Tage netto</option>
              <option value="net14">14 Tage netto</option>
              <option value="net7">7 Tage netto</option>
              <option value="cash">Kasse</option>
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
          {angebot.positionen.map((pos, index) => (
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
                    <Label>Preis (€)</Label>
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
                      disabled={angebot.positionen.length === 1}
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
      id: 'notizen',
      title: 'Notizen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="notizen">Interne Notizen (optional)</Label>
            <Textarea
              id="notizen"
              value={angebot.notizen}
              onChange={(e) => updateField('notizen', e.target.value)}
              placeholder="Zusätzliche Informationen zum Angebot..."
              rows={6}
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
              <h3 className="mb-4 text-lg font-semibold">Angebotsdaten</h3>
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Kunde</dt>
                  <dd className="text-sm">{angebot.kunde || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Ansprechpartner</dt>
                  <dd className="text-sm">{angebot.ansprechpartner || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">E-Mail</dt>
                  <dd className="text-sm">{angebot.email || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Telefon</dt>
                  <dd className="text-sm">{angebot.telefon || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Gültig bis</dt>
                  <dd className="text-sm">
                    {new Date(angebot.gueltigBis).toLocaleDateString('de-DE')}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Zahlungsbedingung</dt>
                  <dd className="text-sm">{angebot.zahlungsbedingung}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">Positionen</h3>
              <div className="space-y-2">
                {angebot.positionen.map((pos, index) => (
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

          {angebot.notizen && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="mb-2 text-lg font-semibold">Notizen</h3>
                <p className="text-sm text-muted-foreground">{angebot.notizen}</p>
              </CardContent>
            </Card>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Neues Angebot erstellen"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/sales/angebote-liste')}
      />
    </div>
  )
}
