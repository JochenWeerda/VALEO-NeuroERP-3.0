/**
 * Außendienst — Potential-Analyse / Cross-Sell-Gap-Dashboard
 *
 * Zeigt dem Außendienstler:
 * - Welche Kunden bauen Getreide an, haben aber keinen Ankaufskontrakt?
 * - Welche Kunden haben Viehbestand, nutzen keinen Futtermittel-/Rationierungsservice?
 * - Welche Kunden nutzen noch keinen Lohnspritzdienst?
 *
 * API: GET /innendienst/potential
 */

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import {
  TrendingUp,
  Users,
  Target,
  ChevronRight,
  Euro,
  Wheat,
  Tractor,
  AlertCircle,
} from 'lucide-react'

type GapTyp = {
  gap_typ: string
  titel: string
  beschreibung: string
  kunden: string[]
  potential_eur_je_kunde: number
}

type PotentialResponse = {
  gap_analyse: GapTyp[]
  schlag_kunden_count: number
  hinweis: string
}

const GAP_ICONS: Record<string, React.ReactNode> = {
  ankauf_kein_kontrakt: <Wheat className="h-5 w-5 text-status-success" />,
  lohnspritz_kein_auftrag: <Tractor className="h-5 w-5 text-status-warning" />,
  ration_kein_rohwaren_kontrakt: <Euro className="h-5 w-5 text-blue-600" />,
}

function GapKarte({ gap }: { gap: GapTyp }) {
  const gesamtPotential = gap.kunden.length * gap.potential_eur_je_kunde
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          <div className="mt-1">{GAP_ICONS[gap.gap_typ] ?? <Target className="h-5 w-5" />}</div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-gray-900">{gap.titel}</span>
              <Badge className="bg-red-100 text-red-700">
                {gap.kunden.length} Kunden
              </Badge>
            </div>
            <p className="text-sm text-gray-600 mb-3">{gap.beschreibung}</p>
            <div className="flex items-center justify-between">
              <div className="text-sm">
                <span className="text-gray-500">Potential: </span>
                <span className="font-bold text-green-700">
                  {gesamtPotential.toLocaleString('de-DE')} €
                </span>
                <span className="text-gray-400 text-xs ml-1">
                  ({gap.potential_eur_je_kunde.toLocaleString('de-DE')} €/Kunde)
                </span>
              </div>
              {gap.kunden.length > 0 && (
                <Button size="sm" variant="outline">
                  Kunden ansehen
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              )}
            </div>
            {gap.kunden.length > 0 && gap.kunden.length <= 5 && (
              <div className="mt-2 flex gap-1 flex-wrap">
                {gap.kunden.map((k) => (
                  <Badge key={k} variant="outline" className="text-xs">{k}</Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function PotentialAnalysePage() {
  const { data, isLoading, isError } = useQuery<PotentialResponse>({
    queryKey: ['potential-analyse'],
    queryFn: async () => {
      const res = await apiClient.get<PotentialResponse>('/innendienst/potential')
      return res.data
    },
    staleTime: 10 * 60 * 1000,
  })

  const gesamtPotential = (data?.gap_analyse ?? []).reduce(
    (sum, g) => sum + g.kunden.length * g.potential_eur_je_kunde, 0
  )
  const gesamtKunden = new Set((data?.gap_analyse ?? []).flatMap((g) => g.kunden)).size

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Target className="h-6 w-6 text-blue-600" />
          Potential-Analyse
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Cross-Sell-Lücken im Kundenstamm — für Außendienst und Innendienst
        </p>
      </div>

      {/* KPI-Leiste */}
      {data && (
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-4 text-center">
              <div className="text-3xl font-bold text-blue-700">{gesamtKunden}</div>
              <div className="text-sm text-gray-500">Kunden mit Potential</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <div className="text-3xl font-bold text-green-700">
                {(gesamtPotential / 1000).toFixed(0)} T€
              </div>
              <div className="text-sm text-gray-500">Geschätztes Gesamtpotential</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <div className="text-3xl font-bold text-amber-700">{data.schlag_kunden_count}</div>
              <div className="text-sm text-gray-500">Kunden mit Schlagkartei</div>
            </CardContent>
          </Card>
        </div>
      )}

      {isLoading && (
        <div className="space-y-3">{[1,2,3].map(i => <Skeleton key={i} className="h-32" />)}</div>
      )}

      {isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>Potentialanalyse konnte nicht geladen werden.</AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        {data?.gap_analyse.map((gap) => (
          <GapKarte key={gap.gap_typ} gap={gap} />
        ))}
      </div>

      {data && (
        <p className="text-xs text-gray-400">{data.hinweis}</p>
      )}
    </div>
  )
}
