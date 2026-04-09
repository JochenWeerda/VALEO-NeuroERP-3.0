/**
 * Rohware-Annahme — Touch-optimierter Kernflow (Gap 002, Wave 92)
 * TouchCards für Artikel- und Lagerort-Auswahl, TouchTextInput/NumericInput für Felder,
 * Keyboard-Shortcuts für Desktop
 */
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, Truck } from 'lucide-react'
import { AgentSuggestionBadge, AgentProcessPanel } from '@/components/agent'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'

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
  { id: 'Silo 1', label: 'Silo 1', description: 'Weizen / Roggen' },
  { id: 'Silo 2', label: 'Silo 2', description: 'Gerste / Hafer' },
  { id: 'Hauptlager', label: 'Hauptlager', description: 'Schüttgut allgemein' },
  { id: 'Außenlager', label: 'Außenlager', description: 'Sonderlager / Saisonware' },
]

export default function RohwareAnnahmePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: chain } = useSupplyChainOverview()
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])

  const [form, setForm] = useState<RohwareFormState>({
    lieferant: '',
    kennzeichen: '',
    lieferscheinNr: '',
    datum: new Date().toISOString().slice(0, 16),
    artikel: '',
    bruttoKg: 0,
    taraKg: 0,
    lagerZiel: '',
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

  function validateRohwareStep(stepId: string): string | null {
    if (stepId === 'lieferant-fahrzeug') {
      if (!form.lieferant.trim()) {
        return 'Lieferant ist ein Pflichtfeld.'
      }
      if (!form.kennzeichen.trim()) {
        return 'Kennzeichen ist ein Pflichtfeld.'
      }
      return null
    }
    if (stepId === 'ware-gewicht') {
      if (!form.artikel.trim()) {
        return 'Bitte einen Artikel auswaehlen.'
      }
      if (!form.lagerZiel.trim()) {
        return 'Bitte ein Lagerziel auswaehlen.'
      }
      if (nettoKg <= 0) {
        return 'Nettogewicht muss groesser 0 kg sein (Brutto und Tara pruefen).'
      }
      return null
    }
    if (stepId === 'qualitaet') {
      return null
    }
    return null
  }

  function handleRohwareStepValidationError(_stepId: string, message: string): void {
    toast({
      title: 'Schritt unvollstaendig',
      description: message,
      variant: 'destructive',
    })
  }

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
      return (await apiClient.post<HarvestAcceptanceResponse>('/api/v1/agrar/harvest-acceptance', payload)).data
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

  const handleFinish = (): void => {
    createAcceptance.mutate()
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: handleFinish,
    onCancel: () => navigate('/annahme/warteschlange'),
    isSaveDisabled: createAcceptance.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  if (acceptanceResult) {
    const acceptanceNumber = acceptanceResult.acceptance_number ?? acceptanceResult.id
    return (
      <div className="p-6">
        <ModuleToolbar
          backTarget="/annahme/warteschlange"
          closeTarget="/annahme/warteschlange"
          title="Rohware-Annahme"
        />
        <Card className="mx-auto max-w-md mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-2">
            <div><div className="text-xs text-muted-foreground">Annahme offen</div><div className="text-xl font-semibold">{chain.waitingInbound}</div></div>
            <div><div className="text-xs text-muted-foreground">Wiegungen offen</div><div className="text-xl font-semibold">{chain.openWeighingTickets}</div></div>
            <div><div className="text-xs text-muted-foreground">Chargen in Prüfung</div><div className="text-xl font-semibold">{chain.blockedCharges}</div></div>
            <div><div className="text-xs text-muted-foreground">Fracht unterwegs</div><div className="text-xl font-semibold">{chain.freightInTransit}</div></div>
          </CardContent>
        </Card>
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
        <TouchSection title="Lieferant & Fahrzeug">
          <div className="flex items-center justify-center mb-2">
            <Truck className="h-16 w-16 text-muted-foreground" />
          </div>
          <TouchTextInput
            label="Lieferant"
            value={form.lieferant}
            onChange={(v) => updateField('lieferant', v)}
            placeholder="Name des Lieferanten"
            required
          />
          <TouchTextInput
            label="Kennzeichen"
            value={form.kennzeichen}
            onChange={(v) => updateField('kennzeichen', v.toUpperCase())}
            placeholder="z.B. AB-CD 1234"
            autoCapitalize="characters"
            required
          />
          <TouchTextInput
            label="Lieferschein-Nr."
            value={form.lieferscheinNr}
            onChange={(v) => updateField('lieferscheinNr', v)}
            placeholder="z.B. LS-2026-0042"
          />
          <div className="space-y-1">
            <Label htmlFor="datum">Datum/Uhrzeit</Label>
            <Input
              id="datum"
              type="datetime-local"
              value={form.datum}
              onChange={(e) => updateField('datum', e.target.value)}
              className="h-12"
            />
          </div>
        </TouchSection>
      ),
    },
    {
      id: 'ware-gewicht',
      title: 'Ware & Gewicht',
      content: (
        <TouchSection title="Ware & Gewicht">
          <AgentSuggestionBadge
            capabilityKey="rohware_annahme_assistant"
            parameters={{ lieferant: form.lieferant, kennzeichen: form.kennzeichen }}
            renderSuggestion={(s: { artikel?: string; lagerZiel?: string }) => (
              <div className="space-y-1 text-xs text-violet-800">
                {s.artikel && <div><span className="font-medium">Artikel:</span> {s.artikel}</div>}
                {s.lagerZiel && <div><span className="font-medium">Lagerziel:</span> {s.lagerZiel}</div>}
              </div>
            )}
            onAccept={(s: { artikel?: string; lagerZiel?: string }) => {
              if (s.artikel) updateField('artikel', s.artikel)
              if (s.lagerZiel) updateField('lagerZiel', s.lagerZiel)
            }}
          />
          <TouchCardGroup label="Artikel" required>
            {ARTIKEL_OPTIONEN.map((art) => (
              <TouchCard
                key={art}
                selected={form.artikel === art}
                onSelect={() => updateField('artikel', art)}
              >
                {art}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchNumericInput
            label="Bruttogewicht"
            value={form.bruttoKg}
            onChange={(v) => updateField('bruttoKg', Number(v))}
            unit="kg"
            min={0}
            step={1}
            required
          />
          <TouchNumericInput
            label="Taragewicht"
            value={form.taraKg}
            onChange={(v) => updateField('taraKg', Number(v))}
            unit="kg"
            min={0}
            step={1}
            required
          />
          <div className="rounded-md bg-muted p-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Nettogewicht (berechnet)</span>
              <span className="text-lg font-bold">{nettoKg.toLocaleString('de-DE')} kg</span>
            </div>
          </div>
          <TouchCardGroup label="Lager-Ziel" required>
            {LAGER_OPTIONEN.map((lo) => (
              <TouchCard
                key={lo.id}
                selected={form.lagerZiel === lo.id}
                onSelect={() => updateField('lagerZiel', lo.id)}
                description={lo.description}
              >
                {lo.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
        </TouchSection>
      ),
    },
    {
      id: 'qualitaet',
      title: 'Qualitätswerte',
      content: (
        <TouchSection title="Qualitätswerte (optional)">
          <div className="rounded-md bg-blue-50 border border-blue-200 p-3 text-sm text-blue-900">
            <p className="font-semibold">Rohware-Annahme ohne Vollanalyse</p>
            <p className="mt-1 text-blue-700">
              Qualitätswerte sind optional. Vollständige Laboranalyse kann nachträglich ergänzt
              werden.
            </p>
          </div>
          <TouchNumericInput
            label="Feuchte %"
            value={form.feuchtePct ? Number(form.feuchtePct) : 0}
            onChange={(v) => updateField('feuchtePct', String(v))}
            unit="%"
            min={0}
            max={100}
            step={0.1}
          />
          <TouchNumericInput
            label="Besatz %"
            value={form.besatzPct ? Number(form.besatzPct) : 0}
            onChange={(v) => updateField('besatzPct', String(v))}
            unit="%"
            min={0}
            max={100}
            step={0.1}
          />
          <TouchNumericInput
            label="Fallzahl"
            value={form.fallzahl ? Number(form.fallzahl) : 0}
            onChange={(v) => updateField('fallzahl', String(v))}
            min={0}
            step={1}
          />
        </TouchSection>
      ),
    },
    {
      id: 'uebersicht',
      title: 'Übersicht & Abschluss',
      content: (
        <div className="space-y-6">
          <div className="flex flex-col items-center gap-2 py-2">
            <CheckCircle className="h-16 w-16 text-emerald-500" />
            <h3 className="text-xl font-bold text-slate-800">Rohware-Annahme prüfen</h3>
          </div>
          <TouchConfirmCard
            title="Lieferant & Fahrzeug"
            fields={[
              { label: 'Lieferant', value: form.lieferant || '—', highlight: true },
              { label: 'Kennzeichen', value: form.kennzeichen || '—', highlight: true },
              { label: 'Lieferschein', value: form.lieferscheinNr || '—' },
              { label: 'Datum', value: form.datum ? new Date(form.datum).toLocaleString('de-DE') : '—' },
            ]}
          />
          <TouchConfirmCard
            title="Ware & Gewicht"
            fields={[
              { label: 'Artikel', value: form.artikel || '—', highlight: true },
              { label: 'Brutto', value: `${form.bruttoKg.toLocaleString('de-DE')} kg` },
              { label: 'Tara', value: `${form.taraKg.toLocaleString('de-DE')} kg` },
              { label: 'Netto', value: `${nettoKg.toLocaleString('de-DE')} kg`, highlight: true },
              { label: 'Lagerziel', value: form.lagerZiel || '—' },
            ]}
          />
          {(form.feuchtePct || form.besatzPct || form.fallzahl) && (
            <TouchConfirmCard
              title="Qualitätswerte"
              fields={[
                ...(form.feuchtePct ? [{ label: 'Feuchte', value: `${form.feuchtePct} %` }] : []),
                ...(form.besatzPct ? [{ label: 'Besatz', value: `${form.besatzPct} %` }] : []),
                ...(form.fallzahl ? [{ label: 'Fallzahl', value: form.fallzahl }] : []),
              ]}
            />
          )}
          <div className="flex justify-center">
            <Badge variant="outline" className="px-4 py-1">
              Rohware-Annahme — STORAGE_ONLY
            </Badge>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-6">
        <ModuleToolbar
          backTarget="/annahme/warteschlange"
          closeTarget="/annahme/warteschlange"
          title="Rohware-Annahme"
        />
        <Card className="mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-4">
            <div><div className="text-xs text-muted-foreground">Annahme offen</div><div className="text-xl font-semibold">{chain.waitingInbound}</div></div>
            <div><div className="text-xs text-muted-foreground">Wiegungen offen</div><div className="text-xl font-semibold">{chain.openWeighingTickets}</div></div>
            <div><div className="text-xs text-muted-foreground">Chargen gesperrt / Prüfung</div><div className="text-xl font-semibold">{chain.blockedCharges}</div></div>
            <div><div className="text-xs text-muted-foreground">Fracht unterwegs</div><div className="text-xl font-semibold">{chain.freightInTransit}</div></div>
          </CardContent>
        </Card>
        <Card className="mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-3">
            <div>
              <div className="text-xs text-muted-foreground">Bottleneck</div>
              <div className="text-lg font-semibold capitalize">{supplyOps.bottleneck}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Druck</div>
              <Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : supplyOps.pressure === 'mittel' ? 'secondary' : 'outline'}>
                {supplyOps.pressure}
              </Badge>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Naechste Aktion</div>
              <div className="text-sm font-semibold">{supplyOps.nextAction}</div>
            </div>
          </CardContent>
        </Card>
        <AgentProcessPanel domain="annahme" className="mb-4" />
        <Wizard
          title="Rohware-Annahme"
          subtitle="4-schrittiger Assistent für die Rohware-Eingangserfassung"
          steps={steps}
          getStepValidationError={validateRohwareStep}
          onStepValidationError={handleRohwareStepValidationError}
          onFinish={handleFinish}
          onCancel={() => navigate('/annahme/warteschlange')}
          loading={createAcceptance.isPending}
        />
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
