import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save } from 'lucide-react'

type KonditionData = {
  id: string
  kunde: string
  artikel: string
  basispreis: number
  rabatt: number
  skonto: number
  gueltigAb: string
  gueltigBis: string
  status: 'aktiv' | 'abgelaufen'
}

export default function KonditionenPage(): JSX.Element {
  const [kondition, _setKondition] = useState<KonditionData>({
    id: 'K-001',
    kunde: 'Landhandel Nord GmbH',
    artikel: 'Weizen Premium',
    basispreis: 220.0,
    rabatt: 5.0,
    skonto: 2.0,
    gueltigAb: '2025-01-01',
    gueltigBis: '2025-12-31',
    status: 'aktiv',
  })

  const nettopreis = kondition.basispreis * (1 - kondition.rabatt / 100)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Preiskonditionen</h1>
          <p className="text-muted-foreground">{kondition.kunde}</p>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="preise">
        <TabsList>
          <TabsTrigger value="preise">Preise</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen</TabsTrigger>
          <TabsTrigger value="historie">Historie</TabsTrigger>
        </TabsList>

        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle>Preisgestaltung - {kondition.artikel}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Basispreis (€/t)</Label>
                  <Input type="number" value={kondition.basispreis} step="0.01" />
                </div>
                <div>
                  <Label>Rabatt (%)</Label>
                  <Input type="number" value={kondition.rabatt} step="0.1" />
                </div>
              </div>
              <div className="rounded-lg border p-4 bg-muted">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-muted-foreground">Netto-Preis</div>
                    <div className="text-3xl font-bold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(nettopreis)} / t
                    </div>
                  </div>
                  <Badge variant="outline" className="text-lg px-4 py-2">
                    -{kondition.rabatt}% Rabatt
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="konditionen">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Skonto (%)</Label>
                  <Input type="number" value={kondition.skonto} step="0.1" />
                </div>
                <div>
                  <Label>Zahlungsziel (Tage)</Label>
                  <Input type="number" defaultValue={30} />
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Gültig ab</Label>
                  <Input type="date" value={kondition.gueltigAb} />
                </div>
                <div>
                  <Label>Gültig bis</Label>
                  <Input type="date" value={kondition.gueltigBis} />
                </div>
              </div>
              <div>
                <Label>Status</Label>
                <div className="mt-2">
                  <Badge variant={kondition.status === 'aktiv' ? 'outline' : 'destructive'}>
                    {kondition.status === 'aktiv' ? 'Aktiv' : 'Abgelaufen'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historie">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">Keine Änderungen</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
