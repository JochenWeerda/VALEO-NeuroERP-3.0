import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Cloud, CloudRain, Loader2, ShieldAlert } from 'lucide-react'
import { useWetterWarnungen, type WetterWarnung } from '@/lib/api/agrar'

const DEFAULT_COORDS = { lat: 53.36, lon: 7.21 } // Emden / Ostfriesland

function severityBorderClass(severity: string): string {
  switch (severity) {
    case 'Extreme': return 'border-red-600'
    case 'Severe': return 'border-orange-500'
    case 'Moderate': return 'border-yellow-500'
    default: return 'border-blue-400'
  }
}

function severityBadgeVariant(severity: string): 'destructive' | 'secondary' | 'outline' {
  switch (severity) {
    case 'Extreme':
    case 'Severe': return 'destructive'
    case 'Moderate': return 'secondary'
    default: return 'outline'
  }
}

function severityLabel(severity: string): string {
  switch (severity) {
    case 'Extreme': return 'Extrem'
    case 'Severe': return 'Schwer'
    case 'Moderate': return 'Mäßig'
    case 'Minor': return 'Gering'
    default: return severity
  }
}

function warnungIcon(event: string) {
  const lower = event.toLowerCase()
  if (lower.includes('regen') || lower.includes('niederschlag')) {
    return <CloudRain className="h-8 w-8 text-blue-600" />
  }
  if (lower.includes('gewitter') || lower.includes('sturm') || lower.includes('wind')) {
    return <ShieldAlert className="h-8 w-8 text-orange-600" />
  }
  return <Cloud className="h-8 w-8 text-gray-600" />
}

export default function WetterwarnungPage(): JSX.Element {
  const { data: warnungen, isLoading, isError } = useWetterWarnungen(DEFAULT_COORDS)

  const aktiv = warnungen?.length ?? 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-3 text-muted-foreground">Wetterwarnungen werden geladen...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wetterwarnungen</h1>
        <p className="text-muted-foreground">DWD-Warnlagebericht</p>
      </div>

      {aktiv > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{aktiv} aktive Wetterwarnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Warnungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{aktiv}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Quelle</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="outline" className="text-base px-4 py-2">DWD Deutscher Wetterdienst</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cloud className="h-5 w-5" />
            Aktuelle Warnungen
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isError && (
            <p className="text-muted-foreground">Wetterwarnungen konnten nicht geladen werden.</p>
          )}
          {!isError && aktiv === 0 && (
            <p className="text-muted-foreground">Derzeit liegen keine Wetterwarnungen vor.</p>
          )}
          <div className="space-y-3">
            {(warnungen ?? []).map((warnung: WetterWarnung) => (
              <Card key={warnung.id} className={severityBorderClass(warnung.severity)}>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-4">
                    {warnungIcon(warnung.event)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-lg">{warnung.headline}</span>
                        <Badge variant={severityBadgeVariant(warnung.severity)}>
                          {severityLabel(warnung.severity)}
                        </Badge>
                      </div>
                      <div className="text-sm space-y-1">
                        <div className="flex gap-2">
                          <span className="text-muted-foreground w-24">Ereignis:</span>
                          <span className="font-semibold">{warnung.event}</span>
                        </div>
                        {warnung.description && (
                          <div className="flex gap-2">
                            <span className="text-muted-foreground w-24">Details:</span>
                            <span>{warnung.description}</span>
                          </div>
                        )}
                        {warnung.instruction && (
                          <div className="flex gap-2">
                            <span className="text-muted-foreground w-24">Hinweis:</span>
                            <span>{warnung.instruction}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
