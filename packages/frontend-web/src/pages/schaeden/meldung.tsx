import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle, Loader2 } from 'lucide-react'
import { useVersicherungen, useSchadenMeldungErstellen } from '@/lib/api/schaeden'
import { useToast } from '@/hooks/use-toast'

type SchadenData = {
  art: string
  datum: string
  ort: string
  beschreibung: string
  schadenhoehe: number
  versicherung_id: string
  zeuge: string
}

export default function SchadenMeldungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: versicherungen = [] } = useVersicherungen()
  const meldungMutation = useSchadenMeldungErstellen()

  const [schaden, setSchaden] = useState<SchadenData>({
    art: '',
    datum: new Date().toISOString().slice(0, 10),
    ort: '',
    beschreibung: '',
    schadenhoehe: 0,
    versicherung_id: '',
    zeuge: '',
  })

  function updateField<K extends keyof SchadenData>(key: K, value: SchadenData[K]): void {
    setSchaden((prev) => ({ ...prev, [key]: value }))
  }

  const selectedVersicherung = versicherungen.find((v) => v.id === schaden.versicherung_id)

  const steps = [
    {
      id: 'grunddaten',
      title: 'Grunddaten',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="art">Schadenart *</Label>
            <select
              id="art"
              value={schaden.art}
              onChange={(e) => updateField('art', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              <option value="hagel">Hagelschaden</option>
              <option value="frost">Frostschaden</option>
              <option value="feuer">Feuerschaden</option>
              <option value="unfall">Fahrzeugunfall</option>
              <option value="diebstahl">Diebstahl</option>
            </select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="datum">Schadendatum *</Label>
              <Input id="datum" type="date" value={schaden.datum} onChange={(e) => updateField('datum', e.target.value)} />
            </div>
            <div>
              <Label htmlFor="ort">Schadenort</Label>
              <Input id="ort" value={schaden.ort} onChange={(e) => updateField('ort', e.target.value)} placeholder="z.B. Schlag S-001" />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'beschreibung',
      title: 'Beschreibung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="beschreibung">Schadenhergang *</Label>
            <Textarea
              id="beschreibung"
              value={schaden.beschreibung}
              onChange={(e) => updateField('beschreibung', e.target.value)}
              rows={6}
              placeholder="Beschreiben Sie den Schadenhergang..."
            />
          </div>
          <div>
            <Label htmlFor="schadenhoehe">Geschätzte Schadenhöhe (€)</Label>
            <Input
              id="schadenhoehe"
              type="number"
              value={schaden.schadenhoehe}
              onChange={(e) => updateField('schadenhoehe', Number(e.target.value))}
              step="100"
            />
          </div>
          <div>
            <Label htmlFor="zeuge">Zeuge(n)</Label>
            <Input id="zeuge" value={schaden.zeuge} onChange={(e) => updateField('zeuge', e.target.value)} placeholder="Name(n) des/der Zeugen" />
          </div>
        </div>
      ),
    },
    {
      id: 'versicherung',
      title: 'Versicherung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="versicherung">Zuständige Versicherung</Label>
            <select
              id="versicherung"
              value={schaden.versicherung_id}
              onChange={(e) => updateField('versicherung_id', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              {versicherungen.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.bezeichnung} ({v.vertragsnummer})
                </option>
              ))}
            </select>
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
              {meldungMutation.isPending ? (
                <Loader2 className="h-20 w-20 text-blue-600 animate-spin" />
              ) : (
                <CheckCircle className="h-20 w-20 text-green-600" />
              )}
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">
              {meldungMutation.isSuccess ? `Meldung ${meldungMutation.data.meldungsnummer} erstellt` : 'Schadenmeldung bereit'}
            </h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Schadenart</dt>
                <dd className="font-semibold">{schaden.art || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Datum</dt>
                <dd className="font-semibold">{new Date(schaden.datum).toLocaleDateString('de-DE')}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Ort</dt>
                <dd className="font-semibold">{schaden.ort || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Schadenhöhe</dt>
                <dd className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(schaden.schadenhoehe)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Versicherung</dt>
                <dd className="font-semibold">
                  {selectedVersicherung
                    ? `${selectedVersicherung.bezeichnung} (${selectedVersicherung.vertragsnummer})`
                    : 'Nicht ausgewählt'}
                </dd>
              </div>
            </dl>
            {meldungMutation.isError && (
              <div className="mt-4 rounded-lg bg-red-50 p-4 text-center text-sm text-red-900">
                <p className="font-semibold">Fehler beim Erstellen der Meldung</p>
                <p className="mt-1">{String(meldungMutation.error)}</p>
              </div>
            )}
            {!meldungMutation.isError && (
              <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
                <p className="font-semibold">Schadenmeldung wird an Versicherung übermittelt</p>
                <p className="mt-1">Ein Sachverständiger wird Sie kontaktieren</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
  ]

  async function handleFinish(): Promise<void> {
    try {
      await meldungMutation.mutateAsync({
        art: schaden.art,
        datum: schaden.datum,
        ort: schaden.ort || undefined,
        beschreibung: schaden.beschreibung,
        schadenhoehe: schaden.schadenhoehe,
        versicherung_id: schaden.versicherung_id || undefined,
        zeuge: schaden.zeuge || undefined,
      })
      toast({
        title: 'Schadenmeldung erstellt',
        description: 'Die Meldung wurde erfolgreich übermittelt.',
      })
      navigate('/schaeden/liste')
    } catch {
      toast({
        title: 'Fehler',
        description: 'Die Schadenmeldung konnte nicht erstellt werden.',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="p-3 md:p-6">
      <Wizard
        title="Schadenmeldung"
        steps={steps}
        onFinish={handleFinish}
        onCancel={() => navigate('/schaeden/liste')}
      />
    </div>
  )
}
