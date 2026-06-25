/**
 * Innendienst — Kundenschlagkartei
 *
 * Zeigt alle Schläge und Maßnahmen eines bestimmten Kunden.
 * Nutzung: Vorbereitung von Lohnspritz-, Mahl+Misch-, Saat-Aufträgen.
 *
 * API: GET /innendienst/kunden/{kunden_nr}/schlaege
 *      GET /innendienst/kunden/{kunden_nr}/massnahmen
 */

import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import {
  Map,
  Droplets,
  ArrowLeft,
  Plus,
  Leaf,
  FileText,
  Users,
} from 'lucide-react'

type Schlag = {
  id: string
  name: string
  flik?: string
  flaeche: number
  kultur: string
  vorkultur?: string
  gemeinde: string
  status: string
}

type Massnahme = {
  id: string
  datum: string
  typ: string
  schlag_name: string
  mittel?: string
  menge?: number
  einheit?: string
  bemerkung?: string
}

// Kunden-Nr kann als Route-Parameter oder Query-String kommen
function useKundenNr(): string {
  // In echten Routen: useParams gibt {kunden_nr}
  // Fallback für Demo
  return 'K-10001'
}

export default function KundenSchlagkarteiPage() {
  const navigate = useNavigate()
  const kundenNr = useKundenNr()
  const [massnahmeTypFilter, setMassnahmeTypFilter] = useState<string>('')

  const { data: schlaege, isLoading: loadingS } = useQuery<{ schlaege: Schlag[]; count: number }>({
    queryKey: ['innendienst-schlaege', kundenNr],
    queryFn: async () => {
      const res = await apiClient.get<{ schlaege: Schlag[]; count: number }>(
        `/innendienst/kunden/${kundenNr}/schlaege`,
      )
      return res.data
    },
  })

  const { data: massnahmen, isLoading: loadingM } = useQuery<{ massnahmen: Massnahme[]; count: number }>({
    queryKey: ['innendienst-massnahmen', kundenNr, massnahmeTypFilter],
    queryFn: async () => {
      const params = massnahmeTypFilter ? `?massnahme_typ=${massnahmeTypFilter}` : ''
      const res = await apiClient.get<{ massnahmen: Massnahme[]; count: number }>(
        `/innendienst/kunden/${kundenNr}/massnahmen${params}`,
      )
      return res.data
    },
  })

  const gesamtFlaeche = (schlaege?.schlaege ?? []).reduce((s, x) => s + (x.flaeche ?? 0), 0)
  const kulturen = [...new Set((schlaege?.schlaege ?? []).map((s) => s.kultur).filter(Boolean))]

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Map className="h-6 w-6 text-green-600" />
            Schlagkartei — Kunde {kundenNr}
          </h1>
          <p className="text-gray-500 text-sm">Innendienst-Sicht: Auftragsvororbereitung Lohnspritz / Mahl+Misch</p>
        </div>
      </div>

      {/* KPI-Leiste */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-green-700">{schlaege?.count ?? '—'}</div>
            <div className="text-sm text-gray-500">Schläge</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-blue-700">{gesamtFlaeche.toFixed(1)} ha</div>
            <div className="text-sm text-gray-500">Gesamtfläche</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-amber-700">{kulturen.length}</div>
            <div className="text-sm text-gray-500">Kulturen</div>
          </CardContent>
        </Card>
      </div>

      {kulturen.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <span className="text-sm text-gray-500 self-center">Angebaute Kulturen:</span>
          {kulturen.map((k) => (
            <Badge key={k} variant="outline" className="bg-green-50">{k}</Badge>
          ))}
        </div>
      )}

      {/* Lohndienst-Schnellaktionen */}
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="pt-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-amber-600" />
            <span className="font-medium text-amber-900">Auftrag direkt aus Schlagkartei anlegen</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button size="sm" variant="outline" className="bg-white">
              <Droplets className="h-4 w-4 mr-1" />
              Lohnspritz-Auftrag anlegen
            </Button>
            <Button size="sm" variant="outline" className="bg-white">
              <Leaf className="h-4 w-4 mr-1" />
              Mahl+Misch-Termin anfragen
            </Button>
            <Button size="sm" variant="outline" className="bg-white">
              <FileText className="h-4 w-4 mr-1" />
              Ankaufsangebot erstellen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="schlaege">
        <TabsList>
          <TabsTrigger value="schlaege">Schläge ({schlaege?.count ?? 0})</TabsTrigger>
          <TabsTrigger value="massnahmen">Maßnahmen ({massnahmen?.count ?? 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="schlaege" className="mt-4">
          {loadingS ? (
            <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
          ) : schlaege?.schlaege.length === 0 ? (
            <Alert><AlertDescription>Keine Schläge für diesen Kunden erfasst.</AlertDescription></Alert>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {['Name', 'Fläche (ha)', 'Kultur', 'Vorkultur', 'Gemeinde', 'Status'].map(h => (
                      <th key={h} className="text-left px-3 py-2 font-medium text-gray-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {schlaege?.schlaege.map((s) => (
                    <tr key={s.id} className="border-t hover:bg-gray-50">
                      <td className="px-3 py-2 font-medium">{s.name}</td>
                      <td className="px-3 py-2">{s.flaeche?.toFixed(2)}</td>
                      <td className="px-3 py-2">{s.kultur}</td>
                      <td className="px-3 py-2 text-gray-500">{s.vorkultur ?? '—'}</td>
                      <td className="px-3 py-2">{s.gemeinde}</td>
                      <td className="px-3 py-2">
                        <Badge variant="outline">{s.status}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </TabsContent>

        <TabsContent value="massnahmen" className="mt-4">
          {loadingM ? (
            <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
          ) : massnahmen?.massnahmen.length === 0 ? (
            <Alert><AlertDescription>Keine Maßnahmen für diesen Kunden erfasst.</AlertDescription></Alert>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {['Datum', 'Typ', 'Schlag', 'Mittel', 'Menge', 'Bemerkung'].map(h => (
                      <th key={h} className="text-left px-3 py-2 font-medium text-gray-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {massnahmen?.massnahmen.map((m) => (
                    <tr key={m.id} className="border-t hover:bg-gray-50">
                      <td className="px-3 py-2">{m.datum}</td>
                      <td className="px-3 py-2"><Badge variant="outline">{m.typ}</Badge></td>
                      <td className="px-3 py-2">{m.schlag_name}</td>
                      <td className="px-3 py-2">{m.mittel ?? '—'}</td>
                      <td className="px-3 py-2">{m.menge ? `${m.menge} ${m.einheit ?? ''}` : '—'}</td>
                      <td className="px-3 py-2 text-gray-500">{m.bemerkung ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
