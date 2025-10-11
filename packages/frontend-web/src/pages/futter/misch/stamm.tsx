import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save } from 'lucide-react'

type MischfutterData = {
  id: string
  typ: string
  tierart: string
  leistungsstufe: string
  rezeptur: Array<{ komponente: string; anteil: number }>
  protein: number
  energie: number
}

export default function MischfutterStammPage(): JSX.Element {
  const [mischfutter, _setMischfutter] = useState<MischfutterData>({
    id: 'MF-001',
    typ: 'Milchviehfutter Hochleistung',
    tierart: 'Rind (Milch)',
    leistungsstufe: 'Hochleistung (>30 l/Tag)',
    rezeptur: [
      { komponente: 'Sojaschrot 44%', anteil: 25 },
      { komponente: 'Weizen', anteil: 30 },
      { komponente: 'Mais', anteil: 20 },
      { komponente: 'Mineralfutter', anteil: 5 },
    ],
    protein: 18.5,
    energie: 11.8,
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{mischfutter.typ}</h1>
          <p className="text-muted-foreground">Mischfutter-Stammdaten</p>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="rezeptur">Rezeptur</TabsTrigger>
          <TabsTrigger value="naehrwerte">Nährwerte</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>Typ</Label>
                <Input value={mischfutter.typ} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Tierart</Label>
                  <Input value={mischfutter.tierart} />
                </div>
                <div>
                  <Label>Leistungsstufe</Label>
                  <Input value={mischfutter.leistungsstufe} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rezeptur">
          <Card>
            <CardHeader>
              <CardTitle>Rezeptur-Komponenten</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mischfutter.rezeptur.map((r, i) => (
                  <div key={i} className="flex justify-between rounded-lg border p-3">
                    <span>{r.komponente}</span>
                    <span className="font-semibold">{r.anteil}%</span>
                  </div>
                ))}
                <div className="mt-4 flex justify-between border-t pt-2 font-bold">
                  <span>Gesamt</span>
                  <span>{mischfutter.rezeptur.reduce((s, r) => s + r.anteil, 0)}%</span>
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
                  <Input type="number" value={mischfutter.protein} step="0.1" />
                </div>
                <div>
                  <Label>Energie (MJ/kg)</Label>
                  <Input type="number" value={mischfutter.energie} step="0.1" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
