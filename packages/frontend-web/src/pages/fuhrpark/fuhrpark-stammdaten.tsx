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
  createFuhrparkTerminart,
  deleteFuhrparkTerminart,
  listFuhrparkTerminarten,
  updateFuhrparkTerminart,
} from '@/lib/api/fuhrpark'
import { fuhrparkTerminartenScreen } from '@/masks/capture-screens'

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function ganzzahl(value: unknown): number {
  if (value == null || value === '') return 0
  return Number(value)
}

export default function FuhrparkStammdatenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({
    queryKey: ['fuhrpark', 'terminarten'],
    queryFn: listFuhrparkTerminarten,
  })
  const rows = liste.data ?? []
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [saving, setSaving] = useState(false)

  const createMutation = useMutation({ mutationFn: createFuhrparkTerminart })
  const updateMutation = useMutation({
    mutationFn: (payload: { id: string; terminart: string; intervall_monate: number; intervall_km: number }) =>
      updateFuhrparkTerminart(payload.id, {
        terminart: payload.terminart,
        intervall_monate: payload.intervall_monate,
        intervall_km: payload.intervall_km,
      }),
  })
  const deleteMutation = useMutation({ mutationFn: deleteFuhrparkTerminart })

  useEffect(() => {
    if (!liste.isError) return
    toast.error('Terminarten nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...fuhrparkTerminartenScreen,
    layout: {
      ...fuhrparkTerminartenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (fuhrparkTerminartenScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(rows.length),
    })),
    actions: (fuhrparkTerminartenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [isTouch, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({
    screen: schema,
    initialValues: {
      terminart: '',
      intervall_monate: '',
      intervall_km: '',
    },
  })

  const workflow = useMemo<WorkflowState>(() => {
    const leer = rows.length === 0
    const gewaehlt = Boolean(selectedId)
    const label = leer ? 'Keine Terminart' : gewaehlt ? 'Terminart gewählt' : 'Terminarten hinterlegt'
    const naechste = leer
      ? 'Bezeichnung eintragen.'
      : gewaehlt
        ? 'Intervall ändern und speichern, oder Neu für eine weitere Art.'
        : 'Eine Terminart wählen oder eine neue anlegen.'
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
    form.setValue('terminart', '')
    form.setValue('intervall_monate', '')
    form.setValue('intervall_km', '')
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const terminart = text(form.values.terminart)
    const monate = ganzzahl(form.values.intervall_monate)
    const km = ganzzahl(form.values.intervall_km)
    if (terminart.length < 2) {
      toast.error('Bezeichnung fehlt', { description: 'Die Terminart braucht mindestens zwei Zeichen.' })
      return
    }
    if (!Number.isInteger(monate) || monate < 0 || !Number.isInteger(km) || km < 0) {
      toast.error('Ungültiges Intervall', { description: 'Monate und Kilometer sind ganze Zahlen ab 0.' })
      return
    }
    setSaving(true)
    try {
      const payload = { terminart, intervall_monate: monate, intervall_km: km }
      if (selectedId) {
        await updateMutation.mutateAsync({ id: selectedId, ...payload })
        toast.success('Terminart gespeichert', { description: `${terminart} wurde aktualisiert.` })
      } else {
        await createMutation.mutateAsync(payload)
        toast.success('Terminart angelegt', { description: `${terminart} wurde erstellt.` })
      }
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'terminarten'] })
      leeren()
    } catch (error) {
      toast.error('Terminart nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [createMutation, form.values, leeren, queryClient, saving, selectedId, updateMutation])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Terminart gelöscht', { description: `${name} wurde entfernt.` })
      if (selectedId === id) leeren()
      await queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'terminarten'] })
    } catch (error) {
      toast.error('Terminart nicht gelöscht', { description: getAxiosErrorMessage(error) })
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
      await loeschen(text(payload.id), text(payload.terminart))
    }
  }, [leeren, loeschen, speichern])

  const selectRow = useCallback((row: Record<string, unknown>) => {
    const id = text(row.id)
    setSelectedId(id)
    form.setValue('terminart', text(row.terminart))
    form.setValue('intervall_monate', String(row.intervall_monate ?? ''))
    form.setValue('intervall_km', String(row.intervall_km ?? ''))
  }, [form])

  const screenContext = useMemo(() => createScreenContext({
    data: { terminarten: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'fuhrpark.saveTerminart': () => handleAction('speichern', {}),
      'fuhrpark.newTerminart': () => handleAction('neu', {}),
      'fuhrpark.deleteTerminart': (payload) => handleAction('loeschen', payload),
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
          terminarten: rows.map((row) => ({
            id: row.id,
            terminart: row.terminart,
            intervall_monate: row.intervall_monate,
            intervall_km: row.intervall_km,
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
        onRowSelect={selectRow}
      />
    </div>
  )
}
