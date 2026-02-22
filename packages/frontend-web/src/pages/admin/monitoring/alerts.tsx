import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useMonitoringAlerts } from '@/lib/api/admin'
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'

export default function MonitoringAlertsPage(): JSX.Element {
  const { data, isLoading } = useMonitoringAlerts()
  const alerts = data?.items ?? []
  const active = data?.active ?? 0
  const critical = data?.critical ?? 0
  const warning = data?.warning ?? 0
  const systemStatus = data?.system_status ?? 'online'

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-[360px]" />
      </div>
    )
  }

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
              <span className="text-2xl font-bold">{active}</span>
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
              <span className="text-2xl font-bold text-red-600">{critical}</span>
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
              <span className="text-2xl font-bold text-orange-600">{warning}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System-Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {systemStatus === 'offline' ? (
                <XCircle className="h-5 w-5 text-red-600" />
              ) : systemStatus === 'degraded' ? (
                <AlertTriangle className="h-5 w-5 text-orange-600" />
              ) : (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
              <Badge
                variant="outline"
                className={
                  systemStatus === 'offline'
                    ? 'text-red-600'
                    : systemStatus === 'degraded'
                      ? 'text-orange-600'
                      : 'text-green-600'
                }
              >
                {systemStatus === 'offline' ? 'Offline' : systemStatus === 'degraded' ? 'Eingeschraenkt' : 'Online'}
              </Badge>
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
            {alerts.map((alert) => (
              <Card
                key={alert.id}
                className={
                  alert.level === 'critical'
                    ? 'border-red-500'
                    : alert.level === 'warning'
                      ? 'border-orange-500'
                      : 'border-blue-500'
                }
              >
                <CardContent className="pt-4">
                  <div className="flex items-start gap-4">
                    {alert.level === 'critical' ? (
                      <XCircle className="h-8 w-8 text-red-600" />
                    ) : alert.level === 'warning' ? (
                      <AlertTriangle className="h-8 w-8 text-orange-600" />
                    ) : (
                      <Info className="h-8 w-8 text-blue-600" />
                    )}
                    <div className="flex-1">
                      <div className="mb-2 flex items-center gap-2">
                        <span className="text-lg font-semibold">{alert.type}</span>
                        <Badge variant={alert.level === 'critical' ? 'destructive' : alert.level === 'warning' ? 'secondary' : 'outline'}>
                          {alert.level === 'critical' ? 'Kritisch' : alert.level === 'warning' ? 'Warnung' : 'Info'}
                        </Badge>
                      </div>
                      <p className="mb-2 text-sm text-muted-foreground">{alert.message}</p>
                      <div className="font-mono text-xs text-muted-foreground">{alert.timestamp}</div>
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
