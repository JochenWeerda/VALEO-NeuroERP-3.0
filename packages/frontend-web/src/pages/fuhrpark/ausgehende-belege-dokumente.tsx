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
  createFuhrparkAusgehendesDokument,
  deleteFuhrparkAusgehendesDokument,
  listFuhrparkAusgehendeDokumente,
  updateFuhrparkAusgehendesDokument,
  type FuhrparkAusgehendesDokumentPayload,
} from '@/lib/api/fuhrpark'
import { fuhrparkAusgehendeDokumenteScreen } from '@/masks/capture-screens'

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function optional(value: unknown): string | null {
  const raw = text(value)
  return raw || null
}

const leer = {
  beleg_typ: '',
  formular: '',
  ziel_modul: '',
  beschreibung: '',
  aktiv: true,
}

export default function AusgehendeBelegeDokumentePage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({
    queryKey: ['fuhrpark', 'ausgehende-dokumente'],
    queryFn: listFuhrparkAusgehendeDokumente,
  })
  const rows = useMemo(
    () => [...(liste.data ?? [])].sort((a, b) => a.beleg_typ.localeCompare(b.beleg_typ, 'de')),
    [liste.data],
  )
  const ohneFormular = rows.filter((row) => !row.formular).length
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [saving, setSaving] = useState(false)
  const createMutation = useMutation({ mutationFn: createFuhrparkAusgehendesDokument })
  const updateMutation = useMutation({
    mutationFn: (input: { id: string; payload: FuhrparkAusgehendesDokumentPayload }) =>
      updateFuhrparkAusgehendesDokument(input.id, input.payload),
  })
  const deleteMutation = useMutation({ mutationFn: deleteFuhrparkAusgehendesDokument })

  useEffect(() => {
    if (!liste.isError) return
    toast.error('Belege nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...fuhrparkAusgehendeDokumenteScreen,
    layout: {
      ...fuhrparkAusgehendeDokumenteScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (fuhrparkAusgehendeDokumenteScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'ohne_formular' ? ohneFormular : rows.length),
    })),
    actions: (fuhrparkAusgehendeDokumenteScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [isTouch, ohneFormular, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })

  const workflow = useMemo<WorkflowState>(() => {
    const keine = rows.length === 0
    const offen = ohneFormular > 0
    const label = keine ? 'Kein Belegtyp' : offen ? 'Formular offen' : 'Belege hinterlegt'
    const naechste = keine
      ? 'Beleg-Typ und Formular eintragen.'
      : offen
        ? `${ohneFormular} Belegtyp ohne Formular.`
        : selectedId
          ? 'Beleg ändern und speichern, oder Neu für einen weiteren Typ.'
          : 'Einen Belegtyp wählen oder einen neuen anlegen.'
    return {
      status: {
        currentStatus: keine ? 'leer' : offen ? 'offen' : 'hinterlegt',
        statusLabel: label,
        tone: keine || offen ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: keine || offen ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [ohneFormular, rows.length, selectedId])

  const leeren = useCallback(() => {
    setSelectedId(null)
    form.setValue('beleg_typ', '')
    form.setValue('formular', '')
    form.setValue('ziel_modul', '')
    form.setValue('beschreibung', '')
    form.setValue('aktiv', true)
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const belegTyp = text(form.values.beleg_typ)
    if (belegTyp.length < 2) {
      toast.error('Beleg-Typ fehlt', { description: 'Der Beleg-Typ braucht mindestens zwei Zeichen.' })
      return
    }
    const payload: FuhrparkAusgehendesDokumentPayload = {
      beleg_typ: belegTyp,
      formular: optional(form.values.formular),
      ziel_modul: optional(form.values.ziel_modul),
      beschreibung: optional(form.values.beschreibung),
      aktiv: form.values.aktiv !== false,
    }
    setSaving(true)
    try {
      if (selectedId) {
        await updateMutation.mutateAsync({ id: selectedId, payload })
        toast.success('Belegtyp gespeichert', { description: `${belegTyp} wurde aktualisiert.` })
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Belegtyp angelegt', { description: `${belegTyp} wurde erstellt.` })
      }
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'ausgehende-dokumente'] })
      leeren()
    } catch (error) {
      toast.error('Belegtyp nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [createMutation, form.values, leeren, queryClient, saving, selectedId, updateMutation])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Belegtyp gelöscht', { description: `${name} wurde entfernt.` })
      if (selectedId === id) leeren()
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'ausgehende-dokumente'] })
    } catch (error) {
      toast.error('Belegtyp nicht gelöscht', { description: getAxiosErrorMessage(error) })
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
      await loeschen(text(payload.id), text(payload.beleg_typ))
    }
  }, [leeren, loeschen, speichern])

  const selectRow = useCallback((row: Record<string, unknown>) => {
    setSelectedId(text(row.id))
    form.setValue('beleg_typ', text(row.beleg_typ))
    form.setValue('formular', text(row.formular))
    form.setValue('ziel_modul', text(row.ziel_modul))
    form.setValue('beschreibung', text(row.beschreibung))
    form.setValue('aktiv', row.aktiv === true || row.aktiv === 'JA')
  }, [form])

  const screenContext = useMemo(() => createScreenContext({
    data: { dokumente: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'fuhrpark.saveDokument': () => handleAction('speichern', {}),
      'fuhrpark.newDokument': () => handleAction('neu', {}),
      'fuhrpark.deleteDokument': (payload) => handleAction('loeschen', payload),
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
          dokumente: rows.map((row) => ({
            id: row.id,
            beleg_typ: row.beleg_typ,
            formular: row.formular ?? '',
            ziel_modul: row.ziel_modul ?? '',
            beschreibung: row.beschreibung ?? '',
            aktiv: row.aktiv ? 'JA' : 'NEIN',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
        onRowSelect={selectRow}
      />
    </div>
  )
}
