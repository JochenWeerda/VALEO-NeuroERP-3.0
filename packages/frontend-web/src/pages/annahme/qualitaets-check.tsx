import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { useWarteschlangeEintrag, usePatchWarteschlangeStatus } from '@/lib/api/inventory'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import {
  TouchSection,
  TouchNumericInput,
  TouchToggle,
  TouchCard,
  TouchCardGroup,
} from '@/components/touch/TouchFieldLayout'

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

function buildHarvestAcceptanceHandoverQuery(input: {
  partnerName: string
  articleId?: string | null
  artikel: string
  lieferscheinNr: string
  vehiclePlate: string
  qualityProtocolId: string
  qpErgebnis: QualitaetsData['ergebnis']
}): string {
  const query = new URLSearchParams()
  query.set('workflowProcess', 'harvest-to-settlement')
  query.set('workflowLabel', `quality-protocol:${input.qualityProtocolId}`)
  query.set('entryMode', 'Qualitaetspruefung')
  if (input.partnerName) query.set('partnerName', input.partnerName)
  if (input.artikel || input.qpErgebnis) query.set('subject', [input.artikel, input.qpErgebnis].filter(Boolean).join(' / '))
  if (input.lieferscheinNr) query.set('lieferscheinNr', input.lieferscheinNr)
  if (input.vehiclePlate) query.set('vehiclePlate', input.vehiclePlate)
  if (input.articleId) query.set('articleId', input.articleId)
  if (input.artikel) query.set('articleName', input.artikel)
  query.set('qpResult', input.qpErgebnis)
  query.set('qualityProtocolId', input.qualityProtocolId)
  return query.toString()
}

export default function QualitaetsCheckPage(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const { toast } = useToast()
  const routeState = (location.state as { eintragId?: string; harvestAcceptanceId?: string; referenceContext?: QualityProtocolResponse['reference_context'] } | null) ?? null
  const eintragId = routeState?.eintragId
  const harvestAcceptanceId = routeState?.harvestAcceptanceId
  const { data: lkwEintrag } = useWarteschlangeEintrag(eintragId)
  const patchStatus = usePatchWarteschlangeStatus()
  const statusSetToInBearbeitung = useRef(false)
  const [savedReferenceContext, setSavedReferenceContext] = useState<QualityProtocolResponse['reference_context']>(routeState?.referenceContext ?? null)

  const [qualitaet, setQualitaet] = useState<QualitaetsData>({
    lieferscheinNr: '',
    artikel: '',
    feuchtigkeit: 0,
    protein: 0,
    verunreinigung: 0,
    fremdgeruch: 'nein',
    schaedlinge: 'nein',
    farbe: 'normal',
    bemerkungen: '',
    ergebnis: 'freigegeben',
  })

  useEffect(() => {
    if (!lkwEintrag) return
    setQualitaet((prev) => ({
      ...prev,
      artikel: lkwEintrag.artikel || prev.artikel,
      lieferscheinNr: lkwEintrag.lieferschein_nr ?? prev.lieferscheinNr,
    }))
  }, [lkwEintrag?.id, lkwEintrag?.artikel, lkwEintrag?.lieferschein_nr])

  useEffect(() => {
    if (!eintragId || !lkwEintrag || statusSetToInBearbeitung.current) return
    if (lkwEintrag.status === 'wartend') {
      statusSetToInBearbeitung.current = true
      patchStatus.mutate({ id: eintragId, status: 'in-bearbeitung' })
    }
  }, [eintragId, lkwEintrag?.status])

  function updateField<K extends keyof QualitaetsData>(key: K, value: QualitaetsData[K]): void {
    const updated = { ...qualitaet, [key]: value }

    // Auto-Bewertung
    let probleme = 0
    if (updated.feuchtigkeit > 16) probleme += 2
    else if (updated.feuchtigkeit > 14) probleme += 1
    if (updated.verunreinigung > 3) probleme += 2
    else if (updated.verunreinigung > 2) probleme += 1
    if (updated.fremdgeruch === 'ja') probleme += 3
    if (updated.schaedlinge === 'ja') probleme += 3
    if (updated.farbe === 'abweichend') probleme += 1

    if (probleme >= 3 || updated.schaedlinge === 'ja') {
      updated.ergebnis = 'gesperrt'
    } else if (probleme > 0) {
      updated.ergebnis = 'bedingt'
    } else {
      updated.ergebnis = 'freigegeben'
    }

    setQualitaet(updated)
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post<QualityProtocolResponse>('/api/v1/agrar/quality-protocols', {
        harvest_acceptance_id: harvestAcceptanceId ?? null,
        moisture_pct: qualitaet.feuchtigkeit || null,
        protein_pct: qualitaet.protein || null,
        impurities_pct: qualitaet.verunreinigung || null,
        source_type: 'manual',
        other_values: {
          fremdgeruch: qualitaet.fremdgeruch,
          schaedlinge: qualitaet.schaedlinge,
          farbe: qualitaet.farbe,
          ergebnis: qualitaet.ergebnis,
          bemerkungen: qualitaet.bemerkungen,
          lieferschein_nr: qualitaet.lieferscheinNr,
          artikel: qualitaet.artikel,
        },
      })
      return response.data
    },
    onSuccess: (data) => {
      setSavedReferenceContext(data.reference_context ?? null)
      toast({ title: 'Qualitätsprüfung gespeichert', description: `Ergebnis: ${qualitaet.ergebnis}` })
      if (eintragId) {
        patchStatus.mutate({ id: eintragId, status: 'abgeschlossen' })
      }
      if (qualitaet.ergebnis === 'gesperrt') {
        navigate('/annahme/warteschlange')
        return
      }
      const handoverQuery = buildHarvestAcceptanceHandoverQuery({
        partnerName: lkwEintrag?.lieferant ?? '',
        articleId: lkwEintrag?.article_id ?? null,
        artikel: qualitaet.artikel,
        lieferscheinNr: qualitaet.lieferscheinNr,
        vehiclePlate: lkwEintrag?.kennzeichen ?? '',
        qualityProtocolId: data.id,
        qpErgebnis: qualitaet.ergebnis,
      })
      navigate({
        pathname: '/agrar/ernte-annahme-erfassung',
        search: `?${handoverQuery}`,
      })
    },
    onError: () => {
      toast({ title: 'Fehler beim Speichern', variant: 'destructive' })
    },
  })

  async function handleSubmit(): Promise<void> {
    saveMutation.mutate()
  }

  const qualityDecisionView = buildDecisionView({
    status:
      qualitaet.ergebnis === 'gesperrt'
        ? 'blocked'
        : qualitaet.ergebnis === 'bedingt'
          ? 'approval-required'
          : 'allowed',
    summary:
      qualitaet.ergebnis === 'gesperrt'
        ? 'Qualitaetspruefung blockiert die weitere Verarbeitung.'
        : qualitaet.ergebnis === 'bedingt'
          ? 'Qualitaetspruefung erlaubt die Verarbeitung nur mit Freigabe.'
          : 'Qualitaetspruefung gibt die Verarbeitung frei.',
    source_scope: 'quality-protocol',
    details: [
      { label: 'Ergebnis', value: qualitaet.ergebnis },
      ...(savedReferenceContext?.anchor_id
        ? [{ label: 'Referenzanker', value: `${savedReferenceContext.anchor_entity}:${savedReferenceContext.anchor_id}` }]
        : []),
    ],
  })

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
              icon={<CheckCircle className="h-5 w-5 text-green-600" />}
              description="Farbe und Aussehen im Normbereich"
            >
              Normal
            </TouchCard>
            <TouchCard
              selected={qualitaet.farbe === 'abweichend'}
              onSelect={() => updateField('farbe', 'abweichend')}
              icon={<AlertTriangle className="h-5 w-5 text-orange-600" />}
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
            {qualitaet.feuchtigkeit > 16 && <p className="text-sm font-semibold text-red-600">⚠ Kritisch überschritten!</p>}
            {qualitaet.feuchtigkeit > 14 && qualitaet.feuchtigkeit <= 16 && <p className="text-sm font-semibold text-orange-600">⚠ Toleranz überschritten</p>}
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
            {qualitaet.verunreinigung > 3 && <p className="text-sm font-semibold text-red-600">⚠ Kritisch überschritten!</p>}
            {qualitaet.verunreinigung > 2 && qualitaet.verunreinigung <= 3 && <p className="text-sm font-semibold text-orange-600">⚠ Toleranz überschritten</p>}
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
                  <CheckCircle className="h-20 w-20 text-green-600" />
                )}
                {qualitaet.ergebnis === 'bedingt' && (
                  <AlertTriangle className="h-20 w-20 text-orange-600" />
                )}
                {qualitaet.ergebnis === 'gesperrt' && <XCircle className="h-20 w-20 text-red-600" />}
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

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => saveMutation.mutate(),
    onCancel: () => navigate('/annahme/warteschlange'),
    isSaveDisabled: saveMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  const goToAbrechnung = (): void => {
    navigate('/annahme/abrechnung', {
      state: {
        fromQualitaetsCheck: true,
        artikel: qualitaet.artikel,
        feuchtigkeit: qualitaet.feuchtigkeit,
        verunreinigung: qualitaet.verunreinigung,
        lieferscheinNr: qualitaet.lieferscheinNr,
        harvestAcceptanceId,
        referenceContext: savedReferenceContext,
      },
    })
  }

  return (
    <div className="flex flex-col">
    <div className="p-6">
      <ModuleToolbar
        backTarget="/annahme/warteschlange"
        closeTarget="/annahme/warteschlange"
        title="Qualitätsprüfung"
        actions={
          <Button variant="outline" size="sm" onClick={goToAbrechnung}>
            Zur Abrechnung
          </Button>
        }
      />
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
      <Wizard
        title="Schnell-Qualitätsprüfung"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/annahme/warteschlange')}
      />
    </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
