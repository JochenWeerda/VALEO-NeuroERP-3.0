import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AuditTimeline,
  EmptyStateWithAction,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import { useMonitoringAlerts } from '@/lib/api/admin'
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'

type MonitoringRole = 'betrieb' | 'admin' | 'security' | 'leitung'

const monitoringRoles = [
  {
    id: 'betrieb',
    label: 'Betrieb',
    description: 'Aktive Alerts pruefen und den naechsten technischen Schritt anstossen.',
  },
  {
    id: 'admin',
    label: 'Admin',
    description: 'Systemstatus, Regeln und Alarmkanaele fuer den Betrieb nachhalten.',
  },
  {
    id: 'security',
    label: 'Security',
    description: 'Kritische Ereignisse auf Risiko, Eskalation und Nachweis pruefen.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Betriebsfaehigkeit, Stopper und Eskalationslage verdichtet bewerten.',
  },
] satisfies Array<{ id: MonitoringRole; label: string; description: string }>

export default function MonitoringAlertsPage(): JSX.Element {
  const [roleFocus, setRoleFocus] = useState<MonitoringRole>('betrieb')
  const { data, isLoading } = useMonitoringAlerts()
  const alerts = data?.items ?? []
  const active = data?.active ?? 0
  const critical = data?.critical ?? 0
  const warning = data?.warning ?? 0
  const systemStatus = data?.system_status ?? 'online'
  const isHealthy = active === 0 && critical === 0 && systemStatus === 'online'
  const monitoringAction =
    critical > 0
      ? 'Kritische Alerts sofort einem Owner zuordnen und Eskalationsnachweis erstellen.'
      : systemStatus !== 'online'
        ? 'Systemstatus pruefen, Stoerungsursache dokumentieren und Wiederherstellung nachhalten.'
        : warning > 0
          ? 'Warnungen pruefen und entscheiden, ob daraus ein Incident oder eine Regelanpassung wird.'
          : 'Keine aktiven Alerts. Regelwerk und Kanaele im naechsten Wartungsfenster pruefen.'

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
        <p className="text-muted-foreground">Betriebsstatus, Eskalation und Nachweise fuer Admins.</p>
      </div>

      <RoleFocusBar
        roles={monitoringRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={alerts.length}
        totalCount={alerts.length}
        title="Arbeitsrolle fuer Monitoring"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: isHealthy,
          allowedLabel: 'Betrieb stabil',
          blockedLabel: 'Betrieb pruefen',
          summary: isHealthy
            ? 'Es liegen keine aktiven Alerts vor und der Systemstatus ist online. Die Umgebung kann normal weiterbetrieben werden.'
            : 'Aktive Alerts oder ein eingeschraenkter Systemstatus brauchen eine nachvollziehbare Bearbeitung mit Owner, Massnahme und Eskalationsnachweis.',
          blockerCount: isHealthy ? 0 : active + (systemStatus === 'online' ? 0 : 1),
          nextFocus: monitoringAction,
          template: {
            label: 'Incident- und Alert-Nachweis',
            href: '/docs/monitoring/incident-alert-nachweis.md',
          },
        }}
      />

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

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Betriebsplan"
          items={[
            {
              label: 'Systemstatus pruefen',
              done: systemStatus === 'online',
              hint: systemStatus === 'online' ? 'System meldet online.' : 'Systemstatus ist nicht online und braucht technische Klaerung.',
            },
            {
              label: 'Kritische Alerts bearbeiten',
              done: critical === 0,
              hint: critical > 0 ? `${critical} kritische Alert(s) sofort eskalieren.` : 'Keine kritischen Alerts aktiv.',
            },
            {
              label: 'Warnungen bewerten',
              done: warning === 0,
              hint: warning > 0 ? `${warning} Warnung(en) auf Ursache und Regelwirkung pruefen.` : 'Keine Warnungen aktiv.',
            },
            {
              label: 'Nachweis sichern',
              done: alerts.length === 0,
              hint: alerts.length > 0 ? 'Aktive Alerts brauchen Owner, Massnahme und Abschlussnotiz.' : 'Kein Incident-Nachweis erforderlich.',
            },
          ]}
        />
        <NextActionPanel action={monitoringAction} tone={isHealthy ? 'emerald' : critical > 0 ? 'red' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{
              label: 'Monitoring-Eskalationsprotokoll',
              href: '/docs/monitoring/monitoring-escalation.md',
            }}
          />
          <AuditTimeline
            title="Letzte Alert-Signale"
            entries={alerts.slice(0, 3).map((alert) => ({
              label: alert.type,
              detail: `${alert.timestamp} - ${alert.message}`,
              tone: alert.level === 'critical' ? 'red' : alert.level === 'warning' ? 'amber' : 'blue',
            }))}
          />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Aktive Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          {alerts.length > 0 ? (
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
          ) : (
            <EmptyStateWithAction
              title="Keine aktiven Alerts"
              description="Der Betrieb ist aktuell unauffaellig. Pruefe bei Bedarf die Monitoring-Regeln oder die Alarmkanaele."
              actionLabel="Regeln pruefen"
              onAction={() => { window.location.href = '/admin/monitoring/regeln' }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
