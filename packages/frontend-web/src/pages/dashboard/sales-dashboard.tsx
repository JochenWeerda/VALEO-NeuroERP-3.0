import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, Euro, FileText, TrendingUp, Users, AlertCircle } from 'lucide-react'
import { useSalesDashboard } from '@/lib/api/dashboard'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type SalesDashboardRoleFocus = 'all' | 'sales' | 'billing' | 'finance' | 'management'

const salesDashboardRoleProfiles: Array<{ id: SalesDashboardRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt Verkaufskennzahlen fuer Vertrieb, Faktura, Finance und Leitung.' },
  { id: 'sales', label: 'Vertrieb', description: 'Fokus auf Umsatz, aktive Kunden und Top-Kunden.' },
  { id: 'billing', label: 'Faktura', description: 'Fokus auf Auftragsvolumen und Rechnungsfolge.' },
  { id: 'finance', label: 'Finance', description: 'Fokus auf Umsatz, Durchschnittswert und OP-Folge.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Entscheidungslage, Prioritaet und naechste Aktion.' },
]

// Skeleton-Komponente für KPI-Karten
function KpiCardSkeleton({ title, icon: Icon }: { title: string; icon?: React.ElementType }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-5 w-5 text-muted-foreground/50" />}
          <Skeleton className="h-8 w-24" />
        </div>
      </CardContent>
    </Card>
  )
}

// Skeleton-Komponente für Top-Kunden Liste
function TopCustomersSkeleton() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Top-Kunden (Monat)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between rounded-lg border p-4">
              <div className="space-y-2">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-5 w-12" />
              </div>
              <Skeleton className="h-7 w-24" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// Dashboard-Skeleton für Ladevorgang und Vorschau
function DashboardSkeleton({ showMessage = false }: { showMessage?: boolean }) {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Verkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Aktuelle Kennzahlen</p>
      </div>

      {showMessage && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Keine Daten vorhanden</AlertTitle>
          <AlertDescription>
            Es sind noch keine Verkaufsdaten verfügbar. Sobald Aufträge und Rechnungen erstellt werden, erscheinen hier die Kennzahlen.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-5">
        <KpiCardSkeleton title="Umsatz Heute" />
        <KpiCardSkeleton title="Umsatz Monat" icon={Euro} />
        <KpiCardSkeleton title="Ø Auftragswert" icon={TrendingUp} />
        <KpiCardSkeleton title="Aufträge Gesamt" icon={FileText} />
        <KpiCardSkeleton title="Kunden Aktiv" icon={Users} />
      </div>

      <TopCustomersSkeleton />
    </div>
  )
}

export default function SalesDashboardPage(): JSX.Element {
  const { data: dashboard, isLoading } = useSalesDashboard()
  const [roleFocus, setRoleFocus] = useState<SalesDashboardRoleFocus>('all')
  
  // Während des Ladens zeigen wir eine Skeleton-Vorschau
  if (isLoading) {
    return <DashboardSkeleton />
  }
  
  // Wenn keine Daten vorhanden sind, zeigen wir eine Vorschau mit Hinweis
  if (!dashboard) {
    return <DashboardSkeleton showMessage />
  }
  const hasRevenue = dashboard.totalRevenue > 0
  const hasOrders = dashboard.totalOrders > 0
  const hasCustomers = dashboard.topCustomers.length > 0
  const dashboardReady = hasRevenue && hasOrders && hasCustomers
  const dashboardNextAction = !hasOrders
    ? 'Ersten Auftrag oder erste Rechnung erfassen.'
    : !hasRevenue
      ? 'Umsatzdaten pruefen oder Faktura nachziehen.'
      : !hasCustomers
        ? 'Kundenumsatz pruefen.'
        : 'Top-Kunden pruefen und offene Verkaufsfolge nachhalten.'
  const dashboardTaskItems: UxTaskItem[] = [
    { label: 'Umsatzlage pruefen', done: hasRevenue, hint: hasRevenue ? `Monatsumsatz ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.totalRevenue)}.` : 'Noch kein Umsatz im Dashboard.' },
    { label: 'Auftragsbasis pruefen', done: hasOrders, hint: hasOrders ? `${dashboard.totalOrders} Auftraege im Dashboard.` : 'Noch keine Auftraege sichtbar.' },
    { label: 'Kunden priorisieren', done: hasCustomers, hint: hasCustomers ? `${dashboard.topCustomers.length} aktive Top-Kunden.` : 'Keine Top-Kunden fuer Follow-up vorhanden.' },
    { label: 'Nachweis sichern', done: dashboardReady, hint: dashboardReady ? 'Dashboard kann als Managementsicht genutzt werden.' : 'Erst Auftrags-, Umsatz- und Kundendaten vervollstaendigen.' },
  ]
  const dashboardCrudCapabilities = [
    { key: 'read', label: 'Lesen', available: true, hint: 'Umsatz, Auftragswert, Auftragsanzahl und Top-Kunden sind sichtbar.' },
    { key: 'follow-up', label: 'Folgeaktionen', available: dashboardReady, hint: dashboardReady ? 'Verkaufsfolge kann aus Top-Kunden und Auftragslage abgeleitet werden.' : 'Folgeaktionen brauchen Verkaufsdaten.' },
    { key: 'evidence', label: 'Managementnachweis', available: dashboardReady, hint: dashboardReady ? 'Kennzahlen bilden den Managementnachweis.' : 'Nachweis entsteht mit belastbaren Verkaufsdaten.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Dashboarddaten kommen aus dem bestehenden Sales-API-Vertrag.' },
  ]

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Verkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Aktuelle Kennzahlen</p>
      </div>

      <div className="space-y-4">
        <RoleFocusBar roles={salesDashboardRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 4 : 1} totalCount={4} />
        <ManagementDecisionPanel
          decision={{
            allowed: dashboardReady,
            allowedLabel: 'Entscheidungsfaehig',
            blockedLabel: 'Datenbasis fehlt',
            summary: dashboardReady ? `Verkaufsbild ist belastbar: ${dashboard.totalOrders} Auftraege, ${dashboard.topCustomers.length} aktive Kunden.` : `Vor der Managemententscheidung ist noch etwas offen: ${dashboardNextAction}`,
            blockerCount: [!hasRevenue, !hasOrders, !hasCustomers].filter(Boolean).length,
            nextFocus: dashboardNextAction,
            template: { label: 'Auftragsliste oeffnen', href: '/sales/auftraege' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Verkaufs-Prioritaetsplan" items={dashboardTaskItems} />
          <div className="space-y-3">
            <NextActionPanel action={dashboardNextAction} tone={dashboardReady ? 'emerald' : hasOrders ? 'amber' : 'blue'} />
            <EvidenceTemplateLink link={{ label: 'Rechnungen pruefen', href: '/sales/rechnungen' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={dashboardCrudCapabilities} />
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umsatz Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.totalRevenue / 30)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umsatz Monat</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.totalRevenue)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Auftragswert</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold text-status-success">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.avgOrderValue)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufträge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              <span className="text-2xl font-bold">{dashboard.totalOrders}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-2xl font-bold">{dashboard.topCustomers.length}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Top-Kunden (Monat)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboard.topCustomers.map((kunde, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{kunde.name}</div>
                  <Badge variant="outline" className="mt-1">#{i + 1}</Badge>
                </div>
                <div className="text-xl font-bold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.revenue)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

