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
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFuhrparkRechnung,
  deleteFuhrparkRechnung,
  listFuhrparkRechnungen,
  updateFuhrparkRechnung,
  type FuhrparkRechnungPayload,
} from '@/lib/api/fuhrpark'
import { fuhrparkRechnungenScreen } from '@/masks/capture-screens'

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function optional(value: unknown): string | null {
  const raw = text(value)
  return raw || null
}

function betrag(value: unknown): number {
  if (value == null || value === '') return Number.NaN
  return Number(value)
}

const today = new Date().toISOString().slice(0, 10)

function leerwerte(datum = today): Record<string, string> {
  return {
    rechnungs_nr: '',
    datum,
    fahrzeug_kennzeichen: '',
    sachkonto: '',
    kostenart: '',
    betrag_eur: '',
    notiz: '',
  }
}

export default function FuhrparkRechnungenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({
    queryKey: ['fuhrpark', 'rechnungen'],
    queryFn: listFuhrparkRechnungen,
  })
  const rows = useMemo(
    () => [...(liste.data ?? [])].sort((a, b) => String(b.datum).localeCompare(String(a.datum))),
    [liste.data],
  )
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [saving, setSaving] = useState(false)
  const createMutation = useMutation({ mutationFn: createFuhrparkRechnung })
  const updateMutation = useMutation({
    mutationFn: (input: { id: string; payload: FuhrparkRechnungPayload }) =>
      updateFuhrparkRechnung(input.id, input.payload),
  })
  const deleteMutation = useMutation({ mutationFn: deleteFuhrparkRechnung })
  const summe = rows.reduce((acc, row) => acc + Number(row.betrag_eur || 0), 0)

  useEffect(() => {
    if (!liste.isError) return
    toast.error('Rechnungen nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...fuhrparkRechnungenScreen,
    layout: {
      ...fuhrparkRechnungenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (fuhrparkRechnungenScreen.summary ?? []).map((item) => ({
      ...item,
      value: item.key === 'betrag'
        ? summe.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
        : String(rows.length),
    })),
    actions: (fuhrparkRechnungenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [isTouch, rows.length, saving, summe])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({
    screen: schema,
    initialValues: leerwerte(),
  })

  const workflow = useMemo<WorkflowState>(() => {
    const leer = rows.length === 0
    const gewaehlt = Boolean(selectedId)
    const label = leer ? 'Keine Rechnung' : gewaehlt ? 'Rechnung gewählt' : 'Rechnungen hinterlegt'
    const naechste = leer
      ? 'Rechnungs-Nr, Datum und Betrag eintragen.'
      : gewaehlt
        ? 'Beleg ändern und speichern, oder Neu für eine weitere Rechnung.'
        : 'Eine Rechnung wählen oder eine neue anlegen.'
    return {
      status: {
        currentStatus: leer ? 'leer' : gewaehlt ? 'gewaehlt' : 'hinterlegt',
        statusLabel: label,
        tone: leer ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: leer ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [rows.length, selectedId])

  const leeren = useCallback(() => {
    setSelectedId(null)
    const werte = leerwerte()
    for (const [key, value] of Object.entries(werte)) form.setValue(key, value)
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const nummer = text(form.values.rechnungs_nr)
    const datum = text(form.values.datum)
    const wert = betrag(form.values.betrag_eur)
    if (nummer.length < 3 || !datum) {
      toast.error('Pflichtfelder fehlen', { description: 'Rechnungs-Nr mit mindestens drei Zeichen und ein Datum.' })
      return
    }
    if (!Number.isFinite(wert) || wert <= 0) {
      toast.error('Betrag fehlt', { description: 'Der Betrag muss größer als 0 sein.' })
      return
    }
    const payload: FuhrparkRechnungPayload = {
      rechnungs_nr: nummer,
      datum: `${datum}T00:00:00.000Z`,
      fahrzeug_kennzeichen: optional(form.values.fahrzeug_kennzeichen),
      sachkonto: optional(form.values.sachkonto),
      kostenart: optional(form.values.kostenart),
      betrag_eur: wert,
      notiz: optional(form.values.notiz),
    }
    setSaving(true)
    try {
      if (selectedId) {
        await updateMutation.mutateAsync({ id: selectedId, payload })
        toast.success('Rechnung gespeichert', { description: `${nummer} wurde aktualisiert.` })
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Rechnung angelegt', { description: `${nummer} wurde erstellt.` })
      }
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'rechnungen'] })
      leeren()
    } catch (error) {
      toast.error('Rechnung nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [createMutation, form.values, leeren, queryClient, saving, selectedId, updateMutation])

  const loeschen = useCallback(async (id: string, nummer: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Rechnung gelöscht', { description: `${nummer} wurde entfernt.` })
      if (selectedId === id) leeren()
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'rechnungen'] })
    } catch (error) {
      toast.error('Rechnung nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [deleteMutation, leeren, pendingDeletes, queryClient, selectedId])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'speichern') {
      await speichern()
      return
    }
    if (key === 'neu') {
      leeren()
      return
    }
    if (key === 'loeschen') {
      await loeschen(text(payload.id), text(payload.rechnungs_nr))
    }
  }, [leeren, loeschen, speichern])

  const selectRow = useCallback((row: Record<string, unknown>) => {
    setSelectedId(text(row.id))
    form.setValue('rechnungs_nr', text(row.rechnungs_nr))
    form.setValue('datum', text(row.datum).slice(0, 10))
    form.setValue('fahrzeug_kennzeichen', text(row.fahrzeug_kennzeichen))
    form.setValue('sachkonto', text(row.sachkonto))
    form.setValue('kostenart', text(row.kostenart))
    form.setValue('betrag_eur', String(row.betrag_eur ?? ''))
    form.setValue('notiz', text(row.notiz))
  }, [form])

  const screenContext = useMemo(() => createScreenContext({
    data: { rechnungen: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'fuhrpark.saveRechnung': () => handleAction('speichern', {}),
      'fuhrpark.newRechnung': () => handleAction('neu', {}),
      'fuhrpark.deleteRechnung': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, rows])

  if (liste.isLoading) {
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
          rechnungen: rows.map((row) => ({
            id: row.id,
            rechnungs_nr: row.rechnungs_nr,
            datum: String(row.datum).slice(0, 10),
            fahrzeug_kennzeichen: row.fahrzeug_kennzeichen ?? '',
            sachkonto: row.sachkonto ?? '',
            kostenart: row.kostenart ?? '',
            betrag_eur: row.betrag_eur,
            notiz: row.notiz ?? '',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
        onRowSelect={selectRow}
      />
    </div>
  )
}
