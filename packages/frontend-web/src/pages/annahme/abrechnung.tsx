import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calculator, FileText, Save, Truck } from 'lucide-react'

type AbrechnungData = {
  lieferscheinNr: string
  lieferant: string
  artikel: string
  bruttoGewicht: number
  taraGewicht: number
  nettoGewicht: number
  basisPreis: number
  feuchtigkeit: number
  protein: number
  verunreinigung: number
  abzuegeFeuchtigkeit: number
  abzuegeProtein: number
  abzuegeVerunreinigung: number
  endpreis: number
  gesamtbetrag: number
}

export default function AnnahmeAbrechnungPage(): JSX.Element {
  const navigate = useNavigate()
  const [abrechnung, setAbrechnung] = useState<AbrechnungData>({
    lieferscheinNr: 'LS-2025-0042',
    lieferant: 'Landwirt Schmidt',
    artikel: 'Weizen',
    bruttoGewicht: 26500,
    taraGewicht: 1500,
    nettoGewicht: 25000,
    basisPreis: 220.0,
    feuchtigkeit: 16.5,
    protein: 12.2,
    verunreinigung: 1.8,
    abzuegeFeuchtigkeit: 5.0,
    abzuegeProtein: 0,
    abzuegeVerunreinigung: 8.0,
    endpreis: 0,
    gesamtbetrag: 0,
  })

  function updateField<K extends keyof AbrechnungData>(key: K, value: AbrechnungData[K]): void {
    const updated = { ...abrechnung, [key]: value }

    // Auto-Berechnung
    if (key === 'bruttoGewicht' || key === 'taraGewicht') {
      updated.nettoGewicht = updated.bruttoGewicht - updated.taraGewicht
    }

    // Qualitätsabzüge berechnen
    if (updated.feuchtigkeit > 14) {
      updated.abzuegeFeuchtigkeit = (updated.feuchtigkeit - 14) * 2
    } else {
      updated.abzuegeFeuchtigkeit = 0
    }

    if (updated.verunreinigung > 2) {
      updated.abzuegeVerunreinigung = (updated.verunreinigung - 2) * 4
    } else {
      updated.abzuegeVerunreinigung = 0
    }

    // Endpreis berechnen
    const gesamtAbzug = updated.abzuegeFeuchtigkeit + updated.abzuegeProtein + updated.abzuegeVerunreinigung
    updated.endpreis = updated.basisPreis - gesamtAbzug
    updated.gesamtbetrag = (updated.nettoGewicht / 1000) * updated.endpreis

    setAbrechnung(updated)
  }

  async function handleSave(): Promise<void> {
    console.log('Abrechnung speichern:', abrechnung)
    navigate('/annahme/warteschlange')
  }

  const istInOrdnung = abrechnung.feuchtigkeit <= 14.5 && abrechnung.verunreinigung <= 2

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Annahme-Abrechnung</h1>
          <p className="text-muted-foreground">Lieferschein {abrechnung.lieferscheinNr}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/annahme/warteschlange')}>
            Abbrechen
          </Button>
          <Button onClick={handleSave} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern & Beleg drucken
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Truck className="h-5 w-5" />
              Lieferdaten
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Lieferant</Label>
              <div className="text-lg font-semibold">{abrechnung.lieferant}</div>
            </div>
            <div>
              <Label>Artikel</Label>
              <div className="text-lg font-semibold">{abrechnung.artikel}</div>
            </div>
            <div>
              <Label>Lieferschein-Nr.</Label>
              <div className="font-medium">{abrechnung.lieferscheinNr}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Gewichte (kg)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="bruttoGewicht">Brutto-Gewicht</Label>
              <Input
                id="bruttoGewicht"
                type="number"
                value={abrechnung.bruttoGewicht}
                onChange={(e) => updateField('bruttoGewicht', Number(e.target.value))}
                min="0"
              />
            </div>
            <div>
              <Label htmlFor="taraGewicht">Tara-Gewicht (LKW)</Label>
              <Input
                id="taraGewicht"
                type="number"
                value={abrechnung.taraGewicht}
                onChange={(e) => updateField('taraGewicht', Number(e.target.value))}
                min="0"
              />
            </div>
            <div>
              <Label>Netto-Gewicht (berechnet)</Label>
              <div className="rounded-md bg-muted p-3 text-lg font-bold">
                {abrechnung.nettoGewicht.toLocaleString('de-DE')} kg ={' '}
                {(abrechnung.nettoGewicht / 1000).toFixed(2)} t
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Qualitätsparameter & Abzüge
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="feuchtigkeit">Feuchtigkeit (%)</Label>
              <Input
                id="feuchtigkeit"
                type="number"
                value={abrechnung.feuchtigkeit}
                onChange={(e) => updateField('feuchtigkeit', Number(e.target.value))}
                step="0.1"
                min="0"
                max="100"
              />
              <div className="text-sm text-muted-foreground">Soll: {'<'} 14%</div>
              {abrechnung.feuchtigkeit > 14 && (
                <div className="text-sm font-semibold text-orange-600">
                  Abzug: {abrechnung.abzuegeFeuchtigkeit.toFixed(2)} €/t
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="protein">Protein (%)</Label>
              <Input
                id="protein"
                type="number"
                value={abrechnung.protein}
                onChange={(e) => updateField('protein', Number(e.target.value))}
                step="0.1"
                min="0"
                max="100"
              />
              <div className="text-sm text-muted-foreground">Soll: {'>'} 12%</div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="verunreinigung">Verunreinigung (%)</Label>
              <Input
                id="verunreinigung"
                type="number"
                value={abrechnung.verunreinigung}
                onChange={(e) => updateField('verunreinigung', Number(e.target.value))}
                step="0.1"
                min="0"
                max="100"
              />
              <div className="text-sm text-muted-foreground">Soll: {'<'} 2%</div>
              {abrechnung.verunreinigung > 2 && (
                <div className="text-sm font-semibold text-orange-600">
                  Abzug: {abrechnung.abzuegeVerunreinigung.toFixed(2)} €/t
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Preisberechnung
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="basisPreis">Basispreis (€/t)</Label>
                <Input
                  id="basisPreis"
                  type="number"
                  value={abrechnung.basisPreis}
                  onChange={(e) => updateField('basisPreis', Number(e.target.value))}
                  step="0.01"
                  min="0"
                />
              </div>
              <div>
                <Label>Qualitätsstatus</Label>
                <div className="mt-2">
                  <Badge variant={istInOrdnung ? 'outline' : 'secondary'}>
                    {istInOrdnung ? '✓ Qualität in Ordnung' : '⚠ Abzüge erforderlich'}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="rounded-lg border-2 border-dashed bg-muted/50 p-6">
              <dl className="grid gap-3 text-lg">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Basispreis:</dt>
                  <dd className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      abrechnung.basisPreis
                    )}
                    /t
                  </dd>
                </div>
                {abrechnung.abzuegeFeuchtigkeit > 0 && (
                  <div className="flex justify-between text-orange-600">
                    <dt>- Abzug Feuchtigkeit:</dt>
                    <dd className="font-semibold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        abrechnung.abzuegeFeuchtigkeit
                      )}
                      /t
                    </dd>
                  </div>
                )}
                {abrechnung.abzuegeVerunreinigung > 0 && (
                  <div className="flex justify-between text-orange-600">
                    <dt>- Abzug Verunreinigung:</dt>
                    <dd className="font-semibold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        abrechnung.abzuegeVerunreinigung
                      )}
                      /t
                    </dd>
                  </div>
                )}
                <div className="flex justify-between border-t pt-3 text-xl">
                  <dt className="font-bold">Endpreis:</dt>
                  <dd className="font-bold text-green-600">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      abrechnung.endpreis
                    )}
                    /t
                  </dd>
                </div>
                <div className="flex justify-between border-t pt-3 text-2xl">
                  <dt className="font-bold">Gesamtbetrag:</dt>
                  <dd className="font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      abrechnung.gesamtbetrag
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
