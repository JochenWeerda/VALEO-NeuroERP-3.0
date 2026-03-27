import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react'
import { useWarehouses } from '@/lib/api/inventory'
import { Skeleton } from '@/components/ui/skeleton'

export default function LagerplaetzePage(): JSX.Element {
  const { data: warehousesData, isLoading } = useWarehouses()
  const items = warehousesData?.items ?? []
  const lager = (() => {
    const bereiche = items.map((w) => {
      const kapazitaet = w.capacity ?? 0
      const bestand = w.used_capacity ?? 0
      const auslastungPct = kapazitaet > 0 ? (bestand / kapazitaet) * 100 : 0
      return {
        name: w.name || w.code || w.id,
        plaetze: Math.max(1, Math.ceil(kapazitaet / 100)),
        belegt: Math.ceil(bestand > 0 ? Math.max(1, Math.ceil(bestand / 100)) : 0),
        kapazitaet,
        bestand,
        auslastungPct,
      }
    })
    const totalKapazitaet = bereiche.reduce((s, b) => s + b.kapazitaet, 0)
    const totalBestand = bereiche.reduce((s, b) => s + b.bestand, 0)
    const plaetze = bereiche.reduce((s, b) => s + b.plaetze, 0)
    const belegt = bereiche.reduce((s, b) => s + b.belegt, 0)
    const frei = plaetze - belegt
    const auslastung = totalKapazitaet > 0 ? (totalBestand / totalKapazitaet) * 100 : 0
    return { plaetze, belegt, frei, auslastung, bereiche }
  })()

  const kritisch = lager.bereiche.length > 0
    ? lager.bereiche.filter((b) => b.plaetze > 0 && b.belegt / b.plaetze > 0.95).length
    : 0

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Lagerplätze</h1>
        <p className="text-muted-foreground">Lagerverwaltung & Auslastung</p>
      </div>

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      )}

      {!isLoading && lager.bereiche.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">Keine Lagerbereiche erfasst. Erfassen Sie Lagerplätze unter Lager &gt; Stammdaten.</p>
          </CardContent>
        </Card>
      )}

      {kritisch > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{kritisch} Lagerbereich(e) über 95% ausgelastet!</span>
            </div>
          </CardContent>
        </Card>
      )}

      {!isLoading && (
      <>
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lagerplätze Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{lager.plaetze}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Belegt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{lager.belegt}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Frei</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{lager.frei}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{lager.auslastung}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Warehouse className="h-5 w-5" />
            Lagerbereiche
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {lager.bereiche.map((bereich, i) => {
              const auslastung = bereich.plaetze > 0 ? (bereich.belegt / bereich.plaetze) * 100 : 0
              const fuellstand = (bereich.kapazitaet ?? 0) > 0 ? ((bereich.bestand ?? 0) / (bereich.kapazitaet ?? 1)) * 100 : 0
              return (
                <div key={i} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-semibold text-lg">{bereich.name}</div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">
                        {`${bereich.belegt} / ${bereich.plaetze} Plätze`}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {`${bereich.bestand} / ${bereich.kapazitaet} t`}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Plätze:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${auslastung > 95 ? 'bg-red-600' : auslastung > 80 ? 'bg-orange-600' : 'bg-green-600'}`}
                          style={{ width: `${auslastung}%` }}
                        />
                      </div>
                      <Badge variant={auslastung > 95 ? 'destructive' : 'outline'}>
                        {`${auslastung.toFixed(0)}%`}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Füllstand:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600" style={{ width: `${fuellstand}%` }} />
                      </div>
                      <Badge variant="outline">{`${fuellstand.toFixed(0)}%`}</Badge>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
      </>
      )}
    </div>
  )
}
