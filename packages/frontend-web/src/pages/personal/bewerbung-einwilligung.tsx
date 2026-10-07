import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useNavigate, useParams } from '@/app/routing/typed-router'
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
import { personalBewerbungEinwilligungScreen } from '@/masks/capture-screens'
import {
  erteileEinwilligung,
  getBewerbungKopf,
  getEinwilligung,
  listErklaerungen,
  widerrufeEinwilligung,
  type Kanal,
} from '@/lib/api/bewerbung-einwilligung'

// Die Bezeichnungen stehen einmal — in der Screen Definition.
const KANAL_LABEL: Record<string, string> = Object.fromEntries(
  ((personalBewerbungEinwilligungScreen as ScreenDefinition).tabs ?? [])
    .flatMap((tab) => tab.fields ?? [])
    .find((field) => field.key === 'kanal')?.options?.map((option) => [String(option.value), option.label]) ?? [],
)

const VORGANG_LABEL: Record<string, string> = { ERTEILT: 'Erteilt', WIDERRUFEN: 'Widerrufen' }

const leer = {
  applicant_name: '',
  position_title: '',
  stand_gueltig_bis: '',
  stand_erteilt_am: '',
  fassung: '',
  gueltig_bis: '',
  kanal: '',
  erfasst_durch: '',
  wortlaut: '',
}

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function datum(value: unknown): string {
  return text(value).slice(0, 10)
}

export default function PersonalBewerbungEinwilligungPage(): JSX.Element {
  const { id = '' } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const kopf = useQuery({
    queryKey: ['bewerbung-einwilligung', id, 'kopf'],
    queryFn: () => getBewerbungKopf(id),
    enabled: Boolean(id),
  })
  const stand = useQuery({
    queryKey: ['bewerbung-einwilligung', id, 'stand'],
    queryFn: () => getEinwilligung(id),
    enabled: Boolean(id),
  })
  const erklaerungen = useQuery({ queryKey: ['einwilligungserklaerungen'], queryFn: listErklaerungen })
  const [pending, setPending] = useState<string | null>(null)
  const [widerrufFragen, setWiderrufFragen] = useState(false)

  useEffect(() => {
    const fehler = kopf.error ?? stand.error ?? erklaerungen.error
    if (!fehler) return
    toast.error('Einwilligung nicht geladen', { description: getAxiosErrorMessage(fehler) })
  }, [erklaerungen.error, kopf.error, stand.error])

  const fassungen = useMemo(() => erklaerungen.data ?? [], [erklaerungen.data])
  const laeuft = stand.data?.laeuft === true
  const hatEinwilligung = Boolean(stand.data?.gueltig_bis)

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalBewerbungEinwilligungScreen,
    layout: {
      ...personalBewerbungEinwilligungScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: personalBewerbungEinwilligungScreen.summary.map((item) => ({
      ...item,
      value: item.key === 'stand'
        ? (laeuft ? 'läuft' : hatEinwilligung ? 'abgelaufen' : 'keine')
        : (datum(stand.data?.gueltig_bis) || '–'),
    })),
    tabs: personalBewerbungEinwilligungScreen.tabs.map((tab) => ({
      ...tab,
      fields: tab.fields?.map((field) => (field.key === 'fassung'
        ? {
            ...field,
            options: fassungen.map((erklaerung) => ({
              value: String(erklaerung.fassung),
              label: `Fassung ${erklaerung.fassung}${erklaerung.erstellt_am ? ` vom ${datum(erklaerung.erstellt_am)}` : ''}`,
            })),
          }
        : field)),
    })),
    actions: personalBewerbungEinwilligungScreen.actions.map((action) => ({
      ...action,
      disabled: pending !== null
        || (action.key === 'erteilen' && fassungen.length === 0)
        || (action.key === 'widerrufen' && !hatEinwilligung),
    })),
  }), [fassungen, hatEinwilligung, isTouch, laeuft, pending, stand.data?.gueltig_bis])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })
  const { setValue } = form

  // Kopf und Stand sind Anzeige; sie kommen aus dem Server, nicht aus der Eingabe.
  const uebernommen = useRef<string | null>(null)
  useEffect(() => {
    if (!kopf.data || !stand.data) return
    const marke = `${kopf.data.id}|${stand.data.gueltig_bis ?? ''}|${stand.data.erteilt_am ?? ''}`
    if (uebernommen.current === marke) return
    uebernommen.current = marke
    setValue('applicant_name', text(kopf.data.applicant_name))
    setValue('position_title', text(kopf.data.position_title) || '–')
    setValue('stand_gueltig_bis', datum(stand.data.gueltig_bis))
    setValue('stand_erteilt_am', datum(stand.data.erteilt_am) || '–')
  }, [kopf.data, setValue, stand.data])

  // Der Wortlaut folgt der gewaehlten Fassung; er ist nie eine eigene Eingabe.
  const gewaehlt = text(form.values.fassung)
  useEffect(() => {
    const erklaerung = fassungen.find((eintrag) => String(eintrag.fassung) === gewaehlt)
    setValue('wortlaut', erklaerung?.wortlaut ?? '')
  }, [fassungen, gewaehlt, setValue])

  const neuLaden = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: ['bewerbung-einwilligung', id] })
  }, [id, queryClient])

  const erteilen = useCallback(async () => {
    if (pending) return
    const fassung = Number(text(form.values.fassung))
    const gueltigBis = datum(form.values.gueltig_bis)
    const kanal = text(form.values.kanal) as Kanal
    if (!fassung || !gueltigBis || !kanal) {
      toast.error('Einwilligung unvollständig', { description: 'Fassung, Gültig bis und Kanal angeben.' })
      return
    }
    setPending('erteilen')
    try {
      const vorgang = await erteileEinwilligung(id, {
        fassung,
        gueltig_bis: gueltigBis,
        kanal,
        erfasst_durch: text(form.values.erfasst_durch) || null,
      })
      toast.success('Einwilligung erteilt', {
        description: `Fassung ${vorgang.fassung ?? fassung}, gültig bis ${datum(vorgang.gueltig_bis) || gueltigBis}`,
      })
      setValue('fassung', '')
      setValue('gueltig_bis', '')
      setValue('erfasst_durch', '')
      await neuLaden()
    } catch (error) {
      toast.error('Einwilligung nicht erteilt', { description: getAxiosErrorMessage(error) })
    } finally {
      setPending(null)
    }
  }, [form.values, id, neuLaden, pending, setValue])

  const widerrufen = useCallback(async () => {
    if (pending) return
    setPending('widerrufen')
    try {
      await widerrufeEinwilligung(id)
      toast.success('Einwilligung widerrufen', {
        description: 'Die Bewerbung ist wieder löschfähig; der nächste Löschlauf nimmt sie mit, wenn die Frist abgelaufen ist.',
      })
      await neuLaden()
    } catch (error) {
      toast.error('Widerruf nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally {
      setPending(null)
      setWiderrufFragen(false)
    }
  }, [id, neuLaden, pending])

  const handleAction = useCallback(async (key: string) => {
    if (key === 'erteilen') await erteilen()
    else if (key === 'widerrufen') setWiderrufFragen(true)
    else if (key === 'zurueck') navigate('/personal/bewerbungen')
    else if (key === 'erklaerungen') navigate('/personal/einwilligungserklaerungen')
  }, [erteilen, navigate])

  const workflow = useMemo<WorkflowState>(() => {
    const label = laeuft ? 'Einwilligung läuft' : hatEinwilligung ? 'Einwilligung abgelaufen' : 'Keine Einwilligung'
    const naechste = laeuft
      ? `Aufbewahrt bis ${datum(stand.data?.gueltig_bis)}. Ein Widerruf wirkt sofort.`
      : fassungen.length === 0
        ? 'Zuerst eine Fassung der Einwilligungserklärung anlegen.'
        : 'Die Aufbewahrung richtet sich nach der beschlossenen Frist.'
    return {
      status: {
        currentStatus: laeuft ? 'laeuft' : hatEinwilligung ? 'abgelaufen' : 'keine',
        statusLabel: label,
        tone: laeuft ? 'success' : hatEinwilligung ? 'warning' : 'neutral',
      },
      nextAllowedActions: [{
        actionKey: laeuft ? 'widerrufen' : 'erteilen',
        label: naechste,
        dangerLevel: laeuft ? 'moderate' : 'safe',
        requiresConfirmation: laeuft,
      }],
      blockingReasons: fassungen.length === 0 && !laeuft
        ? [{ code: 'ohne-fassung', message: naechste, blocking: true }]
        : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [fassungen.length, hatEinwilligung, laeuft, stand.data?.gueltig_bis])

  const vorgaenge = useMemo(() => (stand.data?.vorgaenge ?? []).map((vorgang) => ({
    id: vorgang.id,
    erfolgt_am: vorgang.erfolgt_am ?? '',
    vorgang: VORGANG_LABEL[vorgang.vorgang] ?? vorgang.vorgang,
    fassung: vorgang.fassung ?? '',
    gueltig_bis: datum(vorgang.gueltig_bis),
    // Beim Widerruf nicht erhoben — nicht erfunden.
    kanal: vorgang.kanal ? (KANAL_LABEL[vorgang.kanal] ?? vorgang.kanal) : '–',
    erfasst_durch: text(vorgang.erfasst_durch) || '–',
  })), [stand.data?.vorgaenge])

  const screenContext = useMemo(() => createScreenContext({
    data: { bewerbung: kopf.data ?? null, vorgaenge },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.erteileEinwilligung': () => handleAction('erteilen'),
      'personal.widerrufeEinwilligung': () => handleAction('widerrufen'),
      'personal.openBewerbungen': () => handleAction('zurueck'),
      'personal.openErklaerungen': () => handleAction('erklaerungen'),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, kopf.data, vorgaenge])

  if (!id) {
    return (
      <div className="space-y-6 p-3 md:p-6" role="status">
        Keine Bewerbung gewählt. Die Einwilligung öffnet sich aus der Bewerbungsliste.
      </div>
    )
  }

  if (kopf.isLoading || stand.isLoading) {
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
        entityId={id}
        screenContext={screenContext}
        workflowState={workflow}
        tables={{ vorgaenge }}
        onAction={handleAction}
      />
      <AlertDialog open={widerrufFragen} onOpenChange={(offen) => { if (!pending) setWiderrufFragen(offen) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Einwilligung widerrufen?</AlertDialogTitle>
            <AlertDialogDescription>
              Der Widerruf braucht keinen Grund und wirkt sofort. Danach ist die Bewerbung wieder
              löschfähig; ist die Frist abgelaufen, nimmt der nächste Löschlauf sie mit. Eine
              erneute Einwilligung ist möglich, solange die Daten noch da sind.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={pending !== null}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              disabled={pending !== null}
              onClick={(event) => {
                event.preventDefault()
                void widerrufen()
              }}
            >
              Widerrufen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
