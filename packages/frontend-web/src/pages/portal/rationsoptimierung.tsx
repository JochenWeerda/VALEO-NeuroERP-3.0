/**
 * Kundenportal – Rationsoptimierung (kostenlos für Landwirte)
 *
 * Vereinfachte Ansicht: Kuhprofil, Demo-Optimierung, Rationsvorschlag.
 * Fodjan-inspiriert: Rationen anpassen, Kennzahlen, Futterkosten.
 */

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
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
import { Calculator, Cow, Euro, AlertTriangle, CheckCircle2, Loader2, Gift } from 'lucide-react'

const BREEDS = [
  { value: 'Holstein', label: 'Holstein' },
  { value: 'Simmental', label: 'Fleckvieh' },
  { value: 'BrownSwiss', label: 'Braunvieh' },
]

const defaultProfile: CowProfile = {
  breed: 'Holstein',
  body_weight_kg: 650,
  milk_kg_day: 35,
  milk_fat_pct: 3.8,
  milk_protein_pct: 3.2,
  lactation_stage_days: 150,
  parity: 2,
}

export default function PortalRationsoptimierung() {
  const [profile, setProfile] = useState<CowProfile>(defaultProfile)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data: feeds = [] } = useQuery({
    queryKey: ['portal-rations-feeds'],
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

  const isOptimizing = optimizeMutation.isPending || demoMutation.isPending

  return (
    <div className="space-y-6 p-4">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold">Rationsoptimierung</h1>
          <Badge variant="secondary" className="gap-1">
            <Gift className="h-3 w-3" />
            Kostenlos
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Kostenoptimale Rationen für Ihre Milchkühe – nach GfE-2023
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Cow className="h-4 w-4" />
            Kuhprofil
          </CardTitle>
          <CardDescription>Eckdaten für die Bedarfsberechnung</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label>Rasse</Label>
              <Select value={profile.breed} onValueChange={(v) => setProfile({ ...profile, breed: v })}>
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
              <Label>Milch (kg/Tag)</Label>
              <Input
                type="number"
                value={profile.milk_kg_day ?? ''}
                onChange={(e) =>
                  setProfile({ ...profile, milk_kg_day: Number(e.target.value) || undefined })
                }
                placeholder="35"
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
              />
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => optimizeMutation.mutate()} disabled={isOptimizing} size="sm">
              {isOptimizing ? (
                <Loader2 className="mr-2 h-3 w-3 animate-spin" />
              ) : (
                <Calculator className="mr-2 h-3 w-3" />
              )}
              Optimieren
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => demoMutation.mutate()}
              disabled={isOptimizing}
            >
              Schnell-Demo
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && result.status === 'optimal' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Rationsvorschlag
            </CardTitle>
            <CardDescription>
              <span className="flex items-center gap-1">
                <Euro className="h-3 w-3" />
                {result.total_cost_eur_day?.toFixed(2) ?? '–'} € pro Kuh und Tag
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Futtermittel</TableHead>
                  <TableHead className="text-right">kg TM/Tag</TableHead>
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
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground">
        Entscheidungshilfe – ersetzt keine fachliche Beratung. Für Kunden von VALEO kostenlos.
      </p>
    </div>
  )
}
