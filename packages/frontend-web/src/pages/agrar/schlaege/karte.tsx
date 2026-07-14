import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Map, Sprout } from 'lucide-react'
import { useSchlaege } from '@/lib/api/agrar'

const kulturFarbe: Record<string, string> = {
  Weizen: 'bg-yellow-200', Winterweizen: 'bg-yellow-200', Sommerweizen: 'bg-yellow-100',
  Raps: 'bg-yellow-300', Winterraps: 'bg-yellow-300',
  Mais: 'bg-green-200', Silomais: 'bg-green-300',
  Gerste: 'bg-amber-200', Wintergerste: 'bg-amber-200', Sommergerste: 'bg-amber-100',
  Roggen: 'bg-orange-200', Triticale: 'bg-orange-100',
}

export default function SchlagKartePage(): JSX.Element {
  const { data: schlaegeListe = [], isLoading } = useSchlaege()

  const gesamt = schlaegeListe.length
  const flaeche = schlaegeListe.reduce((sum, s) => sum + s.flaeche, 0)

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
        <Skeleton className="h-96" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Schlagkarte</h1>
        <p className="text-muted-foreground">Übersicht Schläge & Kulturen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Fläche</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold">{flaeche.toFixed(1)} ha</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Schlaggröße</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {gesamt > 0 ? (flaeche / gesamt).toFixed(1) : '0.0'} ha
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Schlagkarte (vereinfacht)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border-2 border-dashed p-6 min-h-[400px] flex items-center justify-center bg-green-50">
            <div className="text-center">
              <Map className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-muted-foreground font-semibold">Interaktive Karte</p>
              <p className="text-sm text-muted-foreground mt-2">Integration: OpenStreetMap / Google Maps</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Schlag-Übersicht</CardTitle>
        </CardHeader>
        <CardContent>
          {schlaegeListe.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Keine Schläge erfasst.</p>
          ) : (
            <div className="space-y-3">
              {schlaegeListe.map((schlag, i) => (
                <div key={schlag.id} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg ${kulturFarbe[schlag.kultur] ?? 'bg-gray-200'} flex items-center justify-center font-mono font-bold text-xs`}>
                        {schlag.flik ? schlag.flik.slice(-4) : `S-${String(i + 1).padStart(3, '0')}`}
                      </div>
                      <div>
                        <div className="font-semibold text-lg">{schlag.name}</div>
                        <div className="text-sm text-muted-foreground">
                          <Badge variant="outline" className="mr-2">{schlag.kultur}</Badge>
                          {schlag.flaeche} ha
                          {schlag.gemeinde && <span className="ml-2 text-muted-foreground">· {schlag.gemeinde}</span>}
                        </div>
                      </div>
                    </div>
                    <Badge variant={schlag.status === 'aktiv' ? 'outline' : 'secondary'}>
                      {schlag.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
