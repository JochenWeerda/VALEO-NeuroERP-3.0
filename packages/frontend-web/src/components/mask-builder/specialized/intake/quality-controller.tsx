import { useDomainQueueEntry } from './domain-data'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable, useDomainDispatch } from './domain-runtime'
import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from '@/app/routing/typed-router'
import { useMutation } from '@tanstack/react-query'

import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'

import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { usePatchWarteschlangeStatus } from '@/lib/api/inventory'
import { buildDecisionView } from '@/policy/decision-view'

import { normalizeOperationalStatus } from '@/lib/operational-status'

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

function buildKlaerungQuery(input: { queueEntryId: string; qualityProtocolId: string }): string {
  const query = new URLSearchParams()
  query.set('queueEntryId', input.queueEntryId)
  query.set('qualityProtocolId', input.qualityProtocolId)
  return query.toString()
}

export function useQualityController(plan: RenderPlan) {
  const navigate = useNavigate()
  const location = useLocation()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const routeState = (location.state as { eintragId?: string; harvestAcceptanceId?: string; referenceContext?: QualityProtocolResponse['reference_context'] } | null) ?? null
  const eintragId = routeState?.eintragId
  const harvestAcceptanceId = routeState?.harvestAcceptanceId
  const { data: lkwEintrag } = useDomainQueueEntry(eintragId)
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
    if (!canDomainAction(plan, 'start') || !eintragId || !lkwEintrag || statusSetToInBearbeitung.current) return
    if (lkwEintrag.status === 'wartend') {
      statusSetToInBearbeitung.current = true
      patchStatus.mutate({ id: eintragId, status: 'in-bearbeitung' })
    }
  }, [eintragId, lkwEintrag?.status])

  function updateField<K extends keyof QualitaetsData>(key: K, value: QualitaetsData[K]): void {
    if (!plan.fieldsByKey[key]?.visible || plan.fieldsByKey[key]?.readOnly) return
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
      if (!canDomainAction(plan, 'save') || !fieldsEditable(plan, ['feuchtigkeit', 'protein', 'verunreinigung', 'fremdgeruch', 'schaedlinge', 'farbe', 'bemerkungen'])) throw new Error('Qualitätsprüfung ist in dieser Ansicht schreibgeschützt')
      const response = await apiClient.post<QualityProtocolResponse>('/api/v1/agrar/quality-protocols', {
        harvest_acceptance_id: harvestAcceptanceId ?? null,
        moisture_pct: qualitaet.feuchtigkeit ?? null,
        protein_pct: qualitaet.protein ?? null,
        impurities_pct: qualitaet.verunreinigung ?? null,
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
      if (qualitaet.ergebnis === 'gesperrt') {
        if (eintragId) {
          patchStatus.mutate({
            id: eintragId,
            status: 'gesperrt',
            klaerung: {
              status: 'offen',
              qp_result: qualitaet.ergebnis,
              quality_protocol_id: data.id,
              updated_at: new Date().toISOString(),
            },
          })
          navigate({
            pathname: '/annahme/klaerung-gesperrt',
            search: `?${buildKlaerungQuery({ queueEntryId: eintragId, qualityProtocolId: data.id })}`,
          })
          return
        }
        navigate('/annahme/warteschlange')
        return
      }
      if (eintragId) {
        patchStatus.mutate({ id: eintragId, status: 'abgeschlossen' })
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
    if (!canDomainAction(plan, 'save') || saveMutation.isPending) return
    try { await saveMutation.mutateAsync() } catch { /* onError keeps the values and reports the failure. */ }
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

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleSubmit() },
    onCancel: () => navigate('/annahme/warteschlange'),
    isSaveDisabled: saveMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  const goToAbrechnung = (): void => {
    if (!canDomainAction(plan, 'billing')) return
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
  const operationalStatus = normalizeOperationalStatus(
    qualitaet.ergebnis === 'gesperrt'
      ? 'blockiert'
      : qualitaet.ergebnis === 'bedingt'
        ? 'wartet_auf_mensch'
        : 'in_pruefung',
  )
  const blocker = qualitaet.ergebnis === 'gesperrt'
    ? 'QS hat eine Sperre gesetzt. Klaerung oder Freigabeentscheidung ist erforderlich.'
    : qualitaet.ergebnis === 'bedingt'
      ? 'Grenzfall erkannt. Freigabe oder Sonderbehandlung muss entschieden werden.'
      : null
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Lieferant', value: lkwEintrag?.lieferant || 'Noch offen' },
        { label: 'Lieferschein', value: qualitaet.lieferscheinNr || 'Noch offen' },
        { label: 'Artikel', value: qualitaet.artikel || 'Noch offen' },
      ],
    },
    {
      title: 'Messwerte',
      items: [
        { label: 'Feuchte', value: `${qualitaet.feuchtigkeit}%` },
        { label: 'Protein', value: `${qualitaet.protein}%` },
        { label: 'Verunreinigung', value: `${qualitaet.verunreinigung}%` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Ergebnis', value: qualitaet.ergebnis },
        { label: 'Queue-Status', value: lkwEintrag?.status || 'nicht verknuepft' },
        { label: 'Referenz', value: savedReferenceContext?.anchor_id || 'Noch kein Anker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'QS-Fall aktiv', detail: lkwEintrag?.kennzeichen ? `Fahrzeug ${lkwEintrag.kennzeichen}` : 'Sichtpruefung und Messwerte werden jetzt dokumentiert.' },
    { label: 'Aktueller QS-Stand', detail: `Ergebnis: ${qualitaet.ergebnis}` },
    ...(savedReferenceContext?.anchor_id
      ? [{
          label: 'Prozessanker geschrieben',
          detail: `${savedReferenceContext.anchor_entity}:${savedReferenceContext.anchor_id}`,
        }]
      : []),
  ]

  useDomainDispatch(plan, { save: handleSubmit, billing: goToAbrechnung, cancel: () => navigate('/annahme/warteschlange') })
  return { plan, navigate, isTouch, qualitaet, updateField, savedReferenceContext, qualityDecisionView, shortcuts, goToAbrechnung, operationalStatus, blocker, contextSections, timelineItems, handleSubmit, saveMutation }
}
export type QualityState = ReturnType<typeof useQualityController>
