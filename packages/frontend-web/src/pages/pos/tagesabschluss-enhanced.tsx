import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AlertTriangle, CheckCircle, FileText } from 'lucide-react'

type TagesabschlussData = {
  datum: string
  kassierer: string
  
  // TSE-Daten (auto-geladen)
  tseTransaktionen: number
  tseUmsatzBar: number
  tseUmsatzEC: number
  tseUmsatzPayPal: number
  tseUmsatzB2B: number
  tseGesamt: number
  
  // Kassenzählung
  bargeldGezaehlt: number
  ecAbrechnung: number
  paypalAbrechnung: number
  
  // Differenzen
  differenzBar: number
  differenzEC: number
  differenzPayPal: number
  
  // Fibu-Buchung
  fibuStatus: 'offen' | 'gebucht'
  fibuBelegnr?: string
  fibuDatum?: string
}

export default function TagesabschlussEnhancedPage(): JSX.Element {
  const navigate = useNavigate()
  
  const [abschluss, setAbschluss] = useState<TagesabschlussData>({
    datum: new Date().toISOString().split('T')[0],
    kassierer: 'Max Mustermann',
    
    // Auto-geladen aus TSE-Journal
    tseTransaktionen: 47,
    tseUmsatzBar: 1250.80,
    tseUmsatzEC: 2890.50,
    tseUmsatzPayPal: 450.20,
    tseUmsatzB2B: 850.00,
    tseGesamt: 5441.50,
    
    // Manuell eingegeben
    bargeldGezaehlt: 1248.30,
    ecAbrechnung: 2890.50,
    paypalAbrechnung: 450.20,
    
    // Auto-berechnet
    differenzBar: -2.50,
    differenzEC: 0,
    differenzPayPal: 0,
    
    fibuStatus: 'offen',
  })

  function calculateDifferenzen(): void {
    setAbschluss({
      ...abschluss,
      differenzBar: abschluss.bargeldGezaehlt - abschluss.tseUmsatzBar,
      differenzEC: abschluss.ecAbrechnung - abschluss.tseUmsatzEC,
      differenzPayPal: abschluss.paypalAbrechnung - abschluss.tseUmsatzPayPal,
    })
  }

  const steps = [
    {
      id: 'tse-daten',
      title: 'TSE-Daten',
      content: (
        <div className="space-y-4">
          <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
            <p className="font-semibold">📊 Daten aus TSE-Journal (automatisch geladen)</p>
            <p className="mt-1">Datum: {new Date(abschluss.datum).toLocaleDateString('de-DE')}</p>
          </div>

          <Card>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between border-b pb-2">
                <span>TSE-Transaktionen</span>
                <span className="font-bold">{abschluss.tseTransaktionen}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span>Umsatz Bar (Soll)</span>
                <span className="font-mono font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzBar)}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span>Umsatz EC (Soll)</span>
                <span className="font-mono font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzEC)}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span>Umsatz PayPal (Soll)</span>
                <span className="font-mono font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzPayPal)}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span>Umsatz B2B (Soll)</span>
                <span className="font-mono font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzB2B)}</span>
              </div>
              <div className="flex justify-between bg-primary text-primary-foreground p-3 rounded-lg">
                <span className="font-bold">Gesamt (Soll)</span>
                <span className="text-xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseGesamt)}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'kassenzaehlung',
      title: 'Kassenzählung',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bargeld">Bargeld gezählt (Ist)</Label>
            <Input
              id="bargeld"
              type="number"
              step="0.01"
              value={abschluss.bargeldGezaehlt}
              onChange={(e) => setAbschluss({ ...abschluss, bargeldGezaehlt: Number(e.target.value) })}
              onBlur={calculateDifferenzen}
              className="font-mono text-lg"
            />
          </div>
          <div>
            <Label htmlFor="ec">EC-Terminal Abrechnung (Ist)</Label>
            <Input
              id="ec"
              type="number"
              step="0.01"
              value={abschluss.ecAbrechnung}
              onChange={(e) => setAbschluss({ ...abschluss, ecAbrechnung: Number(e.target.value) })}
              onBlur={calculateDifferenzen}
              className="font-mono text-lg"
            />
          </div>
          <div>
            <Label htmlFor="paypal">PayPal Abrechnung (Ist)</Label>
            <Input
              id="paypal"
              type="number"
              step="0.01"
              value={abschluss.paypalAbrechnung}
              onChange={(e) => setAbschluss({ ...abschluss, paypalAbrechnung: Number(e.target.value) })}
              onBlur={calculateDifferenzen}
              className="font-mono text-lg"
            />
          </div>

          <Card className="mt-4">
            <CardContent className="pt-4">
              <h3 className="font-semibold mb-3">Differenzen (Ist - Soll)</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Bar:</span>
                  <span className={`font-bold ${abschluss.differenzBar !== 0 ? 'text-orange-600' : 'text-green-600'}`}>
                    {abschluss.differenzBar > 0 ? '+' : ''}
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenzBar)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>EC:</span>
                  <span className={`font-bold ${abschluss.differenzEC !== 0 ? 'text-orange-600' : 'text-green-600'}`}>
                    {abschluss.differenzEC > 0 ? '+' : ''}
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenzEC)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>PayPal:</span>
                  <span className={`font-bold ${abschluss.differenzPayPal !== 0 ? 'text-orange-600' : 'text-green-600'}`}>
                    {abschluss.differenzPayPal > 0 ? '+' : ''}
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenzPayPal)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'fibu-buchung',
      title: 'Fibu-Buchung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Tagesabschluss bereit</h3>

            <div className="space-y-4 mb-6">
              <div className="rounded-lg bg-muted p-4">
                <h4 className="font-semibold mb-3">Automatische Fibu-Buchungen (SKR03)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between font-mono">
                    <span>Soll: 1000 (Kasse)</span>
                    <span className="font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzBar)}</span>
                  </div>
                  <div className="flex justify-between font-mono">
                    <span>Soll: 1200 (Bank/EC)</span>
                    <span className="font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzEC)}</span>
                  </div>
                  <div className="flex justify-between font-mono">
                    <span>Soll: 1210 (PayPal)</span>
                    <span className="font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseUmsatzPayPal)}</span>
                  </div>
                  <div className="flex justify-between font-mono pt-2 border-t">
                    <span>Haben: 8400 (Erlöse)</span>
                    <span className="font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseGesamt)}</span>
                  </div>
                </div>
              </div>

              {Math.abs(abschluss.differenzBar) > 0.01 && (
                <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    <p className="font-semibold">Differenz Bar: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.differenzBar)}</p>
                  </div>
                  <p className="mt-1 text-xs">Wird auf Konto 2150 (Kassenfehlbeträge) gebucht</p>
                </div>
              )}

              <div className="rounded-lg bg-green-50 p-4 text-sm text-green-900">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <p className="font-semibold">TSE-Daten → Fibu-Journal</p>
                </div>
                <p className="mt-1">
                  Buchungsdatum: {new Date(abschluss.datum).toLocaleDateString('de-DE')} •
                  Belegnummer: KA-{abschluss.datum} •
                  TSE-Transaktionen: {abschluss.tseTransaktionen}
                </p>
              </div>
            </div>

            <dl className="grid gap-3 mb-6">
              <div className="flex justify-between border-b pb-2">
                <dt>Kassierer</dt>
                <dd className="font-semibold">{abschluss.kassierer}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Datum</dt>
                <dd className="font-semibold">{new Date(abschluss.datum).toLocaleDateString('de-DE')}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>TSE-Transaktionen</dt>
                <dd className="font-semibold">{abschluss.tseTransaktionen}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Gesamtumsatz</dt>
                <dd className="font-semibold text-lg">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(abschluss.tseGesamt)}</dd>
              </div>
            </dl>

            <Button className="w-full" size="lg">
              In Fibu buchen & TSE-Journal als gebucht markieren
            </Button>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Tagesabschluss mit TSE → Fibu"
        subtitle="Kassenzählung, TSE-Export & automatische Fibu-Buchung"
        steps={steps}
        onFinish={() => {
          // Mock: Fibu-Buchung erstellen
          console.log('Fibu-Buchung erstellt:', {
            datum: abschluss.datum,
            belegnr: `KA-${abschluss.datum}`,
            buchungen: [
              { soll: '1000', haben: '8400', betrag: abschluss.tseUmsatzBar, text: 'Barverkauf lt. TSE' },
              { soll: '1200', haben: '8400', betrag: abschluss.tseUmsatzEC, text: 'EC-Verkauf lt. TSE' },
              { soll: '1210', haben: '8400', betrag: abschluss.tseUmsatzPayPal, text: 'PayPal-Verkauf lt. TSE' },
            ],
          })
          
          // Mock: TSE-Journal-Status updaten
          console.log('TSE-Journal als gebucht markiert (Datum:', abschluss.datum, ')')
          
          navigate('/pos/tse-journal')
        }}
        onCancel={() => navigate('/pos/tse-journal')}
      />
    </div>
  )
}
