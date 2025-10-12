import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'

export default function MonitoringAlertsPage(): JSX.Element {
  const alerts = {
    aktiv: 3,
    liste: [
      { id: '1', stufe: 'critical', typ: 'Lagerbestand kritisch', nachricht: 'Weizen Premium unter Mindestbestand (120t < 200t)', timestamp: '2025-10-11 14:32' },
      { id: '2', stufe: 'warning', typ: 'Inspektion fällig', nachricht: 'Fahrzeug AB-LH 103 - Inspektion in 9 Tagen', timestamp: '2025-10-11 08:15' },
      { id: '3', stufe: 'info', typ: 'Wetter-Warnung', nachricht: 'DWD: Starkregen ab morgen 18:00 Uhr', timestamp: '2025-10-11 06:00' },
    ],
  }

  const kritisch = alerts.liste.filter((a) => a.stufe === 'critical').length
  const warnung = alerts.liste.filter((a) => a.stufe === 'warning').length

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">System-Alerts</h1>
        <p className="text-muted-foreground">Monitoring & Benachrichtigungen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{alerts.aktiv}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kritisch</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-600" />
              <span className="text-2xl font-bold text-red-600">{kritisch}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Warnungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{warnung}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System-Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <Badge variant="outline" className="text-green-600">Online</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Aktive Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.liste.map((alert) => (
              <Card key={alert.id} className={alert.stufe === 'critical' ? 'border-red-500' : alert.stufe === 'warning' ? 'border-orange-500' : 'border-blue-500'}>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-4">
                    {alert.stufe === 'critical' ? (
                      <XCircle className="h-8 w-8 text-red-600" />
                    ) : alert.stufe === 'warning' ? (
                      <AlertTriangle className="h-8 w-8 text-orange-600" />
                    ) : (
                      <Info className="h-8 w-8 text-blue-600" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-lg">{alert.typ}</span>
                        <Badge variant={alert.stufe === 'critical' ? 'destructive' : alert.stufe === 'warning' ? 'secondary' : 'outline'}>
                          {alert.stufe === 'critical' ? 'Kritisch' : alert.stufe === 'warning' ? 'Warnung' : 'Info'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{alert.nachricht}</p>
                      <div className="text-xs text-muted-foreground font-mono">{alert.timestamp}</div>
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
