import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, BarChart3, Euro, FileText, ShoppingCart } from 'lucide-react'
import { useProcurementDashboard } from '@/lib/api/dashboard'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type ProcurementDashboardRoleFocus = 'all' | 'procurement' | 'goods-receipt' | 'finance' | 'supplier' | 'management'

const procurementDashboardRoleProfiles: Array<{ id: ProcurementDashboardRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt Einkaufslage fuer Einkauf, Wareneingang, Finance, Lieferantenmanagement und Leitung.' },
  { id: 'procurement', label: 'Einkauf', description: 'Fokus auf offene Bestellungen, Ueberfaelligkeit und Lieferantenklaerung.' },
  { id: 'goods-receipt', label: 'Wareneingang', description: 'Fokus auf ausstehende Lieferungen und Wareneingangsfolge.' },
  { id: 'finance', label: 'Finance', description: 'Fokus auf Einkaufsvolumen, offene Posten und Rechnungsfolge.' },
  { id: 'supplier', label: 'Lieferanten', description: 'Fokus auf aktive Lieferanten, Bewertung und Eskalationen.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, Volumen und naechste Aktion.' },
]

function DashboardSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Einkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Beschaffungs-Übersicht</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function EinkaufDashboardPage(): JSX.Element {
  const { data: dashboard, isLoading } = useProcurementDashboard()
  const [roleFocus, setRoleFocus] = useState<ProcurementDashboardRoleFocus>('all')

  if (isLoading) {
    return <DashboardSkeleton />
  }

  if (!dashboard) {
    return <DashboardSkeleton />
  }

  const hasOpenOrders = dashboard.bestellungenOffen > 0
  const hasOverdueOrders = dashboard.ueberfaellig > 0
  const hasProcurementVolume = dashboard.einkaufsvolumen > 0
  const hasActiveSuppliers = dashboard.lieferantenAktiv > 0
  const hasOpenPayables = dashboard.offenePosten > 0
  const procurementReady = !hasOverdueOrders && (hasOpenOrders || hasProcurementVolume || hasActiveSuppliers)
  const procurementNextAction = hasOverdueOrders
    ? `${dashboard.ueberfaellig} ueberfaellige Bestellung(en) klaeren.`
    : hasOpenOrders
      ? 'Offene Bestellungen pruefen und Wareneingang nachhalten.'
      : hasOpenPayables
        ? 'Offene Posten mit Rechnungseingang und Finance klaeren.'
        : hasActiveSuppliers
          ? 'Lieferantenlage pruefen und Bewertung nachhalten.'
          : 'Bestellung oder Lieferantenbezug anlegen.'
  const procurementTaskItems: UxTaskItem[] = [
    { label: 'Bestelllage pruefen', done: hasOpenOrders || dashboard.bestellungen.length > 0, hint: `${dashboard.bestellungenOffen} offene Bestellungen, ${dashboard.bestellungen.length} aktuelle Eintraege.` },
    { label: 'Ueberfaelligkeit klaeren', done: !hasOverdueOrders, hint: hasOverdueOrders ? `${dashboard.ueberfaellig} Bestellung(en) sind ueberfaellig.` : 'Keine ueberfaelligen Bestellungen.' },
    { label: 'Finance-Folge pruefen', done: hasProcurementVolume || hasOpenPayables, hint: `Volumen ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.einkaufsvolumen)}, offene Posten ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.offenePosten)}.` },
    { label: 'Lieferantenbasis sichern', done: hasActiveSuppliers, hint: hasActiveSuppliers ? `${dashboard.lieferantenAktiv} aktive Lieferanten.` : 'Keine aktiven Lieferanten im Dashboard.' },
  ]
  const procurementCrudCapabilities = [
    { key: 'read', label: 'Lesen', available: true, hint: 'Offene Bestellungen, Volumen, Lieferanten, offene Posten und aktuelle Bestellungen sind sichtbar.' },
    { key: 'follow-up', label: 'Bestellfolge', available: hasOpenOrders || dashboard.bestellungen.length > 0, hint: hasOpenOrders ? 'Offene Bestellungen koennen in der Bestellliste weitergefuehrt werden.' : 'Bestellfolge braucht offene oder aktuelle Bestellungen.' },
    { key: 'finance', label: 'Rechnungsfolge', available: hasOpenPayables || hasProcurementVolume, hint: 'Offene Posten und Einkaufsvolumen liefern den Finance-Nachweis.' },
    { key: 'supplier', label: 'Lieferantennachweis', available: hasActiveSuppliers, hint: hasActiveSuppliers ? 'Aktive Lieferanten koennen in Stamm und Bewertung geprueft werden.' : 'Lieferantennachweis braucht aktive Lieferanten.' },
    { key: 'evidence', label: 'Managementnachweis', available: procurementReady, hint: procurementReady ? 'Dashboarddaten sind als Managementsicht nutzbar.' : 'Ueberfaellige oder fehlende Daten muessen zuerst geklaert werden.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Dashboarddaten kommen aus dem bestehenden Procurement-API-Vertrag.' },
  ]

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Einkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Beschaffungs-Übersicht</p>
      </div>

      <div className="space-y-4">
        <RoleFocusBar roles={procurementDashboardRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
        <ManagementDecisionPanel
          decision={{
            allowed: procurementReady,
            allowedLabel: 'Arbeitsfaehig',
            blockedLabel: 'Stopper offen',
            summary: procurementReady ? `Einkaufsbild ist nutzbar: ${dashboard.bestellungenOffen} offene Bestellungen, ${dashboard.lieferantenAktiv} aktive Lieferanten.` : `Vor der Einkaufsentscheidung ist noch etwas offen: ${procurementNextAction}`,
            blockerCount: [hasOverdueOrders, !hasOpenOrders && !hasProcurementVolume && !hasActiveSuppliers].filter(Boolean).length,
            nextFocus: procurementNextAction,
            template: { label: 'Bestellungen oeffnen', href: '/einkauf/bestellungen' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Einkaufs-Prioritaetsplan" items={procurementTaskItems} />
          <div className="space-y-3">
            <NextActionPanel action={procurementNextAction} tone={procurementReady ? 'emerald' : hasOverdueOrders ? 'red' : hasOpenOrders ? 'amber' : 'blue'} />
            <EvidenceTemplateLink link={{ label: 'Rechnungseingaenge pruefen', href: '/einkauf/rechnungseingaenge-liste' }} />
            <EvidenceTemplateLink link={{ label: 'Lieferantenbewertung pruefen', href: '/einkauf/lieferantenbewertung' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={procurementCrudCapabilities} />
      </div>

      {dashboard.ueberfaellig > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{dashboard.ueberfaellig} Bestellung(en) überfällig!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bestellungen Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{dashboard.bestellungenOffen}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Einkaufsvolumen (Monat)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.einkaufsvolumen)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferanten Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              <span className="text-2xl font-bold">{dashboard.lieferantenAktiv}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.offenePosten)}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Aktuelle Bestellungen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboard.bestellungen.map((best, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{best.nummer}</div>
                  <div className="text-sm text-muted-foreground">{best.lieferant}</div>
                  <Badge variant="outline" className="mt-1">
                    {best.status === 'offen' ? 'Offen' : best.status === 'teilgeliefert' ? 'Teilgeliefert' : 'Komplett'}
                  </Badge>
                </div>
                <div className="text-xl font-bold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(best.betrag)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
