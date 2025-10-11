import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save } from 'lucide-react'

type FutterData = {
  id: string
  artikel: string
  art: string
  herkunft: string
  lieferant: string
  protein: number
  energie: number
  gvoStatus: string
  qsMilch: boolean
  verfuegbar: number
}

export default function EinzelfutterStammPage(): JSX.Element {
  const [futter, setFutter] = useState<FutterData>({
    id: 'EF-001',
    artikel: 'Sojaschrot 44% Protein',
    art: 'Eiweißfutter',
    herkunft: 'Brasilien',
    lieferant: 'Agrar Import GmbH',
    protein: 44.0,
    energie: 13.2,
    gvoStatus: 'gvo-frei-zertifiziert',
    qsMilch: true,
    verfuegbar: 150,
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{futter.artikel}</h1>
          <p className="text-muted-foreground">Einzelfuttermittel-Stammdaten</p>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="naehrwerte">Nährwerte</TabsTrigger>
          <TabsTrigger value="qs">QS-Attribute</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>Artikel</Label>
                <Input value={futter.artikel} onChange={(e) => setFutter({ ...futter, artikel: e.target.value })} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Art</Label>
                  <Input value={futter.art} onChange={(e) => setFutter({ ...futter, art: e.target.value })} />
                </div>
                <div>
                  <Label>Herkunft</Label>
                  <Input value={futter.herkunft} onChange={(e) => setFutter({ ...futter, herkunft: e.target.value })} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="naehrwerte">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Rohprotein (%)</Label>
                  <Input type="number" value={futter.protein} step="0.1" />
                </div>
                <div>
                  <Label>Energie (MJ/kg)</Label>
                  <Input type="number" value={futter.energie} step="0.1" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="qs">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>GVO-Status</Label>
                <Badge variant="outline">{futter.gvoStatus}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={futter.qsMilch} className="h-4 w-4" />
                <Label>QS-Milch konform</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
