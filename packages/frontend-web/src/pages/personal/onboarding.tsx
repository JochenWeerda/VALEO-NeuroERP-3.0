import { useCallback, useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Skeleton } from '@/components/ui/skeleton'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { toast } from 'sonner'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import {
  personalKeys,
  useCreateOnboardingRun,
  type OnboardingRun,
  type OnboardingStatus,
} from '@/lib/api/personal'
import { personalOnboardingScreen } from '@/masks/capture-screens'

const STAND: Record<OnboardingStatus, string> = {
  not_started: 'Nicht gestartet',
  in_progress: 'In Bearbeitung',
  completed: 'Abgeschlossen',
  cancelled: 'Abgebrochen',
}

const leer = {
  employee_ref: '',
  checklist_id: '',
  assigned_by: '',
  due_date: '',
}

function text(value: unknown): string {
  return String(value ?? '').trim()
}

type ChecklistApi = { id: string; checklist_code: string; title: string }

type RunApi = {
  id: string
  checklist_id: string
  checklist_code?: string
  checklist_title?: string
  employee_ref: string
  assigned_by?: string | null
  due_date?: string | null
  status: OnboardingStatus
  progress_percent?: number
}

function toRun(item: RunApi): OnboardingRun {
  return {
    id: item.id,
    checklistId: item.checklist_id,
    checklistCode: item.checklist_code || undefined,
    checklistTitle: item.checklist_title || undefined,
    employeeRef: item.employee_ref,
    assignedBy: item.assigned_by || undefined,
    dueDate: item.due_date || undefined,
    status: item.status,
    progressPercent: Number(item.progress_percent ?? 0),
  }
}

export default function PersonalOnboardingPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const checklisten = useQuery({
    queryKey: personalKeys.onboardingChecklists(),
    queryFn: async () => (await apiClient.get<ChecklistApi[]>('/api/v1/training/onboarding/checklists')).data,
  })
  const laeufe = useQuery({
    queryKey: personalKeys.onboardingRuns(),
    queryFn: async () => {
      const rows = (await apiClient.get<RunApi[]>('/api/v1/training/onboarding/runs')).data
      return rows.map(toRun)
    },
  })
  const rows = laeufe.data ?? []
  const offen = rows.filter((row) => row.status !== 'completed').length
  const createMutation = useCreateOnboardingRun()
  const [saving, setSaving] = useState(false)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!laeufe.isError && !checklisten.isError) return
    const error = laeufe.error ?? checklisten.error
    toast.error('Onboarding nicht geladen', { description: getAxiosErrorMessage(error) })
  }, [checklisten.error, checklisten.isError, laeufe.error, laeufe.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalOnboardingScreen,
    layout: {
      ...personalOnboardingScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (personalOnboardingScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'offen' ? offen : rows.length),
    })),
    fields: (personalOnboardingScreen.fields ?? []).map((field) => (
      field.key === 'checklist_id'
        ? {
            ...field,
            options: (checklisten.data ?? []).map((entry) => ({
              value: entry.id,
              label: `${entry.checklist_code} – ${entry.title}`,
            })),
          }
        : field
    )),
    actions: (personalOnboardingScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [checklisten.data, isTouch, offen, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })

  const workflow = useMemo<WorkflowState>(() => {
    const keine = rows.length === 0
    const label = keine ? 'Kein Lauf' : offen > 0 ? 'Einarbeitung offen' : 'Läufe abgeschlossen'
    const naechste = keine
      ? 'Mitarbeiter-Referenz und Checkliste eintragen.'
      : offen > 0
        ? `${offen} Lauf noch nicht abgeschlossen.`
        : 'Einen weiteren Lauf anlegen.'
    return {
      status: {
        currentStatus: keine ? 'leer' : offen > 0 ? 'offen' : 'abgeschlossen',
        statusLabel: label,
        tone: keine || offen > 0 ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: keine || offen > 0 ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [offen, rows.length])

  const leeren = useCallback(() => {
    form.setValue('employee_ref', '')
    form.setValue('checklist_id', '')
    form.setValue('assigned_by', '')
    form.setValue('due_date', '')
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const employeeRef = text(form.values.employee_ref)
    const checklistId = text(form.values.checklist_id)
    if (!employeeRef || !checklistId) {
      toast.error('Lauf unvollständig', { description: 'Mitarbeiter-Referenz und Checkliste eintragen.' })
      return
    }
    setSaving(true)
    try {
      await createMutation.mutateAsync({
        checklistId,
        employeeRef,
        assignedBy: text(form.values.assigned_by) || undefined,
        dueDate: text(form.values.due_date) || undefined,
        status: 'not_started',
        progressPercent: 0,
      })
      toast.success('Onboarding-Lauf angelegt', { description: employeeRef })
      await queryClient.invalidateQueries({ queryKey: personalKeys.onboardingRuns() })
      leeren()
    } catch (error) {
      toast.error('Lauf nicht angelegt', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [createMutation, form.values, leeren, queryClient, saving])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await apiClient.delete(`/api/v1/training/onboarding/runs/${id}`)
      toast.success('Lauf gelöscht', { description: name })
      await queryClient.invalidateQueries({ queryKey: personalKeys.onboardingRuns() })
    } catch (error) {
      toast.error('Lauf nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [pendingDeletes, queryClient])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'speichern') {
      await speichern()
      return
    }
    if (key === 'neu') {
      leeren()
      return
    }
    if (key === 'loeschen') await loeschen(text(payload.id), text(payload.employee_ref))
  }, [leeren, loeschen, speichern])

  const screenContext = useMemo(() => createScreenContext({
    data: { laeufe: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.saveOnboarding': () => handleAction('speichern', {}),
      'personal.newOnboarding': () => handleAction('neu', {}),
      'personal.deleteOnboarding': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, rows])

  if (laeufe.isLoading || checklisten.isLoading) {
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
          laeufe: rows.map((row) => ({
            id: row.id,
            employee_ref: row.employeeRef,
            checkliste: row.checklistTitle || row.checklistCode || row.checklistId,
            status: STAND[row.status] ?? 'Nicht gestartet',
            fortschritt: `${row.progressPercent} %`,
            due_date: row.dueDate ? row.dueDate.slice(0, 10) : '',
            assigned_by: row.assignedBy ?? '',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
      />
    </div>
  )
}
