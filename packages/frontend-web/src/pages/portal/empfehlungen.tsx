/**
 * Kundenportal — Personalisierte Empfehlungen (Cross-Sell Intelligence)
 *
 * Zeigt dem Kunden:
 * - Ankaufsangebote basierend auf angebauten Kulturen
 * - Rohwaren-Angebote nach Rationskalkulation
 * - Lohndienst-Empfehlungen (Spritz, Mahl+Misch, TMR)
 *
 * API: GET /portal/empfehlungen/{kunden_nr}
 *      POST /portal/empfehlungen/{kunden_nr}/gesehen/{id}
 */

import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import {
  Sparkles,
  TrendingUp,
  Tractor,
  ShoppingCart,
  Bell,
  Sprout,
  CheckCircle2,
  ChevronRight,
  Filter,
} from 'lucide-react'

// Demo-Kunden-Nr; produktiv aus Auth-Context
const DEMO_KUNDEN_NR = 'K-10001'

type Empfehlung = {
  empfehlung_id: string
  typ: string
  prioritaet: string
  titel: string
  beschreibung: string
  cta_label: string
  cta_ziel: string
  artikel_id: string | null
  gesehen: boolean
  erstellt_am: string
}

const TYP_CONFIG: Record<string, { icon: React.ReactNode; farbe: string; badge: string }> = {
  ankauf_kontrakt: { icon: <TrendingUp className="h-5 w-5" />, farbe: 'border-green-300 bg-green-50', badge: 'Ankauf' },
  rohware_angebot: { icon: <ShoppingCart className="h-5 w-5" />, farbe: 'border-blue-300 bg-blue-50', badge: 'Rohwaren' },
  lohndienst: { icon: <Tractor className="h-5 w-5" />, farbe: 'border-amber-300 bg-amber-50', badge: 'Lohndienst' },
  saatgut_folge: { icon: <Sprout className="h-5 w-5" />, farbe: 'border-lime-300 bg-lime-50', badge: 'Saatgut' },
  vertrag_erinnerung: { icon: <Bell className="h-5 w-5" />, farbe: 'border-red-300 bg-red-50', badge: 'Erinnerung' },
}

const PRIORITAET_FARBE: Record<string, string> = {
  hoch: 'bg-red-100 text-red-800',
  mittel: 'bg-amber-100 text-amber-800',
  niedrig: 'bg-gray-100 text-gray-600',
}

function EmpfehlungCard({ e, onGesehen }: { e: Empfehlung; onGesehen: (id: string) => void }) {
  const navigate = useNavigate()
  const cfg = TYP_CONFIG[e.typ] ?? TYP_CONFIG.rohware_angebot
  return (
    <Card className={`border ${cfg.farbe} ${e.gesehen ? 'opacity-70' : ''}`}>
      <CardContent className="pt-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1">
            <div className="mt-0.5 text-gray-600">{cfg.icon}</div>
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="font-semibold text-gray-900">{e.titel}</span>
                <Badge className={PRIORITAET_FARBE[e.prioritaet]}>{e.prioritaet}</Badge>
                <Badge variant="outline">{cfg.badge}</Badge>
                {e.gesehen && <CheckCircle2 className="h-4 w-4 text-green-500" />}
              </div>
              <p className="text-sm text-gray-600 mb-3">{e.beschreibung}</p>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  onClick={() => {
                    onGesehen(e.empfehlung_id)
                    // Navigation zu relativer Portal-Route
                    // In Produktion: navigate(e.cta_ziel)
                  }}
                >
                  {e.cta_label}
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
                {!e.gesehen && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onGesehen(e.empfehlung_id)}
                    className="text-gray-500"
                  >
                    Als gesehen markieren
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function EmpfehlungenPage() {
  const { toast } = useToast()
  const qc = useQueryClient()
  const [filter, setFilter] = useState<string>('alle')

  const { data, isLoading, isError } = useQuery<{ items: Empfehlung[]; count: number }>({
    queryKey: ['portal-empfehlungen', DEMO_KUNDEN_NR],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Empfehlung[]; count: number }>(
        `/portal/empfehlungen/${DEMO_KUNDEN_NR}`,
      )
      return res.data
    },
  })

  const gesehenMutation = useMutation({
    mutationFn: async (empfehlung_id: string) => {
      await apiClient.post(`/portal/empfehlungen/${DEMO_KUNDEN_NR}/gesehen/${empfehlung_id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portal-empfehlungen'] })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Status konnte nicht gespeichert werden.', variant: 'destructive' })
    },
  })

  const alleItems = data?.items ?? []
  const gefiltert = filter === 'alle' ? alleItems : alleItems.filter((e) => e.typ === filter)
  const ungesehen = alleItems.filter((e) => !e.gesehen).length

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-amber-500" />
            Empfehlungen für Sie
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Personalisierte Angebote basierend auf Ihrer Schlagkartei und Ihren Aktivitäten
          </p>
        </div>
        {ungesehen > 0 && (
          <Badge className="bg-red-500 text-white text-base px-3 py-1">
            {ungesehen} neu
          </Badge>
        )}
      </div>

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        {['alle', 'ankauf_kontrakt', 'rohware_angebot', 'lohndienst', 'vertrag_erinnerung'].map((f) => (
          <Button
            key={f}
            size="sm"
            variant={filter === f ? 'default' : 'outline'}
            onClick={() => setFilter(f)}
          >
            {f === 'alle' ? 'Alle' : TYP_CONFIG[f]?.badge ?? f}
          </Button>
        ))}
      </div>

      {isLoading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-32 w-full" />)}
        </div>
      )}

      {isError && (
        <Alert variant="destructive">
          <AlertDescription>Empfehlungen konnten nicht geladen werden.</AlertDescription>
        </Alert>
      )}

      {data && gefiltert.length === 0 && (
        <Alert>
          <AlertDescription>
            {filter === 'alle'
              ? 'Aktuell liegen keine Empfehlungen vor. Führen Sie eine Rationskalkulation durch oder hinterlegen Sie Ihre Schlagkartei.'
              : 'Keine Empfehlungen in dieser Kategorie.'}
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-3">
        {gefiltert.map((e) => (
          <EmpfehlungCard
            key={e.empfehlung_id}
            e={e}
            onGesehen={(id) => gesehenMutation.mutate(id)}
          />
        ))}
      </div>
    </div>
  )
}
