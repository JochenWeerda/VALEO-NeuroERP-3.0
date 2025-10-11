import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Package, Save } from 'lucide-react'

type ChargeData = {
  id: string
  chargenId: string
  artikel: string
  menge: number
  lieferant: string
  gvoStatus: string
  qsMilch: boolean
  eudr: boolean
  lagerort: string
  status: 'neu' | 'freigegeben' | 'gesperrt' | 'verbraucht'
}

export default function ChargenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [charge, _setCharge] = useState<ChargeData>({
    id: 'CH-001',
    chargenId: '251011-WEI-001',
    artikel: 'Weizen Qualität A',
    menge: 25.0,
    lieferant: 'Landwirt Schmidt',
    gvoStatus: 'gvo-frei-zertifiziert',
    qsMilch: true,
    eudr: true,
    lagerort: 'Silo 1',
    status: 'freigegeben',
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Package className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold font-mono">{charge.chargenId}</h1>
              <p className="text-muted-foreground">{charge.artikel}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/charge/liste')}>
            Zurück
          </Button>
          <Button className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="qs">QS-Attribute</TabsTrigger>
          <TabsTrigger value="bewegungen">Bewegungen</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Chargendaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Chargen-ID</Label>
                  <Input value={charge.chargenId} readOnly className="font-mono font-bold" />
                </div>
                <div>
                  <Label>Artikel</Label>
                  <Input value={charge.artikel} />
                </div>
                <div>
                  <Label>Menge (t)</Label>
                  <Input type="number" value={charge.menge} step="0.001" />
                </div>
                <div>
                  <Label>Lieferant</Label>
                  <Input value={charge.lieferant} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Lagerung & Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Lagerort</Label>
                  <Input value={charge.lagerort} />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={charge.status === 'freigegeben' ? 'outline' : charge.status === 'gesperrt' ? 'destructive' : 'default'}>
                      {charge.status === 'freigegeben' ? '✓ Freigegeben' : charge.status === 'gesperrt' ? '✗ Gesperrt' : charge.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="qs">
          <Card>
            <CardHeader>
              <CardTitle>QS & Nachhaltigkeit</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>GVO-Status</Label>
                <div className="mt-2">
                  <Badge variant="outline">{charge.gvoStatus}</Badge>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input type="checkbox" checked={charge.qsMilch} readOnly className="h-4 w-4" />
                  <Label>QS-Milch konform</Label>
                </div>
                <div className="flex items-center gap-2">
                  <input type="checkbox" checked={charge.eudr} readOnly className="h-4 w-4" />
                  <Label>EUDR-konform (entwaldungsfrei)</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bewegungen">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">Keine Bewegungen</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
