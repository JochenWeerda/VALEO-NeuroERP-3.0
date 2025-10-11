import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BookMarked, Save } from 'lucide-react'

type Buchung = {
  datum: string
  belegnr: string
  text: string
  soll: number
  haben: number
  saldo: number
}

export default function SachkontoPage(): JSX.Element {
  const [konto] = useState({
    kontonummer: '1200',
    bezeichnung: 'Bank',
    kontoart: 'Umlaufvermögen',
    typ: 'Aktiva',
    saldo: 285000,
    buchungen: [
      { datum: '2025-10-11', belegnr: 'RE-2025-0123', text: 'Agrar Schmidt GmbH', soll: 0, haben: 12500, saldo: 285000 },
      { datum: '2025-10-10', belegnr: 'ZE-2025-0045', text: 'Zahlung K-10023', soll: 8750, haben: 0, saldo: 297500 },
      { datum: '2025-10-09', belegnr: 'EB-2025-0098', text: 'Überweisung Lieferant', soll: 0, haben: 18500, saldo: 288750 },
    ] as Buchung[],
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <BookMarked className="h-8 w-8" />
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold font-mono">{konto.kontonummer}</h1>
                <Badge variant="outline">{konto.typ}</Badge>
              </div>
              <p className="text-muted-foreground">{konto.bezeichnung}</p>
            </div>
          </div>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="stamm" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="stamm">Stammdaten</TabsTrigger>
          <TabsTrigger value="buchungen">Buchungen</TabsTrigger>
          <TabsTrigger value="saldo">Saldo & Statistik</TabsTrigger>
        </TabsList>

        <TabsContent value="stamm" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Stammdaten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Kontonummer</Label>
                  <Input value={konto.kontonummer} className="font-mono font-bold text-lg" />
                </div>
                <div>
                  <Label>Kontoart</Label>
                  <Input value={konto.kontoart} />
                </div>
              </div>
              <div>
                <Label>Bezeichnung</Label>
                <Input value={konto.bezeichnung} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Typ</Label>
                  <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                    <option>Aktiva</option>
                    <option>Passiva</option>
                    <option>Aufwand</option>
                    <option>Ertrag</option>
                  </select>
                </div>
                <div>
                  <Label>Steuer</Label>
                  <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                    <option>Keine</option>
                    <option>VSt 19%</option>
                    <option>USt 19%</option>
                    <option>VSt 7%</option>
                    <option>USt 7%</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="buchungen" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Kontobuchungen (letzte 3)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Datum</th>
                      <th className="text-left py-2">Beleg</th>
                      <th className="text-left py-2">Text</th>
                      <th className="text-right py-2">Soll</th>
                      <th className="text-right py-2">Haben</th>
                      <th className="text-right py-2">Saldo</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {konto.buchungen.map((b, i) => (
                      <tr key={i} className="border-b">
                        <td className="py-3">{new Date(b.datum).toLocaleDateString('de-DE')}</td>
                        <td className="py-3 font-mono">{b.belegnr}</td>
                        <td className="py-3">{b.text}</td>
                        <td className="text-right py-3">
                          {b.soll > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.soll) : '-'}
                        </td>
                        <td className="text-right py-3">
                          {b.haben > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.haben) : '-'}
                        </td>
                        <td className="text-right py-3 font-bold">
                          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.saldo)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saldo" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Saldo & Statistik</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="rounded-lg border p-6 text-center">
                <div className="text-sm text-muted-foreground mb-2">Aktueller Saldo</div>
                <div className="text-4xl font-bold text-green-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(konto.saldo)}
                </div>
                <div className="text-sm text-muted-foreground mt-2">Sollseite</div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Buchungen (Monat)</div>
                  <div className="text-2xl font-bold">{konto.buchungen.length}</div>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Soll (Monat)</div>
                  <div className="text-2xl font-bold text-green-600">
                    {new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(konto.buchungen.reduce((sum, b) => sum + b.soll, 0))} €
                  </div>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Haben (Monat)</div>
                  <div className="text-2xl font-bold text-red-600">
                    {new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(konto.buchungen.reduce((sum, b) => sum + b.haben, 0))} €
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
