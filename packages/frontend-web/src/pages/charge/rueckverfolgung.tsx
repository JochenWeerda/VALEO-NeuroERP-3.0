import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowDown, FileDown, Search } from 'lucide-react'

export default function RueckverfolgungPage(): JSX.Element {
  const trace = {
    chargenId: '251011-WEI-001',
    artikel: 'Weizen Premium',
    lieferkette: [
      { stufe: 'Erzeuger', name: 'Landwirt Schmidt', ort: 'Nordhausen', datum: '2025-10-05' },
      { stufe: 'Wareneingang', name: 'VALEO Landhandel', ort: 'Hauptstandort', datum: '2025-10-11' },
      { stufe: 'Lagerung', name: 'Silo 1', ort: 'Hauptstandort', datum: '2025-10-11' },
      { stufe: 'Auslieferung', name: 'Mühle Nord GmbH', ort: 'Südhausen', datum: '2025-10-15' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Chargen-Rückverfolgung</h1>
        <p className="text-muted-foreground">Lieferketten-Transparenz</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Suche
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="search">Chargen-ID oder Lieferschein-Nr.</Label>
              <Input id="search" defaultValue={trace.chargenId} className="font-mono" />
            </div>
            <Button className="self-end gap-2">
              <Search className="h-4 w-4" />
              Suchen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Charge: {trace.chargenId}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <div className="text-2xl font-bold">{trace.artikel}</div>
            <Badge variant="outline" className="mt-2">Vollständig dokumentiert</Badge>
          </div>

          <div className="space-y-4">
            {trace.lieferkette.map((item, i) => (
              <div key={i}>
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className="rounded-full bg-blue-600 p-2 text-white">
                      <div className="h-2 w-2 rounded-full bg-white" />
                    </div>
                    {i < trace.lieferkette.length - 1 && (
                      <ArrowDown className="h-6 w-6 text-muted-foreground my-2" />
                    )}
                  </div>
                  <Card className="flex-1">
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <Badge>{item.stufe}</Badge>
                          <div className="mt-2 font-semibold">{item.name}</div>
                          <div className="text-sm text-muted-foreground">{item.ort}</div>
                        </div>
                        <div className="text-right text-sm text-muted-foreground">
                          {new Date(item.datum).toLocaleDateString('de-DE')}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-end">
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Bericht exportieren
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
