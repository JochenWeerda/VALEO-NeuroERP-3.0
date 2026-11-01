import { canDomainAction, fieldsEditable } from './domain-runtime'

import { DomainWizard as Wizard } from './domain-wizard'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

import { Label } from '@/components/ui/label'

import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'

import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'

import { TouchSection, TouchNumericInput, TouchToggle, TouchCard, TouchCardGroup } from '@/components/touch/TouchFieldLayout'

type QualitaetsData = {
  lieferscheinNr: string
  artikel: string
  feuchtigkeit: number
  protein: number
  verunreinigung: number
  fremdgeruch: 'ja' | 'nein'
  schaedlinge: 'ja' | 'nein'
  farbe: 'normal' | 'abweichend'
  bemerkungen: string
  ergebnis: 'freigegeben' | 'bedingt' | 'gesperrt'
}

type QualityProtocolResponse = {
  id: string
  harvest_acceptance_id?: string | null
  reference_context?: {
    process_key: string
    anchor_entity: string
    anchor_id: string
    chain?: Record<string, string | null | undefined>
  } | null
}

import type { QualityState } from './quality-controller'
export function QualityRenderer({ state }: { state: QualityState }): JSX.Element {
  const { plan, navigate, isTouch, qualitaet, updateField, savedReferenceContext, qualityDecisionView, shortcuts, goToAbrechnung, operationalStatus, blocker, contextSections, timelineItems, handleSubmit, saveMutation } = state
  const steps = [
    {
      id: 'sichtpruefung',
      title: 'Sichtprüfung',
      content: (
        <TouchSection>
          <div className="rounded-lg bg-muted p-4">
            <div className="font-semibold">{qualitaet.artikel}</div>
            <div className="text-sm text-muted-foreground">Lieferschein: {qualitaet.lieferscheinNr}</div>
          </div>
          {/* Gap 024: TouchToggle ersetzt kleine Radio-Buttons */}
          <TouchToggle
            label="Fremdgeruch"
            value={qualitaet.fremdgeruch === 'ja'}
            onChange={(v) => updateField('fremdgeruch', v ? 'ja' : 'nein')}
            labelYes="Ja — Geruch vorhanden"
            labelNo="Nein — kein Geruch"
          />
          <TouchToggle
            label="Schädlinge / Schimmel"
            value={qualitaet.schaedlinge === 'ja'}
            onChange={(v) => updateField('schaedlinge', v ? 'ja' : 'nein')}
            labelYes="Ja — Befall festgestellt"
            labelNo="Nein — kein Befall"
          />
          <TouchCardGroup label="Farbe / Optik" required>
            <TouchCard
              selected={qualitaet.farbe === 'normal'}
              onSelect={() => updateField('farbe', 'normal')}
              icon={<CheckCircle className="h-5 w-5 text-status-success" />}
              description="Farbe und Aussehen im Normbereich"
            >
              Normal
            </TouchCard>
            <TouchCard
              selected={qualitaet.farbe === 'abweichend'}
              onSelect={() => updateField('farbe', 'abweichend')}
              icon={<AlertTriangle className="h-5 w-5 text-status-warning" />}
              description="Farbe oder Aussehen weicht ab"
            >
              Abweichend
            </TouchCard>
          </TouchCardGroup>
        </TouchSection>
      ),
    },
    {
      id: 'messungen',
      title: 'Messungen',
      content: (
        <TouchSection>
          {/* Gap 024: TouchNumericInput ersetzt Standard-Input — löst Ziffernblock auf Tablet/Handy aus */}
          <div className="space-y-1">
            <TouchNumericInput
              label="Feuchtigkeit (%)"
              value={qualitaet.feuchtigkeit}
              onChange={(v) => updateField('feuchtigkeit', Number(v))}
              unit="%"
              step={0.1}
              min={0}
              max={100}
              placeholder="0.0"
              required
            />
            <p className="text-sm text-muted-foreground">Ziel: &lt; 14% | Toleranz: &lt; 16%</p>
            {qualitaet.feuchtigkeit > 16 && <p className="text-sm font-semibold text-status-error">⚠ Kritisch überschritten!</p>}
            {qualitaet.feuchtigkeit > 14 && qualitaet.feuchtigkeit <= 16 && <p className="text-sm font-semibold text-status-warning">⚠ Toleranz überschritten</p>}
          </div>
          <div className="space-y-1">
            <TouchNumericInput
              label="Protein (%)"
              value={qualitaet.protein}
              onChange={(v) => updateField('protein', Number(v))}
              unit="%"
              step={0.1}
              min={0}
              max={100}
              placeholder="0.0"
            />
            <p className="text-sm text-muted-foreground">Ziel: &gt; 12%</p>
          </div>
          <div className="space-y-1">
            <TouchNumericInput
              label="Verunreinigung (%)"
              value={qualitaet.verunreinigung}
              onChange={(v) => updateField('verunreinigung', Number(v))}
              unit="%"
              step={0.1}
              min={0}
              max={100}
              placeholder="0.0"
              required
            />
            <p className="text-sm text-muted-foreground">Ziel: &lt; 2% | Toleranz: &lt; 3%</p>
            {qualitaet.verunreinigung > 3 && <p className="text-sm font-semibold text-status-error">⚠ Kritisch überschritten!</p>}
            {qualitaet.verunreinigung > 2 && qualitaet.verunreinigung <= 3 && <p className="text-sm font-semibold text-status-warning">⚠ Toleranz überschritten</p>}
          </div>
        </TouchSection>
      ),
    },
    {
      id: 'ergebnis',
      title: 'Ergebnis',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center mb-6">
                {qualitaet.ergebnis === 'freigegeben' && (
                  <CheckCircle className="h-20 w-20 text-status-success" />
                )}
                {qualitaet.ergebnis === 'bedingt' && (
                  <AlertTriangle className="h-20 w-20 text-status-warning" />
                )}
                {qualitaet.ergebnis === 'gesperrt' && <XCircle className="h-20 w-20 text-status-error" />}
              </div>
              <div className="text-center mb-6">
                <Badge
                  variant={
                    qualitaet.ergebnis === 'freigegeben'
                      ? 'outline'
                      : qualitaet.ergebnis === 'bedingt'
                        ? 'secondary'
                        : 'destructive'
                  }
                  className="text-lg px-4 py-2"
                >
                  {qualitaet.ergebnis === 'freigegeben' && '✓ Freigegeben'}
                  {qualitaet.ergebnis === 'bedingt' && '⚠ Bedingt freigegeben'}
                  {qualitaet.ergebnis === 'gesperrt' && '✗ Gesperrt'}
                </Badge>
              </div>
              <dl className="grid gap-3">
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Feuchtigkeit</dt>
                  <dd className="font-semibold">{qualitaet.feuchtigkeit}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Protein</dt>
                  <dd className="font-semibold">{qualitaet.protein}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Verunreinigung</dt>
                  <dd className="font-semibold">{qualitaet.verunreinigung}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Fremdgeruch</dt>
                  <dd className="font-semibold">{qualitaet.fremdgeruch === 'ja' ? '✗ Ja' : '✓ Nein'}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Schädlinge</dt>
                  <dd className="font-semibold">{qualitaet.schaedlinge === 'ja' ? '✗ Ja' : '✓ Nein'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div>
            <Label htmlFor="bemerkungen">Bemerkungen (optional)</Label>
            <Textarea
              id="bemerkungen"
              value={qualitaet.bemerkungen}
              onChange={(e) => updateField('bemerkungen', e.target.value)}
              placeholder="Zusätzliche Beobachtungen..."
              rows={4}
            />
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
    <div className="p-3 md:p-6">
      <Wizard
        title="Schnell-Qualitätsprüfung"
        steps={steps.map(step => ({ ...step, content: <fieldset disabled={!fieldsEditable(plan, ['feuchtigkeit', 'protein', 'verunreinigung', 'fremdgeruch', 'schaedlinge', 'farbe', 'bemerkungen'])}>{step.content}</fieldset> }))}
        onFinish={handleSubmit}
        finishDisabled={!canDomainAction(plan, 'save') || saveMutation.isPending}
        labels={{ finish: plan.actions.find(action => action.key === 'save')?.label }}
        onCancel={() => navigate('/annahme/warteschlange')}
      />
      {!isTouch ? (
      <div className="mb-6 mt-4 space-y-4">
        <OperationalCaseHeader
          title="Qualitaetspruefung steuern"
          description="Der Fallkopf verdichtet QS-Zustand, Blocker und die naechste fachliche Entscheidung ohne den Laborarbeitsplatz zu ueberfrachten."
          status={operationalStatus}
          owner="Qualitaetssicherung"
          blocker={blocker}
          nextAction={qualitaet.ergebnis === 'gesperrt' ? 'Klaerung oder Sperrfreigabe ausloesen' : qualitaet.ergebnis === 'bedingt' ? 'Bedingte Freigabe abstimmen' : 'Messwerte abschliessen und uebergeben'}
          caseLabel={qualitaet.lieferscheinNr ? `QS ${qualitaet.lieferscheinNr}` : 'QS-Fall'}
          tags={['Annahme', 'QS']}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="QS-Verlauf" items={timelineItems} />
          <OperationalContextPanel title="QS-Kontext" sections={contextSections} />
        </div>
      <div className="mb-6 grid gap-4 lg:grid-cols-2">
        {qualityDecisionView ? (
          <Card>
            <CardContent className="pt-6">
              <div className="mb-2 text-sm text-muted-foreground">Entscheidungsstatus</div>
              <ProcessStatusPanel view={qualityDecisionView} />
            </CardContent>
          </Card>
        ) : null}
        {savedReferenceContext ? (
          <Card>
            <CardContent className="pt-6">
              <div className="mb-2 text-sm text-muted-foreground">Prozessreferenz</div>
              <div className="text-sm font-medium">
                {savedReferenceContext.process_key} | {savedReferenceContext.anchor_entity}: {savedReferenceContext.anchor_id}
              </div>
              {savedReferenceContext.chain ? (
                <pre className="mt-3 whitespace-pre-wrap text-xs">{JSON.stringify(savedReferenceContext.chain, null, 2)}</pre>
              ) : null}
            </CardContent>
          </Card>
        ) : null}
      </div>
      </div>
      ) : null}
    </div>
      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </div>
  )
}
