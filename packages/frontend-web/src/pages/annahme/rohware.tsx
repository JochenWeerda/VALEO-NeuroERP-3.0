import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, Package, Truck } from 'lucide-react'

type RohwareFormState = {
  // Schritt 1
  lieferant: string
  kennzeichen: string
  lieferscheinNr: string
  datum: string
  // Schritt 2
  artikel: string
  bruttoKg: number
  taraKg: number
  lagerZiel: string
  // Schritt 3
  feuchtePct: string
  besatzPct: string
  fallzahl: string
}

type HarvestAcceptanceResponse = {
  id: string
  acceptance_number?: string
  status?: string
}

const ARTIKEL_OPTIONEN = [
  'Weizen',
  'Gerste',
  'Raps',
  'Mais',
  'Sonnenblumen',
  'Sonstige',
] as const

const LAGER_OPTIONEN = [
  'Silo 1',
  'Silo 2',
  'Hauptlager',
  'Außenlager',
] as const

export default function RohwareAnnahmePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const [form, setForm] = useState<RohwareFormState>({
    lieferant: '',
    kennzeichen: '',
    lieferscheinNr: '',
    datum: new Date().toISOString().slice(0, 16),
    artikel: 'Weizen',
    bruttoKg: 0,
    taraKg: 0,
    lagerZiel: 'Silo 1',
    feuchtePct: '',
    besatzPct: '',
    fallzahl: '',
  })
  const [acceptanceResult, setAcceptanceResult] = useState<HarvestAcceptanceResponse | null>(null)

  function updateField<K extends keyof RohwareFormState>(
    key: K,
    value: RohwareFormState[K],
  ): void {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const nettoKg = useMemo(
    () => Math.max(0, form.bruttoKg - form.taraKg),
    [form.bruttoKg, form.taraKg],
  )

  const createAcceptance = useMutation({
    mutationFn: async () => {
      const payload = {
        acceptance_mode: 'STORAGE_ONLY',
        artikel: form.artikel,
        brutto_kg: form.bruttoKg,
        tara_kg: form.taraKg,
        netto_kg: nettoKg,
        feuchte_pct: form.feuchtePct ? Number(form.feuchtePct) : null,
        besatz_pct: form.besatzPct ? Number(form.besatzPct) : null,
        fallzahl: form.fallzahl ? Number(form.fallzahl) : null,
        lieferant: form.lieferant,
        kennzeichen: form.kennzeichen,
        lieferschein_nr: form.lieferscheinNr,
        lager_ziel: form.lagerZiel,
        datum: form.datum || new Date().toISOString(),
        is_rohware: true,
      }
      return (await apiClient.post<HarvestAcceptanceResponse>('/api/v1/harvest-acceptance', payload)).data
    },
    onSuccess: (data) => {
      setAcceptanceResult(data)
      toast({
        title: 'Rohware-Annahme gespeichert',
        description: `Annahmenummer: ${data.acceptance_number ?? data.id}`,
      })
    },
    onError: (e: unknown) => {
      const message = e instanceof Error ? e.message : 'Unbekannter Fehler'
      toast({ title: 'Fehler beim Speichern', description: message, variant: 'destructive' })
    },
  })

  async function handleFinish(): Promise<void> {
    createAcceptance.mutate()
  }

  if (acceptanceResult) {
    const acceptanceNumber = acceptanceResult.acceptance_number ?? acceptanceResult.id
    return (
      <div className="p-6">
        <ModuleToolbar
          backTarget="/annahme/warteschlange"
          closeTarget="/annahme/warteschlange"
          title="Rohware-Annahme"
        />
        <Card className="mx-auto max-w-md mt-8">
          <CardContent className="pt-8 pb-8 flex flex-col items-center gap-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-600" />
            <div>
              <h2 className="text-xl font-bold">Rohware erfolgreich angenommen</h2>
              <p className="text-muted-foreground mt-1">
                Annahmenummer: <span className="font-semibold">{acceptanceNumber}</span>
              </p>
            </div>
            <div className="w-full rounded-md bg-muted p-4 text-sm text-left space-y-1">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lieferant</span>
                <span className="font-semibold">{form.lieferant}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Kennzeichen</span>
                <span className="font-semibold">{form.kennzeichen}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Artikel</span>
                <span className="font-semibold">{form.artikel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Nettogewicht</span>
                <span className="font-semibold">{nettoKg.toLocaleString('de-DE')} kg</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lagerziel</span>
                <span className="font-semibold">{form.lagerZiel}</span>
              </div>
            </div>
            <div className="flex gap-2 w-full">
              <Button
                variant="outline"
                onClick={() =>
                  navigate('/annahme/abrechnung', {
                    state: {
                      fromQualitaetsCheck: true,
                      artikel: form.artikel,
                      feuchtigkeit: form.feuchtePct ? Number(form.feuchtePct) : 0,
                      verunreinigung: form.besatzPct ? Number(form.besatzPct) : 0,
                    },
                  })
                }
                className="flex-1"
              >
                Zur Abrechnung
              </Button>
              <Button onClick={() => navigate('/annahme/warteschlange')} className="flex-1">
                Zur Warteschlange
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const steps = [
    {
      id: 'lieferant-fahrzeug',
      title: 'Lieferant & Fahrzeug',
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-center mb-2">
            <Truck className="h-16 w-16 text-muted-foreground" />
          </div>
          <div>
            <Label htmlFor="lieferant">Lieferant *</Label>
            <Input
              id="lieferant"
              value={form.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder="Name des Lieferanten"
              required
            />
          </div>
          <div>
            <Label htmlFor="kennzeichen">Kennzeichen *</Label>
            <Input
              id="kennzeichen"
              value={form.kennzeichen}
              onChange={(e) => updateField('kennzeichen', e.target.value.toUpperCase())}
              placeholder="z.B. AB-CD 1234"
              className="font-semibold"
              required
            />
          </div>
          <div>
            <Label htmlFor="lieferscheinNr">Lieferschein-Nr.</Label>
            <Input
              id="lieferscheinNr"
              value={form.lieferscheinNr}
              onChange={(e) => updateField('lieferscheinNr', e.target.value)}
              placeholder="z.B. LS-2026-0042"
            />
          </div>
          <div>
            <Label htmlFor="datum">Datum/Uhrzeit</Label>
            <Input
              id="datum"
              type="datetime-local"
              value={form.datum}
              onChange={(e) => updateField('datum', e.target.value)}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'ware-gewicht',
      title: 'Ware & Gewicht',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="artikel">Artikel *</Label>
            <select
              id="artikel"
              value={form.artikel}
              onChange={(e) => updateField('artikel', e.target.value)}
              className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {ARTIKEL_OPTIONEN.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="bruttoKg">Bruttogewicht (kg) *</Label>
              <Input
                id="bruttoKg"
                type="number"
                min="0"
                step="1"
                value={form.bruttoKg || ''}
                onChange={(e) => updateField('bruttoKg', Number(e.target.value))}
                placeholder="0"
              />
            </div>
            <div>
              <Label htmlFor="taraKg">Taragewicht (kg) *</Label>
              <Input
                id="taraKg"
                type="number"
                min="0"
                step="1"
                value={form.taraKg || ''}
                onChange={(e) => updateField('taraKg', Number(e.target.value))}
                placeholder="0"
              />
            </div>
          </div>
          <div className="rounded-md bg-muted p-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Nettogewicht (berechnet)</span>
              <span className="text-lg font-bold">{nettoKg.toLocaleString('de-DE')} kg</span>
            </div>
          </div>
          <div>
            <Label htmlFor="lagerZiel">Lager-Ziel *</Label>
            <select
              id="lagerZiel"
              value={form.lagerZiel}
              onChange={(e) => updateField('lagerZiel', e.target.value)}
              className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {LAGER_OPTIONEN.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'qualitaet',
      title: 'Qualitätswerte',
      content: (
        <div className="space-y-4">
          <div className="rounded-md bg-blue-50 border border-blue-200 p-3 text-sm text-blue-900">
            <p className="font-semibold">Rohware-Annahme ohne Vollanalyse</p>
            <p className="mt-1 text-blue-700">
              Qualitätswerte sind optional. Vollständige Laboranalyse kann nachträglich ergänzt
              werden.
            </p>
          </div>
          <div>
            <Label htmlFor="feuchtePct">Feuchte % (optional)</Label>
            <Input
              id="feuchtePct"
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={form.feuchtePct}
              onChange={(e) => updateField('feuchtePct', e.target.value)}
              placeholder="z.B. 14.5"
            />
          </div>
          <div>
            <Label htmlFor="besatzPct">Besatz % (optional)</Label>
            <Input
              id="besatzPct"
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={form.besatzPct}
              onChange={(e) => updateField('besatzPct', e.target.value)}
              placeholder="z.B. 2.0"
            />
          </div>
          <div>
            <Label htmlFor="fallzahl">Fallzahl (optional)</Label>
            <Input
              id="fallzahl"
              type="number"
              min="0"
              step="1"
              value={form.fallzahl}
              onChange={(e) => updateField('fallzahl', e.target.value)}
              placeholder="z.B. 250"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'uebersicht',
      title: 'Übersicht & Abschluss',
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-center">
            <Package className="h-16 w-16 text-muted-foreground" />
          </div>
          <Card>
            <CardContent className="pt-4 space-y-2">
              <h3 className="font-semibold text-lg text-center mb-4">Zusammenfassung</h3>

              <div className="space-y-2 text-sm">
                <div className="font-medium text-muted-foreground uppercase text-xs tracking-wide pt-2">
                  Lieferant & Fahrzeug
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Lieferant</span>
                  <span className="font-semibold">{form.lieferant || '—'}</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Kennzeichen</span>
                  <span className="font-semibold">{form.kennzeichen || '—'}</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Lieferschein</span>
                  <span className="font-semibold">{form.lieferscheinNr || '—'}</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Datum</span>
                  <span className="font-semibold">
                    {form.datum ? new Date(form.datum).toLocaleString('de-DE') : '—'}
                  </span>
                </div>

                <div className="font-medium text-muted-foreground uppercase text-xs tracking-wide pt-2">
                  Ware & Gewicht
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Artikel</span>
                  <span className="font-semibold">{form.artikel}</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Brutto</span>
                  <span className="font-semibold">{form.bruttoKg.toLocaleString('de-DE')} kg</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Tara</span>
                  <span className="font-semibold">{form.taraKg.toLocaleString('de-DE')} kg</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Netto</span>
                  <span className="font-bold text-base">{nettoKg.toLocaleString('de-DE')} kg</span>
                </div>
                <div className="flex justify-between border-b pb-1">
                  <span className="text-muted-foreground">Lagerziel</span>
                  <span className="font-semibold">{form.lagerZiel}</span>
                </div>

                {(form.feuchtePct || form.besatzPct || form.fallzahl) && (
                  <>
                    <div className="font-medium text-muted-foreground uppercase text-xs tracking-wide pt-2">
                      Qualität
                    </div>
                    {form.feuchtePct && (
                      <div className="flex justify-between border-b pb-1">
                        <span className="text-muted-foreground">Feuchte</span>
                        <span className="font-semibold">{form.feuchtePct} %</span>
                      </div>
                    )}
                    {form.besatzPct && (
                      <div className="flex justify-between border-b pb-1">
                        <span className="text-muted-foreground">Besatz</span>
                        <span className="font-semibold">{form.besatzPct} %</span>
                      </div>
                    )}
                    {form.fallzahl && (
                      <div className="flex justify-between border-b pb-1">
                        <span className="text-muted-foreground">Fallzahl</span>
                        <span className="font-semibold">{form.fallzahl}</span>
                      </div>
                    )}
                  </>
                )}

                <div className="font-medium text-muted-foreground uppercase text-xs tracking-wide pt-2">
                  Abrechnung
                </div>
                <div className="flex justify-between pt-1">
                  <span className="text-muted-foreground">Abrechnungsgewicht</span>
                  <div className="text-right">
                    <span className="font-bold text-base">{nettoKg.toLocaleString('de-DE')} kg</span>
                    <div className="text-xs text-muted-foreground">= Nettogewicht (keine Qualitätsabzüge)</div>
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <Badge variant="outline" className="w-full justify-center py-1">
                  Rohware-Annahme — STORAGE_ONLY
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <ModuleToolbar
        backTarget="/annahme/warteschlange"
        closeTarget="/annahme/warteschlange"
        title="Rohware-Annahme"
      />
      <Wizard
        title="Rohware-Annahme"
        subtitle="4-schrittiger Assistent für die Rohware-Eingangserfassung"
        steps={steps}
        onFinish={() => { void handleFinish() }}
        onCancel={() => navigate('/annahme/warteschlange')}
        loading={createAcceptance.isPending}
      />
    </div>
  )
}
