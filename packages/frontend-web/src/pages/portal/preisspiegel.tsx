/**
 * Kundenportal — Getreidekurs-Preisspiegel
 *
 * Zeigt dem Ackerbauer seine Erntefrüchte mit allen 4 Preisvarianten:
 *  - Altware ab Hof
 *  - Altware frei Lager Handel (angeliefert)
 *  - Neue Ernte frei Lager Handel
 *  - Neue Ernte ab Hof (Monat nach Ernte)
 *
 * API: GET /portal/preisspiegel/kunde?artikel_ids=...
 *      GET /portal/preisspiegel?frucht_gruppe=...
 */

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import {
  TrendingUp,
  TrendingDown,
  Wheat,
  Truck,
  Home,
  Calendar,
  Info,
  RefreshCw,
  Phone,
} from 'lucide-react'

type PreisVariante = {
  variante: string
  preis_eur_dt: number
  aufschlag_eur_dt: number
  gesamtpreis_eur_dt: number
  ernte_jahr: number
  liefermonat: string | null
  basis_qualitaet: string
  hinweis: string | null
  gueltig_ab: string
}

type ArtikelPreisspiegel = {
  artikel_id: string
  artikel_name: string
  frucht_gruppe: string
  varianten: Record<string, PreisVariante>
}

type PreisspigelResponse = {
  preisspiegel: ArtikelPreisspiegel[]
  stand: string
  hinweis: string
}

// Für Demo: Artikel-IDs die der eingeloggte Bauer anbaut
// Produktiv: aus JWT + Schlagkartei-Kulturen ableiten
const DEMO_ARTIKEL = 'WEI-001,GER-001,RAP-001'

const VARIANTE_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string; beschreibung: string }> = {
  altware_ab_hof: {
    label: 'Altware ab Hof',
    icon: <Home className="h-4 w-4" />,
    color: 'bg-amber-50 border-amber-200',
    beschreibung: 'Altjährige Ware, wir holen bei Ihnen ab',
  },
  altware_frei_lager: {
    label: 'Altware frei Lager',
    icon: <Truck className="h-4 w-4" />,
    color: 'bg-blue-50 border-blue-200',
    beschreibung: 'Altjährige Ware, Sie liefern zu uns',
  },
  neue_ernte_frei_lager: {
    label: 'Neue Ernte frei Lager',
    icon: <Wheat className="h-4 w-4" />,
    color: 'bg-green-50 border-green-200',
    beschreibung: 'Neue Ernte, angeliefert bei uns',
  },
  neue_ernte_ab_hof: {
    label: 'Neue Ernte ab Hof',
    icon: <Calendar className="h-4 w-4" />,
    color: 'bg-emerald-50 border-emerald-200',
    beschreibung: 'Neue Ernte, Abholung ab Ihrem Hof',
  },
}

function PreisKarte({ variante, preis }: { variante: string; preis: PreisVariante }) {
  const cfg = VARIANTE_CONFIG[variante]
  if (!cfg) return null
  return (
    <div className={`rounded-lg border p-4 ${cfg.color}`}>
      <div className="flex items-center gap-2 mb-2">
        {cfg.icon}
        <span className="text-sm font-medium text-gray-700">{cfg.label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">
        {preis.gesamtpreis_eur_dt.toFixed(2)} €/dt
      </div>
      {preis.liefermonat && (
        <div className="text-xs text-gray-500 mt-1">Liefermonat: {preis.liefermonat}</div>
      )}
      <div className="text-xs text-gray-500 mt-1">{preis.basis_qualitaet}</div>
      {preis.hinweis && (
        <div className="text-xs text-amber-700 mt-2 flex items-start gap-1">
          <Info className="h-3 w-3 mt-0.5 shrink-0" />
          {preis.hinweis}
        </div>
      )}
      <div className="text-xs text-gray-400 mt-2">Stand: {preis.gueltig_ab}</div>
    </div>
  )
}

function ArtikelPreiskarte({ artikel }: { artikel: ArtikelPreisspiegel }) {
  const variantenSortiert = [
    'altware_ab_hof',
    'altware_frei_lager',
    'neue_ernte_frei_lager',
    'neue_ernte_ab_hof',
  ]
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{artikel.artikel_name}</CardTitle>
          <Badge variant="outline">{artikel.frucht_gruppe}</Badge>
        </div>
        <CardDescription>Ankaufspreise in allen Liefervarianten</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {variantenSortiert.map((v) =>
            artikel.varianten[v] ? (
              <PreisKarte key={v} variante={v} preis={artikel.varianten[v]} />
            ) : null,
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default function PreisspiedelPage() {
  const [artikelFilter, setArtikelFilter] = useState<string>(DEMO_ARTIKEL)

  const { data, isLoading, isError, refetch, isFetching } = useQuery<PreisspigelResponse>({
    queryKey: ['portal-preisspiegel', artikelFilter],
    queryFn: async () => {
      const res = await apiClient.get<PreisspigelResponse>(
        `/portal/preisspiegel/kunde?artikel_ids=${artikelFilter}`,
      )
      return res.data
    },
    staleTime: 5 * 60 * 1000,
  })

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-green-600" />
            Getreidekurse
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Aktuelle Ankaufspreise für Ihre Ernte — alle Liefervarianten im Überblick
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
          Aktualisieren
        </Button>
      </div>

      {/* Legende */}
      <Card className="bg-gray-50">
        <CardContent className="pt-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            {Object.entries(VARIANTE_CONFIG).map(([k, v]) => (
              <div key={k} className="flex items-start gap-2">
                <span className="text-gray-500 mt-0.5">{v.icon}</span>
                <div>
                  <div className="font-medium text-gray-700">{v.label}</div>
                  <div className="text-gray-500 text-xs">{v.beschreibung}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48 w-full rounded-xl" />)}
        </div>
      )}

      {isError && (
        <Alert variant="destructive">
          <AlertDescription>Preise konnten nicht geladen werden. Bitte versuchen Sie es später erneut.</AlertDescription>
        </Alert>
      )}

      {data && (
        <div className="space-y-4">
          {data.preisspiegel.length === 0 ? (
            <Alert>
              <AlertDescription>
                Für Ihre Früchte liegen aktuell keine Ankaufspreise vor. Wenden Sie sich an Ihren Innendienst.
              </AlertDescription>
            </Alert>
          ) : (
            data.preisspiegel.map((artikel) => (
              <ArtikelPreiskarte key={artikel.artikel_id} artikel={artikel} />
            ))
          )}

          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <Phone className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900">Verbindliche Preisauskunft</div>
                  <div className="text-blue-700 text-sm mt-1">
                    {data.hinweis} Für Kontraktabschlüsse und verbindliche Preiszusagen kontaktieren Sie bitte Ihren Innendienst.
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="text-xs text-gray-400 text-right">Preisstand: {data.stand}</div>
        </div>
      )}
    </div>
  )
}
