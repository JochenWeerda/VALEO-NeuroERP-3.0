import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
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
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFuhrparkFahrzeug,
  deleteFuhrparkFahrzeug,
  getFuhrparkFahrzeug,
  printFuhrparkAkte,
  setupFuhrparkDrucker,
  unfallAnzeige,
  updateFuhrparkFahrzeug,
  type FuhrparkFahrzeug,
  type FuhrparkFahrzeugPayload,
} from '@/lib/api/fuhrpark'
import { fuhrparkFahrzeugStammScreen } from '@/masks/capture-screens'

const DRUCKER = 'Groothusen/Kyocera M3540dn Fach 1'
const DATUM = [
  'erstzulassung',
  'bestelldatum',
  'kaufdatum',
  'verkaufsdatum',
  'abmeldedatum',
  'naechster_tuev_termin',
  'naechster_asu_termin',
  'naechste_inspektion',
] as const
const JA_NEIN = [
  'is_neu',
  'fahrtenschreiber_vorhanden',
  'ahk_vorhanden',
  'ladekran_vorhanden',
  'km_stand_alle_eintraege',
  'versicherung_haftpflicht',
  'versicherung_kasko',
  'winterreifen_vorhanden',
  'winterreifen_eingelagert',
  'handy_freisprecheinrichtung',
] as const
const GANZE = ['afa_jahre', 'leasingdauer_monate'] as const
const ZAHLEN = [
  'leistung_kw',
  'kaufsumme_eur',
  'afa_eur_jaehrlich',
  'afa_eur_monatlich',
  'leasingrate_eur',
  'kfz_steuer_eur',
  'versicherung_satz_eur_monat',
  'leergewicht_kg',
  'nutzlast_kg',
  'gesamtgewicht_kg',
  'anhaengerlast_kg',
] as const
const TEXTE = [
  'ro_nummer',
  'betrieb',
  'bereich',
  'pol_kennzeichen',
  'kennzeichen',
  'verwendung',
  'kfz_brief_nummer',
  'typ',
  'schadstoffgruppe',
  'kraftstoff',
  'fahrgestellnummer',
  'ausstattung',
  'fahrer_name',
  'fahrer_vorname',
  'bestellnummer',
  'haendler',
  'zustand',
  'kostenstelle',
  'abschreibungsart',
  'leasinggesellschaft',
  'kfz_steuernummer',
  'kontierung',
  'finanzamt',
  'versicherungs_gesellschaft',
  'versicherungsschein_nr',
  'handy_fabrikat',
  'handy_rufnummer',
] as const
const AKTEN_AKTIONEN = ['drucker', 'drucken', 'unfall', 'loeschen']

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function dateOnly(value: unknown): string {
  const raw = text(value)
  return raw ? raw.slice(0, 10) : ''
}

function parseDate(value: unknown): string | null {
  const raw = dateOnly(value)
  return raw ? `${raw}T00:00:00.000Z` : null
}

function nummer(value: unknown): number | undefined {
  if (value == null || value === '') return undefined
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : undefined
}

function leerwerte(): Record<string, unknown> {
  const values: Record<string, unknown> = {
    zustand: 'neu',
    kilometerstand: '',
    drucker_name: DRUCKER,
    unfall_ort: '',
    unfall_beschreibung: '',
  }
  for (const key of TEXTE) values[key] = key === 'zustand' ? 'neu' : ''
  for (const key of DATUM) values[key] = ''
  for (const key of JA_NEIN) values[key] = false
  for (const key of GANZE) values[key] = ''
  for (const key of ZAHLEN) values[key] = ''
  return values
}

export default function FuhrparkFahrzeugStammPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const isNew = !id || id === 'neu'
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const fahrzeugQuery = useQuery({
    queryKey: ['fuhrpark', 'fahrzeug', id],
    queryFn: () => getFuhrparkFahrzeug(id as string),
    enabled: !isNew,
  })
  const geladen = useRef<FuhrparkFahrzeug | null>(null)
  const applied = useRef<string | null>(null)
  const [pending, setPending] = useState<Set<string>>(new Set())
  const form = useUniversalFormState({
    screen: fuhrparkFahrzeugStammScreen,
    initialValues: leerwerte(),
  })

  useEffect(() => {
    if (!fahrzeugQuery.isError) return
    toast.error('Fahrzeug nicht geladen', { description: getAxiosErrorMessage(fahrzeugQuery.error) })
  }, [fahrzeugQuery.error, fahrzeugQuery.isError])

  const uebernehmen = useCallback((row: FuhrparkFahrzeug) => {
    geladen.current = row
    for (const key of TEXTE) form.setValue(key, text(row[key]))
    for (const key of DATUM) form.setValue(key, dateOnly(row[key]))
    for (const key of JA_NEIN) form.setValue(key, row[key] === true)
    for (const key of GANZE) form.setValue(key, row[key] ?? '')
    for (const key of ZAHLEN) form.setValue(key, row[key] ?? '')
    form.setValue('kilometerstand', row.kilometerstand ?? '')
    form.setValue('zustand', text(row.zustand) || 'neu')
  }, [form])

  useEffect(() => {
    const row = fahrzeugQuery.data
    if (!row || applied.current === row.id) return
    applied.current = row.id
    uebernehmen(row)
  }, [fahrzeugQuery.data, uebernehmen])

  const schema = useMemo<ScreenDefinition>(() => {
    const km = nummer(form.values.kilometerstand)
    const tuev = dateOnly(form.values.naechster_tuev_termin)
    return {
      ...fuhrparkFahrzeugStammScreen,
      layout: {
        ...fuhrparkFahrzeugStammScreen.layout,
        density: isTouch ? 'comfortable' : 'compact',
      },
      summary: (fuhrparkFahrzeugStammScreen.summary ?? []).map((item) => ({
        ...item,
        value: item.key === 'tuev' ? (tuev || 'offen') : String(km ?? 0),
      })),
      actions: (fuhrparkFahrzeugStammScreen.actions ?? []).map((action) => ({
        ...action,
        disabled: pending.has(action.key) || (AKTEN_AKTIONEN.includes(action.key) && isNew),
      })),
    }
  }, [form.values.kilometerstand, form.values.naechster_tuev_termin, isNew, isTouch, pending])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])

  const workflow = useMemo<WorkflowState>(() => {
    const kennzeichen = text(form.values.kennzeichen)
    const typ = text(form.values.typ)
    const offen = kennzeichen.length < 2 || typ.length < 2
    const label = offen ? 'Stamm offen' : isNew ? 'Bereit zum Speichern' : 'Fahrzeug hinterlegt'
    const naechste = offen
      ? 'Kennzeichen und Typ eintragen.'
      : isNew
        ? 'Speichern legt die Akte an.'
        : 'Akte ändern oder einen Termin nachtragen.'
    return {
      status: {
        currentStatus: offen ? 'offen' : isNew ? 'bereit' : 'hinterlegt',
        statusLabel: label,
        tone: offen ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: offen ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [form.values.kennzeichen, form.values.typ, isNew])

  const payload = useCallback((): FuhrparkFahrzeugPayload => {
    const basis = geladen.current
    const werte = form.values
    const gebaut: Record<string, unknown> = {
      kennzeichen: text(werte.kennzeichen),
      typ: text(werte.typ),
      zustand: text(werte.zustand) || 'neu',
      kilometerstand: nummer(werte.kilometerstand) ?? 0,
      status: basis?.status || 'verfuegbar',
      marke: basis?.marke ?? null,
      modell: basis?.modell ?? null,
      baujahr: basis?.baujahr ?? null,
    }
    for (const key of TEXTE) {
      if (key === 'kennzeichen' || key === 'typ' || key === 'zustand') continue
      gebaut[key] = text(werte[key]) || null
    }
    for (const key of DATUM) gebaut[key] = parseDate(werte[key])
    for (const key of JA_NEIN) gebaut[key] = werte[key] === true
    for (const key of GANZE) gebaut[key] = nummer(werte[key]) == null ? null : Math.trunc(nummer(werte[key]) as number)
    for (const key of ZAHLEN) gebaut[key] = nummer(werte[key]) ?? null
    return gebaut as FuhrparkFahrzeugPayload
  }, [form.values])

  const mitPending = useCallback(async (key: string, work: () => Promise<void>) => {
    if (pending.has(key)) return
    setPending((prev) => new Set(prev).add(key))
    try {
      await work()
    } finally {
      setPending((prev) => {
        const next = new Set(prev)
        next.delete(key)
        return next
      })
    }
  }, [pending])

  const speichern = useCallback(async () => {
    const kennzeichen = text(form.values.kennzeichen)
    const typ = text(form.values.typ)
    if (kennzeichen.length < 2 || kennzeichen.length > 20) {
      toast.error('Kennzeichen fehlt', { description: 'Das Kennzeichen braucht 2 bis 20 Zeichen.' })
      return
    }
    if (typ.length < 2 || typ.length > 50) {
      toast.error('Typ fehlt', { description: 'Der Typ braucht 2 bis 50 Zeichen.' })
      return
    }
    const body = payload()
    await mitPending('speichern', async () => {
      try {
        const saved = isNew
          ? await createFuhrparkFahrzeug(body)
          : await updateFuhrparkFahrzeug(id as string, body)
        toast.success('Fahrzeug gespeichert', { description: saved.kennzeichen })
        await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'fahrzeuge'] })
        await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'fahrzeug', saved.id] })
        if (isNew) navigate(`/fuhrpark/fahrzeug/${saved.id}`)
        else uebernehmen(saved)
      } catch (error) {
        toast.error('Fahrzeug nicht gespeichert', { description: getAxiosErrorMessage(error) })
      }
    })
  }, [form.values.kennzeichen, form.values.typ, id, isNew, mitPending, navigate, payload, queryClient, uebernehmen])

  const loeschen = useCallback(async () => {
    if (isNew || !id || pending.has('loeschen')) return
    if (!window.confirm('Fahrzeug wirklich löschen? Dieser Vorgang ist nicht rückgängig.')) return
    await mitPending('loeschen', async () => {
      try {
        await deleteFuhrparkFahrzeug(id)
        toast.success('Fahrzeug gelöscht')
        await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'fahrzeuge'] })
        navigate('/fuhrpark/fahrzeuge')
      } catch (error) {
        toast.error('Fahrzeug nicht gelöscht', { description: getAxiosErrorMessage(error) })
      }
    })
  }, [id, isNew, mitPending, navigate, pending, queryClient])

  const drucker = useCallback(async () => {
    if (isNew || !id) return
    const name = text(form.values.drucker_name)
    if (name.length < 2) {
      toast.error('Drucker fehlt', { description: 'Der Druckername braucht mindestens zwei Zeichen.' })
      return
    }
    await mitPending('drucker', async () => {
      try {
        await setupFuhrparkDrucker(id, name)
        toast.success('Drucker eingerichtet', { description: name })
      } catch (error) {
        toast.error('Drucker nicht eingerichtet', { description: getAxiosErrorMessage(error) })
      }
    })
  }, [form.values.drucker_name, id, isNew, mitPending])

  const drucken = useCallback(async () => {
    if (isNew || !id) return
    await mitPending('drucken', async () => {
      try {
        await printFuhrparkAkte(id)
        toast.success('Fahrzeugakte gedruckt')
      } catch (error) {
        toast.error('Akte nicht gedruckt', { description: getAxiosErrorMessage(error) })
      }
    })
  }, [id, isNew, mitPending])

  const unfall = useCallback(async () => {
    if (isNew || !id) return
    const ort = text(form.values.unfall_ort)
    const beschreibung = text(form.values.unfall_beschreibung)
    if (ort.length < 2 || beschreibung.length < 3) {
      toast.error('Unfallanzeige unvollständig', { description: 'Ort und Beschreibung eintragen.' })
      return
    }
    await mitPending('unfall', async () => {
      try {
        await unfallAnzeige(id, { datum: new Date().toISOString(), ort, beschreibung })
        toast.success('Unfallanzeige erfasst', { description: ort })
        form.setValue('unfall_ort', '')
        form.setValue('unfall_beschreibung', '')
      } catch (error) {
        toast.error('Unfallanzeige nicht erfasst', { description: getAxiosErrorMessage(error) })
      }
    })
  }, [form, id, isNew, mitPending])

  const handleAction = useCallback(async (key: string) => {
    if (key === 'speichern') await speichern()
    else if (key === 'liste') navigate('/fuhrpark/fahrzeuge')
    else if (key === 'drucker') await drucker()
    else if (key === 'drucken') await drucken()
    else if (key === 'unfall') await unfall()
    else if (key === 'loeschen') await loeschen()
  }, [drucken, drucker, loeschen, navigate, speichern, unfall])

  const screenContext = useMemo(() => createScreenContext({
    data: { fahrzeug: geladen.current },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'fuhrpark.saveFahrzeug': () => handleAction('speichern'),
      'fuhrpark.openFahrzeugListe': () => handleAction('liste'),
      'fuhrpark.setupDrucker': () => handleAction('drucker'),
      'fuhrpark.printAkte': () => handleAction('drucken'),
      'fuhrpark.reportUnfall': () => handleAction('unfall'),
      'fuhrpark.deleteFahrzeug': () => handleAction('loeschen'),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, navigate])

  if (!isNew && fahrzeugQuery.isLoading) {
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
        onAction={handleAction}
      />
    </div>
  )
}
