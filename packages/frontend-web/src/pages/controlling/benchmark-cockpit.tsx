import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useBenchmark, useBenchmarkReadModel } from '@/lib/api/controlling'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart3,
  Loader2,
  AlertTriangle,
  CircleCheck,
  ArrowRight,
} from 'lucide-react'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'

const KPI_LABELS: Record<string, string> = {
  revenue: 'Umsatz',
  orders: 'Auftraege',
  customers: 'Aktive Kunden',
  conversion_rate: 'Konversionsrate',
  avg_order_value: 'Durchschn. Auftragswert',
  revenue_per_customer: 'Umsatz pro Kunde',
}

function formatValue(key: string, val: number): string {
  if (key === 'conversion_rate') return `${val.toFixed(1)} %`
  if (key.includes('revenue') || key.includes('value')) {
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(val)
  }
  return val.toLocaleString('de-DE')
}

function toCategoryLabel(value: string): string {
  return value.charAt(0) + value.slice(1).toLowerCase()
}

function actionFromDelta(delta: number | null): string {
  if (delta == null) return 'Keine belastbare Branchenabweichung verfuegbar.'
  if (delta <= -15) return 'Sofort pruefen: deutliche Unterdeckung gegen Branche.'
  if (delta < 0) return 'Gezielt nachsteuern und Ursachen auf Positionsebene pruefen.'
  if (delta >= 15) return 'Vorsprung sichern und als Best-Practice in andere Bereiche uebertragen.'
  return 'Im Zielkorridor beobachten und stabil halten.'
}

export default function BenchmarkCockpitPage(): JSX.Element {
  const [period, setPeriod] = useState<'month' | 'quarter' | 'year'>('month')

  const { start_date, end_date } = useMemo(() => {
    const end = new Date()
    end.setHours(0, 0, 0, 0)
    const start = new Date(end)
    if (period === 'month') start.setMonth(start.getMonth() - 1)
    else if (period === 'quarter') start.setMonth(start.getMonth() - 3)
    else start.setFullYear(start.getFullYear() - 1)
    return {
      start_date: start.toISOString().slice(0, 10),
      end_date: end.toISOString().slice(0, 10),
    }
  }, [period])

  const { data, isLoading, isError, error } = useBenchmark(start_date, end_date)
  const { data: readModel, isLoading: readModelLoading } = useBenchmarkReadModel()

  const comparisonEntries = useMemo(() => {
    if (!data?.comparison) return []
    return Object.entries(data.comparison).filter(([key]) => Object.keys(KPI_LABELS).includes(key))
  }, [data])

  const sortedByDelta = useMemo(
    () =>
      [...comparisonEntries].sort(
        (a, b) => ((b[1].deviation_pct ?? Number.NEGATIVE_INFINITY) - (a[1].deviation_pct ?? Number.NEGATIVE_INFINITY)),
      ),
    [comparisonEntries],
  )

  const strongest = sortedByDelta.slice(0, 2)
  const weakest = [...sortedByDelta].reverse().slice(0, 2)

  const negativeCount = comparisonEntries.filter(([, value]) => (value.deviation_pct ?? 0) < 0).length
  const positiveCount = comparisonEntries.filter(([, value]) => (value.deviation_pct ?? 0) > 0).length
  const averageDelta = comparisonEntries.length > 0
    ? Math.round(
      (comparisonEntries.reduce((sum, [, value]) => sum + (value.deviation_pct ?? 0), 0) / comparisonEntries.length) * 10,
    ) / 10
    : null

  const managementStatus =
    averageDelta == null
      ? { label: 'Noch keine Management-Wertung', tone: 'secondary' as const, text: 'Es fehlen genug Vergleichsdaten fuer eine belastbare Einordnung.' }
      : averageDelta >= 5
        ? { label: 'Ueber Branche', tone: 'default' as const, text: 'Die Gesamtlage liegt ueber dem Referenzkorridor. Fokus auf Skalierung und Absicherung.' }
        : averageDelta >= -5
          ? { label: 'Im Korridor', tone: 'outline' as const, text: 'Die Werte liegen nahe am Branchenbild. Fokus auf Ausreisser und stabile Umsetzung.' }
          : { label: 'Aufholbedarf', tone: 'destructive' as const, text: 'Mehrere KPI liegen unter Referenz. Fokus auf Priorisierung, Ursachenanalyse und Gegenmassnahmen.' }

  if (isError) {
    return (
      <PageSurface data-page-surface="benchmark-cockpit-error" contentClassName="space-y-6">
        <PageSection title="Branchenbenchmark" description="Vergleich eigener Kennzahlen mit dem Branchenbild im aktualisierten Designsystem.">
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <p className="text-sm text-destructive">
                {error instanceof Error ? error.message : 'Fehler beim Laden des Benchmarks'}
              </p>
            </CardContent>
          </Card>
        </PageSection>
      </PageSurface>
    )
  }

  return (
    <PageSurface data-page-surface="benchmark-cockpit" contentClassName="space-y-6">
      <PageSection
        title="Branchenbenchmark"
        description="Management-Sicht fuer Abweichungen, Stärken, Schwächen und priorisierte Folgeaktionen."
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-semibold">
              <BarChart3 className="h-6 w-6" />
              Branchenbenchmark
            </h1>
            <p className="mt-1 max-w-3xl text-muted-foreground">
              Die Seite zeigt nicht nur KPI-Abweichungen, sondern auch die Management-Einordnung, Kategorie-Sicht und
              die naechsten priorisierten Handlungsfelder fuer Landhandel und Verbundsteuerung.
            </p>
          </div>
          <Badge variant={managementStatus.tone}>{managementStatus.label}</Badge>
        </div>
      </PageSection>

      <PageSection title="Steuerung" description="Vergleichsfenster und Management-Score fuer die aktuelle Periode.">
        <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Vergleichsfenster</CardTitle>
              <CardDescription>Waehlbar nach Monat, Quartal oder Jahr.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <NativeSelect
                value={period}
                onValueChange={(value) => setPeriod(value as 'month' | 'quarter' | 'year')}
                options={[
                  { value: 'month', label: 'Letzter Monat' },
                  { value: 'quarter', label: 'Letztes Quartal' },
                  { value: 'year', label: 'Letztes Jahr' },
                ]}
                className="w-[220px]"
              />
              {data?.period ? (
                <p className="text-sm text-muted-foreground">
                  {data.period.start_date} bis {data.period.end_date}
                </p>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Management-Zusammenfassung</CardTitle>
              <CardDescription>{managementStatus.text}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl border bg-muted/30 p-4">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Durchschnittliche Abweichung</div>
                  <div className="mt-2 text-2xl font-semibold">{averageDelta == null ? 'n/a' : `${averageDelta} %`}</div>
                </div>
                <div className="rounded-xl border bg-muted/30 p-4">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Ueber Branche</div>
                  <div className="mt-2 text-2xl font-semibold">{positiveCount}</div>
                </div>
                <div className="rounded-xl border bg-muted/30 p-4">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Unter Branche</div>
                  <div className="mt-2 text-2xl font-semibold">{negativeCount}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      {isLoading ? (
        <PageSection title="Datenabruf" description="Benchmark-Werte werden geladen.">
          <div className="flex items-center gap-2 py-12 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Lade Benchmark-Daten...</span>
          </div>
        </PageSection>
      ) : data ? (
        <>
          <PageSection title="Kern-KPI" description="Einzelwerte mit direkter Branchenabweichung und Handlungshinweis.">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {comparisonEntries.map(([key, comp]) => {
                const ownVal = comp.own ?? 0
                const branchVal = comp.branch
                const pct = comp.deviation_pct
                const label = KPI_LABELS[key] ?? key

                let statusIcon = <Minus className="h-4 w-4 text-muted-foreground" />
                let statusBadge: React.ReactNode = <Badge variant="outline">ohne Referenz</Badge>
                if (pct != null) {
                  if (pct > 0) {
                    statusIcon = <TrendingUp className="h-4 w-4 text-green-600" />
                    statusBadge = <Badge variant="default" className="bg-green-600">+{pct} %</Badge>
                  } else if (pct < 0) {
                    statusIcon = <TrendingDown className="h-4 w-4 text-amber-600" />
                    statusBadge = <Badge variant="secondary">{pct} %</Badge>
                  } else {
                    statusBadge = <Badge variant="outline">0 %</Badge>
                  }
                }

                return (
                  <Card key={key} className="rounded-2xl border-border/70 shadow-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="flex items-center justify-between text-sm font-medium">
                        {label}
                        {statusIcon}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-baseline justify-between gap-3">
                        <span className="text-2xl font-bold">{formatValue(key, ownVal)}</span>
                        {statusBadge}
                      </div>
                      {branchVal != null ? (
                        <p className="text-xs text-muted-foreground">
                          Branche: {formatValue(key, Number(branchVal))}
                        </p>
                      ) : null}
                      <p className="text-xs text-muted-foreground">{actionFromDelta(pct)}</p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </PageSection>

          <PageSection title="Staerken und Schwaechen" description="Verdichtete Management-Sicht fuer Priorisierung.">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <CircleCheck className="h-5 w-5 text-emerald-600" />
                    Aktuelle Staerken
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {strongest.length > 0 ? strongest.map(([key, comp]) => (
                    <div key={key} className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-medium">{KPI_LABELS[key] ?? key}</span>
                        <Badge variant="default" className="bg-emerald-600">+{comp.deviation_pct ?? 0} %</Badge>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Eigener Wert {formatValue(key, comp.own)} gegenüber Branche {comp.branch != null ? formatValue(key, comp.branch) : 'n/a'}.
                      </p>
                    </div>
                  )) : <p className="text-sm text-muted-foreground">Keine belastbaren Stärken verfuegbar.</p>}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <AlertTriangle className="h-5 w-5 text-amber-600" />
                    Prioritaere Schwaechen
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {weakest.length > 0 ? weakest.map(([key, comp]) => (
                    <div key={key} className="rounded-xl border border-amber-200 bg-amber-50/70 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-medium">{KPI_LABELS[key] ?? key}</span>
                        <Badge variant="secondary">{comp.deviation_pct ?? 0} %</Badge>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{actionFromDelta(comp.deviation_pct)}</p>
                    </div>
                  )) : <p className="text-sm text-muted-foreground">Keine prioritaeren Schwaechen verfuegbar.</p>}
                </CardContent>
              </Card>
            </div>
          </PageSection>
        </>
      ) : null}

      <PageSection title="Kategoriesicht" description="Benchmark-Katalog fuer Verbund-, Prozess- und Verbesserungssteuerung.">
        {readModelLoading ? (
          <div className="flex items-center gap-2 py-6 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Benchmark-Katalog wird geladen...</span>
          </div>
        ) : readModel?.catalog ? (
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Kennzahlen</div>
                  <div className="mt-2 text-2xl font-semibold">{readModel.catalog.kennzahl_count}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Top-10-Felder</div>
                  <div className="mt-2 text-2xl font-semibold">{readModel.catalog.top10_count}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Verbesserungsfelder</div>
                  <div className="mt-2 text-2xl font-semibold">{readModel.catalog.improvement_count}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">Trendserien</div>
                  <div className="mt-2 text-2xl font-semibold">{readModel.catalog.trend_series_count}</div>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="grid gap-4 md:grid-cols-2">
                {readModel.catalog.categories.map((category) => (
                  <Card key={category.kategorie}>
                    <CardHeader>
                      <CardTitle className="text-base">{toCategoryLabel(category.kategorie)}</CardTitle>
                      <CardDescription>{category.kennzahl_count} Kennzahlen in dieser Kategorie.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex justify-between gap-3">
                        <span>Durchschnittsscore</span>
                        <span className="font-medium text-foreground">{Math.round(category.avg_score)} / 100</span>
                      </div>
                      <div className="flex justify-between gap-3">
                        <span>Top-10-Treiber</span>
                        <span className="font-medium text-foreground">{category.top10_count}</span>
                      </div>
                      <div className="flex justify-between gap-3">
                        <span>Verbesserungsfelder</span>
                        <span className="font-medium text-foreground">{category.improvement_count}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Management-Fokus</CardTitle>
                  <CardDescription>Direkte Uebergaben aus dem Benchmark in weitere Controlling-Pfade.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="rounded-xl border bg-muted/30 p-3">
                    <div className="text-xs uppercase tracking-wide text-muted-foreground">Stärkste Kennzahl</div>
                    <div className="mt-1 font-medium">{readModel.catalog.best_metric}</div>
                  </div>
                  <div className="rounded-xl border bg-muted/30 p-3">
                    <div className="text-xs uppercase tracking-wide text-muted-foreground">Schwächste Kennzahl</div>
                    <div className="mt-1 font-medium">{readModel.catalog.weakest_metric}</div>
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    {readModel.coverage_notes.map((note) => (
                      <p key={note}>{note}</p>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Link to="/analytics">
                      <Button variant="outline" size="sm">
                        Analytics oeffnen
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                    <Link to="/admin/control-center/agent-ops">
                      <Button variant="outline" size="sm">Agent Ops fuer Review</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6 text-sm text-muted-foreground">
              Kein Benchmark-Katalog verfuegbar.
            </CardContent>
          </Card>
        )}
      </PageSection>
    </PageSurface>
  )
}
