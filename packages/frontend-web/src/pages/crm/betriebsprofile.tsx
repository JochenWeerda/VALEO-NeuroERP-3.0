import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save, Tractor } from 'lucide-react'

type BetriebData = {
  id: string
  betriebsname: string
  inhaber: string
  flaeche: number
  kulturen: Array<{ kultur: string; flaeche: number }>
  tierbestand: Array<{ tierart: string; anzahl: number }>
}

export default function BetriebsprofilePage(): JSX.Element {
  const [betrieb, _setBetrieb] = useState<BetriebData>({
    id: 'B-001',
    betriebsname: 'Hof Schmidt',
    inhaber: 'Hermann Schmidt',
    flaeche: 250,
    kulturen: [
      { kultur: 'Weizen', flaeche: 120 },
      { kultur: 'Raps', flaeche: 80 },
      { kultur: 'Mais', flaeche: 50 },
    ],
    tierbestand: [
      { tierart: 'Milchkühe', anzahl: 80 },
      { tierart: 'Kälber', anzahl: 25 },
    ],
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Tractor className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{betrieb.betriebsname}</h1>
              <p className="text-muted-foreground">{betrieb.inhaber}</p>
            </div>
          </div>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="kulturen">Kulturen</TabsTrigger>
          <TabsTrigger value="tiere">Tierbestand</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>Betriebsname</Label>
                <Input value={betrieb.betriebsname} />
              </div>
              <div>
                <Label>Inhaber</Label>
                <Input value={betrieb.inhaber} />
              </div>
              <div>
                <Label>Gesamtfläche (ha)</Label>
                <Input type="number" value={betrieb.flaeche} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kulturen">
          <Card>
            <CardHeader>
              <CardTitle>Anbauflächen</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {betrieb.kulturen.map((k, i) => (
                  <div key={i} className="flex justify-between rounded-lg border p-3">
                    <span>{k.kultur}</span>
                    <span className="font-semibold">{k.flaeche} ha</span>
                  </div>
                ))}
                <div className="mt-4 flex justify-between border-t pt-2 font-bold">
                  <span>Gesamt</span>
                  <span>{betrieb.kulturen.reduce((s, k) => s + k.flaeche, 0)} ha</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tiere">
          <Card>
            <CardHeader>
              <CardTitle>Tierbestand</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {betrieb.tierbestand.map((t, i) => (
                  <div key={i} className="flex justify-between rounded-lg border p-3">
                    <span>{t.tierart}</span>
                    <span className="font-semibold">{t.anzahl} Stück</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
