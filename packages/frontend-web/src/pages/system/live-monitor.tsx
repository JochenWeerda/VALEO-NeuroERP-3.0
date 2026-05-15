import { useMemo, useState } from 'react'
import { AlertTriangle, Boxes, FileText, ShieldAlert } from 'lucide-react'
import { useLive } from '@/state/live'
import NavLiveStatus from '@/components/app/NavLiveStatus'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  AuditTimeline,
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type LiveRole = 'betrieb' | 'admin' | 'fachbereich' | 'leitung'

const liveRoles = [
  {
    id: 'betrieb',
    label: 'Betrieb',
    description: 'Prueft, ob Live-Daten ankommen und ob ein Eingriff noetig ist.',
  },
  {
    id: 'admin',
    label: 'Admin',
    description: 'Nutzt Rohdaten und Statusmeldungen fuer technische Diagnose.',
  },
  {
    id: 'fachbereich',
    label: 'Fachbereich',
    description: 'Sieht, welche Vertriebs-, Bestands- oder Policy-Ereignisse zuletzt eingegangen sind.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Bewertet, ob kritische Live-Warnungen den Betrieb blockieren.',
  },
] satisfies Array<{ id: LiveRole; label: string; description: string }>

function formatDate(ts?: number): string {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('de-DE')
}

export default function LiveMonitorPage(): JSX.Element {
  const { sales, inventory, policy } = useLive()
  const [roleFocus, setRoleFocus] = useState<LiveRole>('betrieb')

  const salesDocs = useMemo(() => Object.values(sales), [sales])
  const inventoryEvents = useMemo(() => Object.values(inventory), [inventory])
  const criticalAlerts = policy.filter((alert) => alert.severity === 'crit')
  const warningAlerts = policy.filter((alert) => alert.severity === 'warn')
  const hasLiveData = salesDocs.length + inventoryEvents.length + policy.length > 0
  const liveReady = criticalAlerts.length === 0
  const nextLiveAction = criticalAlerts.length > 0
    ? `${criticalAlerts.length} kritische Policy-Warnung(en) pruefen und fachlichen Owner zuordnen.`
    : !hasLiveData
      ? 'Auf neue Live-Ereignisse warten oder SSE-Verbindung im Navigationsstatus pruefen.'
      : warningAlerts.length > 0
        ? `${warningAlerts.length} Warnung(en) fachlich bewerten und bei Bedarf eskalieren.`
        : 'Live-Lage ist unauffaellig. Rohdaten nur bei Rueckfragen pruefen.'

  const timelineEntries = [
    ...salesDocs.slice(0, 2).map((doc) => ({
      label: `Vertrieb ${doc.number}`,
      detail: `Status ${doc.status}, aktualisiert ${formatDate(doc.updatedAt)}`,
      tone: 'blue' as const,
    })),
    ...inventoryEvents.slice(0, 2).map((event) => ({
      label: `Bestand ${event.sku}`,
      detail: `Aenderung ${event.delta}, neuer Bestand ${event.qty}, ${formatDate(event.ts)}`,
      tone: event.delta < 0 ? 'amber' as const : 'emerald' as const,
    })),
    ...policy.slice(0, 2).map((alert) => ({
      label: alert.title,
      detail: `${alert.message} (${formatDate(alert.ts)})`,
      tone: alert.severity === 'crit' ? 'red' as const : 'amber' as const,
    })),
  ]

  return (
    <div className="container space-y-6 py-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Live-Betriebsmonitor</h1>
          <p className="text-sm text-muted-foreground">
            Aktuelle Vertriebs-, Bestands- und Policy-Ereignisse in verstaendlicher Betriebssprache.
          </p>
        </div>
        <NavLiveStatus />
      </div>

      <RoleFocusBar
        roles={liveRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={salesDocs.length + inventoryEvents.length + policy.length}
        totalCount={salesDocs.length + inventoryEvents.length + policy.length}
        title="Arbeitsrolle fuer Live-Monitoring"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: liveReady,
          allowedLabel: 'Keine kritische Warnung',
          blockedLabel: 'Kritisch pruefen',
          summary: liveReady
            ? 'Es liegen keine kritischen Policy-Warnungen vor. Die Live-Daten koennen normal beobachtet und bei Rueckfragen diagnostiziert werden.'
            : 'Kritische Policy-Warnungen muessen vor einem normalen Weiterbetrieb fachlich bewertet und einem Owner zugeordnet werden.',
          blockerCount: criticalAlerts.length,
          nextFocus: nextLiveAction,
          template: {
            label: 'Live-Monitor-Betriebsnachweis',
            href: '/docs/system/live-monitor-betriebsnachweis.md',
          },
        }}
      />

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Vertriebsereignisse</CardTitle></CardHeader>
          <CardContent className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-700" />
            <span className="text-2xl font-bold">{salesDocs.length}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Bestandsereignisse</CardTitle></CardHeader>
          <CardContent className="flex items-center gap-2">
            <Boxes className="h-5 w-5 text-emerald-700" />
            <span className="text-2xl font-bold">{inventoryEvents.length}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Warnungen</CardTitle></CardHeader>
          <CardContent className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-700" />
            <span className="text-2xl font-bold text-amber-700">{warningAlerts.length}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Kritisch</CardTitle></CardHeader>
          <CardContent className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-red-700" />
            <span className="text-2xl font-bold text-red-700">{criticalAlerts.length}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Live-Betriebsplan"
          items={[
            { label: 'Live-Daten beobachten', done: hasLiveData, hint: hasLiveData ? 'Mindestens ein Live-Ereignis ist vorhanden.' : 'Noch keine Live-Ereignisse im lokalen Store.' },
            { label: 'Kritische Warnungen klaeren', done: criticalAlerts.length === 0, hint: criticalAlerts.length > 0 ? `${criticalAlerts.length} kritische Warnung(en) offen.` : 'Keine kritischen Warnungen.' },
            { label: 'Bestandsaenderungen pruefen', done: inventoryEvents.length > 0, hint: inventoryEvents.length > 0 ? 'Bestandsereignisse sind sichtbar.' : 'Noch kein Bestandssignal eingegangen.' },
            { label: 'Diagnose nachvollziehen', done: true, hint: 'Rohdaten bleiben unten fuer Admins und Support verfuegbar.' },
          ]}
        />
        <NextActionPanel action={nextLiveAction} tone={liveReady ? (hasLiveData ? 'emerald' : 'blue') : 'red'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{ label: 'Live-Status-Pruefprotokoll', href: '/docs/system/live-status-pruefprotokoll.md' }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'read', label: 'Live-Daten lesen', available: true, hint: 'Sales, Bestand und Policy werden aus dem Live-Store gelesen.' },
              { key: 'audit', label: 'Ereignisse nachvollziehen', available: timelineEntries.length > 0, hint: 'Die letzten Ereignisse werden als Zeitleiste verdichtet.' },
              { key: 'export', label: 'Diagnose sichern', available: true, hint: 'Rohdaten koennen aus dem Diagnosebereich nachvollzogen werden.' },
              { key: 'reject', label: 'Stopper klaeren', available: criticalAlerts.length > 0, hint: 'Kritische Policy-Warnungen blockieren den Normalbetrieb.' },
            ]}
          />
        </div>
      </div>

      <AuditTimeline title="Letzte Live-Ereignisse" entries={timelineEntries} />

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Vertrieb</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {salesDocs.slice(0, 5).map((doc) => (
              <div key={doc.id} className="rounded border p-3 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{doc.number}</span>
                  <Badge variant="outline">{doc.status}</Badge>
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {doc.total != null ? `Wert ${doc.total}` : 'Kein Wert uebermittelt'} - {formatDate(doc.updatedAt)}
                </div>
              </div>
            ))}
            {salesDocs.length === 0 ? <p className="text-sm text-muted-foreground">Noch keine Vertriebsereignisse.</p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Bestand</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {inventoryEvents.slice(0, 5).map((event) => (
              <div key={event.sku} className="rounded border p-3 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{event.sku}</span>
                  <Badge variant={event.delta < 0 ? 'secondary' : 'outline'}>{event.delta}</Badge>
                </div>
                <div className="mt-1 text-xs text-muted-foreground">Bestand {event.qty} - {formatDate(event.ts)}</div>
              </div>
            ))}
            {inventoryEvents.length === 0 ? <p className="text-sm text-muted-foreground">Noch keine Bestandsereignisse.</p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Policy-Warnungen</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {policy.slice(0, 5).map((alert) => (
              <div key={alert.id} className="rounded border p-3 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{alert.title}</span>
                  <Badge variant={alert.severity === 'crit' ? 'destructive' : 'secondary'}>
                    {alert.severity === 'crit' ? 'Kritisch' : 'Warnung'}
                  </Badge>
                </div>
                <div className="mt-1 text-xs text-muted-foreground">{alert.message} - {formatDate(alert.ts)}</div>
              </div>
            ))}
            {policy.length === 0 ? <p className="text-sm text-muted-foreground">Keine Policy-Warnungen.</p> : null}
          </CardContent>
        </Card>
      </div>

      <details className="rounded border bg-white p-4">
        <summary className="cursor-pointer text-sm font-semibold">Technische Rohdaten fuer Diagnose</summary>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <section>
            <h2 className="font-semibold">Sales Documents</h2>
            <pre className="mt-2 overflow-auto rounded-md bg-zinc-950 p-3 text-xs text-zinc-100">{JSON.stringify(sales, null, 2)}</pre>
          </section>
          <section>
            <h2 className="font-semibold">Inventory Events</h2>
            <pre className="mt-2 overflow-auto rounded-md bg-zinc-950 p-3 text-xs text-zinc-100">{JSON.stringify(inventory, null, 2)}</pre>
          </section>
          <section>
            <h2 className="font-semibold">Policy Alerts</h2>
            <pre className="mt-2 overflow-auto rounded-md bg-zinc-950 p-3 text-xs text-zinc-100">{JSON.stringify(policy, null, 2)}</pre>
          </section>
        </div>
      </details>
    </div>
  )
}
