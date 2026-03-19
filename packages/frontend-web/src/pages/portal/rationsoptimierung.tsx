/**
 * Kundenportal – Rationsoptimierung (kostenlos für Landwirte)
 *
 * Inspiriert von fodjan "Schnell-Demo", RationPRO MVP.
 * Vereinfachter 2-Schritt-Flow mit Ampel-Nährstoffanzeige und IOFC.
 */

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  optimizeDemo,
  optimizeFromProfile,
  type CowProfile,
  type OptimizationResult,
  type ConstraintReportItem,
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
import {
  Calculator,
  Milk,
  Euro,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  Gift,
  ArrowLeft,
  TrendingUp,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Konstanten
// ---------------------------------------------------------------------------

const BREEDS = [
  { value: 'Holstein', label: 'Holstein' },
  { value: 'Simmental', label: 'Fleckvieh' },
  { value: 'BrownSwiss', label: 'Braunvieh' },
  { value: 'Jersey', label: 'Jersey' },
]

const LAKTATIONS_PRESETS = [
  { value: 'early', label: 'Frühwelt (0–70 d)', days: 35, milk: 40, dmi: 20 },
  { value: 'peak', label: 'Hochleistung (70–150 d)', days: 110, milk: 38, dmi: 22 },
  { value: 'mid', label: 'Mittellaktation', days: 200, milk: 32, dmi: 21 },
  { value: 'late', label: 'Spätlaktation', days: 280, milk: 22, dmi: 18 },
  { value: 'dry', label: 'Trockenstehend', days: 340, milk: 0, dmi: 12 },
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

// ---------------------------------------------------------------------------
// Ampel-Helpers
// ---------------------------------------------------------------------------

type AmpelState = 'ok' | 'warn' | 'error'

function getAmpel(item: ConstraintReportItem): AmpelState {
  if (item.fulfilled) {
    if (item.target > 0 && item.actual > item.target * 1.15) return 'warn'
    return 'ok'
  }
  if (item.status === 'MAX_EXCEEDED') return 'warn'
  return 'error'
}

function AmpelDot({ state }: { state: AmpelState }) {
  const cls =
    state === 'ok' ? 'bg-emerald-500' : state === 'warn' ? 'bg-amber-400' : 'bg-red-500'
  return <span className={`inline-block h-3 w-3 rounded-full ${cls}`} />
}

// ---------------------------------------------------------------------------
// Hauptkomponente
// ---------------------------------------------------------------------------

export default function PortalRationsoptimierung() {
  const [step, setStep] = useState<'eingabe' | 'ergebnis'>('eingabe')
  const [profile, setProfile] = useState<CowProfile>(defaultProfile)
  const [milchPreis, setMilchPreis] = useState(0.42)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  function applyPreset(value: string) {
    const p = LAKTATIONS_PRESETS.find((x) => x.value === value)
    if (!p) return
    setProfile((prev) => ({
      ...prev,
      lactation_stage_days: p.days,
      milk_kg_day: p.milk,
      target_dmi_kg: p.dmi,
    }))
  }

  const optimizeMutation = useMutation({
    mutationFn: () => optimizeFromProfile(profile),
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setStep('ergebnis')
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail ?? 'Optimierung fehlgeschlagen')
    },
  })

  const demoMutation = useMutation({
    mutationFn: optimizeDemo,
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setStep('ergebnis')
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail ?? 'Demo fehlgeschlagen')
    },
  })

  const isOptimizing = optimizeMutation.isPending || demoMutation.isPending

  // IOFC
  const milcherloes = (profile.milk_kg_day ?? 0) * milchPreis
  const iofc = milcherloes - (result?.total_cost_eur_day ?? 0)
  const activeItems = result?.ration_items.filter((r) => r.kgdm > 0.001) ?? []

  // ── SCHRITT 1: EINGABE ──
  if (step === 'eingabe') {
    return (
      <div className="mx-auto max-w-lg space-y-4 p-4">
        {/* Header */}
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
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Milk className="h-4 w-4" />
              Kuhprofil
            </CardTitle>
            <CardDescription>Eckdaten für die Bedarfsberechnung</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Preset */}
            <div>
              <Label className="text-xs text-muted-foreground">Laktationsphase (Schnellwahl)</Label>
              <Select onValueChange={applyPreset}>
                <SelectTrigger className="mt-1 h-8 text-xs">
                  <SelectValue placeholder="Preset wählen…" />
                </SelectTrigger>
                <SelectContent>
                  {LAKTATIONS_PRESETS.map((p) => (
                    <SelectItem key={p.value} value={p.value} className="text-xs">
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label className="text-xs">Rasse</Label>
                <Select value={profile.breed} onValueChange={(v) => setProfile({ ...profile, breed: v })}>
                  <SelectTrigger className="mt-1 h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {BREEDS.map((b) => (
                      <SelectItem key={b.value} value={b.value} className="text-xs">
                        {b.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Körpergewicht (kg)</Label>
                <Input
                  className="mt-1 h-8 text-xs"
                  type="number"
                  value={profile.body_weight_kg}
                  onChange={(e) => setProfile({ ...profile, body_weight_kg: Number(e.target.value) || 0 })}
                  min={300}
                  max={900}
                />
              </div>
              <div>
                <Label className="text-xs">Milch (kg/Tag)</Label>
                <Input
                  className="mt-1 h-8 text-xs"
                  type="number"
                  value={profile.milk_kg_day ?? ''}
                  onChange={(e) => setProfile({ ...profile, milk_kg_day: Number(e.target.value) || undefined })}
                  placeholder="35"
                />
              </div>
              <div>
                <Label className="text-xs">Fett (%)</Label>
                <Input
                  className="mt-1 h-8 text-xs"
                  type="number"
                  step={0.1}
                  value={profile.milk_fat_pct ?? ''}
                  onChange={(e) => setProfile({ ...profile, milk_fat_pct: Number(e.target.value) || undefined })}
                  placeholder="3.8"
                />
              </div>
              <div>
                <Label className="text-xs">Eiweiß (%)</Label>
                <Input
                  className="mt-1 h-8 text-xs"
                  type="number"
                  step={0.1}
                  value={profile.milk_protein_pct ?? ''}
                  onChange={(e) => setProfile({ ...profile, milk_protein_pct: Number(e.target.value) || undefined })}
                  placeholder="3.2"
                />
              </div>
              <div>
                <Label className="text-xs">Laktationstag</Label>
                <Input
                  className="mt-1 h-8 text-xs"
                  type="number"
                  value={profile.lactation_stage_days ?? ''}
                  onChange={(e) => setProfile({ ...profile, lactation_stage_days: Number(e.target.value) || undefined })}
                  placeholder="150"
                />
              </div>
            </div>

            {/* Milchpreis für IOFC */}
            <div className="border-t pt-3">
              <Label className="text-xs text-muted-foreground">Milchpreis (€/kg) für Deckungsbeitrag</Label>
              <Input
                className="mt-1 h-8 w-32 text-xs"
                type="number"
                step={0.01}
                value={milchPreis}
                onChange={(e) => setMilchPreis(Number(e.target.value) || 0.42)}
                min={0.1}
                max={1.0}
              />
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              <Button
                size="sm"
                onClick={() => optimizeMutation.mutate()}
                disabled={isOptimizing}
              >
                {optimizeMutation.isPending ? (
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
                {demoMutation.isPending ? <Loader2 className="mr-2 h-3 w-3 animate-spin" /> : null}
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

        <p className="text-xs text-muted-foreground">
          Entscheidungshilfe – ersetzt keine fachliche Beratung. Für VALEO-Kunden kostenlos.
        </p>
      </div>
    )
  }

  // ── SCHRITT 2: ERGEBNIS ──
  return (
    <div className="mx-auto max-w-lg space-y-4 p-4">
      {/* Back */}
      <Button variant="ghost" size="sm" onClick={() => setStep('eingabe')}>
        <ArrowLeft className="mr-2 h-3 w-3" />
        Neue Berechnung
      </Button>

      {result && result.status !== 'optimal' && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Keine optimale Lösung: {result.status}</AlertTitle>
          <AlertDescription>
            {result.warnings?.join(' ') || 'Prüfen Sie die Eingaben.'}
          </AlertDescription>
        </Alert>
      )}

      {result?.status === 'optimal' && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 gap-3">
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <Euro className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Futterkosten/Tag</p>
                    <p className="text-lg font-bold">{result.total_cost_eur_day?.toFixed(2)} €</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className={iofc >= 0 ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className={`h-4 w-4 ${iofc >= 0 ? 'text-emerald-600' : 'text-red-600'}`} />
                  <div>
                    <p className="text-xs text-muted-foreground">IOFC (DB/Tag)</p>
                    <p className={`text-lg font-bold ${iofc >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>
                      {iofc.toFixed(2)} €
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Rationsvorschlag */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Rationsvorschlag</CardTitle>
              <CardDescription className="text-xs">
                {activeItems.length} Futtermittel · {result.total_cost_eur_day?.toFixed(2)} €/Kuh/Tag
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-xs">Futtermittel</TableHead>
                    <TableHead className="text-right text-xs">kg TM</TableHead>
                    <TableHead className="text-right text-xs">kg FM</TableHead>
                    <TableHead className="text-right text-xs">€/Tag</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeItems.map((r) => (
                    <TableRow key={r.feed_id}>
                      <TableCell className="py-1 text-xs">{r.name}</TableCell>
                      <TableCell className="py-1 text-right font-mono text-xs">{r.kgdm.toFixed(2)}</TableCell>
                      <TableCell className="py-1 text-right font-mono text-xs text-muted-foreground">{r.kgfm.toFixed(2)}</TableCell>
                      <TableCell className="py-1 text-right font-mono text-xs">{r.total_cost.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Nährstoffampel (vereinfacht) */}
          {result.constraint_report.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Nährstoffampel</CardTitle>
                <CardDescription className="text-xs">GfE-Bedarfsdeckung</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-1.5">
                  {result.constraint_report.map((c) => {
                    const ampel = getAmpel(c)
                    const pct = c.target > 0 ? Math.round((c.actual / c.target) * 100) : null
                    return (
                      <div key={c.name} className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <AmpelDot state={ampel} />
                          <span className="truncate text-xs">{c.name}</span>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className={`text-xs font-medium ${
                            ampel === 'ok' ? 'text-emerald-700' : ampel === 'warn' ? 'text-amber-700' : 'text-red-700'
                          }`}>
                            {pct !== null ? `${pct}%` : c.status}
                          </span>
                          {ampel === 'ok' ? (
                            <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                          ) : (
                            <XCircle className="h-3 w-3 text-red-500" />
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-3 flex gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><AmpelDot state="ok" /> Optimal</span>
                  <span className="flex items-center gap-1"><AmpelDot state="warn" /> Abweichung</span>
                  <span className="flex items-center gap-1"><AmpelDot state="error" /> Mangel</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Warnungen */}
          {result.warnings?.length > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle className="text-sm">Hinweise</AlertTitle>
              <AlertDescription className="text-xs">
                <ul className="mt-1 list-disc pl-4">
                  {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </>
      )}

      <p className="text-xs text-muted-foreground">
        IOFC = Milcherlös ({milchPreis.toFixed(2)} €/kg) minus Futterkosten ·
        Entscheidungshilfe nach GfE-2023
      </p>
    </div>
  )
}
