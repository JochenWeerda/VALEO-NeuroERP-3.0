import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ChefHat, Plus, Save, Trash2 } from 'lucide-react'

type Komponente = {
  id: string
  name: string
  anteil: number
}

type RezeptData = {
  id: string
  name: string
  tierart: string
  komponenten: Komponente[]
  protein: number
  energie: number
}

export default function RezeptEditorPage(): JSX.Element {
  const [rezept, setRezept] = useState<RezeptData>({
    id: 'REZ-001',
    name: 'Milchviehfutter Hochleistung',
    tierart: 'Rind (Milch)',
    komponenten: [
      { id: '1', name: 'Sojaschrot 44%', anteil: 25 },
      { id: '2', name: 'Weizen', anteil: 30 },
      { id: '3', name: 'Mais', anteil: 20 },
      { id: '4', name: 'Mineralfutter', anteil: 5 },
    ],
    protein: 18.5,
    energie: 11.8,
  })

  function addKomponente(): void {
    const newId = String(rezept.komponenten.length + 1)
    setRezept((prev) => ({
      ...prev,
      komponenten: [...prev.komponenten, { id: newId, name: '', anteil: 0 }],
    }))
  }

  function removeKomponente(id: string): void {
    setRezept((prev) => ({
      ...prev,
      komponenten: prev.komponenten.filter((k) => k.id !== id),
    }))
  }

  const gesamtAnteil = rezept.komponenten.reduce((sum, k) => sum + k.anteil, 0)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ChefHat className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{rezept.name}</h1>
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
              <Input value={rezept.name} />
            </div>
            <div>
              <Label>Tierart</Label>
              <Input value={rezept.tierart} />
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
              <div className="text-2xl font-bold">{rezept.protein}%</div>
            </div>
            <div>
              <Label>Energie</Label>
              <div className="text-2xl font-bold">{rezept.energie} MJ/kg</div>
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
            {rezept.komponenten.map((k) => (
              <div key={k.id} className="flex items-center gap-4 rounded-lg border p-3">
                <Input value={k.name} placeholder="Komponente" className="flex-1" />
                <Input type="number" value={k.anteil} step="0.1" className="w-24" />
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
