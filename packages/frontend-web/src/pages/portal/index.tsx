/**
 * Kundenportal Dashboard
 * 
 * Übersichtsseite für Kunden mit wichtigen KPIs und Schnellzugriffen
 */

import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useState, useEffect } from 'react'
import {
  ShoppingCart,
  Package,
  FileText,
  Receipt,
  Download,
  Leaf,
  TrendingUp,
  Calendar,
  Bell,
  ChevronRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  Euro,
  Truck,
} from 'lucide-react'

// Mock-Daten - werden später durch echte API-Calls ersetzt
const mockDashboardData = {
  kunde: {
    name: 'Musterhof GmbH',
    kundennummer: 'K-2024-001',
  },
  kpis: {
    offeneBestellungen: 3,
    laufendeVertraege: 5,
    offeneRechnungen: 2,
    offenerBetrag: 4523.50,
    verfuegbareDokumente: 12,
  },
  letzteBestellungen: [
    { id: 'B-2024-0147', datum: '2024-11-25', status: 'in_bearbeitung', betrag: 1250.00, artikel: 'Winterweizen Saatgut' },
    { id: 'B-2024-0142', datum: '2024-11-20', status: 'versendet', betrag: 890.00, artikel: 'NPK Dünger' },
    { id: 'B-2024-0138', datum: '2024-11-15', status: 'abgeschlossen', betrag: 2100.00, artikel: 'Pflanzenschutzmittel' },
  ],
  neueDokumente: [
    { id: 1, name: 'Nährstoffbilanz 2024.pdf', typ: 'naehrstoff', datum: '2024-11-20' },
    { id: 2, name: 'GMP Zertifikat 2024.pdf', typ: 'zertifikat', datum: '2024-11-15' },
    { id: 3, name: 'Rechnung R-2024-0567.pdf', typ: 'rechnung', datum: '2024-11-10' },
  ],
  naechsteTermine: [
    { id: 1, titel: 'Düngerlieferung', datum: '2024-11-28', zeit: '08:00' },
    { id: 2, titel: 'PSM-Beratung', datum: '2024-11-30', zeit: '10:00' },
  ],
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'in_bearbeitung': { label: 'In Bearbeitung', color: 'bg-amber-100 text-amber-800', icon: <Clock className="h-3 w-3" /> },
  'versendet': { label: 'Versendet', color: 'bg-blue-100 text-blue-800', icon: <Truck className="h-3 w-3" /> },
  'abgeschlossen': { label: 'Abgeschlossen', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-3 w-3" /> },
}

export default function PortalDashboard() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<typeof mockDashboardData | null>(null)

  useEffect(() => {
    // Simuliere API-Call
    const timer = setTimeout(() => {
      setData(mockDashboardData)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return <DashboardSkeleton />
  }

  if (!data) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground">Keine Daten verfügbar</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Willkommens-Header */}
      <div className="rounded-2xl bg-gradient-to-r from-emerald-600 to-emerald-800 p-6 text-white shadow-xl">
        <h1 className="text-2xl font-bold">Willkommen, {data.kunde.name}!</h1>
        <p className="mt-1 text-emerald-100">Kundennummer: {data.kunde.kundennummer}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link to="/portal/shop">
            <Button variant="secondary" className="h-auto gap-2 py-2">
              <ShoppingCart className="h-5 w-5" />
              <div className="text-left">
                <div className="font-semibold">Bestellportal</div>
                <div className="text-xs font-normal opacity-80">Futter- und Betriebsmittel bestellen</div>
              </div>
            </Button>
          </Link>
          <Link to="/portal/anfragen">
            <Button variant="outline" className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20">
              <FileText className="h-4 w-4" />
              Anfrage stellen
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Offene Bestellungen"
          value={data.kpis.offeneBestellungen}
          icon={<Package className="h-5 w-5" />}
          link="/portal/bestellungen"
          color="blue"
        />
        <KPICard
          title="Laufende Verträge"
          value={data.kpis.laufendeVertraege}
          icon={<FileText className="h-5 w-5" />}
          link="/portal/vertraege"
          color="emerald"
        />
        <KPICard
          title="Offene Rechnungen"
          value={data.kpis.offeneRechnungen}
          icon={<Receipt className="h-5 w-5" />}
          link="/portal/rechnungen"
          suffix={`€ ${data.kpis.offenerBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
          color="amber"
        />
        <KPICard
          title="Neue Dokumente"
          value={data.kpis.verfuegbareDokumente}
          icon={<Download className="h-5 w-5" />}
          link="/portal/dokumente"
          color="purple"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Letzte Bestellungen */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg">Letzte Bestellungen</CardTitle>
              <CardDescription>Ihre aktuellen Bestellungen</CardDescription>
            </div>
            <Link to="/portal/bestellungen">
              <Button variant="ghost" size="sm" className="gap-1">
                Alle <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.letzteBestellungen.map((bestellung) => {
                const status = statusConfig[bestellung.status]
                return (
                  <div
                    key={bestellung.id}
                    className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{bestellung.id}</span>
                        <Badge className={`${status.color} gap-1`}>
                          {status.icon}
                          {status.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{bestellung.artikel}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">€ {bestellung.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</p>
                      <p className="text-xs text-muted-foreground">{bestellung.datum}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Neue Dokumente */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg">Neue Dokumente</CardTitle>
              <CardDescription>Kürzlich bereitgestellt</CardDescription>
            </div>
            <Link to="/portal/dokumente">
              <Button variant="ghost" size="sm" className="gap-1">
                Alle <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.neueDokumente.map((dokument) => (
                <div
                  key={dokument.id}
                  className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                      <Download className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-medium">{dokument.name}</p>
                      <p className="text-xs text-muted-foreground">{dokument.datum}</p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schnellzugriff */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Schnellzugriff</CardTitle>
          <CardDescription>Häufig verwendete Funktionen</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <QuickAccessCard
              title="Ackerschlagkartei"
              description="Feldbuch einsehen"
              icon={<Leaf className="h-6 w-6" />}
              link="/portal/feldbuch"
              color="emerald"
            />
            <QuickAccessCard
              title="Nährstoffbilanzen"
              description="Jahresübersichten"
              icon={<TrendingUp className="h-6 w-6" />}
              link="/portal/naehrstoffbilanzen"
              color="blue"
            />
            <QuickAccessCard
              title="Zertifikate"
              description="GMP, VLOG, QS..."
              icon={<FileText className="h-6 w-6" />}
              link="/portal/zertifikate"
              color="amber"
            />
            <QuickAccessCard
              title="CSV Export"
              description="Daten exportieren"
              icon={<Download className="h-6 w-6" />}
              link="/portal/feldbuch?tab=export"
              color="purple"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function KPICard({
  title,
  value,
  icon,
  link,
  suffix,
  color = 'blue',
}: {
  title: string
  value: number | string
  icon: React.ReactNode
  link: string
  suffix?: string
  color?: 'blue' | 'emerald' | 'amber' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <Link to={link}>
      <Card className="transition-all hover:shadow-md hover:-translate-y-0.5">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className={`rounded-lg p-2 ${colorClasses[color]}`}>
              {icon}
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-sm text-muted-foreground">{title}</p>
            {suffix && <p className="text-xs text-muted-foreground">{suffix}</p>}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

function QuickAccessCard({
  title,
  description,
  icon,
  link,
  color = 'blue',
}: {
  title: string
  description: string
  icon: React.ReactNode
  link: string
  color?: 'emerald' | 'blue' | 'amber' | 'purple'
}) {
  const colorClasses = {
    emerald: 'bg-emerald-100 text-emerald-700 group-hover:bg-emerald-200',
    blue: 'bg-blue-100 text-blue-700 group-hover:bg-blue-200',
    amber: 'bg-amber-100 text-amber-700 group-hover:bg-amber-200',
    purple: 'bg-purple-100 text-purple-700 group-hover:bg-purple-200',
  }

  return (
    <Link to={link} className="group">
      <div className="flex items-center gap-3 rounded-xl border p-4 transition-all hover:shadow-md hover:border-primary/20">
        <div className={`rounded-lg p-3 transition-colors ${colorClasses[color]}`}>
          {icon}
        </div>
        <div>
          <p className="font-medium">{title}</p>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </Link>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <Skeleton className="h-40 w-full rounded-2xl" />

      {/* KPI Cards Skeleton */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <Skeleton className="mt-3 h-8 w-16" />
              <Skeleton className="mt-1 h-4 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Content Skeleton */}
      <div className="grid gap-6 lg:grid-cols-2">
        {[...Array(2)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent className="space-y-3">
              {[...Array(3)].map((_, j) => (
                <Skeleton key={j} className="h-16 w-full rounded-lg" />
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

