import { useLocation } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Sprout, TrendingUp } from 'lucide-react'
import { useDuengerKomponenten, useSchlaege } from '@/lib/api/agrar'
import { EvidenceTemplateLink, NextActionPanel, OperationalTaskPlan } from '@/components/workflow'

type BedarfsrechnerState = {
  flaeche: number
  kultur: string
  empfehlung: { n: number; p: number; k: number }
  ertragsziel?: number
}

function isBedarfsrechnerState(value: unknown): value is { fromBedarfsrechner: BedarfsrechnerState } {
  if (!value || typeof value !== 'object') return false
  const state = value as { fromBedarfsrechner?: unknown }
  const bedarf = state.fromBedarfsrechner
  if (!bedarf || typeof bedarf !== 'object') return false
  const candidate = bedarf as Partial<BedarfsrechnerState>
  return (
    typeof candidate.flaeche === 'number' &&
    typeof candidate.kultur === 'string' &&
    !!candidate.empfehlung &&
    typeof candidate.empfehlung.n === 'number' &&
    typeof candidate.empfehlung.p === 'number' &&
    typeof candidate.empfehlung.k === 'number'
  )
}

export default function DuengungsplanungPage(): JSX.Element {
  const location = useLocation()
  const fromBedarfsrechner = isBedarfsrechnerState(location.state)
    ? location.state.fromBedarfsrechner
    : undefined
  const { data: komponenten, isLoading: loadingKomponenten } = useDuengerKomponenten()
  const { data: schlaegeListe = [], isLoading: loadingSchlaege } = useSchlaege()

  const gesamtFlaeche = schlaegeListe.reduce((sum, s) => sum + s.flaeche, 0)
  const verfuegbareKomponenten = komponenten ?? []
  const isLoading = loadingKomponenten || loadingSchlaege
  const hasBedarf = Boolean(fromBedarfsrechner?.empfehlung)
  const nextPlanningAction = schlaegeListe.length === 0
    ? 'Zuerst Schlaege anlegen, damit Bedarf und Flaeche geplant werden koennen.'
    : hasBedarf
      ? 'Uebernommene Empfehlung schlagbezogen pruefen und passende Komponente fuer die Ausbringung waehlen.'
      : 'Bedarf im Rechner ermitteln oder je Schlag Kultur, Flaeche und Naehrstoffbedarf nachpflegen.'

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Düngungsplanung</h1>
        <p className="text-muted-foreground">Nährstoffbedarf & Planung ({verfuegbareKomponenten.length} Komponenten verfügbar)</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <NextActionPanel
          title="Naechster Planungsschritt"
          action={nextPlanningAction}
          tone={schlaegeListe.length === 0 ? 'amber' : hasBedarf ? 'blue' : 'neutral'}
        />
        <EvidenceTemplateLink link={{ label: 'Duengebedarf und Ausbringnachweis', href: '/docs/agrar/duengung/duengebedarf-ausbringnachweis.md' }} />
      </div>

      <OperationalTaskPlan
        title="Planung ohne Ueberladung"
        items={[
          { label: 'Schlaege und Flaechen pruefen', done: schlaegeListe.length > 0, hint: `${schlaegeListe.length} Schlaege mit ${gesamtFlaeche.toFixed(1)} ha in der Planung.` },
          { label: 'Bedarf je Kultur klaeren', done: hasBedarf, hint: hasBedarf ? 'Empfehlung aus dem Bedarfsrechner liegt vor.' : 'Bei Bedarf den Rechner starten und Ergebnis uebernehmen.' },
          { label: 'Nachweis vorbereiten', done: verfuegbareKomponenten.length > 0, hint: `${verfuegbareKomponenten.length} Duengerkomponenten sind verfuegbar.` },
        ]}
      />

      {fromBedarfsrechner?.empfehlung && (
        <Card className="border-green-200 bg-green-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Übernahme aus Bedarfsrechner</CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            <p className="mb-2">
              Kultur: <strong>{fromBedarfsrechner.kultur || '–'}</strong>, Fläche: <strong>{fromBedarfsrechner.flaeche} ha</strong>
            </p>
            <p>
              Empfehlung: N <strong>{fromBedarfsrechner.empfehlung.n.toFixed(0)}</strong> kg/ha, P <strong>{fromBedarfsrechner.empfehlung.p.toFixed(0)}</strong> kg/ha, K <strong>{fromBedarfsrechner.empfehlung.k.toFixed(0)}</strong> kg/ha
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold">{schlaegeListe.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Fläche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtFlaeche.toFixed(1)} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="outline" className="text-base px-4 py-2">Planung läuft</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Schläge & Nährstoffbedarf
          </CardTitle>
        </CardHeader>
        <CardContent>
          {schlaegeListe.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">Keine Schläge erfasst.</p>
            ) : (
            <div className="space-y-3">
            {schlaegeListe.map((schlag) => (
              <Card key={schlag.id}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="font-semibold text-lg">{schlag.name}</div>
                      <div className="text-sm text-muted-foreground">{schlag.kultur} - {schlag.flaeche} ha</div>
                    </div>
                    <Badge variant="outline">{schlag.status}</Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="rounded-lg bg-blue-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">N (Stickstoff)</div>
                      <div className="text-lg font-bold text-blue-600 mt-1">—</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
                    </div>
                    <div className="rounded-lg bg-orange-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">P (Phosphor)</div>
                      <div className="text-lg font-bold text-status-warning mt-1">—</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
                    </div>
                    <div className="rounded-lg bg-green-50 p-3 text-center">
                      <div className="text-sm text-muted-foreground">K (Kalium)</div>
                      <div className="text-lg font-bold text-status-success mt-1">—</div>
                      <div className="text-xs text-muted-foreground">kg/ha</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
            )}
        </CardContent>
      </Card>
    </div>
  )
}
