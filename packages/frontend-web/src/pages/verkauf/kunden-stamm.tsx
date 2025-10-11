import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save, User } from 'lucide-react'

type KundeData = {
  id: string
  name: string
  typ: string
  strasse: string
  plz: string
  ort: string
  email: string
  telefon: string
  zahlungsziel: number
  kreditlimit: number
  status: 'aktiv' | 'gesperrt'
}

export default function KundenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [kunde, setKunde] = useState<KundeData>({
    id: 'K-001',
    name: 'Landhandel Nord GmbH',
    typ: 'Landhandel',
    strasse: 'Hauptstraße 42',
    plz: '12345',
    ort: 'Nordhausen',
    email: 'info@landhandel-nord.de',
    telefon: '+49 123 456789',
    zahlungsziel: 30,
    kreditlimit: 50000,
    status: 'aktiv',
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <User className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{kunde.name}</h1>
              <p className="text-muted-foreground">Kundennummer: {kunde.id}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/verkauf/kunden')}>
            Zurück
          </Button>
          <Button className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen</TabsTrigger>
          <TabsTrigger value="historie">Historie</TabsTrigger>
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
                  <Input value={kunde.name} onChange={(e) => setKunde({ ...kunde, name: e.target.value })} />
                </div>
                <div>
                  <Label>Typ</Label>
                  <Input value={kunde.typ} />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={kunde.status === 'aktiv' ? 'outline' : 'destructive'}>
                      {kunde.status === 'aktiv' ? 'Aktiv' : 'Gesperrt'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Adresse</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Straße</Label>
                  <Input value={kunde.strasse} />
                </div>
                <div className="grid gap-4 grid-cols-3">
                  <div className="col-span-1">
                    <Label>PLZ</Label>
                    <Input value={kunde.plz} />
                  </div>
                  <div className="col-span-2">
                    <Label>Ort</Label>
                    <Input value={kunde.ort} />
                  </div>
                </div>
                <div>
                  <Label>E-Mail</Label>
                  <Input type="email" value={kunde.email} />
                </div>
                <div>
                  <Label>Telefon</Label>
                  <Input type="tel" value={kunde.telefon} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="konditionen">
          <Card>
            <CardHeader>
              <CardTitle>Zahlungskonditionen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Zahlungsziel (Tage)</Label>
                  <Input type="number" value={kunde.zahlungsziel} />
                </div>
                <div>
                  <Label>Kreditlimit (€)</Label>
                  <Input type="number" value={kunde.kreditlimit} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historie">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">Keine Einträge</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
