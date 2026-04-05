/**
 * Rationsoptimierung – Professionelle ERP-Maske
 *
 * Inspiriert von fodjan, RationPRO MVP, WinMix.Cattle, MilkingCloud (2026-Recherche).
 * GfE-2023-basiert, least-cost Formulierung via PuLP-Microservice.
 *
 * Kernfeatures:
 *  - 3-stufige Nährstoff-Ampel (grün/amber/rot) mit SOLL/IST/%-Deckung
 *  - IOFC (Income over Feed Cost) als primäre Erlös-KPI
 *  - Laktationsphase-Presets (Frühwelt / Hochleistung / Spätlaktation / Trockenstehend)
 *  - Optimierungsziel-Auswahl (Kosten / Milch / Gesundheit)
 *  - Radar-Chart Nährstoffprofil (Ziel vs. IST)
 *  - Futtermittelauswahl mit Gruppenfilter + Suche
 *  - Stacked Bar: Rationszusammensetzung nach Gruppe
 */

import { useState, useEffect, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
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
  Package,
  Euro,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  BarChart3,
  Leaf,
  ClipboardCheck,
  TrendingUp,
  Target,
  Heart,
  RotateCcw,
  RefreshCw,
} from 'lucide-react'
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell,
} from 'recharts'
import {
  fetchFeeds,
  getRationsApiErrorMessage,
  optimizeDemo,
  optimizeFromProfile,
  type CowProfile,
  type OptimizationResult,
  type ConstraintReportItem,
} from '@/lib/api/rations-optimization'

// ---------------------------------------------------------------------------
// Konstanten & Typehilfen
// ---------------------------------------------------------------------------

const BREEDS = [
  { value: 'Holstein', label: 'Holstein' },
  { value: 'Simmental', label: 'Fleckvieh / Simmental' },
  { value: 'BrownSwiss', label: 'Braunvieh' },
  { value: 'Jersey', label: 'Jersey' },
]

const GROUP_OPTIONS = [
  { value: 'alle', label: 'Alle Gruppen' },
  { value: 'forage', label: 'Grundfutter' },
  { value: 'concentrate', label: 'Kraftfutter' },
  { value: 'mineral', label: 'Mineralfutter' },
  { value: 'supplement', label: 'Ergänzung' },
]

/** Laktationsphasen-Presets (fodjan-inspiriert) */
const LAKTATIONS_PRESETS = [
  { value: 'early', label: 'Frühwelt (0–70 d)', days: 35, milk: 40, fat: 3.5, protein: 3.0, dmi: 20 },
  { value: 'peak', label: 'Hochleistung (70–150 d)', days: 110, milk: 38, fat: 3.8, protein: 3.2, dmi: 22 },
  { value: 'mid', label: 'Mittellaktation (150–250 d)', days: 200, milk: 32, fat: 4.0, protein: 3.4, dmi: 21 },
  { value: 'late', label: 'Spätlaktation (>250 d)', days: 280, milk: 22, fat: 4.2, protein: 3.6, dmi: 18 },
  { value: 'dry', label: 'Trockenstehend', days: 340, milk: 0, fat: 0, protein: 0, dmi: 12 },
]

/** Optimierungsziele (fodjan / MilkingCloud -inspiriert) */
type OptimierungsZiel = 'least_cost' | 'max_milk' | 'health'

const OPTIMIERUNGS_ZIELE: { value: OptimierungsZiel; label: string; desc: string; icon: React.ReactNode }[] = [
  {
    value: 'least_cost',
    label: 'Kosten minimieren',
    desc: 'Günstigste Ration bei Bedarfsdeckung',
    icon: <Euro className="h-4 w-4" />,
  },
  {
    value: 'max_milk',
    label: 'Milchleistung',
    desc: 'ME-Maximierung für Hochleistung',
    icon: <TrendingUp className="h-4 w-4" />,
  },
  {
    value: 'health',
    label: 'Tiergesundheit',
    desc: 'Strukturversorgung, Pansenstabilität',
    icon: <Heart className="h-4 w-4" />,
  },
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

// ---------------------------------------------------------------------------
// Ampel-Helpers (3-stufig: grün / amber / rot)
// ---------------------------------------------------------------------------

type AmpelState = 'ok' | 'warn' | 'error' | 'info'

function getAmpel(item: ConstraintReportItem): AmpelState {
  if (item.fulfilled) {
    // Prüfe auf leichte Überversorgung (>115% des Ziels)
    if (item.target > 0 && item.actual > item.target * 1.15) return 'warn'
    return 'ok'
  }
  if (item.status === 'MAX_EXCEEDED') return 'warn'
  return 'error'
}

function AmpelDot({ state }: { state: AmpelState }) {
  const cls =
    state === 'ok'
      ? 'bg-emerald-500'
      : state === 'warn'
        ? 'bg-amber-400'
        : state === 'error'
          ? 'bg-red-500'
          : 'bg-slate-300'
  return <span className={`inline-block h-3 w-3 rounded-full ${cls}`} />
}

function AmpelIcon({ state }: { state: AmpelState }) {
  if (state === 'ok') return <CheckCircle2 className="h-4 w-4 text-emerald-600" />
  if (state === 'warn') return <AlertTriangle className="h-4 w-4 text-amber-500" />
  if (state === 'error') return <XCircle className="h-4 w-4 text-red-600" />
  return null
}

function pctOfTarget(actual: number, target: number): string {
  if (target <= 0) return '–'
  return `${Math.round((actual / target) * 100)} %`
}

function ampelRowClass(state: AmpelState): string {
  if (state === 'error') return 'bg-red-50'
  if (state === 'warn') return 'bg-amber-50'
  return ''
}

// ---------------------------------------------------------------------------
// Hauptkomponente
// ---------------------------------------------------------------------------

export default function Rationsoptimierung() {
  const [activeTab, setActiveTab] = useState<'eingabe' | 'ergebnis'>('eingabe')
  const [profile, setProfile] = useState<CowProfile>(defaultProfile)
  const [anzahlTiere, setAnzahlTiere] = useState(1)
  const [milchPreis, setMilchPreis] = useState(0.42) // €/kg Milch
  const [optimierungsZiel, setOptimierungsZiel] = useState<OptimierungsZiel>('least_cost')
  const [selectedFeedIds, setSelectedFeedIds] = useState<Set<string>>(new Set())
  const [groupFilter, setGroupFilter] = useState<string>('alle')
  const [nameFilter, setNameFilter] = useState('')
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Futtermittel laden
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

  // Alle Feeds initial selektieren
  useEffect(() => {
    if (feeds.length > 0 && selectedFeedIds.size === 0) {
      setSelectedFeedIds(new Set(feeds.map((f) => f.id)))
    }
  }, [feeds, selectedFeedIds.size])

  // Laktationsphase-Preset anwenden
  function applyPreset(presetValue: string) {
    const p = LAKTATIONS_PRESETS.find((x) => x.value === presetValue)
    if (!p) return
    setProfile((prev) => ({
      ...prev,
      lactation_stage_days: p.days,
      milk_kg_day: p.milk,
      milk_fat_pct: p.fat || prev.milk_fat_pct,
      milk_protein_pct: p.protein || prev.milk_protein_pct,
      target_dmi_kg: p.dmi,
    }))
  }

  // Gefilterte Feeds
  const filteredFeeds = useMemo(
    () =>
      feeds.filter(
        (f) =>
          (groupFilter === 'alle' || f.group === groupFilter) &&
          f.name.toLowerCase().includes(nameFilter.toLowerCase()),
      ),
    [feeds, groupFilter, nameFilter],
  )

  // Optimierungs-Mutation
  const optimizeMutation = useMutation({
    mutationFn: () =>
      optimizeFromProfile(
        profile,
        selectedFeedIds.size < feeds.length ? [...selectedFeedIds] : undefined,
      ),
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setActiveTab('ergebnis')
    },
    onError: (err: unknown) => {
      setError(getRationsApiErrorMessage(err, 'Optimierung fehlgeschlagen'))
      setResult(null)
    },
  })

  const demoMutation = useMutation({
    mutationFn: optimizeDemo,
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setActiveTab('ergebnis')
    },
    onError: (err: unknown) => {
      setError(getRationsApiErrorMessage(err, 'Demo fehlgeschlagen'))
    },
  })

  const isOptimizing = optimizeMutation.isPending || demoMutation.isPending

  function handleReset() {
    setProfile(defaultProfile)
    setAnzahlTiere(1)
    setMilchPreis(0.42)
    setOptimierungsZiel('least_cost')
    setResult(null)
    setError(null)
    setActiveTab('eingabe')
  }

  // Ergebnis-Derived Values
  const activeRationItems = result?.ration_items.filter((r) => r.kgdm > 0.001) ?? []
  const totalKgdm = activeRationItems.reduce((s, r) => s + r.kgdm, 0)
  const totalKgfm = activeRationItems.reduce((s, r) => s + r.kgfm, 0)
  const totalCost = activeRationItems.reduce((s, r) => s + r.total_cost, 0)

  // IOFC: Income over Feed Cost
  const milcherloes = (profile.milk_kg_day ?? 0) * milchPreis
  const iofc = milcherloes - (result?.total_cost_eur_day ?? 0)

  // Radar-Chart Daten: % der Bedarfsdeckung je Nährstoff
  const radarData = useMemo(() => {
    if (!result?.constraint_report?.length) return []
    return result.constraint_report
      .filter((c) => c.target > 0)
      .slice(0, 8)
      .map((c) => ({
        nutrient: c.name.replace(/Dry Matter.*/, 'TM').replace(/Metabolizable.*/, 'ME').replace(/Small Int.*/, 'nXP').replace(/Neutral Det.*/, 'aNDF'),
        pct: Math.min(Math.round((c.actual / c.target) * 100), 150),
        ziel: 100,
      }))
  }, [result])

  // Stacked Bar: Rationszusammensetzung nach Gruppe
  const barData = useMemo(() => {
    if (!activeRationItems.length) return []
    return activeRationItems.map((r) => {
      const feed = feeds.find((f) => f.id === r.feed_id)
      return {
        name: r.name.length > 16 ? `${r.name.slice(0, 14)}…` : r.name,
        gruppe: feed?.group ?? '–',
        kgdm: parseFloat(r.kgdm.toFixed(2)),
        anteil: totalKgdm > 0 ? parseFloat(((r.kgdm / totalKgdm) * 100).toFixed(1)) : 0,
      }
    })
  }, [activeRationItems, feeds, totalKgdm])

  const GROUP_COLORS: Record<string, string> = {
    forage: '#22c55e',
    concentrate: '#3b82f6',
    mineral: '#f59e0b',
    supplement: '#8b5cf6',
  }

  // ===========================================================================
  // RENDER
  // ===========================================================================

  return (
    <div className="space-y-4 p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Rationsoptimierung</h1>
          <p className="text-sm text-muted-foreground">
            GfE-2023 · least-cost LP-Optimierung · Ampel-Nährstoffanalyse
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => demoMutation.mutate()} disabled={isOptimizing}>
            {demoMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : null}
            Demo
          </Button>
          <Button size="sm" onClick={() => optimizeMutation.mutate()} disabled={isOptimizing || feedsLoading}>
            {optimizeMutation.isPending ? (
              <Loader2 className="mr-2 h-3 w-3 animate-spin" />
            ) : (
              <Calculator className="mr-2 h-3 w-3" />
            )}
            Optimieren
          </Button>
        </div>
      </div>

      {/* Service-Error */}
      {feedsError && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Rationsoptimierungs-Service nicht erreichbar</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <span>
              {getRationsApiErrorMessage(
                feedsErrorDetail,
                'RATIONS_OPTIMIZATION_URL möglicherweise nicht konfiguriert.',
              )}
            </span>
            <Button variant="outline" size="sm" onClick={() => void refetchFeeds()} className="w-fit">
              <RefreshCw className="mr-2 h-3 w-3" />
              Erneut versuchen
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
        <TabsList>
          <TabsTrigger value="eingabe">Eingabe</TabsTrigger>
          <TabsTrigger value="ergebnis" disabled={!result}>
            Ergebnis {result?.status === 'optimal' && <Badge className="ml-2 h-4 px-1 text-xs">✓</Badge>}
          </TabsTrigger>
        </TabsList>

        {/* ================================================================
            TAB 1: EINGABE
            ================================================================ */}
        <TabsContent value="eingabe" className="space-y-4">

          {/* Optimierungsziel – fodjan-inspirierte Zielkarten */}
          <div>
            <Label className="mb-2 block text-sm font-medium">Optimierungsziel</Label>
            <div className="grid gap-3 sm:grid-cols-3">
              {OPTIMIERUNGS_ZIELE.map((z) => (
                <button
                  key={z.value}
                  type="button"
                  onClick={() => setOptimierungsZiel(z.value)}
                  className={`flex items-start gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-muted/50 ${
                    optimierungsZiel === z.value
                      ? 'border-primary bg-primary/5 ring-1 ring-primary'
                      : 'border-border'
                  }`}
                >
                  <span className={`mt-0.5 ${optimierungsZiel === z.value ? 'text-primary' : 'text-muted-foreground'}`}>
                    {z.icon}
                  </span>
                  <div>
                    <p className="text-sm font-medium">{z.label}</p>
                    <p className="text-xs text-muted-foreground">{z.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Haupteingabe: Kuhprofil + Futtermittelauswahl */}
          <div className="grid gap-4 lg:grid-cols-5">

            {/* ── Kuhprofil (2/5) ── */}
            <div className="space-y-4 lg:col-span-2">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Milk className="h-4 w-4" />
                    Kuhprofil
                  </CardTitle>
                  <CardDescription>Tierdaten für Bedarfsberechnung (GfE-2023)</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">

                  {/* Laktationsphase-Preset – fodjan-inspiriert */}
                  <div>
                    <Label className="text-xs text-muted-foreground">Laktationsphase-Preset</Label>
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
                      <Select
                        value={profile.breed}
                        onValueChange={(v) => setProfile({ ...profile, breed: v })}
                      >
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
                        onChange={(e) =>
                          setProfile({ ...profile, body_weight_kg: Number(e.target.value) || 0 })
                        }
                        min={300}
                        max={900}
                      />
                    </div>
                    <div>
                      <Label className="text-xs">Milchleistung (kg/Tag)</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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
                      <Label className="text-xs">Fett (%)</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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
                      <Label className="text-xs">Eiweiß (%)</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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
                      <Label className="text-xs">Laktationstag</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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
                      <Label className="text-xs">Laktation Nr.</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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
                      <Label className="text-xs">Ziel-TM (kg/Tag)</Label>
                      <Input
                        className="mt-1 h-8 text-xs"
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

                  {/* Herden- und Wirtschaftlichkeitsparameter */}
                  <div className="border-t pt-3">
                    <p className="mb-2 text-xs font-medium text-muted-foreground">
                      Wirtschaftlichkeit (IOFC)
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div>
                        <Label className="text-xs">Anzahl Tiere</Label>
                        <Input
                          className="mt-1 h-8 text-xs"
                          type="number"
                          value={anzahlTiere}
                          onChange={(e) => setAnzahlTiere(Math.max(1, Number(e.target.value) || 1))}
                          min={1}
                          max={10000}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Milchpreis (€/kg)</Label>
                        <Input
                          className="mt-1 h-8 text-xs"
                          type="number"
                          step={0.01}
                          value={milchPreis}
                          onChange={(e) => setMilchPreis(Number(e.target.value) || 0.42)}
                          min={0.1}
                          max={1.0}
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* ── Futtermittelauswahl (3/5) ── */}
            <div className="lg:col-span-3">
              <Card className="h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Package className="h-4 w-4" />
                      Futtermittelauswahl
                    </CardTitle>
                    <Badge variant="outline" className="text-xs">
                      {selectedFeedIds.size} / {feeds.length} ausgewählt
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  {feedsLoading ? (
                    <div className="space-y-2">
                      {[...Array(6)].map((_, i) => (
                        <Skeleton key={i} className="h-8 w-full" />
                      ))}
                    </div>
                  ) : (
                    <>
                      {/* Filter-Toolbar */}
                      <div className="mb-3 flex flex-wrap gap-2">
                        <Select value={groupFilter} onValueChange={setGroupFilter}>
                          <SelectTrigger className="h-7 w-40 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {GROUP_OPTIONS.map((g) => (
                              <SelectItem key={g.value} value={g.value} className="text-xs">
                                {g.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Input
                          className="h-7 flex-1 text-xs"
                          placeholder="Futtermittel suchen…"
                          value={nameFilter}
                          onChange={(e) => setNameFilter(e.target.value)}
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => setSelectedFeedIds(new Set(feeds.map((f) => f.id)))}
                        >
                          Alle
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => setSelectedFeedIds(new Set())}
                        >
                          Keine
                        </Button>
                      </div>

                      {/* Feed-Tabelle */}
                      <div className="max-h-72 overflow-y-auto rounded border">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead className="w-8 px-2" />
                              <TableHead className="text-xs">Name</TableHead>
                              <TableHead className="text-xs">Gruppe</TableHead>
                              <TableHead className="text-right text-xs">TM%</TableHead>
                              <TableHead className="text-right text-xs">ME</TableHead>
                              <TableHead className="text-right text-xs">€/kg TM</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {filteredFeeds.map((f) => {
                              const checked = selectedFeedIds.has(f.id)
                              const groupColor = GROUP_COLORS[f.group] ?? '#94a3b8'
                              return (
                                <TableRow
                                  key={f.id}
                                  className={`cursor-pointer transition-colors hover:bg-muted/40 ${checked ? '' : 'opacity-50'}`}
                                  onClick={() => {
                                    const next = new Set(selectedFeedIds)
                                    if (checked) {
                                      next.delete(f.id)
                                    } else {
                                      next.add(f.id)
                                    }
                                    setSelectedFeedIds(next)
                                  }}
                                >
                                  <TableCell className="px-2">
                                    <Checkbox
                                      checked={checked}
                                      onCheckedChange={() => {
                                        const next = new Set(selectedFeedIds)
                                        if (checked) {
                                          next.delete(f.id)
                                        } else {
                                          next.add(f.id)
                                        }
                                        setSelectedFeedIds(next)
                                      }}
                                    />
                                  </TableCell>
                                  <TableCell className="py-1 text-xs font-medium">{f.name}</TableCell>
                                  <TableCell className="py-1">
                                    <span
                                      className="rounded px-1.5 py-0.5 text-xs text-white"
                                      style={{ backgroundColor: groupColor }}
                                    >
                                      {f.group}
                                    </span>
                                  </TableCell>
                                  <TableCell className="py-1 text-right text-xs">
                                    {(f.dm_frac * 100).toFixed(0)}
                                  </TableCell>
                                  <TableCell className="py-1 text-right text-xs">
                                    {f.me_mj_kgdm?.toFixed(1)}
                                  </TableCell>
                                  <TableCell className="py-1 text-right text-xs font-mono">
                                    {f.price_eur_kgdm?.toFixed(3)}
                                  </TableCell>
                                </TableRow>
                              )
                            })}
                            {filteredFeeds.length === 0 && (
                              <TableRow>
                                <TableCell colSpan={6} className="py-6 text-center text-xs text-muted-foreground">
                                  Keine Futtermittel gefunden
                                </TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Aktionsleiste */}
          <div className="flex flex-wrap items-center gap-3 rounded-lg border bg-muted/30 p-3">
            <Button
              onClick={() => optimizeMutation.mutate()}
              disabled={isOptimizing || feedsLoading || selectedFeedIds.size === 0}
            >
              {optimizeMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Calculator className="mr-2 h-4 w-4" />
              )}
              Optimierung starten
            </Button>
            <Button variant="outline" onClick={() => demoMutation.mutate()} disabled={isOptimizing}>
              Demo (Beispieldaten)
            </Button>
            <Button variant="ghost" onClick={handleReset} disabled={isOptimizing}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Zurücksetzen
            </Button>
            {selectedFeedIds.size === 0 && (
              <span className="text-xs text-destructive">
                Mindestens ein Futtermittel auswählen
              </span>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Fehler</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </TabsContent>

        {/* ================================================================
            TAB 2: ERGEBNIS
            ================================================================ */}
        <TabsContent value="ergebnis" className="space-y-6">

          {/* Nicht-optimales Ergebnis */}
          {result && result.status !== 'optimal' && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Optimierung nicht erfolgreich: {result.status}</AlertTitle>
              <AlertDescription>
                {result.warnings?.length > 0 ? (
                  <ul className="mt-1 list-disc pl-4 text-sm">
                    {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                ) : (
                  'Keine zulässige Lösung gefunden. Prüfen Sie Futtermittelauswahl und Restriktionen.'
                )}
              </AlertDescription>
            </Alert>
          )}

          {result?.status === 'optimal' && (
            <>
              {/* ── KPI-Leiste (5 Kacheln) ── */}
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                {/* Kosten/Kuh/Tag */}
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Futterkosten/Kuh/Tag</p>
                    <p className="mt-1 text-xl font-bold">
                      {result.total_cost_eur_day?.toFixed(2) ?? '–'} €
                    </p>
                  </CardContent>
                </Card>
                {/* IOFC – Income over Feed Cost */}
                <Card className={iofc >= 0 ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">IOFC (Deckungsbeitrag)</p>
                    <p className={`mt-1 text-xl font-bold ${iofc >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>
                      {iofc.toFixed(2)} €
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Milcherlös {milcherloes.toFixed(2)} € − Futter {result.total_cost_eur_day?.toFixed(2)} €
                    </p>
                  </CardContent>
                </Card>
                {/* Kosten/Herde/Tag */}
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">Futterkosten/Herde/Tag</p>
                    <p className="mt-1 text-xl font-bold">
                      {((result.total_cost_eur_day ?? 0) * anzahlTiere).toFixed(2)} €
                    </p>
                    <p className="text-xs text-muted-foreground">{anzahlTiere} Tiere</p>
                  </CardContent>
                </Card>
                {/* TM-Aufnahme */}
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">TM-Aufnahme</p>
                    <p className="mt-1 text-xl font-bold">
                      {result.nutrient_supply.dmi_kg.toFixed(1)} kg
                    </p>
                  </CardContent>
                </Card>
                {/* GF-Anteil */}
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground">GF-Anteil</p>
                    <p className="mt-1 text-xl font-bold">
                      {result.nutrient_supply.forage_share_pct.toFixed(1)} %
                    </p>
                    <p className={`text-xs ${result.nutrient_supply.forage_share_pct >= 40 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {result.nutrient_supply.forage_share_pct >= 40 ? '✓ ≥ 40% (GfE)' : '✗ < 40% (GfE-Min.)'}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* ── Charts + Rationsvorschlag ── */}
              <div className="grid gap-4 lg:grid-cols-2">

                {/* Rationsvorschlag-Tabelle */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <BarChart3 className="h-4 w-4" />
                      Rationsvorschlag
                    </CardTitle>
                    <CardDescription>
                      {activeRationItems.length} Futtermittel · {totalKgdm.toFixed(1)} kg TM/Tag
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
                          <TableHead className="text-right text-xs">Anteil</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {activeRationItems.map((r) => {
                          const feed = feeds.find((f) => f.id === r.feed_id)
                          const anteil = totalKgdm > 0 ? (r.kgdm / totalKgdm) * 100 : 0
                          const groupColor = GROUP_COLORS[feed?.group ?? ''] ?? '#94a3b8'
                          return (
                            <TableRow key={r.feed_id}>
                              <TableCell className="py-1 text-xs">
                                <div className="flex items-center gap-1.5">
                                  <span
                                    className="inline-block h-2 w-2 rounded-full"
                                    style={{ backgroundColor: groupColor }}
                                  />
                                  {r.name}
                                </div>
                              </TableCell>
                              <TableCell className="py-1 text-right text-xs font-mono">
                                {r.kgdm.toFixed(2)}
                              </TableCell>
                              <TableCell className="py-1 text-right text-xs font-mono text-muted-foreground">
                                {r.kgfm.toFixed(2)}
                              </TableCell>
                              <TableCell className="py-1 text-right text-xs font-mono">
                                {r.total_cost.toFixed(2)}
                              </TableCell>
                              <TableCell className="py-1 text-right text-xs">
                                <div className="flex items-center justify-end gap-1">
                                  <div
                                    className="h-1.5 rounded-full bg-primary"
                                    style={{ width: `${Math.max(anteil * 1.5, 4)}px` }}
                                  />
                                  {anteil.toFixed(1)}%
                                </div>
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                      <TableFooter>
                        <TableRow className="font-medium">
                          <TableCell className="text-xs">Gesamt</TableCell>
                          <TableCell className="text-right text-xs font-mono">{totalKgdm.toFixed(2)}</TableCell>
                          <TableCell className="text-right text-xs font-mono text-muted-foreground">{totalKgfm.toFixed(2)}</TableCell>
                          <TableCell className="text-right text-xs font-mono">{totalCost.toFixed(2)}</TableCell>
                          <TableCell className="text-right text-xs">100%</TableCell>
                        </TableRow>
                      </TableFooter>
                    </Table>
                  </CardContent>
                </Card>

                {/* Stacked Bar: Zusammensetzung */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <BarChart3 className="h-4 w-4" />
                      Rationszusammensetzung
                    </CardTitle>
                    <CardDescription>kg TM/Tag je Futtermittel</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={barData} layout="vertical" margin={{ left: 0, right: 20 }}>
                        <XAxis type="number" tick={{ fontSize: 10 }} unit=" kg" />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={90} />
                        <Tooltip
                          formatter={(value: number) => [`${value.toFixed(2)} kg TM`, '']}
                          contentStyle={{ fontSize: 11 }}
                        />
                        <Bar dataKey="kgdm" radius={[0, 3, 3, 0]}>
                          {barData.map((entry, i) => (
                            <Cell
                              key={i}
                              fill={GROUP_COLORS[entry.gruppe] ?? '#94a3b8'}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    {/* Legende */}
                    <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
                      {Object.entries(GROUP_COLORS).map(([g, c]) => (
                        <span key={g} className="flex items-center gap-1">
                          <span className="inline-block h-2 w-3 rounded" style={{ backgroundColor: c }} />
                          {GROUP_OPTIONS.find((o) => o.value === g)?.label ?? g}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* ── Nährstoffampel + Radar ── */}
              <div className="grid gap-4 lg:grid-cols-2">

                {/* Nährstoff-Ampel Tabelle (WinMix / RationPRO-inspiriert) */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Leaf className="h-4 w-4" />
                      Nährstoffampel
                    </CardTitle>
                    <CardDescription>
                      SOLL/IST-Vergleich · 3-stufige Ampel nach GfE-2023
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-6 px-1" />
                          <TableHead className="text-xs">Nährstoff</TableHead>
                          <TableHead className="text-right text-xs">SOLL</TableHead>
                          <TableHead className="text-right text-xs">IST</TableHead>
                          <TableHead className="text-right text-xs">Deckung</TableHead>
                          <TableHead className="w-6 px-1" />
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {result.constraint_report.map((c) => {
                          const ampel = getAmpel(c)
                          return (
                            <TableRow key={c.name} className={ampelRowClass(ampel)}>
                              <TableCell className="px-1 py-1">
                                <AmpelDot state={ampel} />
                              </TableCell>
                              <TableCell className="py-1 text-xs">{c.name}</TableCell>
                              <TableCell className="py-1 text-right font-mono text-xs text-muted-foreground">
                                {c.target.toFixed(1)}
                              </TableCell>
                              <TableCell className="py-1 text-right font-mono text-xs font-medium">
                                {c.actual.toFixed(1)}
                              </TableCell>
                              <TableCell className={`py-1 text-right text-xs font-medium ${
                                ampel === 'ok' ? 'text-emerald-700' : ampel === 'warn' ? 'text-amber-700' : 'text-red-700'
                              }`}>
                                {pctOfTarget(c.actual, c.target)}
                              </TableCell>
                              <TableCell className="px-1 py-1">
                                <AmpelIcon state={ampel} />
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                    {/* Ampel-Legende */}
                    <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><AmpelDot state="ok" /> Optimal (95–115%)</span>
                      <span className="flex items-center gap-1"><AmpelDot state="warn" /> Leichte Abweichung</span>
                      <span className="flex items-center gap-1"><AmpelDot state="error" /> Defizit / Mangel</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Radar-Chart Nährstoffprofil (fodjan-inspiriert) */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Target className="h-4 w-4" />
                      Nährstoffprofil
                    </CardTitle>
                    <CardDescription>% der GfE-Bedarfsdeckung – Ziel = 100%</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {radarData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={240}>
                        <RadarChart data={radarData}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="nutrient" tick={{ fontSize: 10 }} />
                          <Radar
                            name="Ziel"
                            dataKey="ziel"
                            stroke="#94a3b8"
                            fill="#94a3b8"
                            fillOpacity={0.1}
                            strokeDasharray="4 2"
                          />
                          <Radar
                            name="IST"
                            dataKey="pct"
                            stroke="#22c55e"
                            fill="#22c55e"
                            fillOpacity={0.25}
                          />
                          <Legend wrapperStyle={{ fontSize: 11 }} />
                          <Tooltip
                            formatter={(v: number) => [`${v}%`, '']}
                            contentStyle={{ fontSize: 11 }}
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="py-8 text-center text-xs text-muted-foreground">
                        Keine Constraint-Daten für Radar verfügbar
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* ── Warnungen ── */}
              {result.warnings?.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Hinweise des Optimierers</AlertTitle>
                  <AlertDescription>
                    <ul className="mt-1 list-disc pl-4 text-sm">
                      {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>

      <p className="text-xs text-muted-foreground">
        Entscheidungshilfe nach GfE-2023 · ersetzt keine fachliche Beratung ·
        IOFC = (Milch × Milchpreis) − Futterkosten
      </p>
    </div>
  )
}
