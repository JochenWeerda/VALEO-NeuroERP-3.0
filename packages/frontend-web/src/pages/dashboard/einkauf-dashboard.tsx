import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, BarChart3, Euro, FileText, ShoppingCart } from 'lucide-react'
import { useProcurementDashboard } from '@/lib/api/dashboard'

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

  if (isLoading) {
    return <DashboardSkeleton />
  }

  if (!dashboard) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Einkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Beschaffungs-Übersicht</p>
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
