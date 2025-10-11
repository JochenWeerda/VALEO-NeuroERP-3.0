import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Building2, Save } from 'lucide-react'

type LieferantData = {
  id: string
  name: string
  typ: string
  strasse: string
  plz: string
  ort: string
  email: string
  telefon: string
  qsNummer: string
  bewertung: number
  status: 'aktiv' | 'gesperrt'
}

export default function LieferantenStammPage(): JSX.Element {
  const [lieferant, _setLieferant] = useState<LieferantData>({
    id: 'L-001',
    name: 'Saatgut AG',
    typ: 'Saatgut-Lieferant',
    strasse: 'Industriestr. 15',
    plz: '54321',
    ort: 'Südhausen',
    email: 'info@saatgut-ag.de',
    telefon: '+49 987 654321',
    qsNummer: 'QS-12345',
    bewertung: 4.5,
    status: 'aktiv',
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{lieferant.name}</h1>
              <p className="text-muted-foreground">Lieferantennummer: {lieferant.id}</p>
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
          <TabsTrigger value="qs">QS & Bewertung</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Unternehmensdaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Firmenname</Label>
                  <Input value={lieferant.name} />
                </div>
                <div>
                  <Label>Typ</Label>
                  <Input value={lieferant.typ} />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={lieferant.status === 'aktiv' ? 'outline' : 'destructive'}>
                      {lieferant.status === 'aktiv' ? 'Aktiv' : 'Gesperrt'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Kontaktdaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Straße</Label>
                  <Input value={lieferant.strasse} />
                </div>
                <div className="grid gap-4 grid-cols-3">
                  <div>
                    <Label>PLZ</Label>
                    <Input value={lieferant.plz} />
                  </div>
                  <div className="col-span-2">
                    <Label>Ort</Label>
                    <Input value={lieferant.ort} />
                  </div>
                </div>
                <div>
                  <Label>E-Mail</Label>
                  <Input type="email" value={lieferant.email} />
                </div>
                <div>
                  <Label>Telefon</Label>
                  <Input type="tel" value={lieferant.telefon} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="qs">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <Label>QS-Nummer</Label>
                <Input value={lieferant.qsNummer} />
              </div>
              <div>
                <Label>Bewertung</Label>
                <div className="text-2xl font-bold">{lieferant.bewertung} / 5</div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
