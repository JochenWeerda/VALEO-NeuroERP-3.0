/**
 * Kundenportal Dashboard
 * 
 * Übersichtsseite für Kunden mit wichtigen KPIs und Schnellzugriffen
 */

import { Link } from '@/app/routing/typed-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { usePortalDashboard, type PortalDashboard as PortalDashboardApi } from '@/lib/api/portal'
import { ErrorState } from '@/components/ErrorState'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import {
  ShoppingCart,
  Package,
  FileText,
  Receipt,
  Download,
  Leaf,
  TrendingUp,
  ChevronRight,
  Clock,
  CheckCircle2,
  Truck,
  Calculator,
  Wheat,
  Sparkles,
  Tractor,
} from 'lucide-react'

// Demo-Kunden-Nr; produktiv aus Auth-Context
const DEMO_KUNDEN_NR = 'K-10001'
// Demo Artikel-IDs basierend auf Schlagkartei-Kulturen
const DEMO_ARTIKEL_IDS = 'WEI-001,GER-001,RAP-001'


type PortalDashboardView = {
  kunde: {
    name: string
    kundennummer: string
  }
  kpis: {
    offeneBestellungen: number
    laufendeVertraege: number
    offeneRechnungen: number
    offenerBetrag: number
    verfuegbareDokumente: number
  }
  letzteBestellungen: Array<{
    id: string
    datum: string
    status: string
    betrag: number
    artikel: string
  }>
  neueDokumente: Array<{
    id: number
    name: string
    typ: string
    datum: string
  }>
  naechsteTermine: Array<{
    id: number
    titel: string
    datum: string
    zeit: string
  }>
}
const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'in_bearbeitung': { label: 'In Bearbeitung', color: 'bg-amber-100 text-amber-800', icon: <Clock className="h-3 w-3" /> },
  'versendet': { label: 'Versendet', color: 'bg-blue-100 text-blue-800', icon: <Truck className="h-3 w-3" /> },
  'abgeschlossen': { label: 'Abgeschlossen', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-3 w-3" /> },
}

function mapPortalDashboard(data: PortalDashboardApi): PortalDashboardView {
  const pickNumber = (label: string) => {
    const raw = data.kpis.find((k) => k.label.toLowerCase() === label.toLowerCase())?.value
    if (!raw) return 0
    const normalized = raw.replace(',', '.').replace(/[^\d.-]/g, '')
    const num = Number(normalized)
    return Number.isFinite(num) ? num : 0
  }

  return {
    kunde: {
      name: 'Portal-Kunde',
      kundennummer: 'PORTAL',
    },
    kpis: {
      offeneBestellungen: pickNumber('Offene Bestellungen'),
      laufendeVertraege: pickNumber('Vertragsstatus'),
      offeneRechnungen: pickNumber('Offene Rechnungen'),
      offenerBetrag: pickNumber('Letzte Rechnung'),
      verfuegbareDokumente: pickNumber('Neue Dokumente'),
    },
    letzteBestellungen: data.letzteBestellungen.map((b) => ({
      id: b.nummer || b.id,
      datum: b.datum,
      status: b.status === 'geliefert' ? 'abgeschlossen' : b.status === 'bestellt' ? 'in_bearbeitung' : b.status,
      betrag: b.betrag,
      artikel: 'Portal-Bestellung',
    })),
    neueDokumente: data.neueDokumente.map((d, idx) => ({
      id: idx + 1,
      name: d.name,
      typ: d.typ,
      datum: d.datum,
    })),
    naechsteTermine: [],
  }
}

// ─── Preisspiegel-Widget ──────────────────────────────────────────────────────

type PreisVariante = { gesamtpreis_eur_dt: number; ernte_jahr: number }
type ArtikelPreis = {
  artikel_id: string
  artikel_name: string
  frucht_gruppe: string
  varianten: Record<string, PreisVariante>
}
type PreisspiegalData = { preisspiegel: ArtikelPreis[]; stand: string }

function PreisspiegalWidget() {
  const { data, isLoading } = useQuery<PreisspiegalData>({
    queryKey: ['portal-preisspiegel-widget', DEMO_ARTIKEL_IDS],
    queryFn: async () => {
      const res = await apiClient.get<PreisspiegalData>(
        `/portal/preisspiegel/kunde?artikel_ids=${DEMO_ARTIKEL_IDS}`,
      )
      return res.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const VARIANTE_LABELS: Record<string, string> = {
    altware_ab_hof: 'Altware ab Hof',
    altware_frei_lager: 'Altware frei Lager',
    neue_ernte_frei_lager: 'Neue Ernte frei Lager',
    neue_ernte_ab_hof: 'Neue Ernte ab Hof',
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Aktuelle Getreidekurse
          </CardTitle>
          <CardDescription>
            Ankaufspreise für Ihre Ernte{data ? ` — Stand ${data.stand}` : ''}
          </CardDescription>
        </div>
        <Link to="/portal/preisspiegel">
          <Button variant="ghost" size="sm" className="gap-1 text-green-700">
            Alle Varianten <ChevronRight className="h-4 w-4" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        )}
        {data && (
          <div className="space-y-1">
            {/* Tabellenkopf */}
            <div className="grid grid-cols-5 gap-2 text-xs font-medium text-gray-500 px-2 pb-1 border-b">
              <span className="col-span-1">Frucht</span>
              {Object.values(VARIANTE_LABELS).map((l) => (
                <span key={l} className="text-right leading-tight">{l}</span>
              ))}
            </div>
            {/* Preiszeilen */}
            {data.preisspiegel.map((a) => (
              <div
                key={a.artikel_id}
                className="grid grid-cols-5 gap-2 items-center rounded-lg px-2 py-2 hover:bg-gray-50"
              >
                <div className="col-span-1">
                  <div className="font-medium text-sm text-gray-900">{a.artikel_name}</div>
                  <div className="text-xs text-gray-400">{a.frucht_gruppe}</div>
                </div>
                {Object.keys(VARIANTE_LABELS).map((v) => {
                  const p = a.varianten[v]
                  return (
                    <div key={v} className="text-right">
                      {p ? (
                        <span className="text-sm font-semibold text-gray-800">
                          {p.gesamtpreis_eur_dt.toFixed(2)}{' '}
                          <span className="text-xs font-normal text-gray-400">€/dt</span>
                        </span>
                      ) : (
                        <span className="text-xs text-gray-300">—</span>
                      )}
                    </div>
                  )
                })}
              </div>
            ))}
            {data.preisspiegel.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                Keine Preise für Ihre Früchte hinterlegt.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Empfehlungs-Banner ───────────────────────────────────────────────────────

type EmpfehlungZusammenfassung = { ungesehen: number; gesamt: number; nach_typ: Record<string, number> }

function EmpfehlungsBanner() {
  const { data } = useQuery<EmpfehlungZusammenfassung>({
    queryKey: ['portal-empfehlungen-badge', DEMO_KUNDEN_NR],
    queryFn: async () => {
      const res = await apiClient.get<EmpfehlungZusammenfassung>(
        `/portal/empfehlungen/${DEMO_KUNDEN_NR}/zusammenfassung`,
      )
      return res.data
    },
    staleTime: 2 * 60 * 1000,
  })

  if (!data || data.ungesehen === 0) return null

  // nach_typ kann bei Fehler-/Minimal-Antworten des Portals fehlen
  const ankauf = data.nach_typ?.['ankauf_kontrakt'] ?? 0
  const lohn = data.nach_typ?.['lohndienst'] ?? 0
  const rohware = data.nach_typ?.['rohware_angebot'] ?? 0

  return (
    <Link to="/portal/empfehlungen">
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 flex items-center justify-between gap-4 hover:bg-amber-100 transition-colors cursor-pointer">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-400">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-amber-900 flex items-center gap-2">
              {data.ungesehen} neue Empfehlung{data.ungesehen !== 1 ? 'en' : ''} für Sie
              <Badge className="bg-amber-500 text-white text-xs">{data.ungesehen} neu</Badge>
            </div>
            <div className="text-sm text-amber-700 flex gap-3 mt-0.5">
              {ankauf > 0 && <span>{ankauf} Ankaufsangebot{ankauf !== 1 ? 'e' : ''}</span>}
              {lohn > 0 && <span>{lohn} Lohndienstleistung{lohn !== 1 ? 'en' : ''}</span>}
              {rohware > 0 && <span>{rohware} Rohwaren-Angebot{rohware !== 1 ? 'e' : ''}</span>}
            </div>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-amber-600 shrink-0" />
      </div>
    </Link>
  )
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export default function PortalDashboard() {
  const { data: portalData, isLoading, isError, error, refetch } = usePortalDashboard()

  if (isLoading) {
    return <DashboardSkeleton />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  if (!portalData) {
    return <ErrorState error={new Error('Keine Dashboard-Daten verfuegbar.')} onRetry={() => { void refetch() }} />
  }

  const data = mapPortalDashboard(portalData)

  return (
    <div className="space-y-6">
      {/* Willkommens-Header */}
      <div className="rounded-2xl bg-linear-to-r from-emerald-600 to-emerald-800 p-6 text-white shadow-xl">
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
          <Link to="/portal/preisspiegel">
            <Button variant="outline" className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20">
              <TrendingUp className="h-4 w-4" />
              Getreidekurse
            </Button>
          </Link>
          <Link to="/portal/lohndienste">
            <Button variant="outline" className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20">
              <Tractor className="h-4 w-4" />
              Lohndienste buchen
            </Button>
          </Link>
        </div>
      </div>

      {/* Empfehlungs-Banner (nur wenn neue Empfehlungen vorhanden) */}
      <EmpfehlungsBanner />

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

      {/* Preisspiegel-Widget (volle Breite) */}
      <PreisspiegalWidget />

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
        <CardContent className="space-y-4">
          {/* Neue Agrar-Dienste */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Markt & Dienste</p>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <QuickAccessCard
                title="Getreidekurse"
                description="4 Preisvarianten je Frucht"
                icon={<TrendingUp className="h-6 w-6" />}
                link="/portal/preisspiegel"
                color="emerald"
              />
              <QuickAccessCard
                title="Empfehlungen"
                description="Angebote & Kontrakte für Sie"
                icon={<Sparkles className="h-6 w-6" />}
                link="/portal/empfehlungen"
                color="amber"
              />
              <QuickAccessCard
                title="Lohndienste buchen"
                description="Spritz, Mahl+Misch, TMR"
                icon={<Tractor className="h-6 w-6" />}
                link="/portal/lohndienste"
                color="blue"
              />
              <QuickAccessCard
                title="Rationsberechnung"
                description="Kostenoptimale Ration"
                icon={<Calculator className="h-6 w-6" />}
                link="/portal/rationsoptimierung"
                color="emerald"
              />
            </div>
          </div>
          {/* Feldbuch & Dokumente */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Flächen & Dokumente</p>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <QuickAccessCard
                title="Ackerschlagkartei"
                description="Feldbuch & Maßnahmen"
                icon={<Leaf className="h-6 w-6" />}
                link="/portal/feldbuch"
                color="emerald"
              />
              <QuickAccessCard
                title="Nährstoffbilanzen"
                description="Jahresübersichten"
                icon={<Wheat className="h-6 w-6" />}
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




