/**
 * Rohware-Annahme — Touch-optimierter Kernflow (Gap 002, Wave 92), Studio-Fachoberflaeche.
 */
import { DomainWizard as Wizard } from './domain-wizard'
import { Callout } from '@/components/ui/callout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { CheckCircle, Truck } from 'lucide-react'
import { AgentSuggestionBadge, AgentProcessPanel } from '@/components/agent'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'
import { ARTIKEL_OPTIONEN, LAGER_OPTIONEN, type RohwareState } from './rohware-controller'

export function RohwareRenderer({ state }: { state: RohwareState }): JSX.Element {
  const {
    navigate,
    isTouch,
    chain,
    supplyOps,
    transferSummary,
    form,
    updateField,
    nettoKg,
    operationalStatus,
    operationalBlocker,
    operationalNextAction,
    contextSections,
    timelineItems,
    acceptanceResult,
    submitting,
    validateRohwareStep,
    handleRohwareStepValidationError,
    handleFinish,
    shortcuts,
  } = state

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
            <CheckCircle className="h-16 w-16 text-status-success" />
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
                className="min-h-touch flex-1 touch-manipulation"
              >
                Zur Abrechnung
              </Button>
              <Button onClick={() => navigate('/annahme/warteschlange')} className="min-h-touch flex-1 touch-manipulation">
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
              <div className="space-y-1 text-xs text-muted-foreground">
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
          <Callout variant="info" className="rounded-md border p-3 text-sm">
            <p className="font-semibold">Rohware-Annahme ohne Vollanalyse</p>
            <p className="mt-1 text-foreground">
              Qualitätswerte sind optional. Vollständige Laboranalyse kann nachträglich ergänzt
              werden.
            </p>
          </Callout>
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
            <CheckCircle className="h-16 w-16 text-status-success" />
            <h3 className="text-xl font-bold text-foreground">Rohware-Annahme prüfen</h3>
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
    <div
      className="flex flex-col"
      role="region"
      aria-label="Rohware-Annahme Arbeitsbereich"
    >
      <div className="p-3 md:p-6">
        <ModuleToolbar
          backTarget="/annahme/warteschlange"
          closeTarget="/annahme/warteschlange"
          title="Rohware-Annahme"
        />
        <h1 className="sr-only">Rohware-Annahme</h1>
        <Wizard
          title="Rohware-Annahme"
          subtitle="Lieferant, Ware, Qualität, Abschluss"
          steps={steps}
          getStepValidationError={validateRohwareStep}
          onStepValidationError={handleRohwareStepValidationError}
          onFinish={handleFinish}
          onCancel={() => navigate('/annahme/warteschlange')}
          loading={submitting}
          labels={{ finish: 'Abschliessen', cancel: 'Abbrechen' }}
        />
        {!isTouch ? (
        <>
        <div className="mt-4 space-y-4">
          <OperationalCaseHeader
            title="Rohware-Annahme steuern"
            description="Der Leitstand zeigt nur die naechste noetige Entscheidung: Vorgang, Ressourcenlage und physischen Druck auf einen Blick."
            status={operationalStatus}
            owner="Annahme / Hofannahme"
            blocker={operationalBlocker}
            nextAction={operationalNextAction}
            caseLabel={form.lieferscheinNr ? `Lieferschein ${form.lieferscheinNr}` : 'Annahmefall'}
            tags={['Annahme', 'Rohware']}
          />
          <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <OperationalTimeline title="Vorgangslage" items={timelineItems} />
            <OperationalContextPanel title="Kontext" sections={contextSections} />
          </div>
        </div>
        <Card className="mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-4">
            <div><div className="text-2xs uppercase tracking-wide text-muted-foreground">Annahme offen</div><div className="text-xl font-semibold">{chain.waitingInbound}</div></div>
            <div><div className="text-2xs uppercase tracking-wide text-muted-foreground">Wiegungen offen</div><div className="text-xl font-semibold">{chain.openWeighingTickets}</div></div>
            <div><div className="text-2xs uppercase tracking-wide text-muted-foreground">Chargen gesperrt / Prüfung</div><div className="text-xl font-semibold">{chain.blockedCharges}</div></div>
            <div><div className="text-2xs uppercase tracking-wide text-muted-foreground">Fracht unterwegs</div><div className="text-xl font-semibold">{chain.freightInTransit}</div></div>
          </CardContent>
        </Card>
        <Card className="mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-3">
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Engpass</div>
              <div className="text-lg font-semibold capitalize">{supplyOps.bottleneck}</div>
            </div>
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Druck</div>
              <Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : supplyOps.pressure === 'mittel' ? 'secondary' : 'outline'}>
                {supplyOps.pressure}
              </Badge>
            </div>
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Nächste Aktion</div>
              <div className="text-sm font-semibold">{supplyOps.nextAction}</div>
            </div>
          </CardContent>
        </Card>
        <Card className="mt-4">
          <CardContent className="grid gap-3 pt-6 md:grid-cols-3">
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Übergabedruck</div>
              <Badge variant={transferSummary.transferPressure === 'hoch' ? 'destructive' : 'outline'}>
                {transferSummary.transferPressure}
              </Badge>
            </div>
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Offene Kettenpunkte</div>
              <div className="text-lg font-semibold">{transferSummary.handoverRisk}</div>
            </div>
            <div>
              <div className="text-2xs uppercase tracking-wide text-muted-foreground">Nächste Kettenaktion</div>
              <div className="text-sm font-semibold">{transferSummary.nextAction}</div>
            </div>
          </CardContent>
        </Card>
        <AgentProcessPanel domain="annahme" className="mb-4 mt-4" />
        </>
        ) : null}
      </div>
      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </div>
  )
}
