import { useCallback, useEffect, useMemo, useState } from 'react'
import { Skeleton } from '@/components/ui/skeleton'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { toast } from 'sonner'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import {
  useCreateLieferavis,
  useCreateVersandprofil,
  useDeleteVersandprofil,
  useLieferavise,
  useVersandprofile,
  type Versandart,
} from '@/lib/api/versandprofile'
import { versandprofileScreen } from '@/masks/capture-screens'

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function optional(value: unknown): string | null {
  const raw = text(value)
  return raw || null
}

function menge(value: unknown): number | null {
  if (value == null || value === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const today = new Date().toISOString().slice(0, 10)

export default function VersandprofilePage(): JSX.Element {
  const isTouch = useTouchDevice()
  const profileQuery = useVersandprofile()
  const avisQuery = useLieferavise()
  const createProfil = useCreateVersandprofil()
  const deleteProfil = useDeleteVersandprofil()
  const createAvis = useCreateLieferavis()
  const profile = profileQuery.data ?? []
  const avise = avisQuery.data ?? []
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [savingProfil, setSavingProfil] = useState(false)
  const [savingAvis, setSavingAvis] = useState(false)

  useEffect(() => {
    if (!profileQuery.isError) return
    toast.error('Versandprofile nicht geladen', { description: getAxiosErrorMessage(profileQuery.error) })
  }, [profileQuery.error, profileQuery.isError])

  useEffect(() => {
    if (!avisQuery.isError) return
    toast.error('Lieferavise nicht geladen', { description: getAxiosErrorMessage(avisQuery.error) })
  }, [avisQuery.error, avisQuery.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...versandprofileScreen,
    layout: {
      ...versandprofileScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (versandprofileScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'profile' ? profile.length : avise.length),
    })),
    actions: (versandprofileScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'profil' ? savingProfil : action.key === 'avis' ? savingAvis : false,
    })),
  }), [avise.length, isTouch, profile.length, savingAvis, savingProfil])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({
    screen: schema,
    initialValues: {
      profil_nr: '',
      bezeichnung: '',
      versandart: 'email',
      absender_email: '',
      absender_name: '',
      betreff_vorlage: '',
      avis_datum: today,
      lieferdatum_erwartet: '',
      lieferant_nr: '',
      kunden_nr: '',
      artikel_nr: '',
      menge: '',
      notiz: '',
    },
  })

  const workflow = useMemo<WorkflowState>(() => {
    const leer = profile.length === 0
    const label = leer ? 'Kein Profil' : 'Profile hinterlegt'
    const naechste = leer
      ? 'Profil-Nr und Bezeichnung eintragen.'
      : avise.length === 0
        ? 'Ein Lieferavis ist optional.'
        : `${avise.length} Lieferavise hinterlegt.`
    return {
      status: {
        currentStatus: leer ? 'leer' : 'hinterlegt',
        statusLabel: label,
        tone: leer ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'profil', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: leer ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [avise.length, profile.length])

  const speichern = useCallback(async () => {
    if (savingProfil) return
    const profilNr = text(form.values.profil_nr)
    const bezeichnung = text(form.values.bezeichnung)
    if (!profilNr || !bezeichnung) {
      toast.error('Pflichtfelder fehlen', { description: 'Profil-Nr und Bezeichnung sind erforderlich.' })
      return
    }
    setSavingProfil(true)
    try {
      await createProfil.mutateAsync({
        profil_nr: profilNr,
        bezeichnung,
        versandart: (text(form.values.versandart) || 'email') as Versandart,
        absender_email: optional(form.values.absender_email),
        absender_name: optional(form.values.absender_name),
        betreff_vorlage: optional(form.values.betreff_vorlage),
        archiv_kennzeichen: true,
      })
      toast.success('Versandprofil angelegt', { description: `Profil ${profilNr} wurde erstellt.` })
      form.setValue('profil_nr', '')
      form.setValue('bezeichnung', '')
      form.setValue('versandart', 'email')
      form.setValue('absender_email', '')
      form.setValue('absender_name', '')
      form.setValue('betreff_vorlage', '')
    } catch (error) {
      toast.error('Versandprofil nicht angelegt', { description: getAxiosErrorMessage(error) })
    } finally {
      setSavingProfil(false)
    }
  }, [createProfil, form, savingProfil])

  const avisSpeichern = useCallback(async () => {
    if (savingAvis) return
    const datum = text(form.values.avis_datum)
    if (!datum) {
      toast.error('Pflichtfeld fehlt', { description: 'Avis-Datum ist erforderlich.' })
      return
    }
    setSavingAvis(true)
    try {
      await createAvis.mutateAsync({
        avis_datum: datum,
        lieferdatum_erwartet: optional(form.values.lieferdatum_erwartet),
        lieferant_nr: optional(form.values.lieferant_nr),
        kunden_nr: optional(form.values.kunden_nr),
        artikel_nr: optional(form.values.artikel_nr),
        menge: menge(form.values.menge),
        notiz: optional(form.values.notiz),
      })
      toast.success('Lieferavis angelegt', { description: `Avis für ${datum} wurde erstellt.` })
      form.setValue('avis_datum', today)
      form.setValue('lieferdatum_erwartet', '')
      form.setValue('lieferant_nr', '')
      form.setValue('kunden_nr', '')
      form.setValue('artikel_nr', '')
      form.setValue('menge', '')
      form.setValue('notiz', '')
    } catch (error) {
      toast.error('Lieferavis nicht angelegt', { description: getAxiosErrorMessage(error) })
    } finally {
      setSavingAvis(false)
    }
  }, [createAvis, form, savingAvis])

  const loeschen = useCallback(async (profilNr: string) => {
    if (!profilNr || pendingDeletes.has(profilNr)) return
    setPendingDeletes((prev) => new Set(prev).add(profilNr))
    try {
      await deleteProfil.mutateAsync(profilNr)
      toast.success('Versandprofil gelöscht', { description: `Profil ${profilNr} wurde deaktiviert.` })
    } catch (error) {
      toast.error('Profil nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(profilNr)
        return next
      })
    }
  }, [deleteProfil, pendingDeletes])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'profil') {
      await speichern()
      return
    }
    if (key === 'avis') {
      await avisSpeichern()
      return
    }
    if (key === 'loeschen') {
      await loeschen(text(payload.profil_nr))
    }
  }, [avisSpeichern, loeschen, speichern])

  const screenContext = useMemo(() => createScreenContext({
    data: { profile, avise },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'versand.saveProfile': () => handleAction('profil', {}),
      'versand.saveAvis': () => handleAction('avis', {}),
      'versand.deleteProfile': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [avise, form.values, handleAction, profile])

  if (profileQuery.isLoading || avisQuery.isLoading) {
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
          profile: profile.map((eintrag) => ({
            id: eintrag.id,
            profil_nr: eintrag.profil_nr,
            bezeichnung: eintrag.bezeichnung,
            versandart: eintrag.versandart,
            absender_email: eintrag.absender_email ?? '',
            gesperrt: pendingDeletes.has(eintrag.profil_nr),
          })),
          avise: avise.map((eintrag) => ({
            id: eintrag.id,
            avis_datum: eintrag.avis_datum,
            lieferdatum_erwartet: eintrag.lieferdatum_erwartet ?? '',
            lieferant_nr: eintrag.lieferant_nr ?? eintrag.kunden_nr ?? '',
            artikel_nr: eintrag.artikel_nr ?? '',
            menge: eintrag.menge ?? '',
            notiz: eintrag.notiz ?? '',
          })),
        }}
        onAction={handleAction}
      />
    </div>
  )
}
