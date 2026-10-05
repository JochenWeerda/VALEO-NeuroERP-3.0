import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Callout } from '@/components/ui/callout'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { AlertTriangle, CheckCircle, FileText, Globe, MapPin } from 'lucide-react'

/**
 * EUDR-Stand aus dem Sorgfaltserklärungsregister.
 *
 * Bis zum 01.10.2026 zeigte diese Maske Chargenzahlen aus
 * `domain_inventory.lots` — einer Tabelle, die kein Migrationsstand anlegt. Der
 * Endpunkt fing den Lesefehler und meldete `status: "KONFORM"` mit
 * `deforestation_risk: "NIEDRIG"`; die Maske zeigte daraufhin eine
 * Compliance-Rate von 0,0 % **und** den Status „KONFORM". Nach Art. 3/4 der
 * Verordnung (EU) 2023/1115 ist das Inverkehrbringen ohne Sorgfaltserklärung
 * verboten — eine grüne Anzeige ist hier die gefährlichste Antwort.
 *
 * Jetzt zeigt die Maske, was das Register weiß, und sagt es, wenn sie nichts
 * weiß.
 */
type EUDRStatus = {
  status: string
  last_check: string | null
  due_diligence_statements: number
  statements_submitted: number
  statements_draft: number
  statements_unassessed: number
  origin_countries: string[]
  commodities: string[]
  deforestation_risk: string
  /** Art. 4: relevante Chargen ohne Nachweis dürfen nicht in Verkehr. */
  lots_relevant: number
  lots_covered: number
  lots_open: number
  open_quantity_kg: number
  next_report_due: string | null
}

const STAND_TEXT: Record<string, string> = {
  OHNE_ERKLAERUNG: 'Keine Sorgfaltserklärung erfasst — ohne sie darf nichts in Verkehr gebracht werden.',
  UNVOLLSTAENDIG: 'Erklärungen im Entwurf: noch nicht eingereicht.',
  KRITISCH: 'Mindestens eine Erklärung trägt ein nicht vernachlässigbares Risiko.',
  KONFORM: 'Alle Erklärungen sind eingereicht und tragen vernachlässigbares Risiko.',
}

function standVariante(stand: string): 'success' | 'warning' | 'error' {
  if (stand === 'KONFORM') return 'success'
  if (stand === 'KRITISCH') return 'error'
  return 'warning'
}

export default function EUDRCompliancePage(): JSX.Element {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['compliance', 'eudr'],
    queryFn: async () => (await apiClient.get<EUDRStatus>('/api/v1/compliance/eudr')).data,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const eudr: EUDRStatus = data ?? {
    status: 'UNBEKANNT',
    last_check: null,
    due_diligence_statements: 0,
    statements_submitted: 0,
    statements_draft: 0,
    statements_unassessed: 0,
    origin_countries: [],
    commodities: [],
    deforestation_risk: 'UNBEKANNT',
    lots_relevant: 0,
    lots_covered: 0,
    lots_open: 0,
    open_quantity_kg: 0,
    next_report_due: null,
  }

  const variante = standVariante(eudr.status)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">EUDR-Compliance</h1>
        <p className="text-muted-foreground">
          Entwaldungsfreie Lieferketten — Sorgfaltserklärungen nach Verordnung (EU) 2023/1115
        </p>
      </div>

      <Callout variant={variante}>
        <span className="font-semibold">{eudr.status}</span>
        {' — '}
        {STAND_TEXT[eudr.status] ?? 'Der Stand ist derzeit nicht feststellbar.'}
      </Callout>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erklärungen gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{eudr.due_diligence_statements}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eingereicht</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold text-status-success">
                {eudr.statements_submitted}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Im Entwurf</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">
              {eudr.statements_draft}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ohne Risikobewertung</CardTitle>
          </CardHeader>
          <CardContent>
            <span
              className={
                eudr.statements_unassessed > 0
                  ? 'text-2xl font-bold text-status-error'
                  : 'text-2xl font-bold text-muted-foreground'
              }
            >
              {eudr.statements_unassessed}
            </span>
          </CardContent>
        </Card>
      </div>

      {eudr.lots_open > 0 && (
        <Callout variant="error">
          <AlertTriangle className="mr-2 inline h-4 w-4" />
          {eudr.lots_open} Charge(n) mit {eudr.open_quantity_kg.toLocaleString('de-DE')} kg ohne
          Nachweis. Nach Art. 4 darf diese Ware nicht in Verkehr gebracht werden.
        </Callout>
      )}

      {eudr.statements_unassessed > 0 && (
        <Callout variant="warning">
          <AlertTriangle className="mr-2 inline h-4 w-4" />
          {eudr.statements_unassessed} Erklärung(en) ohne Risikobewertung. Art. 10 verlangt die
          Bewertung, bevor eingereicht werden darf.
        </Callout>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Produktionsländer
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {eudr.origin_countries.length === 0 ? (
              <p className="text-sm text-muted-foreground">Keine Produktionsländer erfasst.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {eudr.origin_countries.map((land) => (
                  <Badge key={land} variant="outline">{land}</Badge>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2 pt-2">
              <Globe className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Rohstoffe:</span>
              {eudr.commodities.length === 0 ? (
                <span className="text-sm text-muted-foreground">–</span>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {eudr.commodities.map((rohstoff) => (
                    <Badge key={rohstoff} variant="outline">{rohstoff}</Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Entwaldungsrisiko</span>
              <span className="font-semibold">{eudr.deforestation_risk}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Chargen mit Nachweis</span>
              <span className="font-semibold">
                {eudr.lots_covered} von {eudr.lots_relevant}
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Ohne Nachweis</span>
              <span
                className={eudr.lots_open > 0 ? 'font-semibold text-status-error' : 'font-semibold'}
              >
                {eudr.lots_open} ({eudr.open_quantity_kg.toLocaleString('de-DE')} kg)
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Nächste Meldung</span>
              <span className="font-semibold">{eudr.next_report_due ?? '–'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stand</span>
              <span className="font-semibold">
                {eudr.last_check ? new Date(eudr.last_check).toLocaleString('de-DE') : '–'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
