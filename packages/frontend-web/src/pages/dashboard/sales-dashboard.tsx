import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, Euro, FileText, TrendingUp, Users, AlertCircle } from 'lucide-react'
import { useSalesDashboard } from '@/lib/api/dashboard'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

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
  
  // Während des Ladens zeigen wir eine Skeleton-Vorschau
  if (isLoading) {
    return <DashboardSkeleton />
  }
  
  // Wenn keine Daten vorhanden sind, zeigen wir eine Vorschau mit Hinweis
  if (!dashboard) {
    return <DashboardSkeleton showMessage />
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Verkaufs-Dashboard</h1>
        <p className="text-muted-foreground">Aktuelle Kennzahlen</p>
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
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
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
