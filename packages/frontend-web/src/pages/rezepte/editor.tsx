import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ChefHat, Plus, Save, Trash2 } from 'lucide-react'
import { useRezeptDetail, type RezeptKomponente } from '@/lib/api/futter'

export default function RezeptEditorPage(): JSX.Element {
  const { id = 'REZ-001' } = useParams<{ id: string }>()
  const { data, isLoading, isError } = useRezeptDetail(id)

  const [name, setName] = useState('')
  const [tierart, setTierart] = useState('')
  const [komponenten, setKomponenten] = useState<RezeptKomponente[]>([])
  const [protein, setProtein] = useState(0)
  const [energie, setEnergie] = useState(0)

  useEffect(() => {
    if (data) {
      setName(data.name)
      setTierart(data.tierart)
      setKomponenten(data.komponenten.map((k) => ({ ...k })))
      setProtein(data.protein)
      setEnergie(data.energie)
    }
  }, [data])

  function addKomponente(): void {
    const newId = String(komponenten.length + 1)
    setKomponenten((prev) => [...prev, { id: newId, name: '', anteil: 0 }])
  }

  function removeKomponente(kid: string): void {
    setKomponenten((prev) => prev.filter((k) => k.id !== kid))
  }

  const gesamtAnteil = komponenten.reduce((sum, k) => sum + k.anteil, 0)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <p className="text-muted-foreground">Lade Rezept…</p>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex items-center justify-center p-12">
        <p className="text-destructive">Rezept konnte nicht geladen werden.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ChefHat className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{name}</h1>
              <p className="text-muted-foreground">Rezeptur-Editor</p>
            </div>
          </div>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Grunddaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <Label>Tierart</Label>
              <Input value={tierart} onChange={(e) => setTierart(e.target.value)} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Nährwerte (berechnet)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Rohprotein</Label>
              <div className="text-2xl font-bold">{protein}%</div>
            </div>
            <div>
              <Label>Energie</Label>
              <div className="text-2xl font-bold">{energie} MJ/kg</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Rezeptur-Komponenten</span>
            <Button size="sm" onClick={addKomponente} className="gap-2">
              <Plus className="h-4 w-4" />
              Komponente
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {komponenten.map((k) => (
              <div key={k.id} className="flex items-center gap-4 rounded-lg border p-3">
                <Input
                  value={k.name}
                  placeholder="Komponente"
                  className="flex-1"
                  onChange={(e) =>
                    setKomponenten((prev) =>
                      prev.map((x) => (x.id === k.id ? { ...x, name: e.target.value } : x)),
                    )
                  }
                />
                <Input
                  type="number"
                  value={k.anteil}
                  step="0.1"
                  className="w-24"
                  onChange={(e) =>
                    setKomponenten((prev) =>
                      prev.map((x) => (x.id === k.id ? { ...x, anteil: Number(e.target.value) } : x)),
                    )
                  }
                />
                <span className="text-sm text-muted-foreground">%</span>
                <Button size="sm" variant="ghost" onClick={() => removeKomponente(k.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <div className="mt-4 flex justify-between border-t pt-3 font-bold">
              <span>Gesamt</span>
              <div className="flex items-center gap-2">
                <span>{gesamtAnteil}%</span>
                <Badge variant={gesamtAnteil === 100 ? 'outline' : 'destructive'}>
                  {gesamtAnteil === 100 ? '✓ OK' : '✗ Nicht 100%'}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
