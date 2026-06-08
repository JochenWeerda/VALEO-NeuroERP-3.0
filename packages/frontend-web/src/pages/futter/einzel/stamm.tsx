import { useState, useEffect } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save } from 'lucide-react'
import { useEinzelfutterDetail } from '@/lib/api/futter'

export default function EinzelfutterStammPage(): JSX.Element {
  const { id = 'EF-001' } = useParams<{ id: string }>()
  const { data, isLoading, isError } = useEinzelfutterDetail(id)

  const [artikel, setArtikel] = useState('')
  const [art, setArt] = useState('')
  const [herkunft, setHerkunft] = useState('')
  const [protein, setProtein] = useState(0)
  const [energie, setEnergie] = useState(0)
  const [gvoStatus, setGvoStatus] = useState('')
  const [qsMilch, setQsMilch] = useState(false)

  useEffect(() => {
    if (data) {
      setArtikel(data.artikel)
      setArt(data.art)
      setHerkunft(data.herkunft)
      setProtein(data.protein)
      setEnergie(data.energie)
      setGvoStatus(data.gvo_status)
      setQsMilch(data.qs_milch)
    }
  }, [data])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <p className="text-muted-foreground">Lade Einzelfuttermittel…</p>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex items-center justify-center p-12">
        <p className="text-destructive">Einzelfuttermittel konnte nicht geladen werden.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{artikel}</h1>
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
                <Input value={artikel} onChange={(e) => setArtikel(e.target.value)} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Art</Label>
                  <Input value={art} onChange={(e) => setArt(e.target.value)} />
                </div>
                <div>
                  <Label>Herkunft</Label>
                  <Input value={herkunft} onChange={(e) => setHerkunft(e.target.value)} />
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
                  <Input type="number" value={protein} step="0.1" onChange={(e) => setProtein(Number(e.target.value))} />
                </div>
                <div>
                  <Label>Energie (MJ/kg)</Label>
                  <Input type="number" value={energie} step="0.1" onChange={(e) => setEnergie(Number(e.target.value))} />
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
                <Badge variant="outline">{gvoStatus}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={qsMilch} onChange={(e) => setQsMilch(e.target.checked)} className="h-4 w-4" />
                <Label>QS-Milch konform</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
