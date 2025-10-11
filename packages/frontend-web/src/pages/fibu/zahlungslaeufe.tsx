import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, CheckCircle, Euro, FileDown } from 'lucide-react'

type ZahlungslaufData = {
  bezeichnung: string
  ausfuehrungsdatum: string
  zahlungen: Array<{
    id: string
    lieferant: string
    betrag: number
    rechnungsNr: string
    selected: boolean
  }>
  format: 'sepa' | 'datev'
}

export default function ZahlungslaeufeePage(): JSX.Element {
  const navigate = useNavigate()
  const [zahlungslauf, setZahlungslauf] = useState<ZahlungslaufData>({
    bezeichnung: '',
    ausfuehrungsdatum: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    zahlungen: [
      {
        id: '1',
        lieferant: 'Saatgut AG',
        betrag: 25000.0,
        rechnungsNr: 'ER-2025-0001',
        selected: true,
      },
      {
        id: '2',
        lieferant: 'Dünger GmbH',
        betrag: 18500.5,
        rechnungsNr: 'ER-2025-0002',
        selected: true,
      },
      {
        id: '3',
        lieferant: 'Technik GmbH',
        betrag: 8900.0,
        rechnungsNr: 'ER-2025-0004',
        selected: false,
      },
    ],
    format: 'sepa',
  })

  function updateField<K extends keyof ZahlungslaufData>(key: K, value: ZahlungslaufData[K]): void {
    setZahlungslauf((prev) => ({ ...prev, [key]: value }))
  }

  function toggleZahlung(id: string): void {
    setZahlungslauf((prev) => ({
      ...prev,
      zahlungen: prev.zahlungen.map((z) => (z.id === id ? { ...z, selected: !z.selected } : z)),
    }))
  }

  async function handleSubmit(): Promise<void> {
    console.log('Zahlungslauf erstellen:', zahlungslauf)
    // Hier würde der SEPA-Export erfolgen
    navigate('/fibu/verbindlichkeiten')
  }

  const selectedZahlungen = zahlungslauf.zahlungen.filter((z) => z.selected)
  const gesamtbetrag = selectedZahlungen.reduce((sum, z) => sum + z.betrag, 0)

  const steps = [
    {
      id: 'auswahl',
      title: 'Zahlungen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bezeichnung">Bezeichnung *</Label>
            <Input
              id="bezeichnung"
              value={zahlungslauf.bezeichnung}
              onChange={(e) => updateField('bezeichnung', e.target.value)}
              placeholder="z.B. Zahlungslauf KW 41"
              required
            />
          </div>
          <div>
            <Label htmlFor="ausfuehrungsdatum">Ausführungsdatum *</Label>
            <Input
              id="ausfuehrungsdatum"
              type="date"
              value={zahlungslauf.ausfuehrungsdatum}
              onChange={(e) => updateField('ausfuehrungsdatum', e.target.value)}
              required
            />
          </div>
          <div className="space-y-2 mt-6">
            <Label>Zahlungen auswählen ({selectedZahlungen.length} von {zahlungslauf.zahlungen.length})</Label>
            {zahlungslauf.zahlungen.map((zahlung) => (
              <Card key={zahlung.id} className={zahlung.selected ? 'border-blue-500' : ''}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={zahlung.selected}
                      onChange={() => toggleZahlung(zahlung.id)}
                      className="h-4 w-4"
                    />
                    <div className="flex-1">
                      <div className="font-semibold">{zahlung.lieferant}</div>
                      <div className="text-sm text-muted-foreground">
                        Rechnung: {zahlung.rechnungsNr}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">
                        {new Intl.NumberFormat('de-DE', {
                          style: 'currency',
                          currency: 'EUR',
                        }).format(zahlung.betrag)}
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
      id: 'export',
      title: 'Export',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="format">Export-Format</Label>
            <select
              id="format"
              value={zahlungslauf.format}
              onChange={(e) => updateField('format', e.target.value as 'sepa' | 'datev')}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="sepa">SEPA XML (pain.001)</option>
              <option value="datev">DATEV CSV</option>
            </select>
          </div>
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <FileDown className="h-4 w-4" />
                  <span>Dateiname:</span>
                  <span className="font-mono">
                    zahlungslauf_{new Date().toISOString().slice(0, 10)}.
                    {zahlungslauf.format === 'sepa' ? 'xml' : 'csv'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Ausführung:</span>
                  <span className="font-semibold">
                    {new Date(zahlungslauf.ausfuehrungsdatum).toLocaleDateString('de-DE')}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Euro className="h-4 w-4" />
                  <span>Anzahl Zahlungen:</span>
                  <span className="font-semibold">{selectedZahlungen.length}</span>
                </div>
              </div>
            </CardContent>
          </Card>
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
              <div className="flex items-center justify-center mb-6">
                <CheckCircle className="h-20 w-20 text-green-600" />
              </div>
              <h3 className="text-center text-2xl font-bold mb-6">Zahlungslauf bereit</h3>
              <dl className="grid gap-4">
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Bezeichnung</dt>
                  <dd className="text-sm font-semibold">{zahlungslauf.bezeichnung || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Ausführungsdatum</dt>
                  <dd className="text-sm font-semibold">
                    {new Date(zahlungslauf.ausfuehrungsdatum).toLocaleDateString('de-DE')}
                  </dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Anzahl Zahlungen</dt>
                  <dd className="text-sm font-semibold">{selectedZahlungen.length}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Export-Format</dt>
                  <dd className="text-sm">
                    <Badge>{zahlungslauf.format === 'sepa' ? 'SEPA XML' : 'DATEV CSV'}</Badge>
                  </dd>
                </div>
                <div className="flex justify-between pt-3">
                  <dt className="text-lg font-bold">Gesamtbetrag</dt>
                  <dd className="text-lg font-bold text-green-600">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      gesamtbetrag
                    )}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">Zahlungslauf wird erstellt und Datei generiert</p>
            <p className="mt-1">Die Datei kann anschließend im Online-Banking importiert werden</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Zahlungslauf erstellen"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/fibu/zahlungsvorschlaege')}
      />
    </div>
  )
}
