import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AlertTriangle, Cloud, CloudRain, Droplets, MapPin, RefreshCw, Sun,
  Thermometer, Wind, Zap,
} from 'lucide-react'
import { useWetterAktuell, useWetterPrognose, useWetterWarnungen } from '@/lib/api/agrar'

// Standardkoordinaten Hannover — in einer echten App vom Nutzerprofil / Schlag
const DEFAULT_COORDS = { lat: 52.37, lon: 9.73 }

const severityVariant = (s: string): 'outline' | 'secondary' | 'destructive' => {
  if (s === 'Extreme' || s === 'Severe') return 'destructive'
  if (s === 'Moderate') return 'secondary'
  return 'outline'
}

const wetterIcon = (cond?: string) => {
  if (!cond) return <Cloud className="h-10 w-10 text-gray-400" />
  if (cond.includes('rain') || cond.includes('drizzle') || cond.includes('shower'))
    return <CloudRain className="h-10 w-10 text-blue-500" />
  if (cond.includes('thunder') || cond.includes('lightning'))
    return <Zap className="h-10 w-10 text-status-warning" />
  if (cond.includes('cloud') || cond.includes('fog') || cond.includes('overcast'))
    return <Cloud className="h-10 w-10 text-gray-500" />
  return <Sun className="h-10 w-10 text-status-warning" />
}

const fmt = (n?: number | null, unit = '') =>
  n !== null && n !== undefined ? `${n.toFixed(1)}${unit}` : '—'

export default function WetterPrognosePage(): JSX.Element {
  const [coords, setCoords] = useState(DEFAULT_COORDS)
  const [latInput, setLatInput] = useState(String(DEFAULT_COORDS.lat))
  const [lonInput, setLonInput] = useState(String(DEFAULT_COORDS.lon))

  const { data: aktuell, isLoading: loadAktuell, refetch: refetchAktuell } = useWetterAktuell(coords)
  const { data: prognose = [], isLoading: loadPrognose, refetch: refetchPrognose } = useWetterPrognose(coords, 7)
  const { data: warnungen = [], isLoading: loadWarnungen } = useWetterWarnungen(coords)

  const handleApply = () => {
    const lat = parseFloat(latInput)
    const lon = parseFloat(lonInput)
    if (!isNaN(lat) && !isNaN(lon)) {
      setCoords({ lat, lon })
    }
  }

  const handleRefresh = () => {
    void refetchAktuell()
    void refetchPrognose()
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Wetter-Prognose</h1>
          <p className="text-muted-foreground">7-Tage-Vorhersage · DWD ICON-D2 via Open-Meteo · Stationsdaten via BrightSky</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleRefresh} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Aktualisieren
        </Button>
      </div>

      {/* Koordinaten-Auswahl */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4" />
            Standort (WGS84)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div>
              <Label>Breitengrad</Label>
              <Input
                className="w-32"
                value={latInput}
                onChange={e => setLatInput(e.target.value)}
                placeholder="z.B. 52.37"
              />
            </div>
            <div>
              <Label>Längengrad</Label>
              <Input
                className="w-32"
                value={lonInput}
                onChange={e => setLonInput(e.target.value)}
                placeholder="z.B. 9.73"
              />
            </div>
            <Button onClick={handleApply} size="sm">Übernehmen</Button>
            {aktuell?.station_name && (
              <span className="text-sm text-muted-foreground">
                Nächste DWD-Station: <strong>{aktuell.station_name}</strong>
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Wetterwarnungen */}
      {!loadWarnungen && warnungen.length > 0 && (
        <div className="space-y-2">
          {warnungen.map(w => (
            <Card key={w.id} className="border-orange-400 bg-orange-50">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-status-warning mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-orange-900">{w.headline}</span>
                      <Badge variant={severityVariant(w.severity)}>{w.severity}</Badge>
                    </div>
                    {w.description && (
                      <p className="text-sm text-orange-800">{w.description}</p>
                    )}
                    {(w.gueltig_von || w.gueltig_bis) && (
                      <p className="text-xs text-orange-700 mt-1">
                        {w.gueltig_von && `von ${new Date(w.gueltig_von).toLocaleString('de-DE')}`}
                        {w.gueltig_bis && ` bis ${new Date(w.gueltig_bis).toLocaleString('de-DE')}`}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Aktuelles Wetter */}
      {loadAktuell ? (
        <Skeleton className="h-36" />
      ) : aktuell ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-6 w-6 text-status-warning" />
              Aktuell
              {aktuell.timestamp && (
                <span className="text-sm font-normal text-muted-foreground ml-2">
                  {new Date(aktuell.timestamp).toLocaleString('de-DE')}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              <div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Thermometer className="h-4 w-4" />
                  Temperatur
                </div>
                <div className="text-3xl font-bold mt-1">{fmt(aktuell.temperatur, '°C')}</div>
                {aktuell.taupunkt !== undefined && (
                  <div className="text-xs text-muted-foreground">Taupunkt: {fmt(aktuell.taupunkt, '°C')}</div>
                )}
              </div>
              <div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Droplets className="h-4 w-4" />
                  Niederschlag
                </div>
                <div className="text-3xl font-bold mt-1">{fmt(aktuell.niederschlag, ' mm')}</div>
                {aktuell.relative_feuchte !== undefined && (
                  <div className="text-xs text-muted-foreground">Feuchte: {aktuell.relative_feuchte}%</div>
                )}
              </div>
              <div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Wind className="h-4 w-4" />
                  Wind
                </div>
                <div className="text-3xl font-bold mt-1">{fmt(aktuell.windgeschwindigkeit, ' km/h')}</div>
                {aktuell.windboee && (
                  <div className="text-xs text-muted-foreground">Böen: {fmt(aktuell.windboee, ' km/h')}</div>
                )}
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Bedingung</div>
                <div className="mt-1">{wetterIcon(aktuell.bedingung)}</div>
                <Badge variant="outline" className="mt-2 text-xs">{aktuell.bedingung ?? '—'}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* 7-Tage-Prognose */}
      <Card>
        <CardHeader>
          <CardTitle>7-Tage-Prognose</CardTitle>
        </CardHeader>
        <CardContent>
          {loadPrognose ? (
            <div className="grid gap-3 sm:grid-cols-4 lg:grid-cols-7">
              {Array.from({ length: 7 }).map((_, i) => (
                <Skeleton key={i} className="h-48" />
              ))}
            </div>
          ) : prognose.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Keine Prognose-Daten verfügbar.</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7">
              {prognose.map((tag) => {
                const d = new Date(tag.datum)
                const label = d.toLocaleDateString('de-DE', { weekday: 'short', day: 'numeric', month: 'numeric' })
                const regen = (tag.niederschlag_summe ?? 0) > 0
                return (
                  <Card key={tag.datum}>
                    <CardContent className="pt-4 pb-3">
                      <div className="text-center space-y-1">
                        <div className="text-xs font-medium text-muted-foreground">{label}</div>
                        <div className="my-2">
                          {regen
                            ? <CloudRain className="h-8 w-8 mx-auto text-blue-500" />
                            : <Sun className="h-8 w-8 mx-auto text-status-warning" />}
                        </div>
                        <div className="text-lg font-bold">{fmt(tag.temperatur_max, '°')}</div>
                        <div className="text-sm text-muted-foreground">{fmt(tag.temperatur_min, '°')}</div>
                        {regen && (
                          <div className="text-xs text-blue-600 font-medium">
                            {fmt(tag.niederschlag_summe, ' mm')}
                          </div>
                        )}
                        {tag.et0_fao !== undefined && tag.et0_fao !== null && (
                          <div className="text-xs text-green-700 mt-1" title="FAO Grasreferenz-Evapotranspiration">
                            ET₀ {fmt(tag.et0_fao, ' mm')}
                          </div>
                        )}
                        {tag.wachstumsgradtage !== undefined && tag.wachstumsgradtage !== null && (
                          <div className="text-xs text-amber-700" title="Wachstumsgradtage (base 0°C)">
                            GDD {fmt(tag.wachstumsgradtage)}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
