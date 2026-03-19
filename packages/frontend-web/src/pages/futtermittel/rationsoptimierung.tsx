/**
 * Rationsoptimierung – Fodjan-inspiriertes Fütterungs-Tool
 *
 * Für Außendienst und Landwirte: Rationen erstellen, anpassen, optimieren.
 * GfE-2023-basiert, least-cost Formulierung via PuLP.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchFeeds,
  optimizeDemo,
  optimizeFromProfile,
  type CowProfile,
  type OptimizationResult,
} from '@/lib/api/rations-optimization'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Calculator,
  Cow,
  Package,
  Euro,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react'

const BREEDS = [
  { value: 'Holstein', label: 'Holstein' },
  { value: 'Simmental', label: 'Fleckvieh / Simmental' },
  { value: 'BrownSwiss', label: 'Braunvieh' },
  { value: 'Jersey', label: 'Jersey' },
]

const defaultProfile: CowProfile = {
  breed: 'Holstein',
  body_weight_kg: 650,
  milk_kg_day: 35,
  milk_fat_pct: 3.8,
  milk_protein_pct: 3.2,
  lactation_stage_days: 150,
  parity: 2,
  target_dmi_kg: 22,
}

export default function Rationsoptimierung() {
  const [profile, setProfile] = useState<CowProfile>(defaultProfile)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const {
    data: feeds = [],
    isLoading: feedsLoading,
    isError: feedsError,
    error: feedsErrorDetail,
    refetch: refetchFeeds,
  } = useQuery({
    queryKey: ['rations-feeds'],
    queryFn: () => fetchFeeds(),
  })

  const optimizeMutation = useMutation({
    mutationFn: () => optimizeFromProfile(profile),
    onSuccess: (data) => {
      setResult(data)
      setError(null)
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail ?? 'Optimierung fehlgeschlagen')
      setResult(null)
    },
  })

  const demoMutation = useMutation({
    mutationFn: optimizeDemo,
    onSuccess: (data) => {
      setResult(data)
      setError(null)
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail ?? 'Demo fehlgeschlagen')
      setResult(null)
    },
  })

  const handleOptimize = () => optimizeMutation.mutate()
  const handleDemo = () => demoMutation.mutate()
  const isOptimizing = optimizeMutation.isPending || demoMutation.isPending

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Rationsoptimierung</h1>
        <p className="text-muted-foreground">
          Kostenoptimale Rationen nach GfE-2023 – für Landwirte und Berater
        </p>
      </div>

      {feedsError && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Rationsoptimierungs-Service nicht erreichbar</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <span>
              {(feedsErrorDetail as { response?: { data?: { detail?: string } }; message?: string })
                ?.response?.data?.detail ??
                (feedsErrorDetail as Error)?.message ??
                'Der Service ist möglicherweise nicht gestartet oder RATIONS_OPTIMIZATION_URL fehlt.'}
            </span>
            <Button variant="outline" size="sm" onClick={() => void refetchFeeds()} className="w-fit">
              Erneut versuchen
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Kuhprofil */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cow className="h-5 w-5" />
              Kuhprofil
            </CardTitle>
            <CardDescription>
              Tierdaten für Bedarfsberechnung und Rationsoptimierung
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Rasse</Label>
                <Select
                  value={profile.breed}
                  onValueChange={(v) => setProfile({ ...profile, breed: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {BREEDS.map((b) => (
                      <SelectItem key={b.value} value={b.value}>
                        {b.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Körpergewicht (kg)</Label>
                <Input
                  type="number"
                  value={profile.body_weight_kg}
                  onChange={(e) =>
                    setProfile({ ...profile, body_weight_kg: Number(e.target.value) || 0 })
                  }
                  min={300}
                  max={900}
                />
              </div>
              <div>
                <Label>Milchleistung (kg/Tag)</Label>
                <Input
                  type="number"
                  value={profile.milk_kg_day ?? ''}
                  onChange={(e) =>
                    setProfile({ ...profile, milk_kg_day: Number(e.target.value) || undefined })
                  }
                  placeholder="35"
                  min={0}
                  max={80}
                />
              </div>
              <div>
                <Label>Fett (%)</Label>
                <Input
                  type="number"
                  step={0.1}
                  value={profile.milk_fat_pct ?? ''}
                  onChange={(e) =>
                    setProfile({ ...profile, milk_fat_pct: Number(e.target.value) || undefined })
                  }
                  placeholder="3.8"
                />
              </div>
              <div>
                <Label>Eiweiß (%)</Label>
                <Input
                  type="number"
                  step={0.1}
                  value={profile.milk_protein_pct ?? ''}
                  onChange={(e) =>
                    setProfile({ ...profile, milk_protein_pct: Number(e.target.value) || undefined })
                  }
                  placeholder="3.2"
                />
              </div>
              <div>
                <Label>Laktationstag</Label>
                <Input
                  type="number"
                  value={profile.lactation_stage_days ?? ''}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      lactation_stage_days: Number(e.target.value) || undefined,
                    })
                  }
                  placeholder="150"
                  min={1}
                  max={400}
                />
              </div>
              <div>
                <Label>Laktation</Label>
                <Input
                  type="number"
                  value={profile.parity ?? ''}
                  onChange={(e) =>
                    setProfile({ ...profile, parity: Number(e.target.value) || undefined })
                  }
                  placeholder="2"
                  min={1}
                  max={15}
                />
              </div>
              <div>
                <Label>Ziel Futteraufnahme (kg TM/Tag)</Label>
                <Input
                  type="number"
                  step={0.1}
                  value={profile.target_dmi_kg ?? ''}
                  onChange={(e) =>
                    setProfile({ ...profile, target_dmi_kg: Number(e.target.value) || undefined })
                  }
                  placeholder="22"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleOptimize} disabled={isOptimizing}>
                {isOptimizing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Calculator className="mr-2 h-4 w-4" />
                )}
                Optimierung starten
              </Button>
              <Button variant="outline" onClick={handleDemo} disabled={isOptimizing}>
                Demo (Beispieldaten)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Futtermittel verfügbar */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Verfügbare Futtermittel
            </CardTitle>
            <CardDescription>
              {feeds.length} Futtermittel für die Optimierung
            </CardDescription>
          </CardHeader>
          <CardContent>
            {feedsLoading ? (
              <Skeleton className="h-48 w-full" />
            ) : (
              <div className="max-h-64 overflow-y-auto rounded border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Gruppe</TableHead>
                      <TableHead className="text-right">Preis €/kg TM</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {feeds.slice(0, 12).map((f) => (
                      <TableRow key={f.id}>
                        <TableCell className="font-medium">{f.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{f.group}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {f.price_eur_kgdm?.toFixed(3)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {feeds.length > 12 && (
                  <p className="p-2 text-xs text-muted-foreground">
                    + {feeds.length - 12} weitere Futtermittel
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Fehler */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Ergebnis */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result.status === 'optimal' ? (
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-amber-600" />
              )}
              Optimierungsergebnis
              <Badge variant={result.status === 'optimal' ? 'default' : 'secondary'}>
                {result.status}
              </Badge>
            </CardTitle>
            <CardDescription>
              {result.status === 'optimal'
                ? `Kosten: ${result.total_cost_eur_day?.toFixed(2) ?? '–'} €/Kuh/Tag`
                : result.warnings?.join(' ') || 'Keine Lösung gefunden'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {result.status === 'optimal' && (
              <div className="space-y-4">
                <div className="flex items-center gap-4 rounded-lg bg-muted/50 p-4">
                  <Euro className="h-8 w-8" />
                  <div>
                    <p className="text-sm text-muted-foreground">Kosten pro Kuh und Tag</p>
                    <p className="text-2xl font-bold">
                      {result.total_cost_eur_day?.toFixed(2) ?? '–'} €
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="mb-2 font-medium">Rationsvorschlag (kg TM/Tag)</h4>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Futtermittel</TableHead>
                        <TableHead className="text-right">kg TM</TableHead>
                        <TableHead className="text-right">€/Tag</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.ration_items
                        ?.filter((r) => (r.amount_kg_dm ?? 0) > 0)
                        .map((r) => (
                          <TableRow key={r.feed_id}>
                            <TableCell>{r.feed_name ?? r.feed_id}</TableCell>
                            <TableCell className="text-right">
                              {(r.amount_kg_dm ?? 0).toFixed(2)}
                            </TableCell>
                            <TableCell className="text-right">
                              {(r.daily_cost ?? 0).toFixed(2)}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </div>
                {result.nutrient_supply && Object.keys(result.nutrient_supply).length > 0 && (
                  <div>
                    <h4 className="mb-2 font-medium">Nährstoffversorgung</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(result.nutrient_supply).map(([k, v]) => (
                        <Badge key={k} variant="secondary">
                          {k}: {typeof v === 'number' ? v.toFixed(1) : v}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground">
        Entscheidungshilfe – ersetzt keine fachliche Beratung. Werte aus Beispieldaten.
      </p>
    </div>
  )
}
