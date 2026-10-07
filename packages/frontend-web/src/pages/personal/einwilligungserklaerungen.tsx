import { useCallback, useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { personalEinwilligungserklaerungenScreen } from '@/masks/capture-screens'
import { legeErklaerungAn, listErklaerungen, vorhandeneFassung } from '@/lib/api/bewerbung-einwilligung'

const leer = { wortlaut: '', erstellt_durch: '' }

function text(value: unknown): string {
  return String(value ?? '').trim()
}

export default function PersonalEinwilligungserklaerungenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const erklaerungen = useQuery({ queryKey: ['einwilligungserklaerungen'], queryFn: listErklaerungen })
  const fassungen = useMemo(() => erklaerungen.data ?? [], [erklaerungen.data])
  const neueste = fassungen[0]?.fassung
  const [saving, setSaving] = useState(false)
  const [anlegenFragen, setAnlegenFragen] = useState(false)

  useEffect(() => {
    if (!erklaerungen.isError) return
    toast.error('Fassungen nicht geladen', { description: getAxiosErrorMessage(erklaerungen.error) })
  }, [erklaerungen.error, erklaerungen.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalEinwilligungserklaerungenScreen,
    layout: {
      ...personalEinwilligungserklaerungenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: personalEinwilligungserklaerungenScreen.summary.map((item) => ({
      ...item,
      value: item.key === 'fassungen' ? String(fassungen.length) : (neueste ? `Fassung ${neueste}` : '–'),
    })),
    actions: personalEinwilligungserklaerungenScreen.actions.map((action) => ({
      ...action,
      disabled: saving,
    })),
  }), [fassungen.length, isTouch, neueste, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })
  const { setValue } = form

  const leeren = useCallback(() => {
    setValue('wortlaut', '')
    setValue('erstellt_durch', '')
  }, [setValue])

  const anlegen = useCallback(async () => {
    if (saving) return
    const wortlaut = text(form.values.wortlaut)
    if (!wortlaut) return
    setSaving(true)
    try {
      const erklaerung = await legeErklaerungAn(wortlaut, text(form.values.erstellt_durch) || null)
      toast.success(`Fassung ${erklaerung.fassung} angelegt`, {
        description: 'Sie ist ab jetzt unveränderlich und kann beim Erteilen gewählt werden.',
      })
      leeren()
      await queryClient.invalidateQueries({ queryKey: ['einwilligungserklaerungen'] })
    } catch (error) {
      const vorhanden = vorhandeneFassung(error)
      if (vorhanden !== null) {
        // Derselbe Wortlaut ist eine Fassung; eine zweite Nummer liesse zwei
        // Formulare gleich aussehen und verschieden heissen.
        toast.error('Diesen Wortlaut gibt es schon', { description: `Er ist Fassung ${vorhanden}.` })
      } else {
        toast.error('Fassung nicht angelegt', { description: getAxiosErrorMessage(error) })
      }
    } finally {
      setSaving(false)
      setAnlegenFragen(false)
    }
  }, [form.values, leeren, queryClient, saving])

  const handleAction = useCallback(async (key: string) => {
    if (key === 'neu') {
      leeren()
      return
    }
    if (key !== 'anlegen') return
    if (!text(form.values.wortlaut)) {
      toast.error('Fassung unvollständig', { description: 'Den Wortlaut eintragen, der unterschrieben wird.' })
      return
    }
    // Nach dem Anlegen ist der Text nicht mehr aenderbar — einmal hinsehen.
    setAnlegenFragen(true)
  }, [form.values.wortlaut, leeren])

  const workflow = useMemo<WorkflowState>(() => {
    const keine = fassungen.length === 0
    const naechste = keine
      ? 'Die erste Fassung anlegen; ohne sie kann keine Einwilligung erteilt werden.'
      : `Erteilt wird gegen eine Fassung. Neueste: Fassung ${neueste}.`
    return {
      status: {
        currentStatus: keine ? 'leer' : 'vorhanden',
        statusLabel: keine ? 'Keine Fassung' : `${fassungen.length} Fassungen`,
        tone: keine ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'anlegen', label: naechste, dangerLevel: 'safe', requiresConfirmation: true }],
      blockingReasons: keine ? [{ code: 'keine-fassung', message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [fassungen.length, neueste])

  const screenContext = useMemo(() => createScreenContext({
    data: { fassungen },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.saveErklaerung': () => handleAction('anlegen'),
      'personal.newErklaerung': () => handleAction('neu'),
    },
    navigation: { push: () => undefined },
  }), [fassungen, form.values, handleAction])

  if (erklaerungen.isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="min-h-touch h-10 w-48" />
        <Skeleton className="h-40" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <UniversalMaskRenderer
        plan={plan}
        formState={form}
        hideFormSubmit
        screenContext={screenContext}
        workflowState={workflow}
        tables={{
          fassungen: fassungen.map((erklaerung) => ({
            id: erklaerung.id,
            fassung: erklaerung.fassung,
            wortlaut: erklaerung.wortlaut,
            erstellt_am: text(erklaerung.erstellt_am).slice(0, 10),
            erstellt_durch: text(erklaerung.erstellt_durch) || '–',
          })),
        }}
        onAction={handleAction}
      />
      <AlertDialog open={anlegenFragen} onOpenChange={(offen) => { if (!saving) setAnlegenFragen(offen) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Fassung {neueste ? neueste + 1 : 1} anlegen?</AlertDialogTitle>
            <AlertDialogDescription>
              Der Wortlaut ist danach nicht mehr änderbar: Wer einer Fassung zugestimmt hat, hat
              genau diesem Text zugestimmt. Ein geänderter Text wird eine neue Fassung.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={saving}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              disabled={saving}
              onClick={(event) => {
                event.preventDefault()
                void anlegen()
              }}
            >
              Anlegen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
