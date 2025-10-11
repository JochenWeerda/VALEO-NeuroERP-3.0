import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Package, Save } from 'lucide-react'

type ArtikelData = {
  id: string
  artikelnr: string
  bezeichnung: string
  warengruppe: string
  einheit: string
  vkPreis: number
  ekPreis: number
  bestand: number
  status: 'aktiv' | 'auslaufend'
}

export default function ArtikelStammPage(): JSX.Element {
  const [artikel, _setArtikel] = useState<ArtikelData>({
    id: 'A-001',
    artikelnr: '10001',
    bezeichnung: 'Weizen Premium Qualität A',
    warengruppe: 'Getreide',
    einheit: 't',
    vkPreis: 220.5,
    ekPreis: 180.0,
    bestand: 450.0,
    status: 'aktiv',
  })

  const marge = ((artikel.vkPreis - artikel.ekPreis) / artikel.vkPreis) * 100

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Package className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{artikel.bezeichnung}</h1>
              <p className="text-muted-foreground">Artikel-Nr.: {artikel.artikelnr}</p>
            </div>
          </div>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="preise">Preise</TabsTrigger>
          <TabsTrigger value="bestand">Bestand</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Grunddaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Artikelnummer</Label>
                  <Input value={artikel.artikelnr} readOnly className="font-mono font-bold" />
                </div>
                <div>
                  <Label>Bezeichnung</Label>
                  <Input value={artikel.bezeichnung} />
                </div>
                <div>
                  <Label>Warengruppe</Label>
                  <Badge variant="outline" className="text-base px-4 py-2">{artikel.warengruppe}</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Einheiten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Einheit</Label>
                  <Input value={artikel.einheit} />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={artikel.status === 'aktiv' ? 'outline' : 'secondary'}>
                      {artikel.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle>Preisinformationen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Verkaufspreis (€/{artikel.einheit})</Label>
                  <Input type="number" value={artikel.vkPreis} step="0.01" />
                </div>
                <div>
                  <Label>Einkaufspreis (€/{artikel.einheit})</Label>
                  <Input type="number" value={artikel.ekPreis} step="0.01" />
                </div>
              </div>
              <div className="rounded-lg border p-4 bg-muted">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm text-muted-foreground">Handelsspanne</div>
                    <div className="text-3xl font-bold">{marge.toFixed(1)}%</div>
                  </div>
                  <Badge variant={marge > 20 ? 'outline' : 'secondary'} className="text-lg px-4 py-2">
                    {marge > 20 ? 'Gut' : 'Niedrig'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bestand">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>Aktueller Bestand</Label>
                <div className="mt-2 text-3xl font-bold">{artikel.bestand.toLocaleString('de-DE')} {artikel.einheit}</div>
              </div>
              <div>
                <Label>Lagerwert</Label>
                <div className="mt-2 text-2xl font-bold text-blue-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(artikel.bestand * artikel.ekPreis)}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
