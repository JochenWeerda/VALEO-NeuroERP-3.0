import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save, Settings } from 'lucide-react'

export default function SystemEinstellungenPage(): JSX.Element {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Settings className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">System-Einstellungen</h1>
              <p className="text-muted-foreground">Konfiguration</p>
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
          <TabsTrigger value="firma">Firmendaten</TabsTrigger>
          <TabsTrigger value="integration">Integrationen</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <Card>
            <CardHeader>
              <CardTitle>Allgemeine Einstellungen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Sprache</Label>
                <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <Label>Zeitzone</Label>
                <select className="w-full rounded-md border border-input bg-background px-3 py-2">
                  <option value="Europe/Berlin">Europe/Berlin (CET)</option>
                </select>
              </div>
              <div>
                <Label>Währung</Label>
                <Badge variant="outline" className="text-base px-4 py-2">EUR (€)</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="firma">
          <Card>
            <CardHeader>
              <CardTitle>Firmendaten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Firmenname</Label>
                <Input defaultValue="VALEO NeuroERP Landhandel" />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Steuernummer</Label>
                  <Input defaultValue="DE123456789" />
                </div>
                <div>
                  <Label>Handelsregister</Label>
                  <Input defaultValue="HRB 12345" />
                </div>
              </div>
              <div>
                <Label>Adresse</Label>
                <Input defaultValue="Hauptstraße 1, 12345 Musterstadt" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integration">
          <Card>
            <CardHeader>
              <CardTitle>API-Integrationen</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">DATEV</div>
                    <div className="text-sm text-muted-foreground">Finanzbuchhaltung</div>
                  </div>
                  <Badge variant="outline">Verbunden</Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">Online-Banking</div>
                    <div className="text-sm text-muted-foreground">Zahlungsabwicklung</div>
                  </div>
                  <Badge variant="outline">Verbunden</Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">Wetter-API</div>
                    <div className="text-sm text-muted-foreground">Wettervorhersage</div>
                  </div>
                  <Badge variant="outline">Verbunden</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
